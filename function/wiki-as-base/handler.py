# SPDX-License-Identifier: Unlicense OR 0BSD

# Default main Wiki-as-base at https://wiki.openstreetmap.org/wiki/User:EmericusPetro/sandbox/Wiki-as-base

# https://osm-faas.etica.ai/function/wiki-as-db/User:EmericusPetro/sandbox/Wiki-as-base

import os
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
                "examples": ["/Key:maxspeed", "/Tag:highway=residential"],
            },
        }

    # content = requests.get(
    #     WIKI_API + event.path)
    req, parsed = parse_wiki_request(search_path)

    parsed_raw = wiki_as_base.wiki_as_base_raw(parsed)

    result = wiki_as_base.wiki_as_base_request(search_path)
    data = {"error": "no data from request"}
    if result:
        data = wiki_as_base.wiki_as_base_all(result)
        # if data:
        #     print(json.dumps(data, ensure_ascii=False, indent=2))

    # TODO: forward some hint for user ip
    # TODO: abort know invalid requests like *.png, *.ico, *.html, ...

    return {
        "statusCode": req.status_code,
        "headers": {"content-type": "application/json; charset=utf-8"},
        # "body": content.text
        # "body": content.text + "\n\n" + "<!--" + repr(content.__dict__)  + '-->'
        # "body": parsed
        # "body": parsed_raw,
        "body": data,
    }


# @see https://github.com/earwig/mwparserfromhell/
def parse_wiki_request(title):
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "rvlimit": 1,
        "titles": title,
        "format": "json",
        "formatversion": "2",
    }
    # headers = {"User-Agent": "My-Bot-Name/1.0"}
    headers = {"User-Agent": USER_AGENT}
    req = requests.get(WIKI_API, headers=headers, params=params)
    # print(req)
    # return req, req
    res = req.json()
    revision = res["query"]["pages"][0]["revisions"][0]
    text = revision["slots"]["main"]["content"]
    return req, mwparserfromhell.parse(text)
