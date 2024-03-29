import json
import random

# характеристики игрока
REPUTATION = {-3: 'Изгой', -2: 'Лузер', -1: 'Недоверие', 0: 'Нейтральная',
              1: 'Хороший человек', 2: 'Надежный капитан', 3: 'Лучший друг'}
MOOD = {-3: 'Cуицидальные наклонности', -2: 'Панические атаки', -1: 'Депрессия', 0: 'Удовлетворительное',
        1: 'Отличное', 2: 'Счастье', 3: 'Абсолютная гармония'}
KARMA = {-3: 'Демоническая', -2: 'Дурная', -1: 'Негативная', 0: 'Чистая',
         1: 'Позитивная', 2: 'Ангельская', 3: 'Божественная'}
# список интентов для обработки
intents = ['YANDEX.HELP', 'description', 'inventory', 'stats',
           'story', 'rules', 'return_game', 'YANDEX.WHAT_CAN_YOU_DO', 'restart']
MISUNDERSTANDING = [
    "Прошу прощения, ответьте конкретнее.",
    "Я Вас совсем не понимаю. Пожалуйста, ответьте точнее.",
    "Простите, не расслышал. Повторите, пожалуйста.",
    "Команда не распознана! Прошу, дайте более чёткий ответ.",
    "Ошибка! Ваш запрос оказался недостаточно полным. Попробуйте ещё раз.",
    "Даже не знаю, что сказать... Попробуйте ответить ещё раз."
]


def dialog_handler(event, context):
    """Основной обработчик запросов пользователя и ответов сервера, принимает на вход request и возвращает response"""
    res = {
        'session': event['session'],
        'version': event['version'],
        'response': {
            'end_session': False
        }
    }
    try:
        # если пользователь первый раз в игре
        if not event['state']['user']:
            return start_handler(res)  # запускаем обработчик start_handler() для приветствия

        if 'death' in event['state']['user']['event']:
            return new_game(res)  # если игрок погиб

        if event['state']['user']['last_response'] == 'restart':
            if 'YANDEX.CONFIRM' in list(event['request']['nlu']['intents'].keys()):
                return new_game(res)  # если подтвердил новую игру
            else:
                res['user_state_update'] = event['state']['user'].copy()
                return intent_handler(res, 'return_game')  # если отказался от новой игры

        # если пользователь просит повторить сообщение
        if event['request']['nlu']['intents'] and 'restart' in list(event['request']['nlu']['intents'].keys()):
            return restart(res, event)  # запускаем обработчик restart() для подтвеждения новой игры

        # если пользователь просит повторить сообщение
        if event['request']['nlu']['intents'] and 'YANDEX.REPEAT' in list(event['request']['nlu']['intents'].keys()):
            return repeat_handler(res, event)  # запускаем обработчик repeat_handler() для повторения

        # если сработал интент
        if event['request']['nlu']['intents']:
            for key in list(event['request']['nlu']['intents'].keys()):
                if key in intents:  # ищем подходящий интент из списка
                    if key != 'return_game' or event['state']['user']['last_response'] == 'command':
                        res['user_state_update'] = event['state']['user'].copy()
                        return intent_handler(res, key)  # запускаем обработчик intent_handler() для ответа на команду

        res['user_state_update'] = event['state']['user'].copy()
        data = data_handler(event['state']['user']['chapter'])

        if event['request']['type'] == 'ButtonPressed':  # если пользователь нажал на кнопку
            # запускаем обработчик button_handler() для ответа на кнопку
            res['user_state_update']['event'] = button_handler(event)

        else:  # если пользователь отправил сообщение
            # запускаем обработчик текста пользователя answer_handler()
            res['user_state_update']['event'] = answer_handler(event, data['events'][event['state']['user']['event']],
                                                               event['request']['original_utterance'].lower())

        if data['events'][event['state']['user']['event']]['last_event']:
            res['user_state_update']['chapter'] = data['next_chapter']
            data = data_handler(data['next_chapter'])  # переходим в новую главу, если это был последний ивент

        if res['user_state_update']['event'] != event['state']['user']['event'] or not event['session']['message_id']:
            # обновляем характеристики
            if -3 < res['user_state_update']['reputation'] < 3:
                res['user_state_update']['reputation'] += data['events'][res['user_state_update']['event']]['stats'][
                    'reputation']
            if -3 < res['user_state_update']['mood'] < 3:
                res['user_state_update']['mood'] += data['events'][res['user_state_update']['event']]['stats']['mood']
            if -3 < res['user_state_update']['karma'] < 3:
                res['user_state_update']['karma'] += data['events'][res['user_state_update']['event']]['stats']['karma']

            # обновляем инвентарь
            for item in data['events'][res['user_state_update']['event']]['items']:
                res['user_state_update']['items'].append(item)

        # возвращаем текст события
        if res['user_state_update']['event'] == event['state']['user']['event'] and event['session']['message_id']:
            # обработка непонятного запроса
            res['response']['text'] = random.choice(MISUNDERSTANDING)
            res['response']['tts'] = res['response']['text']
        else:
            res['response']['text'] = data['events'][res['user_state_update']['event']]['text']  # текст
            res['response']['tts'] = data['events'][res['user_state_update']['event']]['tts']  # голос
        res['response']['buttons'] = data['events'][res['user_state_update']['event']]['buttons']  # кнопки
        if data['events'][res['user_state_update']['event']]['card']:
            res['response']['card'] = data['events'][res['user_state_update']['event']]['card']
        res['user_state_update']['last_response'] = 'event'

        return res
    except Exception:
        print('error')
        return start_handler(res)


