from flask import Flask, request
from datetime import datetime
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_limiter import Limiter
from flask_cors import CORS
from flask_limiter.extension import RateLimitExceeded
import storage_data
import cosine_similarity
import json
import bleach

app = Flask(__name__)
cors = CORS(app, resources={r"/back_end/api/*": {"origins": [
            "https://conradswebsite.com", "https://project.conradswebsite.com"]}})


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
    get_data_counter += 1
    storage_data.write_file(str(get_data_counter))
    return {'message': f'The backend server says hello back! The number of queries is: {get_data_counter}'}


@app.route('/back_end/api/leave_message', methods=['POST'])
@limiter.limit("1/30seconds")
def leave_message():
    data = request.get_json()
    name = data.get('name')
    subject = data.get('subject')
    message = data.get('message')

    # Sanitize the inputs with bleach
    name = bleach.clean(name)
    subject = bleach.clean(subject)
    message = bleach.clean(message)

    current_datetime = datetime.now()
    date_string = current_datetime.strftime('%Y-%m-%d %H:%M:%S')

    message_dict = {"date": date_string, "name": name,
                    "subject": subject, "message": message}
    with open('user_messages.json', 'a') as file:
        file.write(json.dumps(message_dict) + '\n')
    return jsonify({'message': 'Form submission successful'}), 200


@app.route('/back_end/api/cosine', methods=['POST'])
@limiter.limit("1/10seconds")
def get_cosine_similarity():
    data = request.get_json()
    s1, s2 = data.get('sentence1'), data.get('sentence2')
    s1, s2 = bleach.clean(s1), bleach.clean(s2)
    result = cosine_similarity.compute_similarity(s1, s2)
    return jsonify(result)  # Convert the dictionary to a JSON response


@app.route('/back_end/api/download')
@limiter.limit("1/30seconds")
def download_file():
    path = "test100.txt"
    return send_file(path, as_attachment=True)

### This is for debugging without another frontend server
### The host must be local for this work 
#@app.route('/')
#def home():
#    return "Hello, World!"


if __name__ == '__main__':
    app.run(host='0.0.0.0')
