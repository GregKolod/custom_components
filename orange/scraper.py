#!/usr/bin/env python
# coding: utf-8


from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
import datetime
import logging
import re

_LOGGER = logging.getLogger(__name__)
BASE_URL = 'https://programtv.onet.pl/program-tv/'


def channel_scrapper(channel):
    page = urlopen(BASE_URL + channel)
    soup = BeautifulSoup(page, 'lxml')

    channel_list = []

    prog_logo = 'http:' + soup.find('span', class_='logoTV').find('img')['src']
    prog_name1 = soup.find('div', class_='emissions').find('ul').find_all('li')
    print(prog_name1)
    # put soup into json
    jsn_tag = soup.find('div', class_='emissions').find('script', type="application/ld+json").string
    programContent = json.loads(jsn_tag)

    # get data in json format from webpage
    programContentList = programContent['itemListElement']

    for prg_item in range(len(programContentList)):
        prog_name = programContentList[prg_item]['item']['name'].strip()
        prog_url = programContentList[prg_item]['item']['url'].strip()

        # get add info from program link
        page_url = urlopen(prog_url)
        url_soup = BeautifulSoup(page_url, 'lxml')

        prog_img = 'http:' + url_soup.find('img', attrs={'class': 'lazyImg'})['data-original']
        prog_desc = url_soup.find('p', class_='entryDesc').text.strip()

        start_time = datetime.datetime.strptime(programContentList[prg_item]['item']['startDate'], '%Y/%m/%d %H:%M')

        #     prog_type = ul_tag[prg_item].find('p', attrs={'class': 'genre'}).text.strip()
        #
        #     start_time = (datetime.datetime.strptime(ul_tag[prg_item].find('em').text, '%H:%M'))
        #     stop_time = (datetime.datetime.strptime(ul_tag[prg_item + 1].find('em').text, '%H:%M'))
        #     prog_img = 'http:' + (ul_tag[prg_item].find('img')['src'])
        #
        print(prog_name)
        print(prog_desc)

        # print(prog_url)
        print(prog_logo)
        print(start_time)
        # print(stop_time)
        print(prog_img)
    #     # print('start', ul_tag[prg_item].find('em').text, 'stop', ul_tag[prg_item+1].find('em').text)
    #
    #     # print('lista następny', ul_tag.index(li), li)
    #
    # # lista wszystkich li w tagu ul.find('em')
    #
    # prog_start = ul_tag[0].find('em').text
    # # godzina startu programu - [0] bo pierwszy z listy bierzemy
    #
    # start = (datetime.datetime.strptime(prog_start, '%H:%M'))
    #
    # # czas trwania programu - zamieniem na time, bo muszę wyrugowac date, a potem znowu na datetime żeby policzyc różnice
    #
    # # prog_end = ul_tag[1].find('em').text
    # # godzina zakończenie programu - [1] bo drugi listy bierzemy
    # # TODO - zrobić sprawdzenia co robić jak nie można odnaleźć godziny + 2h
    #
    # try:
    #     prog_end = ul_tag[1].find('em').text
    #     stop = datetime.datetime.strptime(prog_end, '%H:%M')
    #
    # except Exception:
    #
    #     stop = start + datetime.timedelta(hours=2)
    #     _LOGGER.error('Exception occured while fetching the program end')
    #
    # durration = stop - start
    #
    # print(durration)
    # teraz = datetime.datetime.now()
    #
    # rok = teraz.date().year
    #
    # jaka_data = soup.find('a', attrs={'class': 'is-selected'}).find('span').text.strip()
    #
    # data = datetime.datetime.strptime(str(rok) + jaka_data, '%Y%d.%m')
    #
    # # + datetime.timedelta(hours=1))
    # # tu znowu zmiana na datetime
    # # TODO do spardzenie i jak bedzie z programem po północy?
    #
    # started = datetime.datetime.combine(data, start.time())
    #
    # progress = str(teraz - started).split('.', 2)[0]
    #
    # title = ul_tag[0].find('div', attrs={'class': 'detail'}).find('a').text
    # # tytuł programu
    #
    # prog_url = ul_tag[0].find('div', attrs={'class': 'detail'}).find('a')['href']
    #
    # print('https://www.teleman.pl/tv/' + prog_url)
    #
    # try:
    #     prog_img_s = 'http:' + (ul_tag[0].find('img')['src'])
    #
    # except Exception:
    #     prog_img_s = ''
    #
    #     _LOGGER.error('Exception occured while fetching the channel logo')
    #
    #     # TODO dodać klasę wyjątku!!! -   https://docs.python.org/3/library/exceptions.html
    #
    # # obraz programu - mały
    #
    # prog_img_b = prog_img_s.replace('crop-100x63', '')
    # # obraz programu - jak usunąc crop-100x63  to będzie full obraz
    #
    # prog_genre = ul_tag[0].find('p', attrs={'class': 'genre'}).text
    # # program typ
    #
    # station_class = soup.find('div', attrs={'class': 'stationTitle'})
    # # zawartośc klasy stationTitle
    #
    # chanLogo_tmp = station_class.find('img')['src']
    #
    # chanLogo = 'http:' + chanLogo_tmp[0:chanLogo_tmp.find('?v=')]
    # # logo kanału
    #
    # # station_nr = station_class.find('a', attrs={'class': 'station-number'}).text.strip()
    # # print('nr stacji: ',station_nr)
    #
    # opis = soup.find('p', attrs={'class': 'genre'}).next_sibling.text.strip()
    #
    # # opis = (ul_tag[0].find('p', attrs={'class': 'genre'})).next_sibling.text.strip()
    # # opis krótki
    #
    # today = datetime.date.today()
    # # print(today.year)
    # # print(prog_genre)
    # # print(prog_start, prog_end)
    # # print(title)
    # # print(opis)
    # # print(prog_img_s)
    # # print(prog_img_b)
    # # print(chanLogo)
    # # print(progress)

    return channel_list


shows = channel_scrapper('tvp-1-321')
