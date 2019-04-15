import datetime
import faulthandler
import itertools
import json
import os
import pathlib
import urllib.parse
from getpass import getpass
from time import sleep
import urllib
import click
import h5py
import pandas as pd
from timer_cm import Timer
from etaprogress.progress import ProgressBar

import flask
import flask_migrate
from flask import (Flask, Response, abort, jsonify, redirect, render_template,
                   request, url_for)
from flask.blueprints import Blueprint
from flask.helpers import send_from_directory
from flask_cors import CORS
from flask_user import current_user, login_required, roles_required, UserManager, UserMixin
from flask_login import logout_user

import sqlalchemy
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import and_, intersect, select, union
from sqlalchemy.sql.expression import bindparam

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from rq import Queue
from rq.job import Job

from morphocut.server.worker import redis_conn
from morphocut.processing.pipeline import *
from morphocut.server import models, helpers, tasks
from morphocut.server.extensions import database, migrate, redis_store
from morphocut.server.frontend import frontend


api = Blueprint("api", __name__)


# ===============================================================================
# Users Routes
# ===============================================================================


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

    if user:
        response_object = {
            'user': {
                'id': user.id,
                'username': user.username,
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

    if user:
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

    if user:
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


@api.route('/projects/<id>/process', methods=['GET'])
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
    if request.method == 'GET':
        with database.engine.begin() as connection:
            app = flask.current_app
            if current_user.get_task_in_progress('process_project'):
                print('A process task is currently in progress')
            else:
                task = current_user.launch_task('morphocut.server.api.process_project',
                                                'Processing project...', id, id)
                response_object['job_id'] = task.id
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

    if user:
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
    print(jsonify(response_object))
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

        stmt = select([models.projects.c.path]).where(
            models.projects.c.project_id == project_id)
        project = connection.execute(stmt).first()

        if project:
            app = flask.current_app
            project_path = os.path.join(
                app.root_path, app.config['DATA_DIRECTORY'], project['path'])
            if 'morphocut' in project_path and app.config['DATA_DIRECTORY'] in project_path:
                print('removing project with id {}'.format(project_id))
                if os.path.exists(project_path):
                    helpers.remove_directory(project_path)

                stmt = models.projects.delete().where(
                    models.projects.c.project_id == project_id
                )
                connection.execute(stmt)

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
    if task.complete and 'morphocut' in task.result and app.config['DATA_DIRECTORY'] in task.result:
        helpers.remove_file(task.result)

    database.session.delete(task)
    database.session.commit()

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
            job = Job.fetch(task.id, connection=redis_conn)
            project = connection.execute(select([sqlalchemy.text(
                '*')]).select_from(models.projects).where(models.projects.c.project_id == task.project_id)).first()
            task_dict = dict(id=task.id, name=task.name, description=task.description,
                             complete=task.complete, result=task.result, progress=task.get_progress(), project_id=task.project_id)
            if job:
                task_dict['status'] = job.get_status()
                if job.started_at:
                    task_dict['started_at'] = job.started_at.strftime(
                        '%Y-%m-%d %H:%M:%S')
            if project:
                task_dict['project_name'] = project['name']
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
                finished_task_dicts.append(task_dict)
            except Exception as err:
                print(err)
            project = connection.execute(select([sqlalchemy.text(
                '*')]).select_from(models.projects).where(models.projects.c.project_id == task.project_id)).first()
            if project:
                task_dict['project_name'] = project['name']
    return finished_task_dicts


def process_project(project_id):
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
    from morphocut.server import morphocut
    with morphocut.app.app_context():
        app = flask.current_app
        with database.engine.begin() as connection:
            result = connection.execute(select(
                [models.projects.c.path])
                .select_from(models.projects)
                .where(models.projects.c.project_id == project_id))
            r = result.fetchone()
            if (r is not None):
                rel_project_path = r['path']
                abs_project_path = os.path.join(
                    app.root_path, app.config['DATA_DIRECTORY'], rel_project_path)
                export_filename = 'ecotaxa_segmentation_{:%Y_%m_%d}_{}.zip'.format(
                    datetime.datetime.now(), helpers.random_string(n=7))
                export_path = os.path.join(
                    abs_project_path, export_filename)

                process_and_zip(abs_project_path, export_path)
            return os.path.join(rel_project_path, export_filename)


def process_and_zip(import_path, export_path):
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

    pipeline = get_default_pipeline(import_path, export_path)

    pipeline.execute()

    return export_path


def get_projects():
    """Get the projects belonging to the current user.

    Returns
    -------
    projects : list
        The projects belonging to the current user.

    """
    with database.engine.begin() as connection:
        result = connection.execute(select(
            [models.projects.c.project_id, models.projects.c.name, models.projects.c.path, models.projects.c.creation_date, models.projects.c.user_id, func.count(models.objects.c.object_id).label('object_count')])
            .select_from(models.projects.outerjoin(models.objects))
            .where(and_(models.projects.c.active == True, models.projects.c.user_id == current_user.id))
            .group_by(models.projects.c.project_id)
            .order_by(models.projects.c.project_id))
        projects = [dict(row) for row in result]
        for project in projects:
            user = models.User.query.filter_by(
                id=project['user_id']).first()
            if user:
                project['username'] = user.username
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
            [models.objects.c.filename, models.objects.c.object_id, models.objects.c.modification_date, models.objects.c.creation_date])
            .select_from(models.objects)
            .where(models.objects.c.project_id == id))
        project = connection.execute(select(
            [models.projects.c.path])
            .select_from(models.projects)
            .where(models.projects.c.project_id == id))
        r = project.fetchone()
        project = ''
        if (r is not None):
            project_path = r['path']
        return [dict(filename=row['filename'],
                     object_id=row['object_id'],
                     modification_date=row['modification_date'],
                     creation_date=row['creation_date'],
                     filepath=url_for(
                         'data', path=os.path.join(project_path, row['filename']))
                     )

                for row in result]


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
            [sqlalchemy.text('*')])
            .select_from(models.projects)
            .where(models.projects.c.project_id == id))
        row = result.fetchone()
        if (row is not None):
            return dict(row)
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
    try_insert_or_update(models.projects.insert(), [dict(
        name=project['name'], path=project['name'], active=True, user_id=current_user.id)])
    return


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
    try_insert_or_update(models.objects.insert(), [dict(
        project_id=_object['project_id'], filename=_object['filename'])])


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
