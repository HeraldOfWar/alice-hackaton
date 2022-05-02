import data_handler

REPUTATION = {-3: 'Ненависть', -2: 'Озлобленные', -1: 'Недоверие', 0: 'Нейтральные',
              1: 'Доброжелательные', 2: 'Дружеские', 3: 'Лучшие друзья'}
MOOD = {-3: 'Cуицид', -2: 'Панические атаки', -1: 'Депрессия', 0: 'Удовлетворительное',
        1: 'Радость', 2: 'Счастье', 3: 'Абсолютная гармония'}
KARMA = {-3: 'Демоническая', -2: 'Дурная', -1: 'Негативная', 0: 'Чистая',
         1: 'Позитивная', 2: 'Ангельская', 3: 'Божественная'}


def handle_dialog(req, res):
    if not req['state']['user']:
        return start(res)
    res['user_state_update'] = req['state']['user']
    return res


def start(res):
    res['user_state_update'] = {
        'chapter': -1,
        'event': 0,
        'reputation': 0,
        'mood': 0,
        'karma': 0
    }
    res['text'] = data_handler.start_reader
    res['tts'] = res['text']
    return res