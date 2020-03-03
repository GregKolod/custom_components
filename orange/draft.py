#!/usr/bin/env python
# coding: utf-8

from urllib.request import urlopen
from bs4 import BeautifulSoup

BASE_URL = 'https://www.teleman.pl/program-tv/stacje/'

page = urlopen(BASE_URL)
soup = BeautifulSoup(page, 'html.parser')

tv_stacje = soup.find('div', attrs={'id': 'stations-index'}).find_all('a')

# zwraca nazwe stacji do przygotowania linku dla scrapera

for stacja in range(len(tv_stacje)):
    link_tv = str(tv_stacje[stacja]['href']).split('/')[3]
    nazwa_stacji = tv_stacje[stacja].text
    print(nazwa_stacji, link_tv)
    # print(BASE_URL+link_tv)
