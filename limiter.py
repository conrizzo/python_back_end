from flask_limiter import Limiter
from flask import request
import redis
from flask_limiter.extension import RateLimitExceeded

# Where some-redis is the docker container name
# some-redis is the docker container name
# 6379 is the default port
# 0 is the default database number
redis_address = 'redis://some-redis:6379/0'

limiter = Limiter(
    # app=app,
    key_func=lambda: request.headers.get('X-Real-IP', request.remote_addr),
    default_limits=["3 per 10 seconds"],
    storage_uri=redis_address,
    storage_options={"socket_connect_timeout": 30},
    strategy="fixed-window",  # or "moving-window"
)

# set reddis to database number 1
redis_address_blackjack = 'redis://some-redis:6379/1'
blackjack_redis_client = redis.Redis.from_url(redis_address_blackjack)
