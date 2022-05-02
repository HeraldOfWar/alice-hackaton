import json

REPUTATION = {-3: 'Ненависть', -2: 'Озлобленные', -1: 'Недоверие', 0: 'Нейтральные',
              1: 'Доброжелательные', 2: 'Дружеские', 3: 'Лучшие друзья'}
MOOD = {-3: 'Cуицид', -2: 'Панические атаки', -1: 'Депрессия', 0: 'Удовлетворительное',
        1: 'Радость', 2: 'Счастье', 3: 'Абсолютная гармония'}
KARMA = {-3: 'Демоническая', -2: 'Дурная', -1: 'Негативная', 0: 'Чистая',
         1: 'Позитивная', 2: 'Ангельская', 3: 'Божественная'}


def handle_dialog(req, res):
    if not req['state']['user']:
        res['user_state_update'] = {
            'chapter': 'start',
            'event': 'greeting',
            'reputation': 0,
            'mood': 0,
            'karma': 0
        }
        data = data_handler('start')
    else:
        res['user_state_update'] = req['state']['user']
        data = data_handler(req['state']['user']['chapter'])
    res['text'] = data[res['user_state_update']['event']]['text']
    res['tts'] = res['text']
    return res


def data_handler(chapter):
    with open(f'data/events/{chapter}.json') as json_file:
        return json.load(json_file)
