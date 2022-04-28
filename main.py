import logging
import json
from flask import Flask, request, abort
from flask_ngrok import run_with_ngrok
from data import db_session
from data.users import User
from data.events import Event
from data.chapters import Chapter

app = Flask(__name__)
run_with_ngrok(app)
logging.basicConfig(level=logging.INFO)


@app.route('/start/<user_id>')
def start(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.user_id == user_id).first()
    if user:
        response = {
            "user": user.user_id,
            "chapter": user.chapter_id,
            "event": user.event_id
        }
        logging.info(f'Response: {response!r}')
        return response
    return abort(404)


@app.route('/create_user', methods=['POST'])
def create_user():
    logging.info(f'Request: {request.json!r}')
    db_sess = db_session.create_session()
    user = User(user_id=request.json['user_id'])
    db_sess.add(user)
    db_sess.commit()
    user = db_sess.query(User).filter(User.user_id == request.json['user_id']).first()
    response = {
        "user": user.user_id,
        "chapter": user.chapter_id,
        "event": user.event_id
    }
    logging.info(f'Response: {response!r}')
    return response


if __name__ == '__main__':
    db_session.global_init('db/hackaton_alice.db')
    app.run()