def start_handler(res):
    """Собираем показатели нового игрока и возвращаем приветственное сообщение"""
    res['user_state_update'] = {
        'chapter': 'start',
        'event': 'greeting',
        'reputation': 0,
        'mood': 0,
        'karma': 0,
        'items': [],
        'last_response': 'greeting'
    }
    data = data_handler('start')
    res['response']['text'] = data['events'][res['user_state_update']['event']]['text']
    res['response']['tts'] = data['events'][res['user_state_update']['event']]['tts']
    res['response']['buttons'] = data['events'][res['user_state_update']['event']]['buttons']
    if data['events'][res['user_state_update']['event']]['card']:
        res['response']['card'] = data['events'][res['user_state_update']['event']]['card']

    return res


def intent_handler(res, intent):
    """Обработчик интентов"""
    if intent == 'return_game':  # воозвращение к основной ветке событий
        if res['user_state_update']['event'] == 'rules_1':
            res['user_state_update']['event'] = 'rules_2'
            res['user_state_update']['last_response'] = 'greeting'
        elif res['user_state_update']['event'] == 'rules_2':
            res['user_state_update']['event'] = 'rules_3'
            res['user_state_update']['last_response'] = 'greeting'
        elif res['user_state_update']['event'] == 'rules_3':
            res['user_state_update']['event'] = 'plot'
            res['user_state_update']['last_response'] = 'greeting'
        elif res['user_state_update']['event'] == 'greeting':
            res['user_state_update']['event'] = 'ready_to_start'
            res['user_state_update']['last_response'] = 'greeting'
        data = data_handler(res['user_state_update']['chapter'])
        res['response']['text'] = data['events'][res['user_state_update']['event']]['text']
        res['response']['tts'] = data['events'][res['user_state_update']['event']]['tts']
        res['response']['buttons'] = data['events'][res['user_state_update']['event']]['buttons']
        if data['events'][res['user_state_update']['event']]['card']:
            res['response']['card'] = data['events'][res['user_state_update']['event']]['card']
        res['user_state_update']['last_response'] = 'event'
        return res
    if intent == 'rules' and res['user_state_update']['chapter'] == 'start':
        data = data_handler('start')
        res['user_state_update']['event'] = 'rules_1'
        res['response']['text'] = data['events']['rules_1']['text']
        res['response']['tts'] = data['events']['rules_1']['tts']
        res['response']['buttons'] = data['events']['rules_1']['buttons']
        if data['events']['rules_1']['card']:
            res['response']['card'] = data['events']['rules_1']['card']
        return res
    data = data_handler('commands')
    res['user_state_update']['last_response'] = 'command'
    if intent == 'stats':  # обработка запроса "Мои показатели"
        res['response']['text'] = f'Твои показатели:\n\nОтношения с командой: ' \
                                  f'{REPUTATION[res["user_state_update"]["reputation"]]} ' \
                                  f'({res["user_state_update"]["reputation"]})\nМоральное состояние: ' \
                                  f'{MOOD[res["user_state_update"]["mood"]]} ({res["user_state_update"]["mood"]})' \
                                  f'\nКарма: {KARMA[res["user_state_update"]["karma"]]} ' \
                                  f'({res["user_state_update"]["karma"]})\n\nДля продолжения скажите ' \
                                  f'\"Продолжить\".'
        res['response']['card'] = data[intent]['card']
        res['response']['card']['description'] = res['response']['text'][18:]
    elif intent == 'inventory':  # обработка запроса "Мой инвентарь"
        if res['user_state_update']['items']:  # если есть вещи
            res['response']['text'] = f'В вашем распоряжении {", ".join(list(res["user_state_update"]["items"]))}.' \
                                      f'\n\nДля продолжения скажите \"Продолжить\".'
        else:  # если нет вещей
            res['response']['text'] = 'Пока что у вас ничего нет!\n\nДля продолжения скажите \"Продолжить\".'
        res['response']['card'] = data[intent]['card']
        res['response']['card']['description'] = res['response']['text']
    else:  # обработка всех остальных ивентов
        res['response']['text'] = f"{data[intent]['text']}\n\nДля продолжения скажите \"Продолжить\""
        if data[intent]['card']:
            res['response']['card'] = data[intent]['card']
            if (intent == 'YANDEX.HELP' or intent == 'YANDEX.WHAT_CAN_YOU_DO') and \
                    res['user_state_update']['chapter'] == 'start':
                res['response']['card']['items'] = res['response']['card']['items'][:-1]
    res['response']['tts'] = res['response']['text']
    res['response']['buttons'] = data[intent]['buttons']
    return res


