from flask import Flask, request, jsonify, render_template, send_file
from PIL import Image
# from io import BytesIO
import deepl
# from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
import urllib.request
import os
import certifi
from paddleocr import PaddleOCR, draw_ocr
import time

# fix certificate not found error https://stackoverflow.com/a/73270162/26629340 
# and PaddleOCR Error #15 https://github.com/PaddlePaddle/PaddleOCR/issues/4613
os.environ['KMP_DUPLICATE_LIB_OK']='True'
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
os.environ["SSL_CERT_FILE"] = certifi.where()

# init
app = Flask(__name__)
apiKey = 'c8254cd6-2590-416f-baae-f5130577b26b:fx'
translator = deepl.Translator(apiKey)
ocr = PaddleOCR(use_angle_cls=True, lang='ch')

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

    # PaddleOCR for optimal chinese to english OCR
    for img in images:
        urllib.request.urlretrieve(img, 'img.jpg')
        ocrData = ocr.ocr('img.jpg', cls=True)
        # ocr returns an extra unnecessary nested list
        ocrData = ocrData[0]
        uselessText = {'新免费漫', 'baozi', '包子漫', '.com'}

        # remove useless text ^
        if ocrData:
            num = len(ocrData) - 1
            try:
                while num != -1:
                    ocrData[num][1] = list(ocrData[num][1])

                    # if anything in uselessText is found in the string the OCR read, delete it
                    if any(string in ocrData[num][1][0] for string in uselessText):
                        del ocrData[num]

                    num -= 1

            except IndexError:
                pass

        # takes the text, translates it to english, and adds the bounding box + translated text to a list
        # i have try except for now because i cant figure out whats wrong with the indexing
            try:
                for index in range(len(ocrData)):
                    try:
                        # while the current line of text's x and y are very close to the next line of text's x and y, group them to make translation more fluid, and stop if they arent
                        print(ocrData[index + 1][0][0][1], ocrData[index][0][0][1])
                        while 0 < ocrData[index + 1][0][0][1] - ocrData[index][0][0][1] < 1000 and  -300 < ocrData[index][0][0][0] - ocrData[index + 1][0][0][0] < 300:
                            ocrData[index + 1][1] = list(ocrData[index + 1][1])
                            ocrData[index][1][0] += ocrData[index + 1][1][0]
                            del ocrData[index + 1]

                    except IndexError:
                        pass
            except IndexError:
                pass

            for lis in ocrData:
                translatedText = translator.translate_text(lis[1][0], source_lang='ZH', target_lang='EN-US',)
                textAndCoords.append([lis[0][0], translatedText.text])
        
        # pseudo code 
        # use IO paint to white out text on the speech bubbles https://github.com/Sanster/IOPaint
        # write code to put the text on to the image and then append it to a list
        # return translated images in render_template along with original to toggle on/off

    print (textAndCoords)
    return render_template('index.html', images=images, textAndCoords=textAndCoords)

if __name__ == '__main__':
    app.run(debug=True)