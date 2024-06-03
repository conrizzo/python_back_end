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

# add dependency datetime, jwt cookies, may, 10 2024

app = Flask(__name__)
bcrypt = Bcrypt(app)
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
JWT_KEY = os.getenv('JWT_KEY')
# Initialize JWTManager - extends Flask app to have JWT capabilities

# Check if the secret key was not found and raise an error
if SECRET_KEY is None:
    raise ValueError(
        "No secret key set. Please set the FLASK_SECRET_KEY environment variable.")

# Where some-redis is the docker container name
redis_address = 'redis://some-redis:6379/0'

# Where postgre-sql is the docker container name
postgresql_address = f'postgresql://conrad:{POSTGRESQL_PASSWORD}@postgre-sql:5432/mydatabase'

# Set key values and addresses
app.config.update(
    SECRET_KEY=SECRET_KEY,  # Add secret key sourced from docker environment variable
    RATELIMIT_STORAGE_URL=redis_address,  # set rate limits to Redis
    POSTGRESQL_URI=postgresql_address,
    JWT_SECRET_KEY=JWT_KEY,
    JWT_COOKIE_SECURE=True,
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=30),
    JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=7),
    JWT_COOKIE_SAMESITE='None',
    JWT_TOKEN_LOCATION=['cookies'],  # Add this line
    JWT_ACCESS_COOKIE_PATH='/backend/api/',
    JWT_REFRESH_COOKIE_PATH='/backend/api/refresh',
)
# this must come after app.config - had this before stupid error I made!
jwt = JWTManager(app)

# Cors permissions for the frontend
"""
cors = CORS(app, resources={r"/backend/api/*": {"origins": [
            "https://conradswebsite.com", "https://project.conradswebsite.com"]}})
            """

# Cors permissions for the frontend, and allow credentials=True
cors = CORS(app, resources={r"/backend/api/*": {"origins": [
            "https://conradswebsite.com", "https://project.conradswebsite.com"]}}, supports_credentials=True)

# Connect to local Redis server docker address
redis_client = redis.Redis(host='some-redis', port=6379, db=0)

limiter = Limiter(
    app=app,
    key_func=lambda: request.headers.get('X-Real-IP', request.remote_addr),
    default_limits=["3 per 10 seconds"],
    storage_uri=redis_address,
    storage_options={"socket_connect_timeout": 30},
    strategy="fixed-window",  # or "moving-window"
)

# Using an `after_request` callback, we refresh any token that is within 30
# minutes of expiring. Change the timedeltas to match the needs of your application.


@app.after_request
def refresh_expiring_jwts(response):
    try:
        if request.path == '/backend/api/refresh':
            return response

        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response


# Initialize the counter
get_data_counter = int(storage_data.read_file())


@app.errorhandler(RateLimitExceeded)
def ratelimit_handler(e):
    return {'message': 'Rate limit exceeded, the limit is 3 queries per 10 seconds.'}, 429


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


"""
@app.route('/backend/api/country_music_generator', methods=['POST'])
@limiter.limit("3/10seconds")
def country_music_lyric_data():
    data = request.get_json()
    front_end_country_music_labels = data.get('countryMusicLabels')
    # cleaned_sentences = [bleach.clean(front_end_country_music_label) for front_end_country_music_label in front_end_country_music_labels]

    return jsonify(results)  # Convert the list to a JSON response
"""


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


def get_db_connection(db_uri):
    """ 
        Connect to the database
        Parameters: db_uri (str): The URI of the database
        Returns: conn (psycopg2.extensions.connection): The connection object    
    """
    conn = psycopg2.connect(db_uri)
    return conn


@app.route('/backend/api/register', methods=['POST'])
def register():
    """
    Registers a user in the PostgreSQL database

    """
    data = request.get_json()
    username = data['username']
    password = data['password']

    conn = get_db_connection(app.config['POSTGRESQL_URI'])
    cur = conn.cursor()

    # Check if username already exists
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cur.fetchone():
        cur.close()
        conn.close()
        # 409 Conflict
        return jsonify({'message': 'Username already exists'}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Proceed with inserting the new user since the username does not exist
    cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, hashed_password))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': 'User created successfully'}), 201


