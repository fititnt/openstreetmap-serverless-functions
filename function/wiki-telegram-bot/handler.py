import os
import requests
import requests_cache

OSM_API_DE_FACTO = os.getenv(
    'OSM_API_DE_FACTO', 'https://www.openstreetmap.org/api/0.6')
CACHE_DRIVER = os.getenv('CACHE_DRIVER', 'sqlite')
CACHE_TTL = os.getenv('CACHE_TTL', '3600')  # 1 hour

# Note: after setup the bot, configure the webkook url
# https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://osm-faas.etica.ai/function/wiki-telegram-bot

# @TODO implement the example from here https://core.telegram.org/bots/webhooks

# @see https://requests-cache.readthedocs.io/en/stable/
requests_cache.install_cache(
    'wikitelegram_cache',
    # /tmp OpenFaaS allow /tmp be writtable even in read-only mode
    # However, is not granted that changes will persist or shared
    db_path= '/tmp/wikitelegram_cache.sqlite',
    backend=CACHE_DRIVER,
    expire_after=CACHE_TTL,
    allowable_codes=[200, 400, 404, 500]
)

def handle(event, context):

    # content = requests.get(
    #     OSM_API_DE_FACTO + event.path)

    # TODO: forward some hint for user ip
    # TODO: abort know invalid requests like *.png, *.ico, *.html, ...

    return {
        # "statusCode": content.status_code,
        "statusCode": 200,
        # "headers": {
        #     'content-type': content.headers['Content-Type']
        # },
        # "body": content.text
        # "body": event.path
        "body": "Hello from OpenFaaS! <<" + event.path + ">> <<" + repr(context.__dict__) + '>> <<' + repr(event.__dict__) + '>>'
    }

# def handle(event, context):
#     return {
#         "statusCode": 200,
#         # "body": "Hello from OpenFaaS! <<" + json.dumps(context.__dict__) + '>> <<' + json.dumps(event.__dict__) + '>>'
#         # "body": "Hello from OpenFaaS! <<" + repr(context.__dict__) + '>> <<' + repr(event.__dict__) + '>>'
#         "body": repr(event.__dict__)
#         # Maybe event['path'] return the path?
#         # https://osm-faas.etica.ai/function/api-proxy/relation/12345.ttl?1234
#         #  - event
#         #    - (...)
#         #    - 'method': 'GET'
#         #    - 'query': ImmutableMultiDict([('1234', '')])
#         #    - 'path': '/relation/12345.ttl'}
#     }