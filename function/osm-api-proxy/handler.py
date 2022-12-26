def handle(event, context):
    print(event)
    print(context)
    return {
        "statusCode": 200,
        "body": "Hello from OpenFaaS!"
    }
