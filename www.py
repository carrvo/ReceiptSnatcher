#!/usr/bin/python3
"""
"""

import cgi
import cgitb
import os
import sys

#import snatcher

# https://serverfault.com/a/515698
cgitb.enable(logdir='/var/log/apache2/python-traceback')

import snatcher

form = cgi.FieldStorage()

MAX_FILE_SIZE = 4000000

# https://www.oreilly.com/library/view/python-cookbook/0596001673/ch11s05.html
URL_PATH = os.environ['SCRIPT_NAME']

DEFAULT = '''
<html>
<head>
    <title>Receipt Snatcher</title>
</head>
<body>
    <form enctype="multipart/form-data" action="{url}" method="post">
        <input type="hidden" name="MAX_FILE_SIZE" value="{MAX_FILE_SIZE}"
        <p>File: <input type="file" name="filename" /></p>
        <p><input type="submit" value="Upload" /></p>
    </form>
</body>
</html>
'''.format(MAX_FILE_SIZE=MAX_FILE_SIZE, url=URL_PATH)

ERROR = '''
<html>
<head>
    <title>Error</title>
</head>
<body>
    <p>{}</p>
</body>
</html>
'''

OCR_body = '''
<html>
<head>
    <title>OCR Results</title>
    <style>
    table, th, td {{
        border: 1px solid black;
    }}
    </style>
</head>
<body>
    <table>
        <tr><th>item</th><th>price</th></tr>
        {ocr_entries}
    </table>
    <br>
    <p><a href="{url}">Another</a></p>
</body>
</html>
'''

OCR_entry = '''
<tr><td>{item}</td><td>{price}</td></tr>
'''

print('Content-Type: text/html\r\n\r\n', end='')

class ExitWithPage(Exception):
    def __init__(self, page):
        self.page = page

try:
    if os.environ['REQUEST_METHOD'] == 'GET':
        raise ExitWithPage(DEFAULT)
    elif os.environ['REQUEST_METHOD'] == 'POST':
        if 'filename' in form:
            fileitem = form['filename']
            if fileitem == '' or not fileitem.file:
                raise ExitWithPage(ERROR.format('No file selected!'))
            content = fileitem.file.read(MAX_FILE_SIZE)
            if fileitem.file.read(1):
                raise ExitWithPage(ERROR.format('File too large!'))
            if len(content) == 0:
                raise ExitWithPage(ERROR.format('No file content!'))
            # this is the base name of the file that was uploaded:
            filename = os.path.basename(fileitem.filename)
            #name, ext = os.path.splitext(filename)
            try:
                pages = snatcher.bytes_to_pages(filename, content)
                rows = snatcher.parse(pages)
                entries = '\n'.join(OCR_entry.format(**row) for row in rows)
            except Exception as error:
                raise ExitWithPage(ERROR.format('OCR failure')) from error
            else:
                raise ExitWithPage(OCR_body.format(ocr_entries=entries, url=URL_PATH))
        else:
            raise ExitWithPage(DEFAULT)
except ExitWithPage as exiting:
    print(exiting.page)

