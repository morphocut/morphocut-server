# Redis
REDIS_URL = "redis://:@localhost:6379/0"

# Database
SQLALCHEMY_DATABASE_URI = "postgresql://morphocut:morphocut@localhost/morphocut"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_OPTIONS = {
    'connect_args': {
        "options": "-c statement_timeout=240s"
    }
}

# Project export directory
PROJECT_EXPORT_DIR = "/tmp"

UPLOAD_FOLDER = 'static'

# Upload Settings
ALLOWED_EXTENSIONS = set(
    ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

SEND_FILE_MAX_AGE_DEFAULT = 0
