
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
# Import the limiter and blackjack game reddis
from limiter import limiter, blackjack_redis_client
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


@first_routes_bp.route('/backend/api/blackjack/reset', methods=['POST'])
@limiter.limit("10/2seconds")
def reset_game_state():
    game_state_json = blackjack_redis_client.get('game_state_key')

    if game_state_json:
        game_state = json.loads(game_state_json)
        player_chips = game_state.get('player_chips', 0)
        if player_chips <= 0:
            player_chips = 10000  # reset to 10000
        # Create a new game state with only player_chips to ensure they persist
        updated_game_state = {'player_chips': player_chips}
    else:
        # If there's no game state, initialize player_chips to a default value
        updated_game_state = {'player_chips': 10000}  # Default starting chips

    # Save the updated game state to Redis
    blackjack_redis_client.set(
        'game_state_key', json.dumps(updated_game_state))
    return jsonify({"message": "Game state reset successfully"}), 200


@first_routes_bp.route('/backend/api/blackjack/gamestate', methods=['POST'])
@limiter.limit("10/2seconds")
def read_game_state():
    game_state_json = blackjack_redis_client.get('game_state_key')
    if game_state_json:
        game_state = json.loads(game_state_json)
    else:
        game_state = {}
    return game_state


def set_game_state(blackjack_redis_client, game):
    game_state = game.serialize_state()
    game_state_json = json.dumps(game_state)
    blackjack_redis_client.set('game_state_key', game_state_json)
    return blackjack_redis_client.get('game_state_key').decode('utf-8')


""" This routes to a blackjack game I made to connect frontend and backend together as a game """


@first_routes_bp.route('/backend/api/blackjack', methods=['POST'])
@limiter.limit("10/2seconds")
def blackjack():
    data = request.get_json()
    action = data.get('action')  # get front end action 'hit' or 'stay'
    bet_amount = data.get('bet_amount', 0)  # get front end bet amount

    game_state_json = blackjack_redis_client.get('game_state_key')
    game = blackjack_game.BlackjackGame()

    if game_state_json:
        game_state = json.loads(game_state_json)
        game.load_state(game_state)
    else:
        game_state = {}  # Example initial state
        game.player_chips = 10000
        set_game_state(blackjack_redis_client, game)

    def confirm_bet():
        if game.player_chips >= bet_amount:
            game.bet = bet_amount
            set_game_state(blackjack_redis_client, game)
        else:
            return False

    if action == 'start':
        if confirm_bet() == False:
            return jsonify({"message": "Insufficient chips"}), 400

        # game.serialize_state()
        # game state would be using the reddis values
        """
            elif action == 'bet':      
                if game.player_chips >= bet_amount:
                    game.bet = bet_amount  # set bet amount       
                    set_game_state(blackjack_redis_client, game)
                else:
                    return jsonify({"message": "Insufficient chips"}), 400
        """
    elif action == 'deal':
        game.deal_initial_hands()  # deal the initial hands
        game_state['continue_betting'] = True

    if game_state['continue_betting']:
        if action == 'hit':
            game.set_action(action)
            game.result(bet_amount)

            set_game_state(blackjack_redis_client, game)
        elif action == 'stay':
            game.set_action(action)
            game.result(bet_amount)
            game_state['continue_betting'] = False
            set_game_state(blackjack_redis_client, game)
    else:
        return jsonify({'error': 'Invalid action'}), 400

    # set_game_state(blackjack_redis_client, game)

    return jsonify(set_game_state(blackjack_redis_client, game))
