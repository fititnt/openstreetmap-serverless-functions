# SPDX-License-Identifier: Unlicense OR 0BSD

# @TODO maybe refactor this code in something better (without changing public
#       interface)

# Default main Wiki-as-base at https://wiki.openstreetmap.org/wiki/User:EmericusPetro/sandbox/Wiki-as-base

# https://osm-faas.etica.ai/function/wiki-as-db/User:EmericusPetro/sandbox/Wiki-as-base

import os
import tempfile
from importlib_metadata import version
import requests_cache
from wiki_as_base import WikitextAsData

WIKI_AS_BASE_LIB_VERSION = version("wiki_as_base")

# @TODO implement logic from https://meta.wikimedia.org/wiki/User-Agent_policy
USER_AGENT = os.getenv(
    "USER_AGENT",
    f"wiki-as-base-faasbot/1.0 (https://github.com/fititnt/openstreetmap-serverless-functions; user@example.org) wiki_as_base-py/{WIKI_AS_BASE_LIB_VERSION}",
)
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
    # We enforce at least 2 characters of search path (before was blocking
    # queries such as "RDF")
    if len(search_path) < 2 or search_path in ["favicon.ico"]:
        return {
            "statusCode": 404,
            "headers": {"content-type": "application/json; charset=utf-8"},
            "body": {
                "error": "Not found",
                "examples": [
                    "Key:maxspeed",
                    "Tag:highway=residential",
                    "User:EmericusPetro/sandbox/Wiki-as-base",
                    "User:EmericusPetro/sandbox/Wiki-as-base.zip",
                    "__about",
                ],
            },
        }

    if search_path in ["__about"]:
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

    wtxt = WikitextAsData().set_pages_autodetect(search_path)

    if not wtxt.prepare().is_success():
        # @TODO maybe explicitly expose this on the library?
        status_code = 400
        data = wtxt.errors

    else:
        status_code = 200
        if content_type != "application/zip":
            data = wtxt.output_jsonld()
        else:
            with tempfile.TemporaryFile(mode="w+b") as file_pointer:
                wtxt.output_zip(file_pointer)
                file_pointer.seek(0)
                data = file_pointer.read()

    return {
        "statusCode": status_code,
        "headers": {"Content-type": content_type},
        "body": data,
    }
