from sqlalchemy import Table, Column, ForeignKey, Index

import datetime

from sqlalchemy.types import Integer, BigInteger, String, DateTime, PickleType, Boolean, Text, Float
from sqlalchemy.sql.schema import UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from morphocut.server.extensions import database

metadata = database.metadata

#: :type datasets: sqlalchemy.sql.schema.Table
datasets = Table('datasets', metadata,
                 Column('dataset_id', Integer, primary_key=True),
                 Column('name', String),
                 Column('author', String),
                 Column('path', String),
                 Column('active', Boolean),
                 Column('creation_date', DateTime,
                        default=datetime.datetime.now),
                 )

#: :type objects: sqlalchemy.sql.schema.Table
objects = Table('objects', metadata,
                Column('object_id', Integer, primary_key=True),
                Column('filename', String),
                Column('creation_date', DateTime,
                       default=datetime.datetime.now),
                Column('modification_date', DateTime,
                       default=datetime.datetime.now),
                Column('dataset_id', Integer, ForeignKey(
                    'datasets.dataset_id'), index=True),
                )


#: :type facets: sqlalchemy.sql.schema.Table
facets = Table('facets', metadata,
               Column('object_id', Integer, primary_key=True),
               Column('filename', String),
               Column('creation_date', DateTime,
                      default=datetime.datetime.now),
               Column('modification_date', DateTime,
                      default=datetime.datetime.now),
               Column('dataset_id', Integer, ForeignKey(
                   'datasets.dataset_id'), index=True),
               )

#: :type objects: sqlalchemy.sql.schema.Table
users = Table('users', metadata,
              Column('user_id', Integer, primary_key=True),
              Column('username', String),
              Column('pwhash', String),
              Column('admin', Boolean, default=False),
              )


#: :type projects: sqlalchemy.sql.schema.Table
projects = Table('projects', metadata,
                 Column('project_id', Integer, primary_key=True),
                 Column('name', String),
                 Column('author', String),
                 Column('active', Boolean),
                 Column('creation_date', DateTime,
                        default=datetime.datetime.now),
                 )

#: :type contributors: sqlalchemy.sql.schema.Table
contributors = Table('contributors', metadata,
                     Column('project_id', Integer),
                     Column('user_id', Integer),
                     Column('project_id', Integer, ForeignKey(
                         'projects.project_id'), index=True),
                     Column('user_id', Integer, ForeignKey(
                         'users.user_id'), index=True),
                     )
