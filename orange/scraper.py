#!/usr/bin/env python
# coding: utf-8


from urllib.request import urlopen
from bs4 import BeautifulSoup
import datetime

BASE_URL = 'https://www.teleman.pl/program-tv/stacje/'


# pobiera dane o akulanym programie ze strony www.teleman.pl

def channel_scrapper(channel):
    page = urlopen(BASE_URL + channel)
    soup = BeautifulSoup(page, 'html.parser')

    channel_list = []

    ul_tag = soup.find('ul', attrs={'class': 'stationItems'}).find_all('li')
    # lista wszystkich li w tagu ul

    prog_start = ul_tag[0].find('em').text
    # godzina startu programu - [0] bo pierwszy z listy bierzemy

    prog_end = ul_tag[1].find('em').text
    # godzina zakończenie programu - [1] bo drugi listy bierzemy

    # TODO - zrobić sprawdzenia co robić jak nie można odnaleźć godziny + 2h

    title = ul_tag[0].find('div', attrs={'class': 'detail'}).find('a').text
    # tytuł programu

   
    try:
        prog_img_s = 'http:' + (ul_tag[0].find('img')['src'])

    except:
    # TODO dodać klasę wyjątku!!! -   https://docs.python.org/3/library/exceptions.html  
        prog_img_s = ''

    # obraz programu - mały

    prog_img_b = prog_img_s.replace('crop-100x63', '')
    # obraz programu - jak usunąc crop-100x63  to będzie full obraz

    prog_genre = ul_tag[0].find('p', attrs={'class': 'genre'}).text
    # program typ

    station_class = soup.find('div', attrs={'class': 'stationTitle'})
    # zawartośc klasy stationTitle

    chanLogo_tmp = station_class.find('img')['src']

    chanLogo = 'http:' + chanLogo_tmp[0:chanLogo_tmp.find('?v=')]
    # logo kanału

    # station_nr = station_class.find('a', attrs={'class': 'station-number'}).text.strip()
    # print('nr stacji: ',station_nr)

    opis = (ul_tag[0].find('p', attrs={'class': 'genre'})).next_sibling.text.strip()
    # opis krótki

    teraz = datetime.datetime.now()
    rok = teraz.date().year

    jaka_data = soup.find('a', attrs={'class': 'is-selected'}).find('span').text.strip()

    data = datetime.datetime.strptime(str(rok) + jaka_data, '%Y%d.%m')

    # czas trwania programu - zamieniem na time, bo muszę wyrugowac date, a potem znowu na datetime żeby policzyc różnice

    start = (datetime.datetime.strptime(prog_start, '%H:%M')).time()
    stop = datetime.datetime.strptime(prog_end, '%H:%M')

    # + datetime.timedelta(hours=1))
    # tu znowu zmiana na datetime
    # TODO do spardzenie i jak bedzie z programem po północy?

    started = datetime.datetime.combine(data, start)

    progress = str(teraz - started).split('.', 2)[0]

    # print(data)
    print(prog_start, prog_end)
    print(title)
    print(opis)
    print(prog_img_s)
    print(prog_img_b)
    print(chanLogo)
    print(progress)

    return channel_list


shows = channel_scrapper('tvp-abc')
