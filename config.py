"""
    All these secret keys need to be set on Docker container run,
    as environment variables, don't forget this or application wont run!
    or in the Docker compose file, multiple ways to do this!

    'some-redis' is the docker container name

    'postgre-sql' is the docker container name
"""

import redis
from redis import Redis, RedisError
import os

from flask import Flask
# PostgreSQL database
import psycopg2
from psycopg2.extras import RealDictCursor


# Keys
SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
if SECRET_KEY is None:
    raise ValueError(
        "No secret key set. Please set the FLASK_SECRET_KEY environment variable.")

POSTGRESQL_PASSWORD = os.getenv('POSTGRESQL_PASSWORD')
JWT_KEY = os.getenv('JWT_KEY')

# Addresses
redis_address = 'redis://some-redis:6379/0'
postgresql_address = f'postgresql://conrad:{POSTGRESQL_PASSWORD}@postgre-sql:5432/mydatabase'
redis_client = redis.Redis(host='some-redis', port=6379, db=0)


