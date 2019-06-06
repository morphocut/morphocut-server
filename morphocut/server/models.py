from sqlalchemy import Table, Column, ForeignKey, Index

import datetime

from sqlalchemy.types import Integer, BigInteger, String, DateTime, PickleType, Boolean, Text, Float
from sqlalchemy.sql.schema import UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from sqlalchemy.sql import func
from morphocut.server.extensions import database, redis_queue
from morphocut.server.worker import redis_conn
from flask_user import current_user, login_required, roles_required, UserManager, UserMixin
import redis
import rq

metadata = database.metadata

#: :type datasets: sqlalchemy.sql.schema.Table
projects = Table('projects', metadata,
                 Column('project_id', Integer, primary_key=True),
                 Column('name', String),
                 Column('path', String),
                 Column('active', Boolean),
                 Column('creation_date', DateTime,
                        default=datetime.datetime.now),
                 Column('user_id', Integer, ForeignKey(
                     'users.id'), index=True),
                 )


#: :type objects: sqlalchemy.sql.schema.Table
objects = Table('objects', metadata,
                Column('object_id', Integer, primary_key=True),
                Column('filename', String),
                Column('creation_date', DateTime,
                       default=datetime.datetime.now),
                Column('modification_date', DateTime,
                       default=datetime.datetime.now),
                Column('project_id', Integer, ForeignKey(
                    'projects.project_id', ondelete="CASCADE"), index=True),
                )


class User(database.Model, UserMixin):
    """SQLAlchemy model of the User table.

    This defines the database representation of users based on the Flask-User framework.

    Attributes
    ----------
    id : str
        The id of the user.
    active : str
        The activate state of the user.
    username : str
        The name of the user.
    password : int
        The password of the user.

    """
    __tablename__ = 'users'
    id = database.Column(
        database.Integer(), primary_key=True)
    active = database.Column('is_active', database.Boolean(),
                             nullable=False, server_default='1')
    email = database.Column(database.String(255),
                            nullable=False, unique=True)
    password = database.Column(database.String(
        255), nullable=False, server_default='')

    # Define the relationship to Role via UserRoles
    roles = database.relationship('Role', secondary='user_roles')

    def launch_task(self, name, description, project_id, *args, job_timeout=360000, **kwargs):
        """Enqueues a job with the given function name which is called with the given *args and **kwargs.

        The job will be stored in the database with relations this user and the project with the given id.

        Parameters
        ----------
        name : str
            The full name of the function, including the modules, that should be enqueued.
        description : str
            The description of the function that should be enqueued.
        project_id : int
            The id of the project that the job belongs to.
        job_timeout : int, optional
            The time in seconds until the job gets stopped.
        *args
            Variable length argument list. Will be passed to the function.
        *kwargs
            Arbitrary keyword arguments. Will be passed to the function.

        Returns
        -------
        task : models.Task
            The task object connected to the enqueued job.

        """
        rq_job = redis_queue.enqueue('morphocut.server.tasks.execute_task_and_save_result',
                                     name, *args, **kwargs,
                                     job_timeout=job_timeout)
        task = Task(id=rq_job.get_id(), name=name, description=description,
                    user_id=self.id, project_id=project_id)
        database.session.add(task)
        database.session.commit()
        return task

    def get_tasks_in_progress(self):
        """Get the unfinished tasks belonging to this user.

        Returns
        -------
        tasks : list
            The unfinished tasks of this user.

        """
        tasks = Task.query.filter_by(
            user_id=self.id, complete=False).all()
        failed_tasks = []
        for task in tasks:
            job = task.get_rq_job()
            if job:
                if job.get_status() == 'failed':
                    failed_tasks.append(task)
        return [t for t in tasks if t not in failed_tasks]

    def get_finished_tasks(self):
        """Get the finished tasks belonging to this user.

        Returns
        -------
        tasks : list
            The finished tasks of this user.

        """
        return Task.query.filter_by(user_id=self.id, complete=True).all()

    def get_task_in_progress(self, name):
        """Get the unfinished tasks with the specified name belonging to this user.

        Parameters
        -------
        name : str
            The name of the tasks that should be returned.

        Returns
        -------
        tasks : list
            The unfinished tasks with the specified name of this user.

        """
        return Task.query.filter_by(name=name, user_id=self.id,
                                    complete=False).first()

    def get_project_tasks_in_progress(self, project_id):
        """Get the unfinished tasks of the project with the given id belonging to this user.

        Parameters
        ----------
        project_id : int
            The id of the project that the jobs belong to.

        Returns
        -------
        tasks : list
            The unfinished tasks of this user and the given project.

        """
        tasks = Task.query.filter_by(
            user_id=self.id, complete=False, project_id=project_id).all()
        failed_tasks = []
        for task in tasks:
            job = task.get_rq_job()
            if job:
                if job.get_status() == 'failed':
                    failed_tasks.append(task)
        return [t for t in tasks if t not in failed_tasks]

    def get_finished_project_tasks(self, project_id):
        """Get the finished tasks of the project with the given id belonging to this user.

        Parameters
        ----------
        project_id : int
            The id of the project that the job belongs to.

        Returns
        -------
        tasks : list
            The finished tasks of this user and the given project.

        """
        return Task.query.filter_by(user_id=self.id, complete=True, project_id=project_id).all()


class Role(database.Model):
    """SQLAlchemy model of the Role table.

    This defines the different roles the users can have.

    Attributes
    ----------
    id : str
        The id of the role.
    name : str
        The name of the role.

    """
    __tablename__ = 'roles'
    id = database.Column(database.Integer(), primary_key=True)
    name = database.Column(database.String(50), unique=True)


class UserRoles(database.Model):
    """SQLAlchemy model of the UserRoles table.

    This defines the relation of users and roles.

    Attributes
    ----------
    id : str
        The id of the UserRole.
    user_id : str
        The if of the user.
    role_id : str
        The id of the role.

    """
    __tablename__ = 'user_roles'
    id = database.Column(database.Integer(), primary_key=True)
    user_id = database.Column(database.Integer(), database.ForeignKey(
        'users.id', ondelete='CASCADE'))
    role_id = database.Column(database.Integer(), database.ForeignKey(
        'roles.id', ondelete='CASCADE'))


class Task(database.Model):
    """SQLAlchemy model of the Task table. 

    This defines the database representation of the redis jobs. Each task has a redis job with the same id connected to it.

    Attributes
    ----------
    id : str
        The id of the task. This is equivalent to the id of the connected redis job.
    name : str
        The full name of the function that is executed in this task.
    description : str
        The description of this task.
    user_id : int
        The id of the user this task belongs to.
    project_id : int
        The id of the project this task belongs to.
    complete : bool
        True when the redis job connected to this task is finished.
    result : str
        The result of the function executed in this task.

    """
    id = database.Column(database.String(36), primary_key=True)
    name = database.Column(database.String(128), index=True)
    description = database.Column(database.String(128))
    user_id = database.Column(
        database.Integer, database.ForeignKey('users.id'))
    project_id = database.Column(
        database.Integer, database.ForeignKey('projects.project_id', ondelete="CASCADE"))
    complete = database.Column(database.Boolean, default=False)
    result = database.Column(database.String())

    def get_rq_job(self):
        """Get the redis job connected to this task.

        Returns
        -------
        job : redis.Job
            The redis job connected to this task.

        """
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=redis_conn)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        """Get the progress of the redis job connected to this task.

        The progress is 0 when no progress is stored in the job object.
        The progress is 100 when there is no redis job connected to this task anymore, e.g. when the job is finished.

        Returns
        -------
        progress : int
            The progress of the redis job connected to this task.

        """
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100
