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
import flask
import flask_migrate
import h5py
import pandas as pd
import sqlalchemy
from etaprogress.progress import ProgressBar
from flask import (Flask, Response, abort, jsonify, redirect, render_template,
                   request, url_for)
from flask.blueprints import Blueprint
from flask.helpers import send_from_directory
from flask_cors import CORS
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import and_, intersect, select, union
from sqlalchemy.sql.expression import bindparam
from timer_cm import Timer
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from rq import Queue
from rq.job import Job
from morphocut.server.worker import redis_conn
from flask_user import current_user, login_required, roles_required, UserManager, UserMixin
from flask_login import logout_user

from morphocut.processing.pipeline import *
from morphocut.server import models, helpers, morphocut, tasks
from morphocut.server.extensions import database, migrate, redis_store, redis_queue
from morphocut.server.frontend import frontend

api = Blueprint("api", __name__)


# =================================================== Users Routes ===================================================


@api.route('/users', methods=['GET', 'POST'])
def get_users_route():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        if post_data is not None:
            pwhash = pwhash = generate_password_hash(
                post_data['password'], method='pbkdf2:sha256:10000', salt_length=12)
            morphocut.add_user_to_database(
                post_data['username'], pwhash, post_data['admin'])
            response_object['message'] = 'User added!'
    else:
        with database.engine.begin() as connection:
            result = connection.execute(select(
                [sqlalchemy.text('*')])
                .select_from(models.users))
            users = [dict(row) for row in result]

            response_object['users'] = users
    return jsonify(response_object)


@api.route("/users/current", methods=['GET'])
def get_current_user_route():
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
    user = current_user

    if user:
        return get_user_jobs_route(user.id)
    else:
        response_object = {'status': 'error'}
    return jsonify(response_object)


@api.route('/users/<id>/jobs', methods=['GET', 'POST'])
def get_user_jobs_route(id):
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


# =================================================== Projects Routes ===================================================


@api.route('/projects', methods=['GET', 'POST'])
def get_projects_route():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        if post_data is not None:
            # datasets.append({
            #     'id': post_data.get('id'),
            #     'name': post_data.get('name'),
            #     'objects': post_data.get('objects')
            # })
            add_project(post_data)
            response_object['message'] = 'Project added!'
    else:
        response_object['projects'] = get_projects()
    return jsonify(response_object)


@api.route('/projects/<id>', methods=['GET'])
def get_project_route(id):
    response_object = {'status': 'success'}
    if request.method == 'GET':
        response_object['project'] = get_project(id)
    return jsonify(response_object)


@api.route('/projects/<id>/files', methods=['GET'])
def get_project_files_route(id):
    response_object = {'status': 'success'}
    if request.method == 'GET':
        response_object['project_files'] = get_project_files(id)
    return jsonify(response_object)


@api.route('/projects/<id>/process', methods=['GET'])
def process_project_route(id):
    response_object = {'status': 'success'}
    if request.method == 'GET':
        with database.engine.begin() as connection:
            result = connection.execute(select(
                [models.projects.c.path])
                .select_from(models.projects)
                .where(models.projects.c.project_id == id))
            r = result.fetchone()
            if (r is not None):
                project_path = r['path']

                app = flask.current_app

                import_path = os.path.join(
                    app.root_path, app.config['UPLOAD_FOLDER'], project_path)
                export_path = os.path.join(
                    app.root_path, app.config['UPLOAD_FOLDER'], project_path)

                if current_user.get_task_in_progress('process_and_zip'):
                    print('A process task is currently in progress')
                else:
                    task = tasks.launch_task('morphocut.server.api.process_and_zip',
                                             'Processing project...', id, import_path, export_path)
                    response_object['job_id'] = task.id
    return jsonify(response_object), 202


@api.route("/projects/<id>/jobs", methods=['GET'])
def get_project_job_status(id):
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
                                                     flask.current_app.config['UPLOAD_FOLDER'], project['path'], filename))

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
    response_object = {'status': 'success'}
    with database.engine.begin() as connection:

        stmt = select([models.projects.c.path]).where(
            models.projects.c.project_id == project_id)
        project = connection.execute(stmt).first()

        if project:
            app = flask.current_app
            project_path = os.path.join(
                app.root_path, app.config['UPLOAD_FOLDER'], project['path'])
            if 'morphocut' in project_path and 'static' in project_path:
                print('removing project with id {}'.format(project_id))
                if os.path.exists(project_path):
                    helpers.remove_directory(project_path)

                stmt = models.projects.delete().where(
                    models.projects.c.project_id == project_id
                )
                connection.execute(stmt)

    return jsonify(response_object)


# =================================================== Tasks Routes ===================================================


@api.route("/jobs/<task_id>/remove", methods=['GET'])
@login_required
def remove_task(task_id):
    response_object = {'status': 'success'}

    task = models.Task.query.filter(models.Task.id == task_id).first()
    print('removing task with id {}'.format(task.id))
    if task.complete and 'morphocut' in task.result and 'static' in task.result:
        helpers.remove_file(task.result)

    database.session.delete(task)
    database.session.commit()

    return jsonify(response_object)


# =================================================== General Routes ===================================================


# =================================================== Helper functions ===================================================


def get_running_task_dicts(tasks):
    running_task_dicts = []
    with database.engine.begin() as connection:
        for task in tasks:
            job = Job.fetch(task.id, connection=redis_conn)
            project = connection.execute(select([sqlalchemy.text(
                '*')]).select_from(models.projects).where(models.projects.c.project_id == task.project_id)).first()
            task_dict = dict(id=task.id, name=task.name, description=task.description,
                             complete=task.complete, result=task.result, progress=task.get_progress(), project_id=task.project_id)
            if job:
                task_dict['status'] = job.status
                if job.started_at:
                    task_dict['started_at'] = job.started_at.strftime(
                        '%Y-%m-%d %H:%M:%S')
            if project:
                task_dict['project_name'] = project['name']
            running_task_dicts.append(task_dict)
    return running_task_dicts


def get_finished_task_dicts(tasks):
    finished_task_dicts = []
    with database.engine.begin() as connection:
        for task in tasks:
            try:
                download_path = 'localhost:5000/static/' + \
                    task.result.split('static/')[1]
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


def process_and_zip(import_path, export_path):
    # If the path does not exist, create it
    if not os.path.exists(export_path):
        os.makedirs(export_path)

    output_fn = os.path.join(
        export_path,
        'ecotaxa_segmentation_{:%Y_%m_%d}_{}.zip'.format(
            datetime.datetime.now(), helpers.random_string(n=7)))

    pipeline = get_default_pipeline(import_path, output_fn)

    pipeline.execute()

    return output_fn


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower(
           ) in flask.current_app.config['ALLOWED_EXTENSIONS']


def get_projects():
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
                     filepath='/static/' + os.path.join(project_path, row['filename']).replace('\\', '/'))
                for row in result]


def get_project(id):
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
    print('add_project: ' + str(project))
    try_insert_or_update(models.projects.insert(), [dict(
        name=project['name'], path=project['name'], active=True, user_id=current_user.id)], "projects")
    return


def add_object(_object):
    print('add_object: ' + str(_object))
    try_insert_or_update(models.objects.insert(), [dict(
        project_id=_object['project_id'], filename=_object['filename'])], "objects")
    return


def try_insert_or_update(insert_function, data, table_name):
    """
    Try to insert a data list into the database
    """
    with database.engine.begin() as connection:
        if len(data) > 0:
            connection.execute(insert_function, data)
