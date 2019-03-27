from flask_cors import CORS
from flask import jsonify
import faulthandler
import itertools
import os
from getpass import getpass
from time import sleep

import click
import flask_migrate
import h5py
import pandas as pd
from etaprogress.progress import ProgressBar
from flask import (Flask, Response, abort, redirect, render_template, request,
                   url_for)
import json
import urllib.parse
import datetime

from flask.helpers import send_from_directory
import sqlalchemy
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import bindparam
from sqlalchemy.sql import select, and_, union, intersect
from timer_cm import Timer
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_user import current_user, login_required, roles_required, UserManager, UserMixin
from flask_login import logout_user

from morphocut.server import models
from morphocut.server.extensions import database, migrate, redis_store
from morphocut.server.frontend import frontend
from morphocut.server.api import api

# Enable fault handler for meaningful stack traces when a worker is killed
faulthandler.enable()

app = Flask(__name__)

app.config.from_object('morphocut.server.config_default')

if 'MORPHOCUT_SETTINGS' in os.environ:
    app.config.from_envvar('MORPHOCUT_SETTINGS')

# Initialize extensions
database.init_app(app)
redis_store.init_app(app)
migrate.init_app(app, database)
CORS(app)
user_manager = UserManager(app, database, models.User)


# Enable batch mode
with app.app_context():
    database.engine.dialect.psycopg2_batch_mode = True


@app.cli.command()
def reset_db():
    """
    Drop all tables and recreate.
    """
    print("Resetting the database.")
    print("WARNING: This is a destructive operation and all data will be lost.")

    if input("Continue? (y/n) ") != "y":
        print("Canceled.")
        return

    with database.engine.begin() as txn:
        database.metadata.drop_all(txn)
        database.metadata.create_all(txn)

        flask_migrate.stamp()


@app.cli.command()
@click.argument('username')
@click.option('--admin/--no-admin', default=False)
def add_user(username, admin):
    print("Adding user {}:".format(username))
    password = getpass("Password: ")
    password_repeat = getpass("Retype Password: ")

    if not len(password):
        print("Password must not be empty!")
        return

    if password != password_repeat:
        print("Passwords do not match!")
        return

    # pwhash = generate_password_hash(
    #     password, method='pbkdf2:sha256:10000', salt_length=12)

    # add_user_to_database(username, pwhash, admin)
    add_user_to_database(username, password, admin)


def add_user_to_database(username, password, admin):
    print('username: {}, admin: {}'.format(username, admin))
    # try:
    #     with database.engine.connect() as conn:
    #         stmt = models.users.insert(
    #             {"username": username, "pwhash": pwhash, 'admin': admin})
    #         conn.execute(stmt)
    # except IntegrityError as e:
    #     print(e)
    if not models.User.query.filter(models.User.username == username).first():
        user = models.User(
            username=username,
            password=user_manager.hash_password(password),
        )
        database.session.add(user)
        database.session.commit()


# Register API and frontend
app.register_blueprint(frontend, url_prefix='/frontend')
app.register_blueprint(api, url_prefix='/api')


@app.route("/")
@login_required
def index():
    print('index request')
    return redirect(url_for("frontend.index"))


@app.route("/frontend")
@roles_required('Admin')    # Use of @roles_required decorator
@login_required
def frontend_route():
    print('frontend request')
    return redirect(url_for("frontend.index"))


# ===============================================================================
# Authentication
# ===============================================================================


def check_auth(username, password, admin_rights):
    # Retrieve entry from the database
    with database.engine.connect() as conn:
        stmt = models.users.select(
            models.users.c.username == username).limit(1)
        user = conn.execute(stmt).first()

        if user is None:
            return False

    return check_password_hash(user["pwhash"], password) and ((not admin_rights) or user['admin'])


# @app.before_request
def require_auth():
    # exclude 404 errors and static routes
    # uses split to handle blueprint static routes as well

    admin_rights = False

    if not request.endpoint or request.endpoint.rsplit('.', 1)[-1] == 'static':
        return

    if 'users' in request.endpoint:
        admin_rights = True

    auth = request.authorization

    success = check_auth(auth.username, auth.password,
                         admin_rights) if auth else None

    if not auth or not success:
        if success is False:
            # Rate limiting for failed passwords
            sleep(1)

        # Send a 401 response that enables basic auth
        return Response(
            'Could not verify your access level.\n'
            'You have to login with proper credentials', 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'})


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r
