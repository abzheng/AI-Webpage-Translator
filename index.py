import deepl.translator
from flask import Flask, request, jsonify, render_template, send_file
import pytesseract
from PIL import Image
# from io import BytesIO
import deepl
# from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
import urllib.request
import os
import certifi

# fix certificate not found error https://stackoverflow.com/a/73270162/26629340
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
os.environ["SSL_CERT_FILE"] = certifi.where()

# init
app = Flask(__name__)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
apiKey = 'c8254cd6-2590-416f-baae-f5130577b26b:fx'
translator = deepl.Translator(apiKey)

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
    textAndCoords = {}
    a = 0

    # avoids non-comic images appending to the images list
    for link in imageLinks:
        if 'https://s1-rsa1-usla.baozicdn.com/scomic/' in link['src']:
            images.append(link['src'])

    # uses tesseract ocr to extract text from the images
    for img in images:
        urllib.request.urlretrieve(img, 'img.jpg')
        im = Image.open('img.jpg')
        ocrData = pytesseract.image_to_data(im, output_type=pytesseract.Output.DICT)
        for i in range(len(ocrData['text'])):
            text = ocrData['text'][i].strip()
            if text:
                x, y, w, h = ocrData['left'][i], ocrData['top'][i], ocrData['width'][i], ocrData['height'][i]
                translatedText = translator.translate_text(text, target_lang='EN-US')
                textAndCoords.update({i: [[x, y, w, h], translatedText.text]})
                if a < 10:
                    print(textAndCoords)
                    a += 1
    
    return render_template('index.html', images=images, textAndCoords=textAndCoords.items())

if __name__ == '__main__':
    app.run(debug=True)