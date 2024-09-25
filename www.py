#!/usr/bin/python3
"""
"""

import cgi
import cgitb
import os

import snatcher

cgitb.enable()
form = cgi.FieldStorage()

MAX_FILE_SIZE = 30000

DEFAULT = '''
<html>
<head>
    <title>Receipt Snatcher</title>
</head>
<body>
    <form enctype="multipart/form-data" action="." method="post">
        <input type="hidden" name="MAX_FILE_SIZE" value="{MAX_FILE_SIZE}"
        <p>File: <input type="file" name="filename" /></p>
        <p><input type="submit" value="Upload" /></p>
    </form>
</body>
</html>
'''.FORMAT(MAX_FILE_SIZE=MAX_FILE_SIZE)

ERROR = '''
<html>
<head>
    <title>Error</title>
</head>
<body>
    <p>{user_error}</p>
</body>
</html>
'''

OCR_body = '''
<html>
<head>
    <title>OCR Results</title>
</head>
<body>
    <table>
        <tr><th>item</th><th>price</th></tr>
        {ocr_entries}
    </table>
</body>
</html>
'''

OCR_entry = '''
<tr><td>{item}</td><td>{price}</td></tr>
'''

print('Content-Type: text/html\r\n\r\n', end='')

if os.environ['REQUEST_METHOD'] == 'GET':
    print(DEFAULT)
    exit()
elif os.environ['REQUEST_METHOD'] == 'POST':
    if 'filename' in form:
        fileitem = form['filename']
        if fileitem == '' or not fileitem.file:
            print(ERROR.format('No file selected!'))
            exit()
        content = fileitem.file.read(size=MAX_FILE_SIZE)
        if fileitem.file.read(size=1):
            print(ERROR.format('File too large!'))
            exit()
        if len(content) == 0:
            print(ERROR.format('No file content!'))
            exit()
        # this is the base name of the file that was uploaded:
        filename = os.path.basename(fileitem.filename)
        #name, ext = os.path.splitext(filename)
        try:
            pages = snatcher.bytes_to_pages(filename, content)
            rows = parse(pages)
            entries = '\n'.join(OCR_entry.format(*row) for row in rows)
            print(OCR_body.format(entries))
            exit()
        except:
            print(ERROR.format('OCR failure'))
            raise
            exit()
    else:
        print(DEFAULT)
        exit()