@app.route('/backend/api/sign_in', methods=['POST'])
def login():
    
    """
    Lets user login to the PostgreSQL database    
    """
    
    data = request.get_json()
    username = data['username']
    password = data['password']

    conn = get_db_connection(app.config['POSTGRESQL_URI'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user and bcrypt.check_password_hash(user['password_hash'], password):
        # Login successful, generate JWT and refresh token
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)

        # Use the tokens to set secure HTTP-only cookies
        response = jsonify({'login': True})
        set_access_cookies(response, access_token,)
        set_refresh_cookies(response, refresh_token)

        return response, 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401


@app.route("/backend/api/sign_out", methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response

@app.route('/backend/api/change_password', methods=['POST'])
@jwt_required()
def change_password():
    
    """
    Lets user change their password
    """
    
    data = request.get_json()
    username = data['username']
    current_password = data['current_password']
    new_password = data['new_password']

    conn = get_db_connection(app.config['POSTGRESQL_URI'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()

    if user and bcrypt.check_password_hash(user['password_hash'], current_password):
        # If the current password is correct, hash new password and update PostgreSQL data
        new_password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        cur.execute("UPDATE users SET password_hash = %s WHERE username = %s", (new_password_hash, username))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Password changed successfully'}), 200
    else:
        cur.close()
        conn.close()
        return jsonify({'message': 'Username or current password is incorrect!'}), 401

@app.route('/backend/api/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity, fresh=False)
        refresh_token = create_refresh_token(identity=identity)
        response = make_response()  # Create an empty response
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        return response, 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/backend/api/account_data', methods=['POST'])
@limiter.limit("6/10seconds")
@jwt_required()
def post_account_data():
    """
    Receives and saves the account data for the currently logged-in user.
    """
    # Get the username from the JWT
    username = get_jwt_identity()

    # Get the data from the request
    data = request.json.get('data')

    conn = get_db_connection(app.config['POSTGRESQL_URI'])
    cur = conn.cursor(cursor_factory=RealDictCursor)  # Use RealDictCursor here

    # Get the user's ID The % signs prevent SQL injection attacks
    cur.execute("SELECT user_id FROM users WHERE username = %s", (username,))
    user_id = cur.fetchone()['user_id']  # Now you can access 'user_id' by name

    # Save the user's account data
    cur.execute(
        "INSERT INTO account_data (user_id, data) VALUES (%s, %s)", (user_id, data))
    conn.commit()

    cur.close()
    conn.close()

    return jsonify(message='Data saved successfully'), 200


@app.route('/backend/api/account_data', methods=['GET'])
@limiter.limit("6/10seconds")
@jwt_required()
def get_account_data():
    
    """
    Fetches and returns the account data for the currently logged-in user.
    """
    
    # Get the username from the JWT
    username = get_jwt_identity()

    conn = get_db_connection(app.config['POSTGRESQL_URI'])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Get the user's ID The % signs prevent SQL injection attacks
    cur.execute("SELECT user_id FROM users WHERE username = %s", (username,))
    user_id = cur.fetchone()['user_id']

    # Get the user's account data along with created_at
    cur.execute(
        "SELECT data, created_at FROM account_data WHERE user_id = %s", (user_id,))
    account_data = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(account_data=account_data), 200


@app.route('/backend/api/account_data/<int:select_item>', methods=['DELETE'])
@limiter.limit("6/10seconds")
@jwt_required()
def delete_account_data(select_item):
    
    """
    This will delete a message by the user specific to it's slot in the array for the user (0-infinite)
    If the select_item is negative e.g -1 to -infinite it will delete all messages

    NOTE: This should only get a negative Input for 'select_item' if the user wants to DELETE ALL MESSAGES!

    """
    
    username = get_jwt_identity()
    conn = get_db_connection(app.config['POSTGRESQL_URI'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT user_id FROM users WHERE username = %s", (username,))
    user_id = cur.fetchone()['user_id']

    if select_item >= 0:
        cur.execute(
            "SELECT data_id FROM account_data WHERE user_id = %s ORDER BY data_id ASC", (user_id,))
        data_ids = [row['data_id'] for row in cur.fetchall()]

        if select_item < len(data_ids):
            cur.execute("DELETE FROM account_data WHERE data_id = %s AND user_id = %s",
                        (data_ids[select_item], user_id))
        else:
            return jsonify({'message': 'Invalid item number'}), 400
    else:
        cur.execute("DELETE FROM account_data WHERE user_id = %s", (user_id,))

    conn.commit()
    return jsonify({'message': 'Item(s) deleted'}), 200

# Just a note - TRAILING COMMAS ARE NOT ALLOWED AT END OF JSON ARRAY
@app.route('/backend/api/special_area', methods=['GET'])
@jwt_required()
def special_area():
    # Get the identity from the JWT
    username = get_jwt_identity()
    # set file name to get messages from
    file_name = "user_messages.json"
    message = ''

    if username == 'conrad':
        # For the moment this accesses messages users send to the server on About page to test this
        with open(file_name, 'r') as f:
            file_data = json.load(f)
            # set message to return to the file data
            message = file_data
    else:
        message = 'Access denied'

    # Create the response
    response = jsonify(message)
    # Return the response
    return response, 200


# This is for debugging without another frontend server
# The host must be local for this work
# @app.route('/')
# def home():
#    return "Hello, World!"


# This is only for development, Gunicorn runs this script automatically and we don't need a main to run the app
# if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=5000)
