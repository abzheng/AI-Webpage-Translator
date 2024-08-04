# from flask import Flask, request, jsonify, render_template, send_file
import pytesseract
from PIL import Image
# from io import BytesIO
# from googletrans import Translator
# from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
import urllib.request
import os
import certifi

# fix certificate not found error https://stackoverflow.com/a/73270162/26629340
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
os.environ["SSL_CERT_FILE"] = certifi.where()

# url and pytesseract init
url = 'https://www.czmanga.com/comic/chapter/silingfashiwojishitianzai-mantudezhuyuanzhuheiniaoshe/0_0.html'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# initializes selenium and opens up web scraper, then parses the html of the webpage and finds all the images
driver = webdriver.Chrome()
driver.get(url)
page = driver.page_source
doc = BeautifulSoup(page, 'html.parser')
imageLinks = doc.find_all('amp-img')
images = []

# avoids non-comic images appending to the images list
for link in imageLinks:
    if 'https://s1-rsa1-usla.baozicdn.com/scomic/' in link['src']:
        images.append(link['src'])

# uses tesseract ocr to extract text from the images
for img in images:
    urllib.request.urlretrieve(img, 'img.jpg')
    im = Image.open('img.jpg')
    text = pytesseract.image_to_string(im, lang = "chi_sim")