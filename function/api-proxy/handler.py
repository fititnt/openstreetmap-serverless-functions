import json
# from pprint import pprint


def handle(event, context):
    return {
        "statusCode": 200,
        # "body": "Hello from OpenFaaS! <<" + json.dumps(context.__dict__) + '>> <<' + json.dumps(event.__dict__) + '>>'
        "body": "Hello from OpenFaaS! <<" + repr(context.__dict__) + '>> <<' + repr(event.__dict__) + '>>'

        # Maybe event['path'] return the path?
        # https://osm-faas.etica.ai/function/api-proxy/relation/12345.ttl?1234
        #  - event
        #    - (...)
        #    - 'method': 'GET'
        #    - 'query': ImmutableMultiDict([('1234', '')])
        #    - 'path': '/relation/12345.ttl'}
    }
