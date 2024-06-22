from flask import current_app
from database_connections import get_db_connection # make database connections to PostgreSQL

from flask import Blueprint
from flask import Flask, jsonify, request, make_response

from flask_jwt_extended import (
    get_jwt, JWTManager, jwt_required, create_access_token,
    create_refresh_token, get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)
from psycopg2.extras import RealDictCursor
import json
from limiter import limiter  # Import the limiter

messages_bp = Blueprint('message', __name__)


@messages_bp.route('/backend/api/account_data', methods=['POST'])
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

    conn = get_db_connection(current_app.config['POSTGRESQL_URI'])
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


@messages_bp.route('/backend/api/account_data', methods=['GET'])
@limiter.limit("6/10seconds")
@jwt_required()
def get_account_data():
    """
    Fetches and returns the account data for the currently logged-in user.
    """

    # Get the username from the JWT
    username = get_jwt_identity()

    conn = get_db_connection(current_app.config['POSTGRESQL_URI'])
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


@messages_bp.route('/backend/api/account_data/<int:select_item>', methods=['DELETE'])
@limiter.limit("6/10seconds")
@jwt_required()
def delete_account_data(select_item):
    """
    This will delete a message by the user specific to it's slot in the array for the user (0-infinite)
    If the select_item is negative e.g -1 to -infinite it will delete all messages

    NOTE: This should only get a negative Input for 'select_item' if the user wants to DELETE ALL MESSAGES!

    """

    username = get_jwt_identity()
    conn = get_db_connection(current_app.config['POSTGRESQL_URI'])
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


@messages_bp.route('/backend/api/special_area', methods=['GET'])
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
