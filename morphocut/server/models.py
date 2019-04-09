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


#: :type objects: sqlalchemy.sql.schema.Table
# users = Table('users', metadata,
#               Column('user_id', Integer, primary_key=True),
#               Column('username', String),
#               Column('pwhash', String),
#               Column('admin', Boolean, default=False),
#               )


class User(database.Model, UserMixin):
    __tablename__ = 'users'
    id = database.Column(
        database.Integer(), primary_key=True)
    active = database.Column('is_active', database.Boolean(),
                             nullable=False, server_default='1')

    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    # email = database.Column(database.String(255),
    #                         nullable=False, unique=True)
    # email_confirmed_at = database.Column(database.DateTime())
    username = database.Column(database.String(255),
                               nullable=False, unique=True)
    password = database.Column(database.String(
        255), nullable=False, server_default='')

    # User information
    # first_name = database.Column(database.String(100),
    #                              nullable=False, server_default='')
    # last_name = database.Column(database.String(100),
    #                             nullable=False, server_default='')

    # Define the relationship to Role via UserRoles
    roles = database.relationship('Role', secondary='user_roles')

    def launch_task(self, name, description, project_id, *args, **kwargs):
        '''
        enqueue job with a maximum runtime of 10 hours
        '''
        rq_job = redis_queue.enqueue(name,
                                     *args, **kwargs, timeout=36000)
        task = Task(id=rq_job.get_id(), name=name, description=description,
                    user_id=self.id, project_id=project_id)
        database.session.add(task)
        return task, rq_job

    def get_tasks_in_progress(self):
        tasks = Task.query.filter_by(
            user_id=self.id, complete=False).all()
        failed_tasks = []
        for task in tasks:
            job = task.get_rq_job()
            if job:
                if job.status == 'failed':
                    failed_tasks.append(task)
        return [t for t in tasks if t not in failed_tasks]

    def get_finished_tasks(self):
        return Task.query.filter_by(user_id=self.id, complete=True).all()

    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, user_id=self.id,
                                    complete=False).first()

    def get_project_tasks_in_progress(self, project_id):
        tasks = Task.query.filter_by(
            user_id=self.id, complete=False, project_id=project_id).all()
        failed_tasks = []
        for task in tasks:
            job = task.get_rq_job()
            if job:
                if job.status == 'failed':
                    failed_tasks.append(task)
        return [t for t in tasks if t not in failed_tasks]

    def get_finished_project_tasks(self, project_id):
        return Task.query.filter_by(user_id=self.id, complete=True, project_id=project_id).all()

# Define the Role data-model


class Role(database.Model):
    __tablename__ = 'roles'
    id = database.Column(database.Integer(), primary_key=True)
    name = database.Column(database.String(50), unique=True)

# Define the UserRoles association table


class UserRoles(database.Model):
    __tablename__ = 'user_roles'
    id = database.Column(database.Integer(), primary_key=True)
    user_id = database.Column(database.Integer(), database.ForeignKey(
        'users.id', ondelete='CASCADE'))
    role_id = database.Column(database.Integer(), database.ForeignKey(
        'roles.id', ondelete='CASCADE'))


class Task(database.Model):
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
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=redis_conn)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100
