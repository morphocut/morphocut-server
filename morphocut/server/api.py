import datetime
import faulthandler
import itertools
import json
import os
import pathlib
import urllib.parse
from getpass import getpass
from time import sleep

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

from morphocut import segmentation
from morphocut.processing.pipeline import *
from morphocut.server import models, helpers, morphocut
from morphocut.server.extensions import database, migrate, redis_store
from morphocut.server.frontend import frontend

api = Blueprint("api", __name__)


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


@api.route('/datasets/<id>/files', methods=['GET'])
def get_dataset_files_route(id):
    response_object = {'status': 'success'}
    if request.method == 'GET':
        response_object['dataset_files'] = get_dataset_files(id)
    return jsonify(response_object)


@api.route('/datasets/<id>', methods=['GET'])
def get_dataset_route(id):
    response_object = {'status': 'success'}
    if request.method == 'GET':
        response_object['dataset'] = get_dataset(id)
    return jsonify(response_object)


@api.route('/datasets', methods=['GET', 'POST'])
def get_datasets_route():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        if post_data is not None:
            # datasets.append({
            #     'id': post_data.get('id'),
            #     'name': post_data.get('name'),
            #     'objects': post_data.get('objects')
            # })
            add_dataset(post_data)
            response_object['message'] = 'Dataset added!'
    else:
        response_object['datasets'] = get_datasets()
    return jsonify(response_object)


@api.route('/datasets/<id>/process', methods=['GET'])
def process_dataset_route(id):
    response_object = {'status': 'success'}
    if request.method == 'GET':
        # response_object['dataset_files'] = get_dataset_files(id)
        with database.engine.begin() as connection:
            result = connection.execute(select(
                [models.datasets.c.path])
                .select_from(models.datasets)
                .where(models.datasets.c.dataset_id == id))
            r = result.fetchone()
            if (r is not None):
                dataset_path = r['path']

                app = flask.current_app

                import_path = os.path.join(
                    app.root_path, app.config['UPLOAD_FOLDER'], dataset_path)

                relative_export_path = os.path.join(
                    app.config['UPLOAD_FOLDER'], dataset_path)
                relative_download_path = '/' + \
                    app.config['UPLOAD_FOLDER'] + '/' + dataset_path + '/'
                export_path = os.path.join(
                    app.root_path, relative_export_path)

                download_filename = process_and_zip(import_path, export_path)

                # download_filename = segmentation.process(
                #     import_path, export_path)

                print('download path: '
                      + relative_download_path + download_filename)
                response_object['download_path'] = relative_download_path + \
                    download_filename
                response_object['download_filename'] = download_filename
    return jsonify(response_object)


@api.route('/datasets/<id>/upload', methods=['GET', 'POST', 'PUT'])
def upload(id):
    response_object = {'status': 'success'}
    print('upload ' + str(request.method) + '\n')
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        dataset = get_dataset(id)
        if file and allowed_file(file.filename):
            # filename = secure_filename(file.filename)
            filename = file.filename
            filepath = os.path.normpath(os.path.join(flask.current_app.root_path,
                                                     flask.current_app.config['UPLOAD_FOLDER'], dataset['path'], filename))

            if not os.path.exists(os.path.dirname(filepath)):
                try:
                    os.makedirs(os.path.dirname(filepath))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise

            file.save(filepath)
            _object = {
                'filename': os.path.normpath(filename),
                'dataset_id': dataset['dataset_id']
            }
            add_object(_object)
            print('save file')
    return jsonify(response_object)


def process_and_zip(import_path, export_path):
    # If the path does not exist, create it
    if not os.path.exists(export_path):
        os.makedirs(export_path)

    output_fn = 'ecotaxa_segmentation_{:%Y_%m_%d}_{}.zip'.format(
        datetime.datetime.now(), helpers.random_string(n=7))
    output_fp = os.path.join(
        export_path,
        output_fn)

    pipeline = get_default_pipeline(import_path, export_path)

    # pipeline = Pipeline([
    #     DataLoader(import_path),
    #     VignetteCorrector(),
    #     ThresholdOtsu('corrected_data', 'binary_image')
    #     ExtractRegions(),
    #     GrayToRGB(),
    #     ContourTransform(),
    #     Exporter(output_fp)
    # ])

    pipeline.execute()

    return output_fn


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower(
           ) in flask.current_app.config['ALLOWED_EXTENSIONS']


def get_datasets():
    with database.engine.begin() as connection:
        result = connection.execute(select(
            [models.datasets.c.dataset_id, models.datasets.c.name, models.datasets.c.path, func.count(models.objects.c.object_id).label('object_count')])
            .select_from(models.datasets.outerjoin(models.objects))
            .where(models.datasets.c.active == True)
            .group_by(models.datasets.c.dataset_id))
        return [dict(id=row['dataset_id'], objects=row['object_count'], name=row['name'], path=row['path']) for row in result]


def get_dataset_files(id):
    with database.engine.begin() as connection:
        result = connection.execute(select(
            [models.objects.c.filename, models.objects.c.object_id, models.objects.c.modification_date, models.objects.c.creation_date])
            .select_from(models.objects)
            .where(models.objects.c.dataset_id == id))
        dataset = connection.execute(select(
            [models.datasets.c.path])
            .select_from(models.datasets)
            .where(models.datasets.c.dataset_id == id))
        r = dataset.fetchone()
        dataset_path = ''
        if (r is not None):
            dataset_path = r['path']
        return [dict(filename=row['filename'],
                     object_id=row['object_id'],
                     modification_date=row['modification_date'],
                     creation_date=row['creation_date'],
                     filepath=os.path.join(dataset_path, row['filename']).replace('\\', '/')) for row in result]


def get_dataset(id):
    with database.engine.begin() as connection:
        result = connection.execute(select(
            [sqlalchemy.text('*')])
            .select_from(models.datasets)
            .where(models.datasets.c.dataset_id == id))
        row = result.fetchone()
        if (row is not None):
            return dict(row)
        return


def add_dataset(dataset):
    print('add_dataset: ' + str(dataset))
    try_insert_or_update(models.datasets.insert(), [dict(
        name=dataset['name'], path=dataset['name'], active=True)], "datasets")
    return


def add_user(user):
    print('add user: ' + str(user))
    try_insert_or_update(models.users.insert(), [dict(
        username=dataset['name'], path=dataset['name'], active=True)], "datasets")
    return


def add_object(_object):
    print('add_object: ' + str(_object))
    try_insert_or_update(models.objects.insert(), [dict(
        dataset_id=_object['dataset_id'], filename=_object['filename'])], "objects")
    return


def try_insert_or_update(insert_function, data, table_name):
    """
    Try to insert a data list into the database
    """
    with database.engine.begin() as connection:
        if len(data) > 0:
            connection.execute(insert_function, data)
