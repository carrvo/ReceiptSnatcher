#!/bin/python3
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

import pytesseract


def pdf_to_img(pdf_file):
    return pdf2image.convert_from_path(pdf_file)


def ocr_core(file):
    options = "--psm 4"
    text = pytesseract.image_to_string(file, config=options)
    return text


def pages(pdf_file):
    images = pdf_to_img(pdf_file)
    for pg, img in enumerate(images):
        yield ocr_core(img).split('\n')

class NotFound:
    def __init__(self):
        self.name = ''
        self.item_row = re.compile('')
        self.stop_row = re.compile('')

class Safeway:
    def __init__(self):
        self.name = 'SAFEWAY'
        self.item_row = re.compile('\+?(?P<item>[\w\d\s]+)\s+(?P<price>-?\$\d+(\.\d+)?)')
        self.stop_row = re.compile('SUBTOTAL')

def parse(pages):
    pages = tuple(pages)
    header = pages[0][0]
    for parser in (Safeway(), NotFound()):
        if re.search(parser.name, header):
            break
    for page in pages:
        for line in page:
            row = parser.item_row.search(line)
            if row:
                yield row.group('item', 'price')
            elif parser.stop_row.search(line):
                raise StopIteration

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath")
    args = parser.parse_args()
    for row in parse(pages(args.filepath)):
        print(row)

