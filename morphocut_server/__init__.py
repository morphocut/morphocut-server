from .morphocut import app


# def create_app():
#     import os
#     from flask import (Flask, Response, abort, redirect, render_template, request,
#                        url_for)
#     from flask_cors import CORS
#     from flask_user import current_user, login_required, roles_required, UserManager, UserMixin

#     from morphocut.server import models
#     from morphocut.server import morphocut as mc
#     from morphocut.server.extensions import database, migrate, redis_store, flask_rq
#     from morphocut.server.api import api
#     from morphocut.server.frontend import frontend
#     from morphocut.server.morphocut import morphocut

#     app = Flask(__name__)

#     app.config.from_object('morphocut.server.config_default')

#     if 'MORPHOCUT_SETTINGS' in os.environ:
#         app.config.from_envvar('MORPHOCUT_SETTINGS')

#     # Initialize extensions
#     database.init_app(app)
#     redis_store.init_app(app)
#     migrate.init_app(app, database)
#     flask_rq.init_app(app)
#     CORS(app)
#     user_manager = UserManager(app, database, models.User)

#     app.register_blueprint(frontend, url_prefix='/frontend')
#     app.register_blueprint(api, url_prefix='/api')
#     app.register_blueprint(morphocut)

#     # app.cli.add_command(mc.reset_db)

#     return app

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
