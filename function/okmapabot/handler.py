# @see https://core.telegram.org/bots/webhooks
# @see https://www.freecodecamp.org/news/telegram-push-notifications-58477e71b2c2/
# Default main Wiki-as-base at https://wiki.openstreetmap.org/wiki/User:EmericusPetro/sandbox/Wiki-as-base

# from ast import Tuple

# import shutil
from dataclasses import dataclass
import datetime
import mimetypes
import re
from typing import Union

# import shutil
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


TELEGRAM_BOT_TOKEN_FILE = os.getenv("TELEGRAM_BOT_TOKEN_FILE", "")

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN", get_faas_secret(TELEGRAM_BOT_TOKEN_FILE)
)

# X-Telegram-Bot-Api-Secret-Token
TELEGRAM_BOT_APISECRET_FILE = os.getenv("TELEGRAM_BOT_APISECRET_FILE", "")
TELEGRAM_BOT_APISECRET = os.getenv(
    "TELEGRAM_BOT_APISECRET", get_faas_secret(TELEGRAM_BOT_APISECRET_FILE)
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


_TEMP_EXEMPLOS = [
    "/dictionario highway=trunk",
    "/dictionario estrada",
    "/overpassql node[name='Gielgen'];out;",
    "/nominatim Rio Branco, Brasil",
    "/id",
    "/sobre",
]

# ____________________________________________________________________________ #


def guess_extension_from_content_type(content_type: str):
    content_type = content_type.lower()

    if content_type.find(";") > -1:
        # application/json; charset=UTF-8
        content_type = content_type.split("/")[0].strip()

    # Some from OSM are not on python mimetypes... yet
    _private = {"application/osm3s+xml": "osm"}
    if content_type in _private:
        return _private[content_type]

    # TODO remove this redundancy
    if content_type.startswith("application/json"):
        return "json"

    ext = mimetypes.guess_extension(content_type, strict=0)
    if not ext:
        ext = "raw"

    return ext


def guess_filename_from_overpassql_query(overpassql: str):
    result = "overpassql-result"
    if overpassql:
        parts = list(re.split(r"\W", overpassql))
        parts.sort(key=len, reverse=True)
        return parts[0]

    return result


@dataclass
class FileResource:
    content: Union[bytes, str]
    content_type: str
    # filename: str = None
    filename: str = "untitled"

    def __post_init__(self):
        if not self.filename:
            self.filename = "untitled"

        # if not self.content_type:
        #     self.content_type = "application/octet-stream"

        if self.filename.find(".") == -1:
            ext = guess_extension_from_content_type(self.content_type)

            self.filename = self.filename + "." + ext

    def set_name(self, name_without_extension: str, normalize: bool = True):
        name_norm = re.sub(r"\W+", "_", name_without_extension)
        if len(name_norm) > 30:
            name_norm = name_norm[0:30]

        ext = guess_extension_from_content_type(self.content_type)
        self.filename = name_norm + "." + ext
        return self


def bot_brain_init_external_files_fallback() -> str:
    """bot_brain_init_external_files fetch files and return local path"""
    brain_files = {
        "begin.rive": "https://raw.githubusercontent.com/fititnt/openstreetmap-serverless-functions/main/function/okmapabot/brain/begin.rive",
        "osm-tagging-pt.rive": "https://raw.githubusercontent.com/fititnt/openstreetmap-tags-to-rivescript/main/example/brain/osm-tagging-pt.rive",
        "osm-tagging-reverse_pt.rive": "https://raw.githubusercontent.com/fititnt/openstreetmap-tags-to-rivescript/main/example/brain/osm-tagging-reverse_pt.rive",
        "generico.rive": "https://raw.githubusercontent.com/fititnt/openstreetmap-tags-to-rivescript/main/example/brain/generico.rive",
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


def faas_nominatim(nominatim_query: str) -> requests.Request:
    # @see https://nominatim.org/release-docs/latest/api/Search/
    # faas_func = "overpass-proxy"

    # @TODO additional implementation to q
    NOMINATIM_API = "https://nominatim.openstreetmap.org/search?format=jsonv2&q="

    # req = requests.get(NOMINATIM_API + urllib.parse.quote(" ".join(nominatim_query)))
    resp = requests.get(NOMINATIM_API + urllib.parse.quote(nominatim_query))
    return resp


def faas_overpassql(overpassql_query: str) -> requests.Request:
    faas_func = "overpass-proxy"
    req = requests.post(FAAS_BACKEND + faas_func, data=overpassql_query)
    return req


def faas_response_as_markdown(content: str, mediatype: str = None):
    # TODO deal with mediatype
    return "```\n" + content + "\n```"


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


def about() -> dict:
    """about quick summary of what this faas is about"""
    about = {
        "@type": "faas/okmapabot",
        "faas_name": "okmapabot",
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
    file_upload_data = ""
    file_upload_name = "untitled.txt"
    message_text = ""
    err = True
    pass_to_riverbrain = True
    is_file_upload = None
    is_telegram_message = True
    resp_status_code = ""
    resp_text = ""

    resp_fileupload = None
    resp_file_text = None
    file_upload_data = None

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

        if message_text.startswith("/exemplos"):
            message_reply = "```\n" + "\n".join(_TEMP_EXEMPLOS) + "\n```"
            pass_to_riverbrain = False

        if message_text.startswith("/dicionario"):
            # Ja estamos este topico
            message_text = message_text.lstrip("/dicionario")

        if message_text.startswith("/id"):
            message_text = message_text.lstrip("/id")
            message_reply = "/id ainda não implementado. Volte em breve."
            pass_to_riverbrain = False

        if message_text.startswith("/nominatim"):
            nominatim_query = message_text.lstrip("/nominatim").strip()
            # message_reply = "/nominatim ainda não implementado. Volte em breve."
            try:
                _resp = faas_nominatim(nominatim_query)
                message_reply = faas_response_as_markdown(_resp.text)

                filename_hint = nominatim_query

                file_upload_data = FileResource(
                    content=_resp.text,
                    content_type=_resp.headers["content-type"],
                )

                file_upload_data.set_name(filename_hint)
                is_file_upload = True
                is_telegram_message = False

            except Exception as err:
                message_reply = (
                    "/nominatim retornout erro \n" + faas_response_as_markdown(str(err))
                )

            pass_to_riverbrain = False

        if message_text.startswith("/overpassql"):
            message_reply = "/overpassql ainda não implementado. Volte em breve."
            message_text.lstrip("/overpassql data=")
            message_text.lstrip("/overpassql ")
            try:
                overpassql_query = message_text.lstrip("/overpassql").strip()
                req = faas_overpassql(overpassql_query)
                if req.status_code == 200:
                    # @TODO improve this part
                    # filename_hint = "overpass-result"
                    filename_hint = guess_filename_from_overpassql_query(
                        overpassql_query
                    )

                    file_upload_data = FileResource(
                        content=req.text,
                        content_type=req.headers["content-type"],
                    )
                    file_upload_data.set_name(filename_hint)

                    is_file_upload = True
                    is_telegram_message = False
                else:
                    message_reply = (
                        "/overpassql algum erro nao grave aconteceu erro \n"
                        + faas_response_as_markdown(str(req.text))
                    )
            except Exception as err:
                message_reply = (
                    "/overpassql retornout erro \n"
                    + faas_response_as_markdown(str(err))
                )

            pass_to_riverbrain = False

        if message_text.startswith("/sobre"):
            message_reply = json.dumps(about())
            pass_to_riverbrain = False

        if message_text.startswith("/debug"):
            message_reply = json.dumps(about())
            pass_to_riverbrain = False

        if pass_to_riverbrain:
            message_text = message_text.strip()
            message_reply = BOT.reply("user" + str(user_id), message_text)

        if is_file_upload:
            _resp = telegram_bot_send_file(chat_id, file_upload_data)
            resp_fileupload, resp_file_text = _resp.status_code, _resp.text

        if is_telegram_message:
            _resp = telegram_bot_send_message(chat_id, message_reply)
            resp_status_code, resp_text = _resp.status_code, _resp.text

    return {
        # "statusCode": 400,
        "statusCode": 200,
        "headers": {"content-type": "application/json; charset=utf-8"},
        "body": {
            # "input": tlg_in_msg,
            # "output": tlg_out_msg,
            # "message_in": message_text,
            # "message_reply": message_reply,
            "telegram_response_file": [resp_fileupload, resp_file_text],
            "file_upload_data": file_upload_data,
            # "telegram_response_message": [resp_status_code, resp_text]
        },
    }


def telegram_bot_send_file(chat_id: int, file: FileResource) -> requests.Request:
    """telegram_bot_send_file Send file via telegram bot

    Args:
        message_reply (str): text message
        chat_id (int): The chat ID
    """

    # raise Exception(notification_text)
    # notification_text = urllib.parse.quote_plus(message_reply)

    # if not file_contents:
    #     file_contents = "empty file"

    notification_text = ""
    extras = []
    extra_params = ""
    if TELEGRAM_MESSAGE_DISABLE_NOTIFICATION:
        extras.append("disable_notification=true")
    if TELEGRAM_MESSAGE_WEB_PREVIEW:
        extras.append("no_webpage=true")
    if len(extras):
        extra_params = "&" + "&".join(extras)

    # headers = {"content-type": "application/x-www-form-urlencoded"}

    # files = {"document": ("file.txt", file_contents, "text/plain")}
    files = {"document": (file.filename, file.content, file.content_type)}

    # print('telegram_bot_send_file...', file_contents)
    resp = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument?chat_id={chat_id}{extra_params}",
        # data=file_contents,
        files=files,
    )

    # return [resp.status_code, resp.text, notification_text]
    # return [resp.status_code, resp.text]
    return resp


def telegram_bot_send_message(chat_id: int, message: str) -> requests.Request:
    """telegram_bot_send_message Send text message via telegram bot

    _extended_summary_

    Args:
        message_reply (str): text message
        chat_id (int): The chat ID
        is_file_upload (bool, optional): _description_. Defaults to False.
    """

    # raise Exception(notification_text)
    # notification_text = urllib.parse.quote_plus(message_reply)

    notification_text = ""
    extras = []
    extra_params = ""
    if TELEGRAM_MESSAGE_DISABLE_NOTIFICATION:
        extras.append("disable_notification=true")
    if TELEGRAM_MESSAGE_WEB_PREVIEW:
        extras.append("no_webpage=true")
    if len(extras):
        extra_params = "&" + "&".join(extras)

    # https://limits.tginfo.me/pt-BR 4096 characters
    if len(message) > 4096:
        message = message[0:4000] + "\n\n\n (...cropped message)"
    resp = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={chat_id}{extra_params}",
        data={"text": message},
    )

    # return [resp.status_code, resp.text, notification_text]
    # return [resp.status_code, resp.text]
    return resp
