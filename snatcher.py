#!/usr/bin/python3
"""
https://stackoverflow.com/a/58339704
"""

import argparse
import re
import pdf2image

try:
    from PIL import Image
except ImportError:
    import Image

import cv2
import pytesseract

DEBUG = False


def ocr_core(file):
    options = "--psm 4"
    text = pytesseract.image_to_string(file, config=options)
    return text.split('\n')


def file_to_pages(filepath):
    if filepath.endswith('pdf'):
        images = pdf2image.convert_from_path(filepath)
        return tuple(
            line # kudos to https://stackoverflow.com/a/952952
            for img in images
            for line in ocr_core(img)
        )
    else:
        # assumes that the images is pre-processed (straightened, et cetera)
        return ocr_core(cv2.imread(filepath))

def bytes_to_pages(filename, content):
    if filename.endswith('pdf'):
        images = pdf2image.convert_from_bytes(content)
        return tuple(
            line # kudos to https://stackoverflow.com/a/952952
            for img in images
            for line in ocr_core(img)
        )
    else:
        # assumes that the images is pre-processed (straightened, et cetera)
        return ocr_core(cv2.imdecode(content))


class NotFound:
    def __init__(self):
        self.name = ''
        self.item_row = re.compile('\n')
        self.stop_row = re.compile('.')
        self.fields = ('item', 'price')

class Safeway(NotFound):
    def __init__(self):
        super().__init__()
        self.name = 'SAFEWAY'
        self.item_row = re.compile('\+?(?P<item>\w[\w\d\s]+)\s+(?P<price>-?\$\d+(\.\d+)?)')
        self.stop_row = re.compile('SUBTOTAL')

class Costco(NotFound):
    def __init__(self):
        super().__init__()
        self.name = 'COSTCO'
        self.item_row = re.compile('(?P<code>\d+)\s+(?P<item>\w[\w\d\s]+)\s+(?P<price>\d+(\.\d+)?)')
        self.stop_row = re.compile('SUBTOT')
        if DEBUG:
            self.fields = ('code', 'item', 'price')

def parse(pages):
    pages = tuple(pages)
    header = pages[0]
    for parser in (Safeway(), Costco(), NotFound()):
        if re.search(parser.name, header):
            break
    for line in pages:
        row = parser.item_row.search(line)
        if row:
            parsed = {field: row.group(field) for field in parser.fields}
            if DEBUG:
                parsed.update({'line': line})
            yield parsed
        elif parser.stop_row.search(line):
            return #StopIteration()

if __name__ == '__main__':
    #global DEBUG
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath")
    parser.add_argument("--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("--raw", help="print the raw text instead of parsing", action="store_true")
    args = parser.parse_args()
    if args.verbose:
        DEBUG = True
    pages = file_to_pages(args.filepath)
    rows = pages if args.raw else parse(pages)
    for row in rows:
        print(row)

