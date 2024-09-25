#!/bin/python3
"""
https://stackoverflow.com/a/58339704
"""

import argparse
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


def print_pages(pdf_file):
    images = pdf_to_img(pdf_file)
    for pg, img in enumerate(images):
        print(ocr_core(img))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath")
    args = parser.parse_args()
    print_pages(args.filepath)

