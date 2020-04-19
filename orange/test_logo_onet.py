#!/usr/bin/env python
# coding: utf-8

from bs4 import BeautifulSoup
import logging
from urllib.request import urlopen

_CACHE = {}
_LOGGER = logging.getLogger(__name__)
BASE_URL = 'https://programtv.onet.pl'

page = urlopen(BASE_URL)
soup = BeautifulSoup(page, 'lxml')

last_page = False
next_page_nr = 0

channel_list = []

# have to go thru all the channels pages to retrive all names and logos
while last_page is not True:
    page = urlopen(BASE_URL + '/?dzien=0&strona=' + str(next_page_nr))
    soup = BeautifulSoup(page, 'lxml')
    channels_on_page = soup.find_all('span', class_='headerTV')
    # retrieve channel name and link to logo
    for channel in range(len(channels_on_page)):
        channel_name = channels_on_page[channel].find('span', class_='tvName').text.strip()
        channelLogo = 'http:' + channels_on_page[channel].find('img', class_='lazyLoad')['data-original']
        channel_list.append({'channel': channel_name, 'logo': channelLogo})

    # have to determine if current page is the last one, if trur  finish loop
    if soup.find('div', class_='pager').find('a', class_='nextLnk'):
        next_page_nr += 1
    else:
        last_page = True

print(channel_list)
