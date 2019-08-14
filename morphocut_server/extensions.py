
from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis
from flask_migrate import Migrate
# from flask_rq2 import RQ

from rq import Queue
from morphocut_server.worker import redis_conn

database = SQLAlchemy()
redis_store = FlaskRedis()
migrate = Migrate()
redis_queue = Queue(connection=redis_conn)
flask_rq = None
