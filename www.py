#!/usr/bin/python3
"""
"""

import cgi
import cgitb
import os
import sys
import traceback
import json

import flask
from flask import Flask, request, Response, url_for, abort
from markupsafe import escape
#from flask_basicauth import BasicAuth

# https://modwsgi.readthedocs.io/en/master/user-guides/application-issues.html#application-working-directory
sys.path.insert(0, os.path.dirname(__file__))

import snatcher
import db
from counter import group_count

# kudos to https://flask.palletsprojects.com/en/2.0.x/deploying/cgi/
# kudos to https://stackoverflow.com/a/64583458
app = Flask('snatcher')
app.config['FLASK_AUTH_REALM'] = 'Receipt Snatcher'

MAX_FILE_SIZE = 4000000

DEFAULT_raw = '''<!DOCTYPE html>
<html>
<head>
    <title>Receipt Snatcher</title>
    <link rel="manifest" href="{url}/manifest.json" />
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
    <link rel="manifest" href="{url}/manifest.json" />
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
    <link rel="manifest" href="{url}/manifest.json" />
    <link rel="stylesheet" href="{url}.css"/>
    <script src="{url}.js"></script>
    <script>
        const blank_row = `{blank_row}`;
    </script>
</head>
<body>
    <a id="app" hidden href="{url}"></a>
    <table>
        <tr>
            <th></th>
            <th>business</th>
            <th>date</th>
            <th>item</th>
            <th>price</th>
        </tr>
{ocr_entries}
    </table>
    <button type="submit" onclick="submitEntries(this)">submit</button>
    <span />
    <button type="button" onclick="addEntry()">Add</button>
    <br>
    <p><a href="{url}">Another</a></p>
</body>
</html>
'''

OCR_entry = '''
        <tr class="entry" >
            <td><button class="delete" onclick="deleteEntry(this)">Delete</button></td>
            <td>{business_name}</td>
            <td>{transaction_date}</td>
            <td><input type="text" value="{item}" /></td>
            <td><input type="number" value="{price}" /></td>
        </tr>
'''

OCR_blank = '''
            <td><button class="delete" onclick="deleteEntry(this)">Delete</button></td>
            <td>{business_name}</td>
            <td>{transaction_date}</td>
            <td><input type="text" value="" /></td>
            <td><input type="number" value="0" /></td>
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

class ExitWithJson(ExitWithData):
    def __init__(self, obj):
        super().__init__('application/json', json.dumps(obj))

def log_exception(ex):
    app.logger.error('\n'.join(traceback.format_exception(ex)))

class ExitWithError(ExitWithPage):
    def __init__(self, client_message, log_message=None, exception=None, **log_format):
        try:
            super().__init__(ERROR.format(client_message, url=URL_PATH))
            if not exception:
                exception = self
            log_exception(ex)
            if not log_message:
                log_message = client_message
            app.logger.exception(log_message, **log_format)
        except Exception as ex:
            log_exception(ex)

@app.route('/', methods=['GET', 'POST', 'PUT'])
#@auth.required
def homepage():
    global URL_PATH
    URL_PATH = url_for('homepage')[0:-1] # strip trailing /
    DEFAULT = DEFAULT_raw.format(MAX_FILE_SIZE=MAX_FILE_SIZE, url=URL_PATH)
    form = request.form if request.content_type != 'application/json' else request.json
    try:
        if request.method == 'GET':
            raise ExitWithPage(DEFAULT)
        elif request.method == 'POST':
            if 'filename' in request.files:
                if not request.content_type.startswith("multipart/form-data"):
                    raise ExitWithError('Only support Content-Type: "multipart/form-data (not {})"'.format(request.content_type))
                fileitem = request.files['filename']
                if fileitem == '' or not fileitem.filename:
                    raise ExitWithError('No file selected!')
                content = fileitem.read(MAX_FILE_SIZE)
                if fileitem.read(1):
                    raise ExitWithError('File too large!')
                if len(content) == 0:
                    raise ExitWithError('No file content!')
                # this is the base name of the file that was uploaded:
                filename = os.path.basename(fileitem.filename)
                #name, ext = os.path.splitext(filename)
                try:
                    pages = snatcher.bytes_to_pages(filename, content)
                    rows = snatcher.parse(pages)
                    blank_row = OCR_blank.format(**rows[0])
                    entries = '\n'.join(OCR_entry.format(**row) for row in rows)
                except Exception as error:
                    raise ExitWithError('OCR failure:\n{}'.format(error)) from error
                else:
                    raise ExitWithPage(OCR_body.format(ocr_entries=entries, blank_row=blank_row, url=URL_PATH))
            else:
                raise ExitWithError('No form submitted!')
        elif request.method == 'PUT':
            #raise ExitWithJson(tuple(request.headers.keys()))
            #raise ExitWithJson({'username': request.authorization.username, 'password': request.authorization.password})
            #raise ExitWithData('text/plain', 'Received Data! {}'.format(json.dumps(form)))
            row_quantity = group_count(form, fields=('business_name', 'transaction_date', 'correctedItem', 'correctedPrice'), count_field='quantity')
            try:
                with db.DB() as database:
                    _ = database.insert_ml(form)
                    row_ids = database.insert(row_quantity)
                    raise ExitWithJson(row_ids)
            except db.ProgrammingError as sqlerror:
                if 'Access denied' in str(sqlerror):
                    abort(403)
                else:
                    raise ExitWithData('text/plain', ERROR.format('SQL failure', url=URL_PATH)) from sqlerror
            except db.DatabaseError as sqlerror:
                #raise ExitWithJson({'error':str(sqlerror), 'data':row_quantity, 'form':form})
                raise ExitWithError('SQL failure', log_message=json.dumps({'error':str(sqlerror), 'data':row_quantity, 'form':form})) from sqlerror
        else:
            raise ExitWithError('Unsupported method: {}'.format(request.method))
    except ExitWithData as exiting:
        return exiting.respond()
    except Exception as ex:
        log_exception(ex)
        return Response('Server Failure', status=500)

application = app

