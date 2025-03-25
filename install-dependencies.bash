#!/usr/bin/bash

echo LAMP stack
sudo apt install apache2 php php8.1-mysql libapache2-mod-wsgi-py3
echo Tesseract Python stack
sudo apt install tesseract-ocr libtesseract-dev libleptonica-dev pkg-config pytesseract w3m python3-opencv

echo PIP
sudo apt install python3-pip

echo Python Flask stack
sudo pip3 install mysql-connector-python Flask #Flask-BasicAuth Flask-HtPasswd
echo Tesseract Python stack
sudo pip3 install cv2 opencv-python pillow tesserocr pytesseract imutils scipy.spatial scipy pdf2image

