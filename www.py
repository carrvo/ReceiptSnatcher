#!/usr/bin/python3
"""
"""

import cgi
import cgitb
import os
import sys
import json

#import snatcher

# https://serverfault.com/a/515698
cgitb.enable(logdir='/var/log/apache2/python-traceback')

import snatcher

form = cgi.FieldStorage() if os.environ.get('CONTENT_TYPE') != 'application/json' else json.loads(sys.stdin.read(int(os.environ["CONTENT_LENGTH"]))) # FieldStorage says "reading multipart/form-data" ~ /usr/lib/python3.10/cgi.py ; kudos to https://stackoverflow.com/questions/10718572/post-json-to-python-cgi
#if os.environ.get('CONTENT_TYPE') == 'application/json': # https://bugs.python.org/issue27777
#    os.environ['REQUEST_METHOD'] = 'PUT'

MAX_FILE_SIZE = 4000000

# https://www.oreilly.com/library/view/python-cookbook/0596001673/ch11s05.html
URL_PATH = os.environ['SCRIPT_NAME']

DEFAULT = '''<!DOCTYPE html>
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
'''.format(MAX_FILE_SIZE=MAX_FILE_SIZE, url=URL_PATH)

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
        <tr><th>item</th><th>price</th></tr>
        {ocr_entries}
    </table>
    <button type="submit" onclick="submitEntries(this)">submit</button>
    <br>
    <p><a href="{url}">Another</a></p>
</body>
</html>
'''

OCR_entry = '''
<tr class="entry"><td><input type="text" value="{item}" /></td><td><input type="number" value="{price}" /></td></tr>
'''

class ExitWithData(Exception):
    def __init__(self, content_type, data):
        self.content_type = content_type
        self.data = data
    def respond(self):
        print('Content-Type: {}\r\n\r\n'.format(self.content_type), end='')
        print(self.data)

class ExitWithPage(ExitWithData):
    def __init__(self, page):
        super().__init__('text/html', page)

try:
    if os.environ['REQUEST_METHOD'] == 'GET':
        raise ExitWithPage(DEFAULT)
    elif os.environ['REQUEST_METHOD'] == 'POST':
        if 'filename' in form:
            if not os.environ['CONTENT_TYPE'].startswith("multipart/form-data"):
                raise ExitWithPage(ERROR.format('Only support Content-Type: "multipart/form-data (not {})"'.format(os.environ['CONTENT_TYPE']), url=URL_PATH))
            fileitem = form['filename']
            if fileitem == '' or not fileitem.file:
                raise ExitWithPage(ERROR.format('No file selected!', url=URL_PATH))
            content = fileitem.file.read(MAX_FILE_SIZE)
            if fileitem.file.read(1):
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
                raise ExitWithPage(ERROR.format('OCR failure', url=URL_PATH)) from error
            else:
                raise ExitWithPage(OCR_body.format(ocr_entries=entries, url=URL_PATH))
        else:
            raise ExitWithPage(ERROR.format('No form submitted!', url=URL_PATH))
    elif os.environ['REQUEST_METHOD'] == 'PUT':
        raise ExitWithData('text/plain', 'Received Data! {}'.format(json.dumps(form)))
    else:
        raise ExitWithPage(ERROR.format('Unsupported method: {}'.format(os.environ['REQUEST_METHOD']), url=URL_PATH))
except ExitWithData as exiting:
    exiting.respond()

