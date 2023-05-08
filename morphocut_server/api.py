import datetime
import errno
import faulthandler
import itertools
import json
import os
import pathlib
import urllib
import urllib.parse
from getpass import getpass
from time import sleep

import click
import flask
import flask_migrate
import pandas as pd
import sqlalchemy
from flask import (Flask, Response, abort, jsonify, redirect, render_template,
                   request, url_for)
from flask.blueprints import Blueprint
from flask.helpers import send_from_directory
from flask_cors import CORS
from flask_login import logout_user, login_user
from flask_user import (UserManager, UserMixin, current_user, login_required,
                        roles_required)
from rq import Queue
from rq.job import Job
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import and_, intersect, select, union
from sqlalchemy.sql.expression import bindparam
from timer_cm import Timer
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

#from morphocut.pipeline import *
from morphocut_server import helpers, models, tasks
from morphocut_server.extensions import database, migrate, redis_store
from morphocut_server.frontend import frontend
from morphocut_server.worker import redis_conn
from morphocut_server.pipeline import *
from flask_jwt_extended import jwt_required, get_jwt_identity

api = Blueprint("api", __name__)


# ===============================================================================
# Users Routes
# ===============================================================================


@api.route("/users", methods=['GET', 'POST'])
# @login_required
# @roles_required('admin')
def get_current_users_route():
    """Get the users currently registered.

    Returns
    -------
    response : str
        The jsonified response object.

    """
    if request.method == 'POST':
        from morphocut_server import morphocut
        user = request.get_json()
        morphocut.add_user_to_database(
            user['email'], user['password'], user['admin'])

        response_object = {'status': 'success', 'message': 'User added successfully'}
        return jsonify(response_object)
    else:
        response_object = {'status': 'success'}
        users = models.User.query.all()
        user_list = []

        for u in users:
            user_list.append({
                'id': u.id,
                'email': u.email,
            })

        response_object = {
            'users': user_list
        }

        return jsonify(response_object)

@api.route("/users/current", methods=['GET'])
def get_current_user_route():
    """Get the user currently logged in.

    Returns
    -------
    repsonse : str
        The jsonified response object.

    """
    response_object = {'status': 'success'}
    user = current_user

    if user.get_id() is not None:
        admin_role = False
        user_role = models.UserRoles.query.filter(
            models.UserRoles.user_id == user.id).first()
        if user_role and user_role.role_id == 1:
            admin_role = True
        response_object = {
            'user': {
                'id': user.id,
                'email': user.email,
                'admin': admin_role,
            }
        }
    else:
        response_object = {'status': 'error'}
    return jsonify(response_object)


@api.route("/users/current/jobs", methods=['GET'])
def get_current_user_tasks_route():
    """Get the jobs belonging to the user currently logged in.

    Returns
    -------
    repsonse : str
        The jsonified response object.

    """
    user = current_user

    if user.get_id() is not None:
        return get_user_jobs_route(user.id)
    else:
        response_object = {'status': 'error'}
    return jsonify(response_object)


@api.route('/users/<id>/jobs', methods=['GET', 'POST'])
def get_user_jobs_route(id):
    """Get the jobs belonging to the user wth the specified id.

    Parameters
    ----------
    id : int
        The id of the user.

    Returns
    -------
    repsonse : str
        The jsonified response object.

    """
    user = models.User.query.filter_by(id=id).first()

    if user.get_id() is not None:
        _tasks = user.get_tasks_in_progress()
        running_tasks = get_running_task_dicts(_tasks)

        _tasks = user.get_finished_tasks()
        finished_tasks = get_finished_task_dicts(_tasks)

        response_object = {
            'running_tasks': running_tasks,
            'finished_tasks': finished_tasks
        }
    else:
        response_object = {'status': 'error'}
    print(jsonify(response_object))
    return jsonify(response_object)


# ===============================================================================
# Projects Routes
# ===============================================================================

