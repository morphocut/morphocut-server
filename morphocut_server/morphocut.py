import faulthandler
import itertools
import os
from getpass import getpass
from time import sleep

import click
import flask_migrate
import pandas as pd
from timer_cm import Timer

import json
import urllib.parse
import datetime

from flask import (Flask, Response, abort, redirect, render_template, request,
                   url_for, current_app, make_response)
from flask_cors import CORS
from flask import jsonify
from flask.helpers import send_from_directory
from flask.blueprints import Blueprint
from flask_user import current_user, login_required, roles_required, UserManager, UserMixin
from flask_login import logout_user, LoginManager, login_user

import sqlalchemy
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import bindparam
from sqlalchemy.sql import select, and_, union, intersect

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from morphocut_server import models
from morphocut_server.extensions import database, migrate, redis_store, flask_rq
from morphocut_server.frontend import frontend
from morphocut_server.api import api

# Enable fault handler for meaningful stack traces when a worker is killed
faulthandler.enable()


# ===============================================================================
# App Setup
# ===============================================================================


app = Flask(__name__)

app.config.from_object('morphocut_server.config_default')

if 'MORPHOCUT_SETTINGS' in os.environ:
    app.config.from_envvar('MORPHOCUT_SETTINGS')

# Initialize extensions
database.init_app(app)
redis_store.init_app(app)
migrate.init_app(app, database)
# flask_rq.init_app(app)
CORS(app)
user_manager = UserManager(
    app, database, models.User)


# Enable batch mode
with app.app_context():
    database.engine.dialect.psycopg2_batch_mode = True


# ===============================================================================
# Commands
# ===============================================================================


@app.cli.command()
def reset_db():
    """Command function to reset the database.

    Drops all of the current database tables and recreates the database based on the current models.py.

    Returns
    -------
    None

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
@click.argument('email')
@click.option('--admin/--no-admin', default=False)
def add_user(email, admin):
    """Command function to add a user to the database.

    Parameters
    ----------
    username : str
        The name of the user that should be added.

    Returns
    -------
    None

    """
    print("Adding user with mail {}:".format(email))
    password = getpass("Password: ")
    password_repeat = getpass("Retype Password: ")

    if not len(password):
        print("Password must not be empty!")
        return

    if password != password_repeat:
        print("Passwords do not match!")
        return

    add_user_to_database(email, password, admin)


def add_user_to_database(email, password, admin):
    """Adds a user with the specified parameters to the database.

    Parameters
    ----------
    email : str
        The mail of the user that should be added.
    password : str
        The password of the user that should be added.

    Returns
    -------
    None

    """
    if not models.User.query.filter(models.User.email == email).first():
        user = models.User(
            email=email,
            password=user_manager.hash_password(password),
        )
        database.session.add(user)  # pylint: disable=no-member
        database.session.commit()  # pylint: disable=no-member
        app.logger.info(f"User with email {email} added successfully.")
        app.logger.info(user)

        if admin:
            check_admin_role()
            role = models.Role.query.filter(
                models.Role.name == app.config['ADMIN_ROLE_NAME']).first()
            user_role = models.UserRoles(user_id=user.id, role_id=role.id)
            database.session.add(user_role)  # pylint: disable=no-member
            database.session.commit()  # pylint: disable=no-member
            app.logger.info(f"User with email {email} granted admin role.")


def check_admin_role():
    # add admin role
    if not models.Role.query.filter(models.Role.name == app.config['ADMIN_ROLE_NAME']).first():
        admin_role = models.Role(
            name=app.config['ADMIN_ROLE_NAME']
        )
        database.session.add(admin_role)  # pylint: disable=no-member
        database.session.commit()  # pylint: disable=no-member

# ===============================================================================
# Blueprint Registration
# ===============================================================================


# Register API and frontend
app.register_blueprint(frontend, url_prefix='/frontend')
app.register_blueprint(api, url_prefix='/api')


# ===============================================================================
# Routes
# ===============================================================================


@app.route("/")
def index():
    """Redirects index requests to the frontend index page.

    """
    print('index request')

    return redirect(url_for("frontend.index"))


@app.route("/imprint")
def imprint():
    """Redirects index requests to the frontend index page.

    """
    print('index request')

    return redirect(url_for("frontend.imprint"))


@app.route('/api/login', methods=['POST'])
def login():
    # data = request.get_json()
    # user = models.User.query.filter_by(email=data['email']).first()
    #
    # if user and user_manager.verify_password(data['password'], user.password):
    #     login_user(user)
    #
    #     # Create a response with the access token as a cookie
    #     response = make_response(jsonify({'status': 'success', 'message': 'Logged in successfully'}))
    #     response.headers['X-User-Id'] = user.id
    #
    #     return response
    # else:
    #     return jsonify({'status': 'error', 'message': 'Invalid email or password'})

    data = request.get_json()
    user = models.User.query.filter_by(email=data['email']).first()

    if user and user_manager.verify_password(data['password'], user.password):
        login_user(user)

        return jsonify({
            'status': 'success',
            'message': 'Logged in successfully',
            'user_id': user.id
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Invalid email or password'
        })


@app.route("/api/logout", methods=["GET"])
@login_required
def logout():
    """Logs out the current user and redirects to the index page."""
    logout_user()
    return jsonify({
        'status': 'success',
        'message': 'Logged out successfully'
    })


@app.route("/data/<path:path>")
def data(path):
    """Get the file from the specified path from the data directory.

    Parameters
    ----------
    path : str
        The relative path to the file in the data directory.

    Returns
    -------
    file : File
        The requested file.

    """
    return send_from_directory(app.config['DATA_DIRECTORY'], path)


@app.after_request
def add_header(r):
    """Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.

    Parameters
    ----------
    r : Request
        The request that should be edited.

    Returns
    -------
    r : Request
        The edited request.

    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r
