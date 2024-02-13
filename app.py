# GNU nano 6.2                                                                                                        app.py                                                                                                                 from flask import Flask, request

from datetime import datetime


from flask import Flask, request  # this is for debugging on local server

from flask_limiter import Limiter
from flask_cors import CORS
from flask_limiter.extension import RateLimitExceeded
import json

import storage_data

app = Flask(__name__)

# "http://localhost:8080" only for testing in the cors
cors = CORS(app, resources={r"/back_end/api/*": {"origins": ["https://conradswebsite.com","http://localhost:8080"]}})

limiter = Limiter(
    app=app,
    key_func=lambda: request.headers.get('X-Real-IP', request.remote_addr),
    default_limits=["3 per 10 seconds"]
)

# Initialize the counter
get_data_counter = int(storage_data.read_file())

@app.errorhandler(RateLimitExceeded)
def ratelimit_handler(e):
    return {'message': 'Rate limit exceeded, the limit is 3 queries per 10 seconds.'}, 429

@app.route('/back_end/api/data')
@limiter.limit("3/10seconds")
def get_data():
    global get_data_counter
    get_data_counter+=1
    storage_data.write_file(str(get_data_counter))
    return {'message': f'The backend server says hello back! The number of queries is: {get_data_counter}'}


@app.route('/back_end/api/leave_message', methods=['POST'])
@limiter.limit("1/30seconds")
def leave_message():
    data = request.get_json()
    name = data.get('name')
    subject = data.get('subject')
    message = data.get('message')
    
    current_datetime = datetime.now()
    date_string = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    
    message_dict = {"date": date_string, "name": name,"subject": subject, "message": message}
    with open('user_messages.json', 'a') as file:
        file.write(json.dumps(message_dict) + '\n')
    return jsonify({'message': 'Message received'}), 200


@app.route('/back_end/api/cosine', methods=['POST'])
@limiter.limit("1/10seconds")
def get_cosine_similarity():
    data = request.get_json()
    s1 = data.get('sentence1')
    s2 = data.get('sentence2')
    result = cosine_similarity.compute_similarity(s1, s2)
    return jsonify(result)  # Convert the dictionary to a JSON response


# this is for debugging without frontend server
@app.route('/')
def home():
    return "Hello, World!"


if __name__ == '__main__':
    # app.run(host='0.0.0.0')    
    app.run(host='127.0.0.1', debug=True) # this is for debugging without frontend server
