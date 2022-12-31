# @see https://core.telegram.org/bots/webhooks
# @see https://www.freecodecamp.org/news/telegram-push-notifications-58477e71b2c2/
# Default main Wiki-as-base at https://wiki.openstreetmap.org/wiki/User:EmericusPetro/sandbox/Wiki-as-base

from ast import Tuple
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
        with open("/var/openfaas/secrets/" + secret_key, "r") as f:
            output = f.read()
    except OSError:
        return False

    return output.strip()


TELEGRAM_BOT_FILE_TOKEN = os.getenv(
    "TELEGRAM_BOT_FILE_TOKEN", "secret-wiki-telegram-bot-001"
)

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN", get_faas_secret(TELEGRAM_BOT_FILE_TOKEN)
)

TELEGRAM_BOT_NAME = os.getenv("TELEGRAM_BOT_NAME", "XptoTest123Bot")

# disable_notification
TELEGRAM_MESSAGE_DISABLE_NOTIFICATION = bool(
    os.getenv("TELEGRAM_MESSAGE_DISABLE_NOTIFICATION", "1")
)
TELEGRAM_MESSAGE_WEB_PREVIEW = bool(os.getenv("TELEGRAM_MESSAGE_WEB_PREVIEW", "1"))

FAAS_BACKEND = os.getenv("FAAS_BACKEND", "https://osm-faas.etica.ai/function/")

FAAS_ALLOWED = os.getenv(
    "FAAS_ALLOWED", "api-rdf,api-proxy,overpass-proxy,wiki-as-base,nodeinfo,cows"
).split(",")


def response_as_markdown(content: str, mediatype: str = None):
    # TODO deal with mediatype
    return "```\n" + content + "\n```"


def parse_telegram_in(body_text: str):
    return json.loads(body_text)


def parse_telegram2faas_required(message_text_in):
    if message_text_in.startswith("/faas"):
        return True
    if message_text_in.startswith(tuple(FAAS_ALLOWED)):
        return True
    if ("/" + message_text_in).startswith(tuple(FAAS_ALLOWED)):
        return True
    return False


# def parse_telegram2faas_request(message_text_in) -> tuple(str, dict):
def parse_telegram2faas_request(message_text_in) -> Tuple(str, dict):
    options = []
    faas_func = None
    faas_func_arg = ""

    # This part needs more testing
    if (
        len(TELEGRAM_BOT_NAME) > 0
        and message_text_in.find("@" + TELEGRAM_BOT_NAME) > -1
    ):
        message_text_in = message_text_in.replace("@" + TELEGRAM_BOT_NAME, "")

    for item in FAAS_ALLOWED:
        item_norm = item.lower().replace("-", "")
        option = f"/faas__{item_norm}"
        options.append(option)

        if message_text_in.startswith(f"/faas /{item_norm}"):
            faas_func = item
            faas_func_arg = message_text_in[len(f"/faas /{item_norm}") :].strip()
            break

        if message_text_in.startswith(option):
            faas_func = item
            faas_func_arg = message_text_in[len(option) :].strip()
            break

        if message_text_in.startswith("/" + option):
            faas_func = item
            faas_func_arg = message_text_in[len("/" + option) :].strip()
            break

    if faas_func is None:
        return "\n".join(options), None

    faas_full_url = FAAS_BACKEND + faas_func + faas_func_arg

    if faas_func == "overpass-proxy":
        # pass
        req = requests.post(FAAS_BACKEND + faas_func, data=message_text_in)
        return req, req.text
    else:
        req = requests.get(faas_full_url)

    if req.status_code == 200:
        return response_as_markdown(req.text, req.headers["content-type"]), None

    if (
        req.status_code == 404
        and req.headers["content-type"].startswith("application/json")
        and "examples" in req.json()
    ):
        return "404\n\n" + "\n".join(req.json()["examples"]), None
    else:
        return f"{req.status_code} {faas_full_url}", None

    # return '@TODO proxy this request ' + message_text_in + '<' + faas_func_arg + '>'
    # return False


def parse_telegram_out(tlg_in: str):
    chat_id = tlg_in["message"]["chat"]["id"]
    # notification_text = urllib.parse.quote_plus(tlg_in['message']['text'])

    if parse_telegram2faas_required(tlg_in["message"]["text"]):
        notification_text, req2 = parse_telegram2faas_request(tlg_in["message"]["text"])
    else:
        notification_text = urllib.parse.quote_plus(tlg_in["message"]["text"])
        req2 = None

    # raise Exception(notification_text)

    extras = []
    extra_params = ""
    if TELEGRAM_MESSAGE_DISABLE_NOTIFICATION:
        extras.append("disable_notification=true")
    if TELEGRAM_MESSAGE_WEB_PREVIEW:
        extras.append("no_webpage=true")
    if len(extras):
        extra_params = "&" + "&".join(extras)

    # Maybe increase the 200 characters to avoid send everyting as download file
    if len(notification_text) <= 200 or req2 is None:
        resp = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={notification_text}{extra_params}"
        )
    else:
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument?chat_id={chat_id}{extra_params}",
            data=notification_text,
        )

    # https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={notification_text}.
    return [resp.status_code, resp.text, notification_text]


def handle(event, context):

    # We would need to validate Telegram servers here (or protect the API)
    # at firewall/ip/etc strategy.

    # print(repr(event.__dict__))
    # print(repr(context.__dict__))

    # @TODO implement bot also reply to edited messages
    tlg_in_msg = False
    tlg_out_msg = False
    if event.method == "POST" and event.body and len(event.body) > 10:
        tlg_in_msg = parse_telegram_in(event.body)
        if tlg_in_msg and "message" in tlg_in_msg:
            tlg_out_msg = parse_telegram_out(tlg_in_msg)

    return {
        "statusCode": 200,
        "headers": {"content-type": "application/json; charset=utf-8"},
        "body": {
            "input": tlg_in_msg,
            "output": tlg_out_msg,
            # 'debug': "Hello from OpenFaaS! <<" + event.path + ">> <<" + repr(context.__dict__) + '>> <<' + repr(event.__dict__) + '>>' + '<<tok ' + str(TELEGRAM_BOT_TOKEN) + 'tok >>' + '<<' + str(get_faas_secret(TELEGRAM_BOT_FILE_TOKEN)) + '>>'
            # 'debug': "Hello from OpenFaaS! <<" + event.path + ">> <<" + repr(context.__dict__) + '>> <<' + repr(event.__dict__) + '>>'
        },
    }
