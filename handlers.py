import json
import random

REPUTATION = {-3: 'Ненависть', -2: 'Озлобленные', -1: 'Недоверие', 0: 'Нейтральные',
              1: 'Доброжелательные', 2: 'Дружеские', 3: 'Лучшие друзья'}
MOOD = {-3: 'Cуицидальные наклонности', -2: 'Панические атаки', -1: 'Депрессия', 0: 'Удовлетворительное',
        1: 'Отличное', 2: 'Счастье', 3: 'Абсолютная гармония'}
KARMA = {-3: 'Демоническая', -2: 'Дурная', -1: 'Негативная', 0: 'Чистая',
         1: 'Позитивная', 2: 'Ангельская', 3: 'Божественная'}
intents = ['YANDEX.HELP', 'description', 'inventory', 'stats', 'story', 'rules', 'return_game']


def dialog_handler(req, res):
    if not req['state']['user']:
        return start_handler(res)
    if req['request']['nlu']['intents'] and 'YANDEX.REPEAT' in list(req['request']['nlu']['intents'].keys()):
        return repeat_handler(res, req)
    if req['request']['nlu']['intents'] and 'rules' in list(req['request']['nlu']['intents'].keys()) and \
            req['state']['user']['chapter'] != 'start':
        res['user_state_update'] = req['state']['user'].copy()
        return intent_handler(res, list(req['request']['nlu']['intents'].keys())[0])
    if req['request']['nlu']['intents'] and 'rules' not in list(req['request']['nlu']['intents'].keys()):
        for key in list(req['request']['nlu']['intents'].keys()):
            if key in intents:
                res['user_state_update'] = req['state']['user'].copy()
                return intent_handler(res, key)
    res['user_state_update'] = req['state']['user'].copy()
    data = data_handler(req['state']['user']['chapter'])
    if req['request']['type'] == 'ButtonPressed':
        res = button_handler(res, req, data)
        if data['events'][req['state']['user']['event']]['last_event']:
            data = data_handler(data['next_chapter'])
    else:
        res['user_state_update']['event'] = answer_handler(req, data['events'][req['state']['user']['event']],
                                                           req['request']['original_utterance'])

    res['user_state_update']['reputation'] += data['events'][res['user_state_update']['event']]['stats'][
        'reputation']
    res['user_state_update']['mood'] += data['events'][res['user_state_update']['event']]['stats']['mood']
    res['user_state_update']['karma'] += data['events'][res['user_state_update']['event']]['stats']['karma']
    for item in data['events'][res['user_state_update']['event']]['items']:
        res['user_state_update']['items'].append(item)
    if data['events'][res['user_state_update']['event']]['text'] == req['request']['original_utterance'] and req['session']['message_id']:
        res['response']['text'] = f"Прошу прощения, ответьте конкретнее.\n\n" \
                                  f"{data['events'][res['user_state_update']['event']]['text']}"
    else:
        res['response']['text'] = data['events'][res['user_state_update']['event']]['text']
    res['response']['tts'] = res['response']['text']
    res['response']['buttons'] = data['events'][res['user_state_update']['event']]['buttons']
    return res


def start_handler(res):
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
    return res


def intent_handler(res, intent):
    if intent == 'return_game':
        if res['user_state_update']['event'] == 'rules_1':
            res['user_state_update']['event'] = 'rules_2'
        if res['user_state_update']['event'] == 'rules_2':
            res['user_state_update']['event'] = 'rules_3'
        if res['user_state_update']['event'] == 'rules_3':
            res['user_state_update']['event'] = 'plot'
        data = data_handler(res['user_state_update']['chapter'])
        res['response']['text'] = data['events'][res['user_state_update']['event']]['text']
        res['response']['tts'] = res['response']['text']
        res['response']['buttons'] = data['events'][res['user_state_update']['event']]['buttons']
        return res
    data = data_handler('commands')
    if intent == 'stats':
        if res['user_state_update']['event'] == 'rules_2':
            res['user_state_update']['event'] = 'rules_3'
        res['response']['text'] = f'Твои показатели:\n\nОтношения с командой: ' \
                                  f'{REPUTATION[res["user_state_update"]["reputation"]]} ' \
                                  f'({res["user_state_update"]["reputation"]})\nМоральное состояние:' \
                                  f'{MOOD[res["user_state_update"]["mood"]]} ({res["user_state_update"]["mood"]})' \
                                  f'\nКарма: {KARMA[res["user_state_update"]["karma"]]} ' \
                                  f'({res["user_state_update"]["karma"]})\n\nДля продолжения скажите ' \
                                  f'\"Продолжить\".'
    elif intent == 'inventory':
        if res['user_state_update']['event'] == 'rules_3':
            res['user_state_update']['event'] = 'plot'
        if res['user_state_update']['items']:
            res['response']['text'] = f'В вашем распоряжении {", ".join(list(res["user_state_update"]["items"]))}' \
                                      f'\n\nДля продолжения скажите \"Продолжить\".'
        else:
            res['response']['text'] = 'Пока что у вас ничего нет!\n\nДля продолжения скажите \"Продолжить\".'
    else:
        res['response']['text'] = f"{data[intent]['text']}\n\nДля продолжения скажите \"Продолжить\""
    res['response']['tts'] = res['response']['text']
    res['response']['buttons'] = data[intent]['buttons']
    return res


def button_handler(res, req, data):
    if not req['request']['payload']['random']:
        res['user_state_update']['event'] = req['request']['payload']['next_event'][0]['event']
    else:
        res['user_state_update']['event'] = random.choice(req['request']['payload']['next_event'])['event']
    return res


def answer_handler(req, events, text):
    if not text:
        return req['state']['user']['event']
    for event in events['next_events']:
        for word in event['keys']:
            if word in text.lower():
                return event['event']
    for event in events['next_events']:
        if 'misunderstanding' in event['event']:
            return event['event']
    return req['state']['user']['event']


def repeat_handler(res, req):
    data = data_handler(req['state']['user']['chapter'])
    res['user_state_update'] = req['state']['user'].copy()
    res['response']['text'] = ""
    res['response']['tts'] = data['events'][res['user_state_update']['event']]['text']
    res['response']['buttons'] = data['events'][res['user_state_update']['event']]['buttons']
    return res


def data_handler(chapter):
    with open(f'data/events/{chapter}.json') as json_file:
        return json.load(json_file)