@api.route('/projects', methods=['GET', 'POST'])
@login_required
def get_projects_route():
    """Get the projects from the database.

    Returns
    -------
    repsonse : str
        The jsonified response object.

    """
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        if post_data is not None:
            add_project(post_data)
            response_object['message'] = 'Project added!'
    else:
        response_object['projects'] = get_projects()

    if not current_user.is_authenticated:
        return jsonify({'status': 'error', 'message': 'User not authenticated'}), 401

    return jsonify(response_object)


@api.route('/projects/<id>', methods=['GET'])
def get_project_route(id):
    """Get the project with the specified id.

    Parameters
    ----------
    id : int
        The id of the project.

    Returns
    -------
    repsonse : str
        The jsonified response object.

    """
    response_object = {'status': 'success'}
    if request.method == 'GET':
        response_object['project'] = get_project(id)
    return jsonify(response_object)


@api.route('/projects/<id>/files', methods=['GET'])
def get_project_files_route(id):
    """Get the objects belonging to the project with the specified id.

    Parameters
    ----------
    id : int
        The id of the project of which to get the objects.

    Returns
    -------
    repsonse : str
        The jsonified response object.

    """
    response_object = {'status': 'success'}
    if request.method == 'GET':
        response_object['project_files'] = get_project_files(id)
    return jsonify(response_object)


@api.route('/projects/<id>/process', methods=['POST'])
def process_project_route(id):
    """Launches a background job to process the project with the specified id.

    Parameters
    ----------
    id : int
        The id of the project that should be processed.

    Returns
    -------
    repsonse : str
        The jsonified response object.

    """
    response_object = {'status': 'success'}
    if request.method == 'POST':
        with database.engine.begin() as connection:
            app = flask.current_app
            params = request.get_json()['params']
            task = current_user.launch_task('morphocut_server.api.process_project',
                                            'Processing project...', id, id, params)
            response_object['job_id'] = task.id
    print("return process")
    return jsonify(response_object), 202


@api.route("/projects/<id>/jobs", methods=['GET'])
def get_project_job_status(id):
    """Get the job status of all the tasks connected to the project with the specified id.

    Parameters
    ----------
    id : int
        The id of the project of which to get the status.

    Returns
    -------
    repsonse : str
        The jsonified response object.

    """
    user = current_user

    if user.get_id() is not None:
        _tasks = user.get_project_tasks_in_progress(id)
        running_task_dicts = get_running_task_dicts(_tasks)

        _tasks = user.get_finished_project_tasks(id)
        finished_task_dicts = get_finished_task_dicts(_tasks)

        response_object = {
            'running_tasks': running_task_dicts,
            'finished_tasks': finished_task_dicts
        }
    else:
        response_object = {'status': 'error'}
    # print(jsonify(response_object))
    return jsonify(response_object)


@api.route('/projects/<id>/upload', methods=['GET', 'POST', 'PUT'])
def upload(id):
    """Uploads a file from the client to the server, adds it to the database and saves it.

    Parameters
    ----------
    id : int
        The id of the project to which the uploaded file should be connected.

    Returns
    -------
    repsonse : str
        The jsonified response object.

    """
    response_object = {'status': 'success'}
    print('upload ' + str(request.method) + '\n')
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        project = get_project(id)
        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.normpath(os.path.join(flask.current_app.root_path,
                                                     flask.current_app.config['DATA_DIRECTORY'], project['path'], filename))

            if not os.path.exists(os.path.dirname(filepath)):
                try:
                    os.makedirs(os.path.dirname(filepath))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise

            file.save(filepath)
            _object = {
                'filename': os.path.normpath(filename),
                'project_id': project['project_id']
            }
            add_object(_object)
            print('save file')
    return jsonify(response_object)


