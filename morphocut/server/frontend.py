"""
Frontend blueprint
"""

import datetime

from flask.blueprints import Blueprint
from flask.helpers import send_from_directory
from flask_user import current_user, login_required, roles_required, UserManager, UserMixin

frontend = Blueprint("frontend", __name__,
                     static_folder="frontend/dist/static", static_url_path="static")


@frontend.route('/', defaults={'path': ''})
def index(path):
    return redirect(path)


@frontend.route('/imprint', defaults={'path': 'imprint'})
def imprint(path):
    return redirect(path)


@frontend.route('/<path:path>', defaults={'path': ''})
@login_required
def routes(path):
    return redirect(path)


def redirect(path):
    response = send_from_directory("frontend/dist", 'index.html')
    del response.headers['Expires']
    del response.headers['ETag']
    response.headers['Last-Modified'] = datetime.datetime.now()
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'

    return response
