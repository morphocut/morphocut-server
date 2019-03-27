
from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis
from flask_migrate import Migrate

from rq import Queue
from morphocut.server.worker import redis_conn

database = SQLAlchemy()
redis_store = FlaskRedis()
migrate = Migrate()
redis_queue = Queue(connection=redis_conn)
