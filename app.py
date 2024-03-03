from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_limiter import Limiter
from flask_cors import CORS
from flask_limiter.extension import RateLimitExceeded
import storage_data
import cosine_similarity
import json
import bleach
import redis
from redis import Redis, RedisError


app = Flask(__name__)
#activate_redis = redis.Redis(host='localhost', port=6379, db=0)
#storage = RedisStorage(activate_redis)
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
app.config['RATELIMIT_STORAGE_URL'] = 'redis://localhost:6379/0'

cors = CORS(app, resources={r"/back_end/api/*": {"origins": [
            "https://conradswebsite.com", "https://project.conradswebsite.com"]}})


limiter = Limiter(
    app=app,
    key_func=lambda: request.headers.get('X-Real-IP', request.remote_addr),
    default_limits=["3 per 10 seconds"],
    storage_uri="redis://localhost:6379",
    storage_options={"socket_connect_timeout": 30},
    strategy="fixed-window", # or "moving-window"
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
    name, subject, message = data.get('name'), data.get('subject'), data.get('message')  
    # Sanitize the inputs with bleach
    name,subject,message = bleach.clean(name), bleach.clean(subject), bleach.clean(message)    
    
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

# This is only for development, Gunicorn runs this script automatically and we don't need a main to run the app
#if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=5000)

