from flask import current_app
from database_connections import get_db_connection # make database connections to PostgreSQL

from flask import Blueprint

from flask import Flask, jsonify, request, make_response
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    create_refresh_token, get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)
from psycopg2.extras import RealDictCursor
from limiter import limiter  # Import the limiter

authorization_bp = Blueprint('authorization', __name__)

@authorization_bp.route('/backend/api/register', methods=['POST'])
def register():
    """
    Registers a user in the PostgreSQL database

    """
    data = request.get_json()
    username = data['username']
    password = data['password']

    conn = get_db_connection(current_app.config['POSTGRESQL_URI'])
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


@authorization_bp.route('/backend/api/sign_in', methods=['POST'])
def login():
    """
    Lets user login to the PostgreSQL database    
    """

    data = request.get_json()
    username = data['username']
    password = data['password']

    conn = get_db_connection(current_app.config['POSTGRESQL_URI'])
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


@authorization_bp.route("/backend/api/sign_out", methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response


@authorization_bp.route('/backend/api/change_password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Lets user change their password
    """

    data = request.get_json()
    username = data['username']
    current_password = data['current_password']
    new_password = data['new_password']

    conn = get_db_connection(current_app.config['POSTGRESQL_URI'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()

    if user and bcrypt.check_password_hash(user['password_hash'], current_password):
        # If the current password is correct, hash new password and update PostgreSQL data
        new_password_hash = bcrypt.generate_password_hash(
            new_password).decode('utf-8')
        cur.execute("UPDATE users SET password_hash = %s WHERE username = %s",
                    (new_password_hash, username))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Password changed successfully'}), 200
    else:
        cur.close()
        conn.close()
        return jsonify({'message': 'Username or current password is incorrect!'}), 401


@authorization_bp.route('/backend/api/refresh', methods=['POST'])
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
    
@authorization_bp.after_request
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
