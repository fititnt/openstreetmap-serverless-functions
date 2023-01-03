#!/usr/bin/env python
import sys
from flask import Flask, request, jsonify, make_response
from waitress import serve
import os

from function import handler

app = Flask(__name__)

class Event:
    def __init__(self):
        self.body = request.get_data()
        self.headers = request.headers
        self.method = request.method
        self.query = request.args
        self.path = request.path

class Context:
    def __init__(self):
        self.hostname = os.getenv('HOSTNAME', 'localhost')

def format_status_code(resp):
    if 'statusCode' in resp:
        return resp['statusCode']
    
    return 200

def format_body(resp, content_type):
    if content_type == 'application/octet-stream':
        return resp['body']
    
    # @TODO implement a more generic check for binary output formats
    if content_type == 'application/zip':
        return resp['body']

    if 'body' not in resp:
        return ""
    elif type(resp['body']) == dict:
        return jsonify(resp['body'])
    else:
        return str(resp['body'])

def get_content_type(res):
    content_type = ""
    if 'headers' in res:
        content_type = res['headers'].get('Content-type', '')
    return content_type

def format_headers(resp):
    if 'headers' not in resp:
        return []
    elif type(resp['headers']) == dict:
        headers = []
        for key in resp['headers'].keys():
            header_tuple = (key, resp['headers'][key])
            headers.append(header_tuple)
        return headers
    
    return resp['headers']

def format_response(resp):
    if resp == None:
        return ('', 200)

    statusCode = format_status_code(resp)
    content_type = get_content_type(resp)
    body = format_body(resp, content_type)
    headers = format_headers(resp)

    return (body, statusCode, headers)

@app.route('/', defaults={'path': ''}, methods=['GET', 'PUT', 'POST', 'PATCH', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'PUT', 'POST', 'PATCH', 'DELETE'])
def call_handler(path):
    event = Event()
    context = Context()
    response_data = handler.handle(event, context)

    content_type = get_content_type(response_data)
    if content_type in ['application/zip', 'application/octet-stream'] and \
        isinstance(response_data['body'], bytes):

        flask_resp = make_response(response_data['body'])
        flask_resp.headers['Content-type'] = content_type

        return flask_resp

    # raise ValueError([content_type, type(response_data['body'])])
    resp = format_response(response_data)
    return resp

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
