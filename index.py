# from flask import Flask, request, jsonify, render_template, send_file
# import pytesseract
# from PIL import Image
# from io import BytesIO
# from googletrans import Translator
# from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver

url = 'https://www.czmanga.com/comic/chapter/silingfashiwojishitianzai-mantudezhuyuanzhuheiniaoshe/0_0.html'

# initializes selenium and takes 
driver = webdriver.Chrome()
driver.get(url)
page = driver.page_source
doc = BeautifulSoup(page, 'html.parser')
images = doc.find_all('img')

for i in images:
    print(i['src'])