@api.route("/projects/<project_id>/remove", methods=['GET'])
def remove_project(project_id):
    """Removes a project and all of the connected objects from the database and deletes the corresponding files.

    Parameters
    ----------
    project_id : int
        The id of the project that should be deleted.

    Returns
    -------
    repsonse : str
        The jsonified response object.

    """
    response_object = {'status': 'success'}
    with database.engine.begin() as connection:

        stmt = select(models.projects.c.path).where(
            models.projects.c.project_id == project_id)
        project = connection.execute(stmt).first()

        if project:
            app = flask.current_app
            project_path = os.path.join(
                app.root_path, app.config['DATA_DIRECTORY'], project._asdict()['path'])
            if 'morphocut' in project_path and app.config['DATA_DIRECTORY'] in project_path:
                print('removing project with id {}'.format(project_id))
                if os.path.exists(project_path):
                    helpers.remove_directory(project_path)

                stmt = models.projects.delete().where(  # pylint: disable=no-value-for-parameter
                    models.projects.c.project_id == project_id)

                connection.execute(stmt)

    return jsonify(response_object)


@api.route("/users/<user_id>/remove", methods=['GET'])
def remove_user(user_id):
    """Removes a project and all of the connected objects from the database and deletes the corresponding files.

    Parameters
    ----------
    project_id : int
        The id of the project that should be deleted.

    Returns
    -------
    repsonse : str
        The jsonified response object.

    """
    response_object = {'status': 'success'}
    models.User.query.filter(models.User.id == user_id).delete()
    database.session.commit()  # pylint: disable=no-member

    return jsonify(response_object)


# ===============================================================================
# Tasks Routes
# ===============================================================================


@api.route("/jobs/<task_id>/remove", methods=['GET'])
@login_required
def remove_task(task_id):
    """Removes a task from the database.

    Parameters
    ----------
    task_id : int
        The id of the task that should be deleted.

    Returns
    -------
    response : str
        The jsonified response object.

    """
    response_object = {'status': 'success'}

    task = models.Task.query.filter(models.Task.id == task_id).first()
    print('removing task with id {}'.format(task.id))
    app = flask.current_app
    absolute_path = os.path.join(
        app.root_path, app.config['DATA_DIRECTORY'], task.result)
    helpers.remove_file(absolute_path)

    database.session.delete(task)  # pylint: disable=no-member
    database.session.commit()  # pylint: disable=no-member

    return jsonify(response_object)


# ===============================================================================
# Objects Routes
# ===============================================================================


@api.route("/objects/<object_id>/remove", methods=['GET'])
@login_required
def remove_object(object_id):
    response_object = {'status': 'success'}
    with database.engine.begin() as connection:

        stmt = select([models.objects.c.object_id, models.objects.c.filename, models.objects.c.project_id]).where(
            models.objects.c.object_id == object_id)
        obj = connection.execute(stmt).first()

        if obj:
            stmt = select([models.projects.c.path]).where(
                models.projects.c.project_id == obj['project_id'])
            project = connection.execute(stmt).first()

            if project:
                app = flask.current_app
                obj_path = os.path.join(
                    app.root_path, app.config['DATA_DIRECTORY'], project['path'], obj['filename'])
                if 'morphocut' in obj_path and app.config['DATA_DIRECTORY'] in obj_path:
                    print('removing object with id {}'.format(
                        obj['object_id']))
                    if os.path.exists(obj_path):
                        helpers.remove_file(obj_path)

                    stmt = models.objects.delete().where(  # pylint: disable=no-value-for-parameter
                        models.objects.c.object_id == obj['object_id']
                    )

                    connection.execute(stmt)

    return jsonify(response_object)


# ===============================================================================
# Helper functions
# ===============================================================================


