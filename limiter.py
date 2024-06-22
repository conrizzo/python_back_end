from flask_limiter import Limiter
from flask import request
import redis


# Where some-redis is the docker container name
redis_address = 'redis://some-redis:6379/0'

limiter = Limiter(
        # app=app,
        key_func=lambda: request.headers.get('X-Real-IP', request.remote_addr),
        default_limits=["3 per 10 seconds"],
        storage_uri=redis_address,
        storage_options={"socket_connect_timeout": 30},
        strategy="fixed-window",  # or "moving-window"
    )