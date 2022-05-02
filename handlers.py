import json
import random

REPUTATION = {-3: 'Ненависть', -2: 'Озлобленные', -1: 'Недоверие', 0: 'Нейтральные',
              1: 'Доброжелательные', 2: 'Дружеские', 3: 'Лучшие друзья'}
MOOD = {-3: 'Cуицид', -2: 'Панические атаки', -1: 'Депрессия', 0: 'Удовлетворительное',
        1: 'Отличное', 2: 'Счастье', 3: 'Абсолютная гармония'}
KARMA = {-3: 'Демоническая', -2: 'Дурная', -1: 'Негативная', 0: 'Чистая',
         1: 'Позитивная', 2: 'Ангельская', 3: 'Божественная'}


def dialog_handler(req, res):
    if not req['state']['user']:
        res['user_state_update'] = {
            'chapter': 'start',
            'event': 'greeting',
            'reputation': 0,
            'mood': 0,
            'karma': 0,
            'items': []
        }
        data = data_handler('start')
    else:
        res['user_state_update'] = req['state']['user']
        data = data_handler(req['state']['user']['chapter'])
        if req['request']['payload']:
            if data['events'][req['state']['user']['event']]['last_event']:
                data = data_handler(data['next_chapter'])
            elif not req['request']['payload']['random']:
                res['user_state_update']['event'] = req['request']['payload']['next_event'][0]['event']
            else:
                res['user_state_update']['event'] = random.choice(req['request']['payload']['next_event'])['event']
        else:
            res['user_state_update']['event'] = answer_handler(req['original_utterance'])
        res['user_state_update']['reputation'] += data['events'][res['user_state_update']['event']]['reputation']
        res['user_state_update']['mood'] += data['events'][res['user_state_update']['event']]['mood']
        res['user_state_update']['karma'] += data['events'][res['user_state_update']['event']]['karma']
        for item in data['events'][res['user_state_update']['event']]['items']:
            res['user_state_update']['items'].append(item)
    res['text'] = data['events'][res['user_state_update']['event']]['text']
    res['tts'] = res['text']
    res['buttons'] = data['events'][res['user_state_update']['event']]['buttons']
    return res


def data_handler(chapter):
    with open(f'data/events/{chapter}.json') as json_file:
        return json.load(json_file)


def answer_handler(text):
    return