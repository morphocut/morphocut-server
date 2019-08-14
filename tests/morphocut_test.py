from morphocut_server import api
from morphocut_server import morphocut
from morphocut_server.extensions import database, migrate
from morphocut_server import models
from morphocut.pipeline import *

import os
import tempfile
import pytest
import click
from flask import (Flask, Response, abort, redirect, render_template, request,
                   url_for)
import flask_migrate
from alembic.command import upgrade
from alembic.config import Config


def test_process_and_zip(tmp_path):
    import_path = os.path.dirname(os.path.realpath(__file__))
    export_path = tmp_path / "export"
    export_path.mkdir()
    output = api.process_and_zip(import_path, export_path)
    assert 'ecotaxa_segmentation' in output
    assert 'zip' in output


def test_pipeline_append():
    pipeline = Pipeline()
    assert len(pipeline.sequence) == 0
    o = object
    pipeline.append(o)
    assert len(pipeline.sequence) == 1


def test_dataloader():
    import_path = os.path.dirname(os.path.realpath(__file__))
    dataloader = DataLoader(import_path)
    options = dataloader.get_options()
    ground_truth = dict(
        object_extensions={'.png'},
        index_files=[]
    )
    assert options == ground_truth
    output = [f for f in dataloader()]
    assert len(output) == 3


def test_processor():
    import_path = os.path.dirname(os.path.realpath(__file__))
    dataloader = DataLoader(import_path)
    vignette_corrector = VignetteCorrector()
    processor = Processor()
    output = [f for f in processor(vignette_corrector(dataloader()))]
    assert len(output) == 30


# TESTDB = 'test_project.db'
# TESTDB_PATH = 'test_db\{}'.format(TESTDB)
# TEST_DATABASE_URI = 'sqlite:///' + TESTDB_PATH
# ALEMBIC_CONFIG = r'C:\Bibliotheken\Dokumente\hiwi_geomar\morphocut\lead-eagle\migrations\alembic.ini'


# def apply_migrations():
#     """Applies all alembic migrations."""
#     config = Config(ALEMBIC_CONFIG)
#     upgrade(config, 'head')


# @pytest.fixture(scope='session')
# def app(request):
#     """Session-wide test `Flask` application."""

#     app = Flask(__name__)

#     app.config.from_object('morphocut_server.config_default')

#     if 'morphocut_SETTINGS' in os.environ:
#         app.config.from_envvar('morphocut_SETTINGS')

#     app.config['SQLALCHEMY_DATABASE_URI'] = TEST_DATABASE_URI
#     app.config['TESTING'] = True

#     # Establish an application context before running the tests.
#     ctx = app.app_context()
#     ctx.push()

#     def teardown():
#         ctx.pop()

#     request.addfinalizer(teardown)
#     return app


# @pytest.fixture(scope='session')
# def db(app, request):
#     """Session-wide test database."""
#     if os.path.exists(TESTDB_PATH):
#         os.unlink(TESTDB_PATH)

#     def teardown():
#         database.drop_all()
#         os.unlink(TESTDB_PATH)

#     database.app = app
#     # database.create_all()
#     # apply_migrations()
#     database.init_app(app)
#     migrate.init_app(app, database)
#     with database.engine.begin() as txn:
#         database.metadata.drop_all(txn)
#         database.metadata.create_all(txn)

#         flask_migrate.stamp()

#     request.addfinalizer(teardown)
#     return database


# @pytest.fixture(scope='function')
# def connection(db, request):
#     """Creates a new database connection for a test."""
#     connection = db.engine.connect()
#     transaction = connection.begin()

#     options = dict(bind=connection, binds={})
#     session = db.create_scoped_session(options=options)

#     db.session = session

#     def teardown():
#         transaction.rollback()
#         connection.close()
#         session.remove()

#     request.addfinalizer(teardown)
#     return connection


# def test_post_model(connection):
#     connection.execute(models.datasets.insert(), dict(
#         name='test_dataset', path='path/to/test_dataset', active=True))
#     result = connection.execute(
#         select([models.datasets.c.dataset_id]).select_from(models.datasets))
#     id = result.fetchone()

#     assert id > 0


# @pytest.fixture
# def client(monkeypatch):
#     db_fd, morphocut.app.config['SQLALCHEMY_DATABASE_URI'] = tempfile.mkstemp()
#     morphocut.app.config['TESTING'] = True
#     client = morphocut.app.test_client()

#     with morphocut.app.app_context():
#         monkeypatch.setattr('builtins.input', lambda x: "y")
#         morphocut.reset_db()

#     yield client

#     os.close(db_fd)
#     os.unlink(morphocut.app.config['DATABASE'])


# def test_frontend(client):
#     rv = client.get('/frontend')
#     assert b'Datasets' in rv.data
#     assert b'Projects' in rv.data
