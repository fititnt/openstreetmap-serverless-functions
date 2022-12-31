import os
import urllib
import requests
import requests_cache

# @see http://overpass-api.de/command_line.html
# @see https://wiki.openstreetmap.org/wiki/User:Tagtheworld/overpass-api_commandline
OVERPASS_API_DE_FACTO = os.getenv(
    'OVERPASS_API_DE_FACTO', 'https://overpass-api.de/api/interpreter')
CACHE_DRIVER = os.getenv('CACHE_DRIVER', 'sqlite')
CACHE_TTL = os.getenv('CACHE_TTL', '3600')  # 1 hour


# Not fully tested yet
HELP_MESSAGE = {
  "$schema": "https://osm-faas.etica.ai/schema.json",
  "@context": "https://osm-faas.etica.ai/context.jsonld",
  "@id": "https://osm-faas.etica.ai",
  "data": [
    {
        "@type": "_:example",
        "POST": "data=node[name='Gielgen'];out;"
    },
    # {
    #     "@type": "_:example",
    #     "GET": "?data=node%5Bname%3D%27Gielgen%27%5D%3Bout%3B"
    # },
    # {
    #     "@type": "_:example",
    #     "GET": "?data=node[name='Gielgen'];out;"
    # },
  ]
}

# echo "data=node[name='Gielgen'];out;" > query.osm
# wget -O target.osm --post-file=query.osm "https://overpass-api.de/api/interpreter"
# curl -o target_local.osm -d @query.osm "http://localhost:8080/"

# @TODO implement via get method
# curl -o target_local_get.osm --globoff 'http://localhost:8080/?data=node[name="Gielgen"];out;'
# curl -o target_local_get.osm --globoff 'http://localhost:8080/?node[name="Gielgen"];out;'
# curl -o target_local_get.osm --globoff 'http://localhost:8080/data=node[name="Gielgen"];out;'

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
    # if not event.path.startswith(('/node/', '/way/', '/relation/')):
    if (len(event.path) < 6 and event.method != 'POST') or \
        (len(event.body) < 10 and event.method == 'POST'):

        # pass

        return {
            "statusCode": 400,  # 400 Bad Request
            "headers": {
                'content-type': 'application/json'
            },
            # "body": {
            #     'error': 'Not found.',
            #     'examples': [
            #         "data=node[name=\"Gielgen\"];out;",
            #         "@see http://overpass-api.de/command_line.html"
            #     ]
            # }
            "body": HELP_MESSAGE
        }

    urlencoded = urllib.parse.quote_plus(event.path)

    if event.method == 'POST':
        content = requests.post(OVERPASS_API_DE_FACTO, data=event.body)
    else:
        if urlencoded.startswith('data'):
            content = requests.get(
                OVERPASS_API_DE_FACTO + '?' + urlencoded)
        elif urlencoded.startswith('?data='):
            content = requests.get(
                OVERPASS_API_DE_FACTO + '' + urlencoded)
        else:
            content = requests.get(
                OVERPASS_API_DE_FACTO + '' + urlencoded)

    return {
        "statusCode": content.status_code,
        "headers": {
            'content-type': content.headers['Content-Type']
        },
        "body": content.text
        # "body": content.text + "\n\n" + "<!--" + repr(content.__dict__)  + '-->'
        # "body": content.text
        # "body": "<<" + repr(context.__dict__) + '>> <<' + repr(event.__dict__) + '>>'
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