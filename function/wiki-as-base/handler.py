# SPDX-License-Identifier: Unlicense OR 0BSD

# @TODO maybe refactor this code in something better (without changing public
#       interface)

# Default main Wiki-as-base at https://wiki.openstreetmap.org/wiki/User:EmericusPetro/sandbox/Wiki-as-base

# https://osm-faas.etica.ai/function/wiki-as-db/User:EmericusPetro/sandbox/Wiki-as-base

import os
import tempfile
from importlib_metadata import version
import mwparserfromhell
import requests
import requests_cache
import wiki_as_base

USER_AGENT = os.getenv("USER_AGENT", "wiki-as-base/1.0")
WIKI_API = os.getenv("WIKI_API", "https://wiki.openstreetmap.org/w/api.php")
CACHE_DRIVER = os.getenv("CACHE_DRIVER", "sqlite")
CACHE_TTL = os.getenv("CACHE_TTL", "3600")  # 1 hour

# @see https://requests-cache.readthedocs.io/en/stable/
requests_cache.install_cache(
    "osmapi_cache",
    # /tmp OpenFaaS allow /tmp be writtable even in read-only mode
    # However, is not granted that changes will persist or shared
    db_path="/tmp/osmwiki_cache.sqlite",
    backend=CACHE_DRIVER,
    expire_after=CACHE_TTL,
    allowable_codes=[200, 400, 404, 500],
)


def about() -> dict:
    """about quick summary of what this faas is about"""
    about = {
        "@type": "faas/wiki-as-base",
        "faas_name": "wiki-as-base",
        "wiki_as_base.__version__": version("wiki_as_base"),
        "CACHE_TTL": CACHE_TTL,
        "USER_AGENT": USER_AGENT,
        "WIKI_API": WIKI_API,
    }
    return about


def handle(event, context):
    search_path = event.path.lstrip("/")
    # if search_path in ['favicon.ico']:
    #     return False

    # Quick help for the lost souls who don't read documentation
    if len(search_path) < 4 or search_path in ["favicon.ico"]:
        return {
            "statusCode": 404,
            "headers": {"content-type": "application/json; charset=utf-8"},
            "body": {
                "error": "Not found",
                "examples": [
                    "Key:maxspeed",
                    "Tag:highway=residential",
                    "User:EmericusPetro/sandbox/Wiki-as-base",
                    "__about",
                ],
            },
        }

    if search_path in ["_about", "__about"]:
        return {
            "statusCode": 200,
            "headers": {"content-type": "application/json; charset=utf-8"},
            "body": {
                "data": [about()],
            },
        }

    content_type = "application/json; charset=utf-8"
    if search_path.endswith(".json"):
        search_path = search_path.rstrip(".json")
    if search_path.endswith(".jsonld"):
        search_path = search_path.rstrip(".jsonld")
    if search_path.endswith(".zip"):
        content_type = "application/zip"
        search_path = search_path.rstrip(".zip")

    result = wiki_as_base.wiki_as_base_request(search_path)
    data = {"error": "no data from request"}
    status_code = 400
    if result:
        data = wiki_as_base.wiki_as_base_all(result)
        status_code = 200
        if content_type == "application/zip":
            with tempfile.TemporaryFile(mode='w+b') as fp:
                wabzip = wiki_as_base.WikiAsBase2Zip(data, verbose=True)
                # wabzip.output(test_dir + "/temp/chatbotpor.zip")
                wabzip.output(fp)
                fp.seek(0)
                # data_bytes = fp.read()
                # data = data_bytes.decode()
                data = fp.read()
                content_type = "application/zip"
                # content_type = "application/octet-stream"
                # raise ValueError([type(data), len(data)])

                # the OpenFaaS python-http will enforce str() on this output
                # so we do it upfront
                # data = data_bytes.decode('hex')
                # data = data_bytes.decode('iso-8859-1')
                # data = data_bytes.decode('ascii')
                # pass
        # if data:
        #     print(json.dumps(data, ensure_ascii=False, indent=2))

    # TODO: forward some hint for user ip
    # TODO: abort know invalid requests like *.png, *.ico, *.html, ...

    return {
        "statusCode": status_code,
        # "headers": {"content-type": "application/json; charset=utf-8"},
        "headers": {"Content-type": content_type},
        # "body": content.text
        # "body": content.text + "\n\n" + "<!--" + repr(content.__dict__)  + '-->'
        # "body": parsed
        # "body": parsed_raw,
        "body": data,
    }


# # @see https://github.com/earwig/mwparserfromhell/
# def parse_wiki_request(title):
#     params = {
#         "action": "query",
#         "prop": "revisions",
#         "rvprop": "content",
#         "rvslots": "main",
#         "rvlimit": 1,
#         "titles": title,
#         "format": "json",
#         "formatversion": "2",
#     }
#     # headers = {"User-Agent": "My-Bot-Name/1.0"}
#     headers = {"User-Agent": USER_AGENT}
#     req = requests.get(WIKI_API, headers=headers, params=params)
#     # print(req)
#     # return req, req
#     res = req.json()
#     revision = res["query"]["pages"][0]["revisions"][0]
#     text = revision["slots"]["main"]["content"]
#     return req, mwparserfromhell.parse(text)
