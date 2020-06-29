#!/usr/bin/env python
# coding: utf-8

from bs4 import BeautifulSoup
import json
import logging
from urllib.request import urlopen
import requests

programs = []
_CACHE = {}
_LOGGER = logging.getLogger(__name__)
URL = 'https://programtv.onet.pl/program-tv/tvp-1-321'

source = urlopen(URL)
soup = BeautifulSoup(source, 'html.parser')

js = json.loads(soup.find('div', class_='emissions').find('script', type='application/ld+json').text)
_data = js['itemListElement']

for i in range(len(_data)):
    start_time = _data[i]['item']['startDate']
    end_time = _data[i + 1]['item']['startDate']
    progURL = _data[i]['item']['url']
    print(progURL)
    sourceProg = urlopen(progURL)
    soupProg = BeautifulSoup(sourceProg, 'html.parser')
    jsonProg = json.loads(soupProg.find('script', type='application/ld+json').text)

    print(jsonProg)
    name = jsonProg[1]['workPerformed']['name']
    # genre = jsonProg[1]['workPerformed']['genre']
    # img = jsonProg[1]['workPerformed']['thumbnailUrl']
    # summary = jsonProg[1]['description']
    # print(programs)

    programs.append(
        {'name': name, 'season': '', 'episode': '', 'type': 'genre', 'img': 'img', 'url': '',
         'summary': 'summary', 'start_time': start_time, 'end_time': end_time})

# print(programs)
