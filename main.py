import logging
import json
from flask import Flask, request
from flask_ngrok import run_with_ngrok
from data import db_session
from data.users import User
from data.events import Event
from data.chapters import Chapter

app = Flask(__name__)
run_with_ngrok(app)
logging.basicConfig(level=logging.INFO)


@app.route("/")
def hello():
    return "Hello World!"


@app.route('/start', methods=['POST'])
def start():
    logging.info(f'Request: {request.json!r}')

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.user_id == request.json['user_id']).first()
    if user:
        response = {
            'user': user.user_id,
            'chapter': user.chapter.title,
            'event': user.event.content,
            'new_user': False
        }
        logging.info(f'Response: {response!r}')
        return json.dumps(response, ensure_ascii=False)

    user = User(user_id=request.json['user_id'])
    db_sess.add(user)
    db_sess.commit()
    user = db_sess.query(User).filter(User.user_id == request.json['user_id']).first()

    response = {
        'user': user.user_id,
        'chapter': user.chapter.title,
        'event': user.event.content,
        'new_user': True
    }
    logging.info(f'Response: {response!r}')
    return json.dumps(response, ensure_ascii=False)


if __name__ == '__main__':
    db_session.global_init('db/hackaton_alice.db')
    app.run()
