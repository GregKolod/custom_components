#!/usr/bin/env python
# coding: utf-8

# from urllib.request import urlopen
# from bs4 import BeautifulSoup
#
# BASE_URL = 'https://www.teleman.pl/program-tv/stacje/'
#
# page = urlopen(BASE_URL)
# soup = BeautifulSoup(page, 'html.parser')
#
# tv_stacje = soup.find('div', attrs={'id': 'stations-index'}).find_all('a')
#
# # zwraca nazwe stacji do przygotowania linku dla scrapera
#
# for stacja in enumerate(tv_stacje):
#     link_tv = str(stacja[1]['href']).split('/')[3]
#     nazwa_stacji = stacja[1].text
#     print(nazwa_stacji, link_tv)
#     # print(BASE_URL+link_tv)
#

import requests
from io import BytesIO
from PIL import Image

img_url = 'https://media.teleman.pl/photos/Anglik-Ktory-Mnie-Kochal.jpeg'
img_url = ''
basewidth = 300
response = requests.get(img_url)
img = Image.open(BytesIO(response.content))

wpercent = (basewidth / float(img.size[0]))
hsize = int((float(img.size[1]) * float(wpercent)))
img = img.resize((basewidth, hsize), Image.ANTIALIAS)

img.show()
