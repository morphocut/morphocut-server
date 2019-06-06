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

DATA_DIRECTORY = 'data'
STATIC_DIRECTORY = 'static'

# Upload Settings
ALLOWED_EXTENSIONS = set(
    ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

SEND_FILE_MAX_AGE_DEFAULT = 0

# Flask-User settings
# Shown in and email templates and page footers
USER_APP_NAME = "morphocut"
USER_ENABLE_EMAIL = True        # Disable email authentication
USER_ENABLE_USERNAME = False    # Enable username authentication
USER_ENABLE_REGISTER = False
USER_ENABLE_CONFIRM_EMAIL = False
USER_EMAIL_SENDER_EMAIL = ''
USER_EMAIL_SENDER_EMAIL = USER_APP_NAME

ADMIN_ROLE_NAME = 'admin'


SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'
