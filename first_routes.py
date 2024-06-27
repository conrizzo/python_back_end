
from config import redis_client, Redis, RedisError

# Required imports
from datetime import datetime, timedelta, timezone
from flask import Flask, request, jsonify, send_file, make_response

import json
import bleach
import socket
from flask import Blueprint, current_app

# Files for the backend
import storage_data
import cosine_similarity
from limiter import limiter  # Import the limiter

"""
off for now
import country_music_lyrics
"""

# Initialize the counter
get_data_counter = int(storage_data.read_file())

first_routes_bp = Blueprint('first_routes', __name__)




@first_routes_bp.route('/backend/api/data')
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


@first_routes_bp.route('/backend/api/leave_message', methods=['POST'])
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


@first_routes_bp.route('/backend/api/cosine', methods=['POST'])
@limiter.limit("1/10seconds")
def get_cosine_similarity():
    data = request.get_json()
    s1, s2 = data.get('sentence1'), data.get('sentence2')
    s1, s2 = bleach.clean(s1), bleach.clean(s2)
    result = cosine_similarity.compute_similarity(s1, s2)
    return jsonify(result)  # Convert the dictionary to a JSON response


@first_routes_bp.route('/backend/api/download')
@limiter.limit("1/30seconds")
def download_file():
    path = "test100.txt"
    return send_file(path, as_attachment=True)
