import deepl.translator
from flask import Flask, request, jsonify, render_template, send_file
import easyocr
from PIL import Image
# from io import BytesIO
import deepl
# from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
import urllib.request
import os
import certifi
import numpy as np
import cv2
#from matplotlib import pyplot as plt
import csv

# fix certificate not found error https://stackoverflow.com/a/73270162/26629340
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
os.environ["SSL_CERT_FILE"] = certifi.where()

# init
app = Flask(__name__)
apiKey = 'c8254cd6-2590-416f-baae-f5130577b26b:fx'
translator = deepl.Translator(apiKey)
reader = easyocr.Reader(['ch_sim', 'en'])

# html route init
@app.route('/')
def index():
    return render_template('index.html')

# function for translation
@app.route('/process', methods=['POST'])
def process():
    # initializes selenium and opens up web scraper, then parses the html of the webpage and finds all the images
    url = request.form.get('url')
    driver = webdriver.Chrome()
    driver.get(url)
    page = driver.page_source
    doc = BeautifulSoup(page, 'html.parser')
    imageLinks = doc.find_all('amp-img')
    images = []
    textAndCoords = []

    # avoids non-comic images appending to the images list (only testing this script on this one site for now)
    for link in imageLinks:
        if 'https://s1-rsa1-usla.baozicdn.com/scomic/' in link['src']:
            images.append(link['src'])

    # easyocr to extract text from the images
    for img in images:
        urllib.request.urlretrieve(img, 'img.jpg')
        im = Image.open('img.jpg')
        ocrData = reader.readtext(im, width_ths=1, ycenter_ths=1, paragraph=True) # setting to make reader group text instead of reading word by word

        # adds text and coordinates to a list
        for (bbox, text) in ocrData:
            if text:
                translatedText = translator.translate_text(text, source_lang='ZH', target_lang='EN-US',)
                textAndCoords.append([bbox[0], translatedText.text])

    print (textAndCoords)
    return render_template('index.html', images=images, textAndCoords=textAndCoords)

if __name__ == '__main__':
    app.run(debug=True)