def button_handler(req):
    """Обработка кнопок"""
    if req['request']['payload']['random']:  # если следующее событие конкретное
        return random.choice(req['request']['payload']['next_event'])['event']
    else:  # если следующее событие случайное
        return req['request']['payload']['next_event'][0]['event']


def answer_handler(req, events, text):
    """Обработка текстового запроса пользователя"""
    if not text:  # пустое сообщение
        return req['state']['user']['event']
    if req['state']['user']['chapter'] == 'start':
        for event in events['next_events']:  # поиск ключевых слов в тексте
            if not event['keys']:
                return event['event']
            for word in event['keys']:
                if word in text:
                    return event['event']
    for event in events['next_events']:
        if not event['random']:
            if not event['keys']:
                return event['event']
            for word in event['keys']:
                if word in text:
                    return event['event']
        else:
            if not event['keys']:
                return random.choice(event['event'])
            for word in event['keys']:
                if word in text:
                    return random.choice(event['event'])

    return req['state']['user']['event']  # непонятный ответ


def repeat_handler(res, req):
    """Обработчик повторения"""
    data = data_handler(req['state']['user']['chapter'])
    res['user_state_update'] = req['state']['user'].copy()
    res['response']['text'] = data['events'][res['user_state_update']['event']]['text']
    res['response']['tts'] = data['events'][res['user_state_update']['event']]['tts']
    res['response']['buttons'] = data['events'][res['user_state_update']['event']]['buttons']
    if data['events'][res['user_state_update']['event']]['card']:
        res['response']['card'] = data['events'][res['user_state_update']['event']]['card']
    return res


def restart(res, req):
    """Обработчик запроса новой игры"""
    res['user_state_update'] = req['state']['user'].copy()
    data = data_handler('commands')
    res['response']['text'] = data['restart']['text']
    res['response']['tts'] = res['response']['text']
    res['response']['buttons'] = data['restart']['buttons']
    res['user_state_update']['last_response'] = 'restart'
    return res


def new_game(res):
    """Начинает новую игру, сбрасывает показатели игрока"""
    res['user_state_update'] = {
        'chapter': 'prologue',
        'event': 'event_0',
        'reputation': 0,
        'mood': 0,
        'karma': 0,
        'items': [],
        'last_response': 'event'
    }
    data = data_handler('prologue')
    res['response']['text'] = data['events'][res['user_state_update']['event']]['text']
    res['response']['tts'] = data['events'][res['user_state_update']['event']]['tts']
    res['response']['buttons'] = data['events'][res['user_state_update']['event']]['buttons']
    if data['events'][res['user_state_update']['event']]['card']:
        res['response']['card'] = data['events'][res['user_state_update']['event']]['card']

    return res


def data_handler(chapter):
    """Возвращает json-файл с нужной главой"""
    with open(f'data/events/{chapter}.json') as json_file:
        return json.load(json_file)
