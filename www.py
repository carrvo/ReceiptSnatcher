#!/usr/bin/python3
"""
"""

import cgi
import cgitb
import os
import sys
import json

import flask
from flask import Flask, request, Response, url_for, abort
from markupsafe import escape
#from flask_basicauth import BasicAuth

# https://modwsgi.readthedocs.io/en/master/user-guides/application-issues.html#application-working-directory
sys.path.insert(0, os.path.dirname(__file__))

import snatcher
import db

# kudos to https://flask.palletsprojects.com/en/2.0.x/deploying/cgi/
# kudos to https://stackoverflow.com/a/64583458
app = Flask('snatcher')
app.config['FLASK_AUTH_REALM'] = 'Receipt Snatcher'

MAX_FILE_SIZE = 4000000

DEFAULT_raw = '''<!DOCTYPE html>
<html>
<head>
    <title>Receipt Snatcher</title>
</head>
<body>
    <form enctype="multipart/form-data" action="{url}" method="post">
        <input type="hidden" name="MAX_FILE_SIZE" value="{MAX_FILE_SIZE}" />
        <p>File: <input type="file" name="filename" /></p>
        <p><input type="submit" value="Upload" /></p>
    </form>
</body>
</html>
'''

ERROR = '''<!DOCTYPE html>
<html>
<head>
    <title>Error</title>
</head>
<body>
    <p>{}</p>
    <p><a href="{url}">Another</a></p>
</body>
</html>
'''

OCR_body = '''<!DOCTYPE html>
<html>
<head>
    <title>OCR Results</title>
    <link rel="stylesheet" href="{url}.css"/>
    <script src="{url}.js"></script>
</head>
<body>
    <a id="app" hidden href="{url}"></a>
    <table>
        <tr><th>business</th><th>date</th><th>item</th><th>price</th></tr>
        {ocr_entries}
    </table>
    <button type="submit" onclick="submitEntries(this)">submit</button>
    <br>
    <p><a href="{url}">Another</a></p>
</body>
</html>
'''

OCR_entry = '''
<tr class="entry"><td>{business_name}</td><td>{transaction_date}</td><td><input type="text" value="{item}" /></td><td><input type="number" value="{price}" /></td></tr>
'''

class ExitWithData(Exception):
    def __init__(self, content_type, data):
        self.content_type = content_type
        self.data = data
    def respond(self):
        return Response(self.data, status=200, mimetype=self.content_type)

class ExitWithPage(ExitWithData):
    def __init__(self, page):
        super().__init__('text/html', page)

@app.route('/', methods=['GET', 'POST', 'PUT'])
#@auth.required
def homepage():
    URL_PATH = url_for('homepage')[0:-1] # strip trailing /
    DEFAULT = DEFAULT_raw.format(MAX_FILE_SIZE=MAX_FILE_SIZE, url=URL_PATH)
    form = request.form if request.content_type != 'application/json' else request.json
    try:
        if request.method == 'GET':
            raise ExitWithPage(DEFAULT)
        elif request.method == 'POST':
            if 'filename' in request.files:
                if not request.content_type.startswith("multipart/form-data"):
                    raise ExitWithPage(ERROR.format('Only support Content-Type: "multipart/form-data (not {})"'.format(request.content_type), url=URL_PATH))
                fileitem = request.files['filename']
                if fileitem == '' or not fileitem.filename:
                    raise ExitWithPage(ERROR.format('No file selected!', url=URL_PATH))
                content = fileitem.read(MAX_FILE_SIZE)
                if fileitem.read(1):
                    raise ExitWithPage(ERROR.format('File too large!', url=URL_PATH))
                if len(content) == 0:
                    raise ExitWithPage(ERROR.format('No file content!', url=URL_PATH))
                # this is the base name of the file that was uploaded:
                filename = os.path.basename(fileitem.filename)
                #name, ext = os.path.splitext(filename)
                try:
                    pages = snatcher.bytes_to_pages(filename, content)
                    rows = snatcher.parse(pages)
                    entries = '\n'.join(OCR_entry.format(**row) for row in rows)
                except Exception as error:
                    #raise ExitWithPage(ERROR.format('OCR failure', url=URL_PATH)) from error
                    raise ExitWithPage(ERROR.format('OCR failure:\n{}'.format(error), url=URL_PATH)) from error
                else:
                    raise ExitWithPage(OCR_body.format(ocr_entries=entries, url=URL_PATH))
            else:
                raise ExitWithPage(ERROR.format('No form submitted!', url=URL_PATH))
        elif request.method == 'PUT':
            #raise ExitWithData('application/json', json.dumps(tuple(request.headers.keys())))
            #raise ExitWithData('application/json', json.dumps({'username': request.authorization.username, 'password': request.authorization.password}))
            #raise ExitWithData('text/plain', 'Received Data! {}'.format(json.dumps(form)))
            #raise ExitWithData('application/json', json.dumps(form))
            try:
                with db.DB() as database:
                    row_ids = database.insert(form)
                    raise ExitWithData('application/json', json.dumps(row_ids))
            except db.ProgrammingError as sqlerror:
                if 'Access denied' in str(sqlerror):
                    abort(403)
                else:
                    raise ExitWithData(ERROR.format('SQL failure')) from sqlerror
        else:
            raise ExitWithPage(ERROR.format('Unsupported method: {}'.format(request.method), url=URL_PATH))
    except ExitWithData as exiting:
        return exiting.respond()

application = app

