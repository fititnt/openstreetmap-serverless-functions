#!/usr/bin/env python3
# ==============================================================================
#
#          FILE:  osmrdf2023.py
#
#         USAGE:  # this is a library. Import into your code:
#                     from osmrdf2022 import *
#
#   DESCRIPTION:  ---
#
#       OPTIONS:  ---
#
#  REQUIREMENTS:  - python3
#                   - lxml
#          BUGS:  - No big XML dumps output format support (not yet)
#                 - No support for PBF Format (...not yet)
#         NOTES:  ---
#       AUTHORS:  Emerson Rocha <rocha[at]ieee.org>
# COLLABORATORS:  ---
#       LICENSE:  Public Domain dedication or Zero-Clause BSD
#                 SPDX-License-Identifier: Unlicense OR 0BSD
#       VERSION:  v0.3.0
#       CREATED:  2022-11-25 19:22:00Z v0.1.0 started
#      REVISION:  2022-11-26 20:47:00Z v0.2.0 node, way, relation basic turtle,
#                                      only attached tags (no <nd> <member> yet)
#                 2022-12-21 01:46:00Z v0.3.0 osmrdf2022.py -> osmrdf2023.py
# ==============================================================================

import os
import requests
import requests_cache

from osmrdf2023.osmrdf2023 import (
    # osmrdf_xmldump2_ttl,
    osmrdf_node_xml2ttl,
    osmrdf_relation_xml2ttl,
    osmrdf_way_xml2ttl
)

## TODO: extra code over https://github.com/EticaAI/openstreetmap-semantic-conventions-2023/blob/main/poc/osmapi2rdfproxy.py

OSM_API_DE_FACTO = os.getenv(
    'OSM_API_DE_FACTO', 'https://www.openstreetmap.org/api/0.6')
CACHE_DRIVER = os.getenv('CACHE_DRIVER', 'sqlite')
CACHE_TTL = os.getenv('CACHE_TTL', '3600')  # 1 hour

# @see https://requests-cache.readthedocs.io/en/stable/
requests_cache.install_cache(
    'osmapi_cache',
    # /tmp OpenFaaS allow /tmp be writtable even in read-only mode
    # However, is not granted that changes will persist or shared
    db_path= '/tmp/osmapi_cache.sqlite',
    backend=CACHE_DRIVER,
    expire_after=CACHE_TTL,
    allowable_codes=[200, 400, 404, 500]
)

def handle(event, context):

    # Quick help for the lost souls who don't read documentation
    if not event.path.startswith(('/node/', '/way/', '/relation/')):
        return {
            "statusCode": 404,
            # "statusCode": 200,
            "headers": {
                'content-type': 'application/json; charset=utf-8'
            },
            "body": {
                'error': 'Not found.',
                # 'message': 'Not found.',
                'examples': ["/node/1", "/way/100", "/relation/10000"]
            }
        }

    content = requests.get(
        OSM_API_DE_FACTO + event.path)

    body_text = content.text
    content_type = content.headers['Content-Type']

    if content.status_code == 200:
        if event.path.startswith('/node'):
            content_type = 'text/turtle; charset=utf-8'
            body_text = osmrdf_node_xml2ttl(body_text)
            # body_text = osmrdf_xmldump2_ttl(body_text)

        elif event.path.startswith('/relation'):
            content_type = 'text/turtle; charset=utf-8'
            body_text = osmrdf_relation_xml2ttl(body_text)
            # body_text = osmrdf_xmldump2_ttl(body_text)

        elif event.path.startswith('/way'):
            content_type = 'text/turtle; charset=utf-8'
            body_text = osmrdf_way_xml2ttl(body_text)
            # body_text = osmrdf_xmldump2_ttl(body_text)

    return {
        "statusCode": content.status_code,
        "headers": {
            'content-type': content_type
        },
        "body": body_text
    }
