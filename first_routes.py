
from config import redis_client, Redis, RedisError
import redis

# Required imports
from datetime import datetime, timedelta, timezone
from flask import Flask, request, jsonify, send_file, make_response

import json
import bleach
import socket
from flask import Blueprint, current_app

# Extra Files for this page to use with the routes
from limiter import limiter  # Import the limiter
import storage_data  # Simply reads and writes to a file
# This just runs a pre-trained sentence transformers cosine similarity model
import cosine_similarity
import blackjack_game  # This is a simple blackjack game

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


""" This routes to a blackjack game I made to connect frontend and backend together as a game """


@first_routes_bp.route('/backend/api/blackjack', methods=['POST'])
@limiter.limit("10/2seconds")
def blackjack():
    data = request.get_json()
    action = data.get('action')
    bet_amount = data.get('bet_amount', 0)
    response = {}

    if action == 'start':
        # Initialize the game, shuffle the deck, etc.
        blackjack_game.main()
        response['message'] = 'Game started'
        # Add more game initialization logic here
    elif action == 'bet':
        if self.player_chips > 0:
            # Process the bet
            response['message'] = f'Bet of {bet_amount} placed'
            # Add more bet handling logic here
        else:
            return jsonify({"message": "Insufficient chips", "inputRequired": True}), 400
    elif action == 'hit':
        # Process the hit action
        response['message'] = 'Hit action processed'
        # Add more hit handling logic here
    elif action == 'stay':
        # Process the stay action
        response['message'] = 'Stay action processed'
        # Add more stay handling logic here
    else:
        return jsonify({'error': 'Invalid action'}), 400

    game_state_json_retrieved = blackjack_redis_client.get('game_state_key')
    if game_state_json_retrieved:
        game_state_retrieved = json.loads(game_state_json_retrieved)
        player_hand = game_state_retrieved['player_hand']
        dealer_hand = game_state_retrieved['dealer_hand']
        dealer_score = game_state_retrieved['dealer_score']
        player_score = game_state_retrieved['player_score']
        player_chips = game_state_retrieved['player_chips']
        game_result = game_state_retrieved['winner']

    response["gameResult"] = game_result
    response["playerHand"] = player_hand
    response["dealerScore"] = dealer_score
    response["dealerHand"] = dealer_hand
    response["playerScore"] = player_score
    response["playerChips"] = player_chips

    return jsonify(response)  # Return the response object
