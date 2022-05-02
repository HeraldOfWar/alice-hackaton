# импортируем библиотеки
from flask import Flask, request
import logging
import os
from req_res_handler import handle_dialog

# создаём приложение
# мы передаём __name__, в нем содержится информация,
# в каком модуле мы находимся.
# В данном случае там содержится '__main__',
# так как мы обращаемся к переменной из запущенного модуля.
# если бы такое обращение, например,
# произошло внутри модуля logging, то мы бы получили 'logging'
app = Flask(__name__)

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

# Создадим словарь, чтобы для каждой сессии общения
# с навыком хранились подсказки, которые видел пользователь.
# Это поможет нам немного разнообразить подсказки ответов
# (buttons в JSON ответа).
# Когда новый пользователь напишет нашему навыку,
# то мы сохраним в этот словарь запись формата
# sessionStorage[user_id] = {'suggests': ["Не хочу.", "Не буду.", "Отстань!" ]}
# Такая запись говорит, что мы показали пользователю эти три подсказки.
# Когда он откажется купить слона,
# то мы уберем одну подсказку. Как будто что-то меняется :)
sessionStorage = {}


@app.route('/post', methods=['POST'])
# Функция получает тело запроса и возвращает ответ.
# Внутри функции доступен request.json - это JSON,
# который отправила нам Алиса в запросе POST
def main():
    logging.info(f'Request: {request.json!r}')

    # Начинаем формировать ответ, согласно документации
    # мы собираем словарь, который потом при помощи
    # библиотеки json преобразуем в JSON и отдадим Алисе
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    # Отправляем request.json и response в функцию handle_dialog.
    # Она сформирует оставшиеся поля JSON, которые отвечают
    # непосредственно за ведение диалога
    response = handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    # Преобразовываем в JSON и возвращаем
    return response


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # порт
    app.run(host='0.0.0.0', port=port)  # запуск


# @app.route('/start/<user_id>')
# def start(user_id):
#     db_sess = db_session.create_session()
#     user = db_sess.query(User).filter(User.user_id == user_id).first()
#     if user:
#         response = {
#             "user": user.user_id,
#             "chapter_id": user.chapter_id,
#             "chapter": user.chapter.title,
#             "event_id": user.event_id,
#             "event": user.event.content
#         }
#         logging.info(f'Response: {response!r}')
#         return response
#     return abort(404)
#
#
# @app.route('/reset/<user_id>', methods=['POST'])
# def reset(user_id):
#     logging.info(f'Request: RESET {user_id} START')
#     db_sess = db_session.create_session()
#     user = db_sess.query(User).filter(User.user_id == user_id).first()
#     if user:
#         try:
#             user.chapter_id = 0
#             user.event_id = 0
#             user.reputation = 0
#             user.mood = 0
#             user.karma = 0
#             for item in db_sess.query(Item).filter(Item.user_id == user.id).all():
#                 db_sess.delete(item)
#             db_sess.commit()
#             logging.info(f'Request: RESET {user_id} SUCCESS')
#             return True
#         except Exception:
#             return 'Unexpected error'
#     return abort(404)
#
#
# @app.route('/create_user', methods=['POST'])
# def create_user():
#     logging.info(f'Request: {request.json!r}')
#     db_sess = db_session.create_session()
#     user = User(user_id=request.json['user_id'])
#     db_sess.add(user)
#     db_sess.commit()
#     user = db_sess.query(User).filter(User.user_id == request.json['user_id']).first()
#     response = {
#         "user": user.user_id,
#         "chapter_id": user.chapter_id,
#         "chapter": user.chapter.title,
#         "event_id": user.event_id,
#         "event": user.event.content
#     }
#     logging.info(f'Response: {response!r}')
#     return response
#
#
# @app.route('/get_event/<user_id>')
# def get_event(user_id):
#     db_sess = db_session.create_session()
#     user = db_sess.query(User).filter(User.user_id == user_id).first()
#     if user:
#         response = {
#             "event": user.event.content,
#             "buttons": user.event.buttons
#         }
#         logging.info(f'Response: {response!r}')
#         return response
#     return abort(404)
#
#
# @app.route('/next_event/<user_id>', methods=['POST'])
# def get_new_event(user_id):
#     logging.info(f'Request: {request.json!r}')
#     db_sess = db_session.create_session()
#     user = db_sess.query(User).filter(User.user_id == user_id).first()
#     if user:
#         event = db_sess.query(Event).filter(Event.id == user.event_id).first()
#         if not event:
#             return abort(404)
#         next_event_id = event.next_events[int(request.json['answer'])]
#         user.event_id = next_event_id
#         db_sess.commit()
#         response = {
#             "event": user.event.content,
#             "buttons": user.event.buttons
#         }
#         logging.info(f'Response: {response!r}')
#         return response
#     return abort(404)
#
#
# @app.route('/get_stats/<user_id>')
# def get_stats(user_id):
#     db_sess = db_session.create_session()
#     user = db_sess.query(User).filter(User.user_id == user_id).first()
#     if user:
#         response = {
#             "reputation": f'{REPUTATION[user.reputation]} ({user.reputation})',
#             "mood": f'{MOOD[user.mood]} ({user.mood})',
#             "karma": f'{KARMA[user.karma]} ({user.karma})'
#         }
#         logging.info(f'Response: {response!r}')
#         return response
#     return abort(404)
#
#
# @app.route('/add_stats/<user_id>', methods=['POST'])
# def add_stats(user_id):
#     db_sess = db_session.create_session()
#     user = db_sess.query(User).filter(User.user_id == user_id).first()
#     if user:
#         user.reputation += int(request.json['reputation'])
#         user.mood += int(request.json['mood'])
#         user.karma += int(request.json['karma'])
#         response = {
#             "reputation": f'{REPUTATION[user.reputation]} ({user.reputation})',
#             "mood": f'{MOOD[user.mood]} ({user.mood})',
#             "karma": f'{KARMA[user.karma]} ({user.karma})'
#         }
#         db_sess.commit()
#         logging.info(f'Response: {response!r}')
#         return response
#     return abort(404)
#
#
# @app.route('/get_stock/<user_id>')
# def get_stock(user_id):
#     db_sess = db_session.create_session()
#     user = db_sess.query(User).filter(User.user_id == user_id).first()
#     if user:
#         response = {
#             "items": ', '.join([item.title for item in user.items])
#         }
#         logging.info(f'Response: {response!r}')
#         return response
#     return abort(404)
#
#
# @app.route('/get_item/<item_title>')
# def get_item(item_title):
#     db_sess = db_session.create_session()
#     item = db_sess.query(Item).filter(Item.title == item_title.lower().strip()).first()
#     if item:
#         response = {
#             "title": item.title,
#             "description": item.description,
#             "user_id": item.user_id
#         }
#         logging.info(f'Response: {response!r}')
#         return response
#     return abort(404)
#
#
# @app.route('/add_item/<user_id>', methods=['POST'])
# def add_item(user_id):
#     logging.info(f'Request: {request.json!r}')
#     db_sess = db_session.create_session()
#     user = db_sess.query(User).filter(User.user_id == user_id).first()
#     if user:
#         item = Item(title=request.json['title'],
#                     description=request.json['description'],
#                     user_id=user.id)
#         user.items.append(item)
#         db_sess.merge(user)
#         db_sess.commit()
#         response = {
#             "title": item.title,
#             "description": item.description,
#             "user_id": item.user_id
#         }
#         logging.info(f'Response: {response!r}')
#         return response
#     return abort(404)


# if __name__ == '__main__':
#     db_session.global_init('db/hackaton_alice.db')
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host='0.0.0.0', port=port)
