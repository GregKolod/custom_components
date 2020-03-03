#!/usr/bin/env python
# coding: utf-8


from urllib.request import urlopen
from bs4 import BeautifulSoup

BASE_URL = 'https://www.teleman.pl/program-tv/stacje/'

page = urlopen(BASE_URL + channel)
soup = BeautifulSoup(BASE_URL, 'html.parser')

tv_stacje = soup.find('div', attrs={'id': 'stations-index'}).find_all('a')

print(tv_stacje)
