import json
import random

REPUTATION = {-3: 'Ненависть', -2: 'Озлобленные', -1: 'Недоверие', 0: 'Нейтральные',
              1: 'Доброжелательные', 2: 'Дружеские', 3: 'Лучшие друзья'}
MOOD = {-3: 'Cуицидальные наклонности', -2: 'Панические атаки', -1: 'Депрессия', 0: 'Удовлетворительное',
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
        res['response']['text'] = data['events'][res['user_state_update']['event']]['text']
    elif req['request']['nlu']['intents'] and req['state']['user']['chapter'] != 'start':
        res['user_state_update'] = req['state']['user']
        return intent_handler(res, list(req['request']['nlu']['intents'].keys())[0])
    else:
        res['user_state_update'] = req['state']['user'][:]
        data = data_handler(req['state']['user']['chapter'])
        if req['request']['type'] == 'ButtonPressed':
            if data['events'][req['state']['user']['event']]['last_event']:
                res['user_state_update']['event'] = data['events'][req['state']['user']['event']]['next_event'][0][
                    'event']
                data = data_handler(data['next_chapter'])
            elif not req['request']['payload']['random']:
                res['user_state_update']['event'] = req['request']['payload']['next_event'][0]['event']
            else:
                res['user_state_update']['event'] = random.choice(req['request']['payload']['next_event'])['event']
        else:
            res['user_state_update']['event'] = answer_handler(req, data['events'][req['state']['user']['event']],
                                                               req['request']['original_utterance'])

        res['user_state_update']['reputation'] += data['events'][res['user_state_update']['event']]['stats'][
            'reputation']
        res['user_state_update']['mood'] += data['events'][res['user_state_update']['event']]['stats']['mood']
        res['user_state_update']['karma'] += data['events'][res['user_state_update']['event']]['stats']['karma']
        for item in data['events'][res['user_state_update']['event']]['items']:
            res['user_state_update']['items'].append(item)
        if res['user_state_update']['event'] == req['state']['user']['event']:
            print(res['user_state_update']['event'])
            print(req['state']['user']['event'])
            res['response']['text'] = f"Прошу прощения, ответьте конкретнее.\n\n" \
                                      f"{data['events'][res['user_state_update']['event']]['text']}"
        else:
            res['response']['text'] = data['events'][res['user_state_update']['event']]['text']
    res['response']['tts'] = res['response']['text']
    res['response']['buttons'] = data['events'][res['user_state_update']['event']]['buttons']

    return res


def data_handler(chapter):
    with open(f'data/events/{chapter}.json') as json_file:
        return json.load(json_file)


def intent_handler(res, intent):
    if intent == 'stats':
        return
    if intent == 'equipment':
        return
    data = data_handler('commands')
    return


def answer_handler(req, events, text):
    for event in events['next_events']:
        for word in event['keys']:
            if word in text:
                return event['event']
    for event in events['next_events']:
        if 'misunderstanding' in event['event']:
            return event['event']
    return req['state']['user']['event']
