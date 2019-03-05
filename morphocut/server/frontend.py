"""
Frontend blueprint
"""

import datetime

from flask.blueprints import Blueprint
from flask.helpers import send_from_directory

frontend = Blueprint("frontend", __name__,
                     static_folder="frontend/dist/static", static_url_path="static")


@frontend.route('/', defaults={'path': ''})
@frontend.route('/<path:path>')
def index(path):
    response = send_from_directory("frontend/dist", 'index.html')
    del response.headers['Expires']
    del response.headers['ETag']
    response.headers['Last-Modified'] = datetime.datetime.now()
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'

    return response
