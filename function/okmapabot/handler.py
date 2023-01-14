# @see https://core.telegram.org/bots/webhooks
# @see https://www.freecodecamp.org/news/telegram-push-notifications-58477e71b2c2/
# Default main Wiki-as-base at https://wiki.openstreetmap.org/wiki/User:EmericusPetro/sandbox/Wiki-as-base

# from ast import Tuple

# import shutil
import datetime
import shutil
import urllib
import json
import os
from importlib_metadata import version
import requests

# import wiki_as_base
# from wiki_as_base import WikitextAsData

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
    # "FAAS_ALLOWED", "api-rdf|api-proxy|overpass-proxy|wiki-as-base|nodeinfo|cows"
    "FAAS_ALLOWED",
    "",
).split("|")

RIVE_FILES_0 = os.getenv("RIVE_FILES_0", "")
RIVE_FILES_1 = os.getenv("RIVE_FILES_1", "")
RIVE_FILES_2 = os.getenv("RIVE_FILES_2", "")
RIVE_WIKIASBASE_BRAIN_1 = os.getenv("RIVE_WIKIASBASE_BRAIN_1", "")
RIVE_WIKIASBASE_BRAIN_2 = os.getenv("RIVE_WIKIASBASE_BRAIN_2", "")

RIVE_WIKIASBASE_BRAIN_0 = os.getenv("RIVE_WIKIASBASE_BRAIN_0", "")
RIVE_WIKIASBASE_BRAIN_1 = os.getenv("RIVE_WIKIASBASE_BRAIN_1", "")
RIVE_WIKIASBASE_BRAIN_2 = os.getenv("RIVE_WIKIASBASE_BRAIN_2", "")

# @TODO implement CHATBOT_WIKIASBASE_BRAIN_1 and CHATBOT_WIKIASBASE_BRAIN_2
CHATBOT_WIKIASBASE_BRAIN_1 = os.getenv("CHATBOT_WIKIASBASE_BRAIN_1", "")
# CHATBOT_WIKIASBASE_BRAIN_1 = os.getenv(
#     "CHATBOT_WIKIASBASE_BRAIN_1",
#     "User:EmericusPetro/sandbox/Chatbot-por/OSMCPLPChatbot",
# )

CHATBOT_WIKIASBASE_BRAIN_2 = os.getenv("CHATBOT_WIKIASBASE_BRAIN_2", "")

RIVER_BRAIN_SOURCES = []
RIVER_BRAIN_UPDATED = -1

# ____________________________________________________________________________ #

# @TODO ideally the rivestript server should initialyze only once and not
#       in each request, see
#       https://github.com/aichaos/rivescript/wiki/Make-a-Single-Shared-Bot-Instance
#       This TODO is mostly to check later if we're somewhat okay


def bot_brain_init_external_files_fallback() -> str:
    """bot_brain_init_external_files fetch files and return local path"""
    brain_files = {
        "osm-tagging-pt.rive": "https://raw.githubusercontent.com/fititnt/openstreetmap-tags-to-rivescript/main/example/brain/osm-tagging-pt.rive",
        "osm-tagging-reverse_pt.rive": "https://raw.githubusercontent.com/fititnt/openstreetmap-tags-to-rivescript/main/example/brain/osm-tagging-reverse_pt.rive",
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


# def bot_brain_init_external_files_wikiasbase(wikiasbase_autodetect: str) -> str:
#     """bot_brain_init_external_files_wikiasbase fetch from wikibase"""

#     # wikimarkup_raw = wiki_as_base.wiki_as_base_request(RIVE_WIKIASBASE_BRAIN_0)
#     # wikiasbase_jsonld = wiki_as_base.wiki_as_base_all(wikimarkup_raw)
#     # # TODO implement additional files
#     # wabzip = wiki_as_base.WikiAsBase2Zip(wikiasbase_jsonld, verbose=True)
#     # wabzip.output("/tmp/brain.zip")

#     wtxt = WikitextAsData().set_pages_autodetect(wikiasbase_autodetect)
#     if not wtxt.prepare().is_success():
#         raise IOError("WikitextAsData err")

#     wtxt.output_zip("/tmp/brain.zip")

#     shutil.unpack_archive("/tmp/brain.zip", "/tmp/brain")
#     return "/tmp/brain/"


# Disabled wiki request fallback


# if RIVE_WIKIASBASE_BRAIN_0:
#     try:
#         _brain_base = bot_brain_init_external_files_wikiasbase(RIVE_WIKIASBASE_BRAIN_0)
#     except Exception as err:
#         print(err)

# if RIVE_WIKIASBASE_BRAIN_1:
#     try:
#         _brain_base = bot_brain_init_external_files_wikiasbase(RIVE_WIKIASBASE_BRAIN_1)
#     except Exception as err:
#         print(err)

# if RIVE_WIKIASBASE_BRAIN_2:
#     try:
#         _brain_base = bot_brain_init_external_files_wikiasbase(RIVE_WIKIASBASE_BRAIN_2)
#     except Exception as err:
#         print(err)

# if RIVE_FILES_0:
#     try:
#         _brain_base = bot_brain_init_external_files_wikiasbase(RIVE_WIKIASBASE_BRAIN_1)
#     except Exception as err:
#         print(err)


_brain_base = bot_brain_init_external_files_fallback()

# _brain_base = bot_brain_init_external_files_wikiasbase()


RIVER_BRAIN_LOCALFILES = os.listdir(_brain_base)
RIVER_BRAIN_UPDATED = datetime.datetime.now().isoformat()


# try:
#     _brain_base = bot_brain_init_external_files_wikiasbase()
#     RIVER_BRAIN_SOURCES.append(RIVE_WIKIASBASE_BRAIN_0)
#     RIVER_BRAIN_UPDATED = datetime.datetime.now().isoformat()
# except Exception:
#     _brain_base = bot_brain_init_external_files_fallback()
#     RIVER_BRAIN_SOURCES.append("!!!fallback!!!")
#     RIVER_BRAIN_UPDATED = datetime.datetime.now().isoformat()

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

    return [resp.status_code, resp.text, notification_text]


def about() -> dict:
    """about quick summary of what this faas is about"""
    about = {
        "@type": "faas/wiki-telegram-chatbot",
        "faas_name": "wiki-as-base",
        # "wiki_as_base.__version__": version("wiki_as_base"),
        "rivescript.__version__": version("rivescript"),
        "RIVER_BRAIN_SOURCES": RIVER_BRAIN_SOURCES,
        "RIVER_BRAIN_UPDATED": RIVER_BRAIN_UPDATED,
        "RIVER_BRAIN_LOCALFILES": RIVER_BRAIN_LOCALFILES,
        # "CACHE_TTL": CACHE_TTL,
        # "USER_AGENT": USER_AGENT,
        # "WIKI_API": WIKI_API,
    }
    return about


def handle(event, context):
    search_path = event.path.lstrip("/")

    if search_path in ["__about"]:
        return {
            "statusCode": 200,
            "headers": {"content-type": "application/json; charset=utf-8"},
            "body": {
                "data": [about()],
            },
        }

    # @TODO implement bot also reply to edited messages
    tlg_in_msg = False
    tlg_out_msg = False

    message_reply = "...silence..."
    message_text = ""
    err = True
    if event.method == "POST" and event.body and len(event.body) > 10:
        tlg_in_msg = json.loads(event.body)
        # message = {}
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
        # "statusCode": 400,
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
