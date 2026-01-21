from flask import Blueprint, render_template, request, jsonify, abort, current_app
from flask_login import login_required, current_user
from src.extensions import socketio, db
from src.models.user import User, ChatMessage
from flask_socketio import join_room, leave_room, emit
from datetime import datetime

chat = Blueprint('chat', __name__)


@chat.route('/chat')
@login_required
def chat_page():
    # provide a contact list: doctors for patients, patients for doctors
    if (current_user.role or '').strip().lower() == 'patient':
        contacts = User.query.filter(User.role.ilike('doctor')).order_by(User.username).all()
    else:
        contacts = User.query.filter(User.role.ilike('patient')).order_by(User.username).all()
    return render_template('chat.html', contacts=contacts)


@chat.route('/api/get_messages/<int:other_id>')
@login_required
def get_messages(other_id):
    # ensure other user exists
    other = User.query.get_or_404(other_id)
    # authorize: allow chats between any users (application may restrict later)
    msgs = ChatMessage.query.filter(
        ((ChatMessage.sender_id == current_user.id) & (ChatMessage.receiver_id == other_id)) |
        ((ChatMessage.sender_id == other_id) & (ChatMessage.receiver_id == current_user.id))
    ).order_by(ChatMessage.timestamp.asc()).all()

    data = [
        {'id': m.id, 'from': m.sender_id, 'to': m.receiver_id, 'text': m.message_text, 'timestamp': m.timestamp.isoformat()}
        for m in msgs
    ]
    return jsonify(data)


@socketio.on('connect')
def handle_connect():
    # when a client connects, join them to a room named after their user id (if available)
    try:
        uid = current_user.id
        join_room(str(uid))
        current_app.logger.debug('User %s joined socket room %s', uid, uid)
    except Exception:
        current_app.logger.debug('Socket connect: anonymous or no user')


@socketio.on('private_message')
def handle_private_message(data):
    # data expected: { 'to_user_id': 123, 'message': 'Hi' }
    sender = None
    try:
        sender = current_user
    except Exception:
        emit('error', {'error': 'Authentication required'})
        return

    to_id = data.get('to_user_id')
    text = data.get('message', '').strip()
    if not to_id or not text:
        emit('error', {'error': 'Missing fields'})
        return

    # persist message
    msg = ChatMessage(sender_id=sender.id, receiver_id=int(to_id), message_text=text, timestamp=datetime.utcnow())
    db.session.add(msg)
    db.session.commit()

    payload = {'id': msg.id, 'from': msg.sender_id, 'to': msg.receiver_id, 'text': msg.message_text, 'timestamp': msg.timestamp.isoformat()}

    # emit to receiver's room and sender (so sender sees it too)
    emit('new_message', payload, room=str(to_id))
    emit('new_message', payload, room=str(sender.id))
