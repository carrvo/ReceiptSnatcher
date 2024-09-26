#!/usr/bin/python3
"""
https://stackoverflow.com/a/58339704
"""

import argparse
import re
import datetime
import pdf2image

try:
   from PIL import Image
except ImportError:
   import Image

import cv2
import pytesseract


def parse_date(date_string, date_format):
   """
   https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
   """
   return datetime.datetime.strptime(date_string, date_format).date()

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
   def __init__(self, debug = False):
       self.debug = debug
       self.name = ''
       self.item_row = re.compile('\n')
       self.stop_row = re.compile('.')
       self.date_row = re.compile('\n')
       self.date_format = ''
       self.fields = ('item', 'price')
       self.state = 'idle'

   def parse(self, line):
       if self.state == 'idle' or self.state == 'finished':
           self.state = 'in-progress'
       if self.state == 'in-progress':
           row = self.item_row.search(line)
           if row:
               parsed = {field: row.group(field).replace('$', '') for field in self.fields}
               if self.debug:
                   parsed.update({'line': line})
               return parsed
           elif self.stop_row.search(line):
               #raise StopIteration()
               self.state = 'item-complete'
       elif self.state == 'item-complete':
           row = self.date_row.search(line)
           if row:
               self.date = parse_date(row.group('date'), self.date_format)
               self.state = 'finished'
               raise StopIteration()

class Safeway(NotFound):
   def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)
       self.name = 'SAFEWAY'
       self.item_row = re.compile('\+?(?P<item>\w[\w\d\s]+)\s+(?P<price>-?\$\d+(\.\d+)?)')
       self.stop_row = re.compile('SUBTOTAL')
       self.date_row = re.compile('(?P<date>\d\d/\d\d/\d\d)\s*')
       self.date_format = '%m/%d/%y'

class Costco(NotFound):
   def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)
       self.name = 'COSTCO'
       self.item_row = re.compile('(?P<code>\d+)\s+(?P<item>\w[\w\d\s]+)\s+(?P<price>\d+(\.\d+)?)')
       self.stop_row = re.compile('SUBTOT')
       if self.debug:
           self.fields = ('code', 'item', 'price')
       self.date_row = re.compile('AUTH.+(?P<date>\d\d\d\d/\d\d/\d\d)\s+(?P<time>\d\d:\d\d:\d\d)')
       self.date_format = '%Y/%m/%d'

def parse_line(parser, line):
   if parser.state == 'finished':
       return
   try:
       return parser.parse(line)
   except StopIteration:
       return

def parse(pages, debug=False):
   pages = tuple(pages)
   header = pages[0]
   for parser in tuple(klass(debug=debug) for klass in (Safeway, Costco, NotFound)):
       if re.search(parser.name, header):
           break
   parsed = tuple(
       row
       for row in (
           parse_line(parser, line)
           for line in pages
       )
       if row
   )
   for row in parsed:
       row.update({'transaction_date': parser.date})
   return parsed

if __name__ == '__main__':
   parser = argparse.ArgumentParser()
   parser.add_argument("filepath")
   parser.add_argument("--verbose", help="increase output verbosity", action="store_true")
   parser.add_argument("--raw", help="print the raw text instead of parsing", action="store_true")
   args = parser.parse_args()
   pages = file_to_pages(args.filepath)
   rows = pages if args.raw else parse(pages, debug=args.verbose)
   for row in rows:
       print(row)

