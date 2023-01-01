# @see https://core.telegram.org/bots/webhooks
# @see https://www.freecodecamp.org/news/telegram-push-notifications-58477e71b2c2/
# Default main Wiki-as-base at https://wiki.openstreetmap.org/wiki/User:EmericusPetro/sandbox/Wiki-as-base

from ast import Tuple

# import shutil
import urllib
import json
import os
import requests

from rivescript import RiveScript

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


# ____________________________________________________________________________ #

# @TODO ideally the rivestript server should initialyze only once and not
#       in each request, see
#       https://github.com/aichaos/rivescript/wiki/Make-a-Single-Shared-Bot-Instance
#       This TODO is mostly to check later if we're somewhat okay


def bot_brain_init_external_files() -> str:
    """bot_brain_init_external_files fetch files and return local path"""
    brain_files = {
        "ola.rive": "https://raw.githubusercontent.com/fititnt/openstreetmap-serverless-functions/main/data/rivescript/pt/ola.rive"
    }
    if not os.path.isdir("/tmp/brain"):
        os.makedirs("/tmp/brain")

    for finename, url in brain_files.items():
        if not os.path.isfile("/tmp/brain/" + finename):
            response = requests.get(url, stream=True)
            with open("/tmp/brain/" + finename, "w") as out_file:
                out_file.write(response.text)
            # with open("/tmp/brain/" + finename, "w") as out_file:
            #     shutil.copyfileobj(response.raw, out_file)
    return "/tmp/brain/"


_brain_base = bot_brain_init_external_files()
# print(os.listdir(_brain_base))

BOT = RiveScript()
BOT.load_directory(_brain_base)
BOT.sort_replies()

# ____________________________________________________________________________ #


def parse_telegram_out(message_reply: str, chat_id: int):

    notification_text = urllib.parse.quote_plus(message_reply)

    # raise Exception(notification_text)

    extras = []
    extra_params = ""
    if TELEGRAM_MESSAGE_DISABLE_NOTIFICATION:
        extras.append("disable_notification=true")
    if TELEGRAM_MESSAGE_WEB_PREVIEW:
        extras.append("no_webpage=true")
    if len(extras):
        extra_params = "&" + "&".join(extras)

    resp = requests.get(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={notification_text}{extra_params}"
    )

    # Maybe increase the 200 characters to avoid send everyting as download file
    # if len(notification_text) <= 200 or req2 is None:
    #     resp = requests.get(
    #         f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={notification_text}{extra_params}"
    #     )
    # else:
    #     resp = requests.post(
    #         f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument?chat_id={chat_id}{extra_params}",
    #         data=notification_text,
    #     )

    # https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={notification_text}.
    return [resp.status_code, resp.text, notification_text]


def handle(event, context):

    # @TODO implement bot also reply to edited messages
    tlg_in_msg = False
    tlg_out_msg = False

    message_reply = "...silence..."
    err = True
    if event.method == "POST" and event.body and len(event.body) > 10:
        tlg_in_msg = json.loads(event.body)
        message = {}
        message_text = ""
        user_id = 1
        chat_id = None

        # @TODO deal with edited messages, files, etc
        if "message" in tlg_in_msg and "text" in tlg_in_msg["message"]:
            message_text = tlg_in_msg["message"]["text"]

        if (
            "message" in tlg_in_msg
            and "chat" in tlg_in_msg["message"]
            and "id" in tlg_in_msg["message"]["chat"]
        ):
            chat_id = tlg_in_msg["message"]["chat"]["id"]

        if (
            "message" in tlg_in_msg
            and "from" in tlg_in_msg["message"]
            and "id" in tlg_in_msg["message"]["from"]
        ):
            user_id = tlg_in_msg["message"]["from"]["id"]

        # chat_id = message["chat"]["id"]

        message_reply = BOT.reply("user" + str(user_id), message_text)

        parse_telegram_out(message_reply, chat_id)

    return {
        "statusCode": 200,
        "headers": {"content-type": "application/json; charset=utf-8"},
        "body": {
            "input": tlg_in_msg,
            "output": tlg_out_msg,
            "message_in": message_text,
            "message_reply": message_reply,
            # 'debug': "Hello from OpenFaaS! <<" + event.path + ">> <<" + repr(context.__dict__) + '>> <<' + repr(event.__dict__) + '>>' + '<<tok ' + str(TELEGRAM_BOT_TOKEN) + 'tok >>' + '<<' + str(get_faas_secret(TELEGRAM_BOT_FILE_TOKEN)) + '>>'
            # 'debug': "Hello from OpenFaaS! <<" + event.path + ">> <<" + repr(context.__dict__) + '>> <<' + repr(event.__dict__) + '>>'
        },
    }
