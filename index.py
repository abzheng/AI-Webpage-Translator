# from flask import Flask, request, jsonify, render_template, send_file
# import pytesseract
# from io import BytesIO
from bs4 import BeautifulSoup
# from googletrans import Translator
# import urllib.request
# import os
# import certifi
from PIL import Image
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

url = 'https://www.czmanga.com/comic/chapter/silingfashiwojishitianzai-mantudezhuyuanzhuheiniaoshe/0_0.html'

# # to get rid of certificate not found error from urllib
# os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
# os.environ["SSL_CERT_FILE"] = certifi.where()

# initializes selenium, removes top of browser and opens the url
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
driver = webdriver.Chrome(options=options)
driver.get(url)

# takes a picture of the entire webpage and saves it
fullWidth = driver.execute_script('return document.body.parentNode.scrollWidth')
fullHeight = driver.execute_script('return document.body.parentNode.scrollHeight')
driver.set_window_size(fullWidth, fullHeight)
time.sleep(20)

# page = driver.page_source
# doc = BeautifulSoup(page, 'html.parser')
# imageLinks = doc.find_all('img')
# print(imageLinks)

# try:
#WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.XPATH, '//img')))

# except TimeoutException as ex:
#     print('Error' + str(ex))
#     driver.close()

driver.save_screenshot('imgCombined.png')

imageCombined = Image.open('imgCombined.png')
imageCombined.show()

# for i in range(4):
#     img = imageLinks[i]
#     imgURL = img['src']
#     urllib.request.urlretrieve(imgURL, 'image')
#     image = Image.open('image')
#     images.append(image)

# # parses through list of images and takes the url, which is then converted to bytes and opened, then appended to image list
# for img in imageLinks:
#     imgURL = img['src']
#     urllib.request.urlretrieve(imgURL, 'image')
#     image = Image.open('image')
#     images.append(image)

# minSize = sorted([(numpy.sum(i.size), i.size) for i in images])[0][1]
# imgCombined = numpy.vstack([img.resize(minSize) for img in images])
# imgCombined = Image.fromarray(imgCombined, 'RGB')
# imgCombined.save('combined.png')
# imgCombined.show()

