from flask import Flask, request, jsonify, render_template, send_file
from PIL import Image, ImageDraw, ImageFont
# from io import BytesIO
import deepl
# from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
import urllib.request
import os
import certifi
from paddleocr import PaddleOCR, draw_ocr

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
    whitedImage = []
    finalImages = []
    groupedOcrData = []

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

            while num != -1:
                ocrData[num][1] = list(ocrData[num][1])

                # if anything in uselessText is found in the string the OCR read, delete it
                if any(string in ocrData[num][1][0] for string in uselessText):
                    del ocrData[num]

                num -= 1
            
            # white-ing out the text to prepare it to get drawn over
            im = Image.open('img.jpg')
            imgToEdit = ImageDraw.Draw(im)
            for line in ocrData:
                # making the area a bit bigger because it usually cuts a bit short
                xy1 = line[0][0]
                xy2 = line[0][2]
                xy1[0] -= 10
                xy1[1] -= 10
                xy2[0] += 10
                xy2[1] += 10

                imgToEdit.rectangle([tuple(xy1), tuple(xy2)], fill ='#FFFFFF')
                im.save('img.jpg')
                whitedImage.append(im)

            if len(ocrData) == 1:
                bottomRight = ocrData[0][0][2]
                ocrData[0].append(bottomRight)
                translatedText = translator.translate_text(ocrData[0][1][0], source_lang='ZH', target_lang='EN-US',)

        # takes the text, translates it to english, and adds the bounding box + translated text to a list
            else:
                index = 0
                while index < len(ocrData) - 1:
                    currentGroup = ocrData[index]
                    currentText = currentGroup[1][0]
                    bottomRight = currentGroup[0][2]

                    # while the current line of text's x and y are very close to the next line of text's x and y, group them to make translation more fluid, and stop if they aren't close
                    # bounding box is read topleft, topright, bottomright, bottomleft
                    # ocrData[index][0][0][1] = index's y value
                    # ocrData[index][0][0][0] = index's x value
                    while (index < len(ocrData) - 1 and 0 < ocrData[index + 1][0][0][1] - ocrData[index][0][0][1] < 1000 and  -300 < ocrData[index][0][0][0] - ocrData[index + 1][0][0][0] < 300):
                        nextGroup = ocrData[index + 1]
                        currentText += nextGroup[1][0]
                        bottomRight = nextGroup[0][2]
                        index += 1

                    translatedText = translator.translate_text(currentText, source_lang='ZH', target_lang='EN-US')
                    groupedOcrData.append([currentGroup[0][0], translatedText.text, bottomRight])

                    index += 1
                    
                    wordList = translatedText.text.split()
                    line = []
                    groupText = []
                    font = ImageFont.truetype(font='buddychampion.ttf', size=25)
                    draw = ImageDraw.Draw(whitedImage[0])
                    # right - left of the original text bbox 
                    deltaTextLen = groupedOcrData[-1][2][0] - groupedOcrData[-1][0][0]
                    for word in wordList:
                        line.append(word)
                        print(' '.join(line))
                        # right - left of the line length
                        deltaLineLen = font.getbbox(' '.join(line))[2] - font.getbbox(' '.join(line))[0]
                        print(deltaLineLen, '>', deltaTextLen)
                        if deltaLineLen  > deltaTextLen:
                            line.insert(-2, '\n')
                            groupText.append([line])
                            line = []

        # pseudo code
        # write code to put the text on to the image and then append it to a list
        # return translated images in render_template along with original to toggle on/off
            # for data in ocrData:
            #     fontSize = 18
            #     font = ImageFont.truetype('arial', fontSize)
            #     draw = ImageDraw.Draw(whitedImage[0])
            #     xLength = data[0][1][0] - data[0][0][0]
            #     yLength = data[0][2][1] - data[0][1][1]
            #     print(xLength, yLength,'\n')

            #     # make a tuple out of this based on the lengths of each side !!!!!!!!!!!!!!!!!!!!!!!!!
            #     textBbox = draw.textbbox((int((data[0][0][0] + data[0][2][0]) / 2), int((data[0][0][1] + data[0][2][1]) / 2)), translatedText.text, font=font)
            #     textBboxTuple = (textBbox[2] - textBbox[0], textBbox[3] - textBbox[1])
            #     while textBboxTuple > (xLength, yLength):
            #         font = ImageFont.truetype('arial', fontSize)
            #         fontSize -= 1
            #         textBbox = draw.textbbox((int((data[0][0][0] + data[0][2][0]) / 2), int((data[0][0][1] + data[0][2][1]) / 2)), translatedText.text, font=font)
            #         textBboxTuple = (textBbox[2] - textBbox[0], textBbox[3] - textBbox[1])                

                #draw.text(, translatedText.text, tuple(data[0][2]), font)

    print (groupedOcrData)
    whitedImage[6].show()
    return render_template('index.html', images=images, textAndCoords=textAndCoords, finalImages=finalImages)

if __name__ == '__main__':
    app.run(debug=True)