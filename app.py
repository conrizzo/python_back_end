

# Required imports
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta, timezone
from flask import Flask, request, jsonify, send_file, make_response
from flask_limiter import Limiter
from flask_cors import CORS
from flask_limiter.extension import RateLimitExceeded
import json
import bleach
import redis
from redis import Redis, RedisError
import socket
import os

# File Imports for the backend
# make database connections to PostgreSQL
from database_connections import get_db_connection
from authorization import authorization_bp
from messages import messages_bp
from limiter import limiter

# websockets
# from websocket import socketio

# Files for the backend
import storage_data
import cosine_similarity
"""
off for now
import country_music_lyrics
"""
# PostgreSQL database
import psycopg2
from psycopg2.extras import RealDictCursor

# Session cookies and access tokens
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, create_refresh_token, get_jwt, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)

# Initialize the counter
get_data_counter = int(storage_data.read_file())
# from .database import database_bp

# add dependency datetime, jwt cookies, may, 10 2024


# activate_redis = redis.Redis(host='localhost', port=6379, db=0)
# storage = RedisStorage(activate_redis)
"""
ADD A KEY TO THE CONFIG ----------- not public
"""

"""
All these secret keys need to be set on Docker container run,
as environment variables, don't forget this or application wont run!
or in the Docker compose file, multiple ways to do this!
"""
SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
POSTGRESQL_PASSWORD = os.getenv('POSTGRESQL_PASSWORD')
# Initialize JWTManager - extends Flask app to have JWT capabilities
JWT_KEY = os.getenv('JWT_KEY')
# Check if the secret key was not found and raise an error
if SECRET_KEY is None:
    raise ValueError(
        "No secret key set. Please set the FLASK_SECRET_KEY environment variable.")
# Where some-redis is the docker container name
redis_address = 'redis://some-redis:6379/0'
# Where postgre-sql is the docker container name
postgresql_address = f'postgresql://conrad:{POSTGRESQL_PASSWORD}@postgre-sql:5432/mydatabase'

# jwt = JWTManager(app) # this jwt must come after app.config - had this before stupid error I made!
# bcrypt = Bcrypt(app) # Initialize the Bcrypt app - encryption of passwords with hashing
# socketio.init_app(app)  # Initialize the socketio app - websockets


jwt = JWTManager()
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)

    @app.errorhandler(RateLimitExceeded)
    def ratelimit_handler(e):
        return {'message': 'Rate limit exceeded, the limit is 3 queries per 10 seconds.'}, 429
    # Connect to local Redis server docker address
    redis_client = redis.Redis(host='some-redis', port=6379, db=0)
    # Cors permissions for the frontend
    """
    cors = CORS(app, resources={r"/backend/api/*": {"origins": [
                "https://conradswebsite.com", "https://project.conradswebsite.com"]}})
    """
    # Cors permissions for the frontend, and allow credentials=True
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

    @app.route('/backend/api/data')
    @limiter.limit("3/10seconds")
    def get_data():
        global get_data_counter
        get_data_counter += 1
        # Redis
        counter = redis_client.get('counter')
        redis_client.incr('counter')
        with open('counter.txt', 'w') as f:
            f.write(str(counter))
        storage_data.write_file(str(get_data_counter))
        return {'message': f'The backend server says hello back! The number of queries is: {get_data_counter}'}

    @app.route('/backend/api/leave_message', methods=['POST'])
    @limiter.limit("1/30seconds")
    def leave_message():
        data = request.get_json()
        name, subject, message = data.get('name'), data.get(
            'subject'), data.get('message')
        # Sanitize the inputs with bleach
        name, subject, message = bleach.clean(
            name), bleach.clean(subject), bleach.clean(message)

        current_datetime = datetime.now()
        date_string = current_datetime.strftime('%Y-%m-%d %H:%M:%S')

        message_dict = {"date": date_string, "name": name,
                        "subject": subject, "message": message}

        # Load the existing messages
        with open('user_messages.json', 'r') as file:
            existing_messages = json.load(file)

            # append the new message
            existing_messages.append(message_dict)

            # Write the messages back to the file
            with open('user_messages.json', 'w') as file:
                json.dump(existing_messages, file)

        return jsonify({'message': 'Form submission successful'}), 200

    @app.route('/backend/api/cosine', methods=['POST'])
    @limiter.limit("1/10seconds")
    def get_cosine_similarity():
        data = request.get_json()
        s1, s2 = data.get('sentence1'), data.get('sentence2')
        s1, s2 = bleach.clean(s1), bleach.clean(s2)
        result = cosine_similarity.compute_similarity(s1, s2)
        return jsonify(result)  # Convert the dictionary to a JSON response

    @app.route('/backend/api/download')
    @limiter.limit("1/30seconds")
    def download_file():
        path = "test100.txt"
        return send_file(path, as_attachment=True)

    
    
    return app



"""
def get_db_connection(db_uri):

        Connect to the database
        Parameters: db_uri (str): The URI of the database
        Returns: conn (psycopg2.extensions.connection): The connection object    

    conn = psycopg2.connect(db_uri)
    return conn
"""

"""
@app.route('/backend/api/country_music_generator', methods=['POST'])
@limiter.limit("3/10seconds")
def country_music_lyric_data():
    data = request.get_json()
    front_end_country_music_labels = data.get('countryMusicLabels')
    # cleaned_sentences = [bleach.clean(front_end_country_music_label) for front_end_country_music_label in front_end_country_music_labels]

    return jsonify(results)  # Convert the list to a JSON response
"""

# This is for debugging without another frontend server
# The host must be local for this work
# @app.route('/')
# def home():
#    return "Hello, World!"


# This is only for development, Gunicorn runs this script automatically and we don't need a main to run the app
# if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=5000)


""" 
local development

app = create_app()

if __name__ == "__main__":
    app.run()

"""
app = create_app()

