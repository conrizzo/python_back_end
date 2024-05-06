from flask_bcrypt import Bcrypt
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_limiter import Limiter
from flask_cors import CORS
from flask_limiter.extension import RateLimitExceeded



import storage_data
import cosine_similarity

""" 
off for now 
import country_music_lyrics 
"""

import json
import bleach
import redis
from redis import Redis, RedisError

import socket
import os

# PostgreSQL database
import psycopg2
from psycopg2.extras import RealDictCursor

# Session cookies
from flask_jwt_extended import JWTManager, create_access_token


app = Flask(__name__)
# activate_redis = redis.Redis(host='localhost', port=6379, db=0)
# storage = RedisStorage(activate_redis)
'''
def test_redis_connection():
    try:
        # Create a new Redis connection (replace with your settings if necessary)
        r = Redis(host='localhost', port=6379, db=0)

        # Perform a simple operation to check the connection
        r.ping()

        print("Successfully connected to Redis.")
    except RedisError:
        print("Failed to connect to Redis.")

# Call the function to test the connection
test_redis_connection()
'''
'''
app.config['RATELIMIT_STORAGE_URL'] = 'redis://localhost:6379/0'

cors = CORS(app, resources={r"/backend/api/*": {"origins": [
            "https://conradswebsite.com", "https://project.conradswebsite.com"]}})

# Connect to local Redis server
r = redis.Redis(host='localhost', port=6379, db=0)
'''

'''
redis_address = 'redis://localhost:6379/0'
app.config['RATELIMIT_STORAGE_URL'] = redis_address

cors = CORS(app, resources={r"/backend/api/*": {"origins": [
            "https://conradswebsite.com", "https://project.conradswebsite.com"]}})

# Connect to local Redis server
# Connect to local Redis server
r = redis.Redis(host='localhost', port=6379, db=0)

limiter = Limiter(
    app=app,
    key_func=lambda: request.headers.get('X-Real-IP', request.remote_addr),
    default_limits=["3 per 10 seconds"],
    storage_uri=redis_address,
    storage_options={"socket_connect_timeout": 30},
    strategy="fixed-window", # or "moving-window"
)



ADD A KEY TO THE CONFIG ----------- not public
'''


""" 
All these secret keys need to be set on Docker container run,
as environment variables, don't forget this or application wont run!
or in the Docker compose file, multiple ways to do this!
"""
SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
POSTGRESQL_PASSWORD = os.getenv('POSTGRESQL_PASSWORD')
JWT_KEY = os.getenv('JWT_KEY')

# Initialize JWTManager - extends Flask app to have JWT capabilities
jwt = JWTManager(app)

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
)

# Cors permissions for the frontend
cors = CORS(app, resources={r"/backend/api/*": {"origins": [
            "https://conradswebsite.com", "https://project.conradswebsite.com"]}})

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
    with open('user_messages.json', 'a') as file:
        file.write(json.dumps(message_dict) + '\n')

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


bcrypt = Bcrypt(app)



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
        return jsonify({'error': 'Username already exists'}), 409  # 409 Conflict

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Proceed with inserting the new user since the username does not exist
    cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, hashed_password))
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({'message': 'User created successfully'}), 201

@app.route('/backend/api/login', methods=['POST'])
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
        # Login successful, generate JWT
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401
    
# This is for debugging without another frontend server
# The host must be local for this work
# @app.route('/')
# def home():
#    return "Hello, World!"


# This is only for development, Gunicorn runs this script automatically and we don't need a main to run the app
# if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=5000)


# Test psql connection --- testing purposes
def test_postgresql_connection():
    try:
        # Connect to your PostgreSQL database
        conn = get_db_connection(app.config['POSTGRESQL_URI'])

        # Create a cursor object
        cur = conn.cursor()

        # Execute a simple query
        cur.execute('SELECT version();')

        # Fetch and print the result
        db_version = cur.fetchone()
        print(f"Connected to PostgreSQL database: {db_version[0]}")

        # Close the cursor and connection
        cur.close()
        conn.close()

    except Exception as e:
        print(f"An error occurred: {e}")


test_postgresql_connection()
