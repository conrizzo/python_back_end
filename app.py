
# config.py imports
from config import SECRET_KEY, JWT_KEY, redis_address, postgresql_address, redis_client
# extensions.py imports
from extensions import bcrypt, jwt

# database_connections.py imports postgresql
from database_connections import get_db_connection

# import blueprints
from authorization import authorization_bp
from messages import messages_bp
from first_routes import first_routes_bp

# rate limiter using redis
from limiter import limiter, RateLimitExceeded
from flask import Flask
from datetime import timedelta
# websockets
# from websocket import socketio

from flask_cors import CORS


# PostgreSQL database
import psycopg2
from psycopg2.extras import RealDictCursor

# Session cookies and access tokens
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, create_refresh_token, get_jwt, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)

# activate_redis = redis.Redis(host='localhost', port=6379, db=0)
# storage = RedisStorage(activate_redis)
# socketio.init_app(app)  # Initialize the socketio app - websockets


def create_app():
    app = Flask(__name__)

    @app.errorhandler(RateLimitExceeded)
    def ratelimit_handler(e):
        return {'message': 'Rate limit exceeded, the limit is 3 queries per 10 seconds.'}, 429

    cors = CORS(app, resources={r"/backend/api/*": {"origins": [
        "https://conradswebsite.com", "https://project.conradswebsite.com"]}}, supports_credentials=True)

    app.config.update(
        SECRET_KEY=SECRET_KEY,
        RATELIMIT_STORAGE_URL=redis_address,
        POSTGRESQL_URI=postgresql_address,
        JWT_SECRET_KEY=JWT_KEY,
        JWT_COOKIE_SECURE=True,
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=30),
        JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=7),
        JWT_COOKIE_SAMESITE='None',
        JWT_TOKEN_LOCATION=['cookies'],
        JWT_ACCESS_COOKIE_PATH='/backend/api/',
        JWT_REFRESH_COOKIE_PATH='/backend/api/refresh',
    )

    limiter.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)

    app.register_blueprint(authorization_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(first_routes_bp)

    return app


app = create_app()

"""
@app.route('/backend/api/country_music_generator', methods=['POST'])
@limiter.limit("3/10seconds")
def country_music_lyric_data():
    data = request.get_json()
    front_end_country_music_labels = data.get('countryMusicLabels')
    # cleaned_sentences = [bleach.clean(front_end_country_music_label) for front_end_country_music_label in front_end_country_music_labels]

    return jsonify(results)  # Convert the list to a JSON response
"""


""" 
local development

app = create_app()

if __name__ == "__main__":
    app.run()

"""
