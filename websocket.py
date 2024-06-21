"""
from flask_socketio import SocketIO, emit

socketio = SocketIO()

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('message')
def handle_message(data):
    print('Received message: ' + data)
    emit('response', 'This is a response')
    
    
    

from flask_socketio import SocketIO, emit, join_room, leave_room

socketio = SocketIO()

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('message', {'username': username, 'message': username + ' has entered the room.'}, room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('message', {'username': username, 'message': username + ' has left the room.'}, room=room)

@socketio.on('message')
def handle_message(data):
    emit('message', {'username': data['username'], 'message': data['message']}, room=data['room'])
    
"""