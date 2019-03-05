
from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis
from flask_migrate import Migrate

database = SQLAlchemy()
redis_store = FlaskRedis()
migrate = Migrate()
