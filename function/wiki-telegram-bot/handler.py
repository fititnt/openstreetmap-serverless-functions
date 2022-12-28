# @see https://core.telegram.org/bots/webhooks
# @see https://www.freecodecamp.org/news/telegram-push-notifications-58477e71b2c2/
# Default main Wiki-as-base at https://wiki.openstreetmap.org/wiki/User:EmericusPetro/sandbox/Wiki-as-base

import urllib
import json
import os
import requests
# import requests_cache


def get_faas_secret(secret_key: str):
    """get_faas_secret Read some secret from a file
    See https://docs.openfaas.com/reference/secrets/
    """
    try:
        with open('/var/openfaas/secrets/' + secret_key,'r') as f:
            output = f.read()
    except OSError:
        return False

    return output.strip()

TELEGRAM_BOT_FILE_TOKEN = os.getenv('TELEGRAM_BOT_FILE_TOKEN',
    'secret-wiki-telegram-bot-001')

TELEGRAM_BOT_TOKEN = os.getenv(
    'TELEGRAM_BOT_TOKEN',
    get_faas_secret(TELEGRAM_BOT_FILE_TOKEN)
)

FAAS_BACKEND = os.getenv('FAAS_BACKEND',
    'https://osm-faas.etica.ai/function/')

FAAS_ALLOWED = os.getenv('FAAS_ALLOWED',
    'api-rdf,api-proxy,wiki-as-base,nodeinfo').split(',')

def parse_telegram_in(body_text: str):
    return json.loads(body_text)

def parse_telegram2faas_required(message_text_in):
    if message_text_in.startswith('/faas'):
        return True
    return False

def parse_telegram2faas_request(message_text_in):
    options = []
    faas_func = None
    for item in FAAS_ALLOWED:
        options.append(f'/faas__{item}')
        if message_text_in.startswith(f'/faas__{item}'):
            faas_func = item

    if faas_func is None:
        return '\n'.join(options)

    return '@TODO proxy this request ' + message_text_in
    # return False

def parse_telegram_out(tlg_in: str):
    chat_id = tlg_in['message']['chat']['id']
    # notification_text = urllib.parse.quote_plus(tlg_in['message']['text'])

    if parse_telegram2faas_required(tlg_in['message']['text']):
        notification_text = parse_telegram2faas_request(tlg_in['message']['text'])
    else:
        notification_text = urllib.parse.quote_plus(tlg_in['message']['text'])

    # raise Exception(notification_text)

    resp = requests.get(f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={notification_text}')
    # https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={notification_text}.
    return [resp.status_code, resp.text]

def handle(event, context):

    # We would need to validate Telegram servers here (or protect the API)
    # at firewall/ip/etc strategy.
    if event.method == 'POST' and len(event.body) > 10:
        tlg_in_msg = parse_telegram_in(event.body)
        if tlg_in_msg and 'message' in tlg_in_msg:
            tlg_out_msg = parse_telegram_out(tlg_in_msg)
    else:
        tlg_in_msg = False
        tlg_out_msg = False

    return {
        "statusCode": 200,
        "headers": {
            'content-type': 'application/json; charset=utf-8'
        },
        "body": {
            'input': tlg_in_msg,
            'output': tlg_out_msg,
            # 'debug': "Hello from OpenFaaS! <<" + event.path + ">> <<" + repr(context.__dict__) + '>> <<' + repr(event.__dict__) + '>>' + '<<' + str(TELEGRAM_BOT_TOKEN) + '>>' + '<<' + str(get_faas_secret(TELEGRAM_BOT_FILE_TOKEN)) + '>>'
            'debug': "Hello from OpenFaaS! <<" + event.path + ">> <<" + repr(context.__dict__) + '>> <<' + repr(event.__dict__) + '>>'
        }
    }