def allowed_file(filename):
    """Check if the specified filename is valid to be uploaded and not harmful.

    Parameters
    ----------
    filename : str
        The filename that should be checked.

    Returns
    -------
    allowed : bool
        True if the filename is valid.

    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower(
           ) in flask.current_app.config['ALLOWED_EXTENSIONS']


def get_running_task_dicts(tasks):
    """Get dictionary representations of the unfinished tasks from the specified list.

    Parameters
    ----------
    tasks : list
        The tasks that should be converted to dictionaries.

    Returns
    -------
    unfinished_tasks : list
        The unfinished tasks in the form of dictionaries.

    """
    running_task_dicts = []
    with database.engine.begin() as connection:
        for task in tasks:
            print(json.loads(task.meta))
            job = Job.fetch(task.id, connection=redis_conn)
            project = connection.execute(select(sqlalchemy.text(
                '*')).select_from(models.projects).where(models.projects.c.project_id == task.project_id)).first()
            task_dict = dict(id=task.id, name=task.name, description=task.description,
                             complete=task.complete, result=task.result, progress=task.get_progress(), project_id=task.project_id)
            task_dict['meta'] = json.loads(
                task.meta) if task.meta is not None else {}

            if job:
                task_dict['status'] = job.get_status()
                # task_dict['started_at'] = datetime.datetime.fromtimestamp(
                #     task_dict['meta']['scheduled_at'])
                # print('scheduled_at: {}'.format(task_dict['started_at']))
            if project:
                task_dict['project_name'] = project[1]
            running_task_dicts.append(task_dict)
    return running_task_dicts


def get_finished_task_dicts(tasks):
    """Get dictionary representations of the finished tasks from the specified list. 

    Parameters
    ----------
    tasks : list
        The tasks that should be converted to dictionaries.

    Returns
    -------
    finished_tasks : list
        The finished tasks in the form of dictionaries.

    """
    finished_task_dicts = []
    with database.engine.begin() as connection:
        for task in tasks:
            try:
                download_path = url_for('data', path=task.result)
                task_dict = dict(id=task.id, name=task.name, description=task.description,
                                 complete=task.complete, result=task.result, download_path=download_path, status='finished', project_id=task.project_id)
                task_dict['meta'] = json.loads(
                    task.meta) if task.meta is not None else {}
                finished_task_dicts.append(task_dict)
                project = connection.execute(select(sqlalchemy.text(
                    '*')).select_from(models.projects).where(models.projects.c.project_id == task.project_id)).first()
                if project:
                    task_dict['project_name'] = project[1]
            except Exception as err:
                print('exception in api.get_finished_task_dicts')
                print(err)
    return finished_task_dicts


def process_project(project_id, params):
    """Processes a project.

    Parameters
    ----------
    project_id : int
        The id of the project that should be processed.

    Returns
    -------
    download_path : str
        The path to the exported file relative to the data directory.

    """
    from morphocut_server import morphocut
    with morphocut.app.app_context():
        app = flask.current_app
        with database.engine.begin() as connection:
            result = connection.execute(select(
                models.projects.c.path)
                .select_from(models.projects)
                .where(models.projects.c.project_id == project_id))
            r = result.fetchone()
            if (r is not None):
                rel_project_path = r._asdict()['path']
                abs_project_path = os.path.join(
                    app.root_path, app.config['DATA_DIRECTORY'], rel_project_path)
                export_filename = 'ecotaxa_segmentation_{:%Y_%m_%d}_{}.zip'.format(
                    datetime.datetime.now(), helpers.random_string(n=7))
                export_path = os.path.join(
                    abs_project_path, export_filename)

                process_and_zip(abs_project_path, export_path, params)
            return os.path.join(rel_project_path, export_filename)


def process_and_zip(import_path, export_path, params=None):
    """Executes the default pipeline with the specified import and export paths.

    Parameters
    ----------
    import_path : str
        The path from which the data should get imported.
    export_path : str
        The path to where the results should be saved.

    Returns
    -------
    export_path : str
        The path to which the resulting zipfile was saved.

    """
    # If the path does not exist, create it
    export_dirpath = os.path.dirname(export_path)
    print(export_dirpath)
    if not os.path.exists(export_dirpath):
        os.makedirs(export_dirpath)

    if params is not None:
        # print('get pipeline with params {}'.format(params))
        pipeline = get_default_pipeline_parameterized(
            import_path, export_path, params)
    else:
        pipeline = get_default_pipeline(import_path, export_path)

    pipeline.execute()

    return export_path


@login_required
def get_projects():
    """Get the projects belonging to the current user.

    Returns
    -------
    projects : list
        The projects belonging to the current user.

    """
    print("Access token received")
    print("get_projects called, current_user ID:", current_user.get_id())  # Add this line

    if current_user.get_id() is None:
        return
    with database.engine.begin() as connection:
        result = connection.execute(
            select(
                models.projects.c.project_id,
                models.projects.c.name,
                models.projects.c.path,
                models.projects.c.creation_date,
                models.projects.c.user_id,
                func.count(models.objects.c.object_id).label('object_count')
            )
            .select_from(models.projects.outerjoin(models.objects))
            .where(and_(models.projects.c.active == True, models.projects.c.user_id == current_user.id))
            .group_by(models.projects.c.project_id)
            .order_by(models.projects.c.project_id)
        )
        projects = [row._asdict() for row in result]
        print("Fetched projects:", projects)  # Add this line
        for project in projects:
            user = models.User.query.filter_by(
                id=project['user_id']).first()
            if user:
                project['email'] = user.email
        return projects


def get_project_files(id):
    """Get the objects belonging to the project with the specified id.

    Parameters
    ----------
    id : int
        The id of the project of which to get the objects.

    Returns
    -------
    objects : list
        The objects belonging to the specified project.

    """
    with database.engine.begin() as connection:
        result = connection.execute(select(
            models.objects.c.filename, models.objects.c.object_id, models.objects.c.modification_date, models.objects.c.creation_date)
            .select_from(models.objects)
            .where(models.objects.c.project_id == id))
        print(f'Query result for project_id {id}: {result}')
        project = connection.execute(select(
            models.projects.c.path)
            .select_from(models.projects)
            .where(models.projects.c.project_id == id))
        r = project.fetchone()
        project = ''
        if (r is not None):
            project_path = r._asdict()['path']
        objects = [dict(filename=row._asdict()['filename'],
                     object_id=row._asdict()['object_id'],
                     modification_date=row._asdict()['modification_date'],
                     creation_date=row._asdict()['creation_date'],
                     filepath=url_for(
                         'data', path=os.path.join(project_path, row._asdict()['filename']))
                    )
                    for row in result]
        print(f'Objects for project_id {id}: {objects}')
        return objects


def get_project(id):
    """Get the project with the specified id.

    Parameters
    ----------
    id : int
        The id of the project.

    Returns
    -------
    project : models.Project
        The project with the specified id.

    """
    with database.engine.begin() as connection:
        result = connection.execute(select(
            sqlalchemy.text('*'))
            .select_from(models.projects)
            .where(models.projects.c.project_id == id))
        row = result.fetchone()
        if (row is not None):
            return row._asdict()
        return


def add_project(project):
    """Adds a prject to the database.

    Parameters
    ----------
    project : models.Project
        The project that should be added to the database.

    Returns
    -------
    None

    """
    print('add_project: ' + str(project))
    try_insert_or_update(models.projects.insert(),  # pylint: disable=no-value-for-parameter
                         [dict(
                             name=project['name'], path=project['name'], active=True, user_id=current_user.id)])


def add_object(_object):
    """Adds an object to the database.

    Parameters
    ----------
    _object : models.Object
        The object that should be added to the database.

    Returns
    -------
    None

    """
    print('add_object: ' + str(_object))
    try_insert_or_update(
        models.objects.insert(),  # pylint: disable=no-value-for-parameter
        [dict(
            project_id=_object['project_id'], filename=_object['filename'])])
    print(f'Object added: {_object}')


def try_insert_or_update(insert_function, data):
    """Inserts a list of data into database.

    Parameters
    ----------
    insert_function : str
        The sqlalchemy statement that should be executed.
    data : str
        The data that should be inserted into the database.

    Returns
    -------
    None

    """
    with database.engine.begin() as connection:
        if len(data) > 0:
            connection.execute(insert_function, data)
