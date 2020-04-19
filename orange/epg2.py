#!/usr/bin/env python
# coding: utf-8

from urllib.request import urlopen
from bs4 import BeautifulSoup
import aiohttp
import datetime
import asyncio
import logging
import re
from urllib.request import urlopen

_CACHE = {}
_LOGGER = logging.getLogger(__name__)
BASE_URL = 'https://www.telemagazyn.pl'


async def _async_request_soup(url):
    '''
    Perform a GET web request and return a bs4 parser
    '''

    _LOGGER.debug('GET %s', url)
    # text = urlopen(url)
    # return BeautifulSoup(text, 'html.parser')

    async with aiohttp.ClientSession() as session:
        # print('_async_request_soup url', url)
        resp = await session.get(url)
        # print('_async_request_soup resp', resp)
        text = await resp.text()

        return BeautifulSoup(text, 'html.parser')


async def async_determine_channel(channel):
    # TODO do przerobienia  - pobieramy kanały z  list channels.py
    '''
    Check whether the current channel is correct. If not try to determine it
    using fuzzywuzzy
    '''
    from fuzzywuzzy import process
    channel_data = await async_get_channels()
    # print('async_determine_channel channel_data ', channel_data)
    if not channel_data:
        _LOGGER.error('No channel data. Cannot determine requested channel.')
        return
    channels = [c for c in channel_data.get('data', {}).keys()]
    # print('async_determine_channel channels ', channels)
    if channel in channels:
        # print('if async_determine_channel channel ', channel)
        return channel
    else:
        res = process.extractOne(channel, channels)[0]
        _LOGGER.debug('No direct match found for %s. Resort to guesswork.'
                      'Guessed %s', channel, res)
        # print('async_determine_channel res', res)
        return res


async def async_get_channels(no_cache=False, refresh_interval=4):
    '''
    Get channel list and corresponding urls
    '''
    # Check cache
    now = datetime.datetime.now()
    max_cache_age = datetime.timedelta(hours=refresh_interval)
    if not no_cache and 'channels' in _CACHE:
        cache = _CACHE.get('channels')
        # print('async_get_channels cache ', cache)
        cache_age = cache.get('last_updated')
        if now - cache_age < max_cache_age:
            _LOGGER.debug('Found channel list in cache.')
            # print('async_get_channels cache ', cache)
            return cache
        else:
            _LOGGER.debug('Found outdated channel list in cache. Update it.')
            _CACHE.pop('channels')

    soup = await _async_request_soup(BASE_URL + '/stacje/')
    channels = {}

    tv_stacje = soup.find('div', attrs={'class': 'listaStacji'}).find_all('li', attrs={'class': 'polska'})

    for stacja in range(len(tv_stacje)):
        try:
            href = tv_stacje[stacja].find('a')['href']

            nazwa_stacji = tv_stacje[stacja].text
            # print('nazwa_stacji', nazwa_stacji)
            channels[nazwa_stacji] = BASE_URL + href
            # print('nazwa_stacji channels', channels[nazwa_stacji])

        except Exception as exc:
            _LOGGER.error('Exception occured while fetching the channel '
                          'list: %s', exc)
    if channels:
        _CACHE['channels'] = {'last_updated': now, 'data': channels}

        return _CACHE['channels']


def resize_program_image(img_url, img_size=300):
    '''
    Resize a program's thumbnail to the desired dimension
    '''
    try:
        imgr_url = img_url.replace('crop-100x63', '470x265')
    # todo
    except Exception as exc:
        _LOGGER.error('Exception occured while converting image %s', exec)
        imgr_url = img_url

    return imgr_url


def get_current_program_progress(program):
    # todo to chyba bez zmian
    '''
    Get the current progress of the program in %
    '''
    now = datetime.datetime.now()
    program_duration = get_program_duration(program)
    if not program_duration:
        return
    progress = now - program.get('start_time')
    return progress.seconds * 100 / program_duration


def get_program_duration(program):
    # todo to chyba bez zmian
    '''
    Get a program's duration in seconds
    '''
    program_start = program.get('start_time')
    program_end = program.get('end_time')
    if not program_start or not program_end:
        _LOGGER.error('Could not determine program start and/or end times.')
        _LOGGER.debug('Program data: %s', program)
        return
    program_duration = program_end - program_start
    return program_duration.seconds


def get_remaining_time(program):
    # todo to chyba bez zmian
    '''
    Get the remaining time in seconds of a program that is currently on.
    '''
    now = datetime.datetime.now()
    program_start = program.get('start_time')
    program_end = program.get('end_time')
    if not program_start or not program_end:
        _LOGGER.error('Could not determine program start and/or end times.')
        _LOGGER.debug('Program data: %s', program)
        return
    if now > program_end:
        _LOGGER.error('The provided program has already ended.')
        _LOGGER.debug('Program data: %s', program)
        return 0
    progress = now - program_start
    # print(progress)
    return progress.seconds


def extract_program_summary(data):
    '''
    Extract the summary data from a program's detail page
    '''
    soup = BeautifulSoup(data, 'html.parser')

    try:

        # summary = soup.find('div', class_='daneZajawka').find('p').text.strip()
        summary = soup.find('div', class_='markdown').find('p').text.strip()

        # print(summary)
        return summary


    except Exception:
        # print("brak ", soup.find('h1').text)
        _LOGGER.info('No summary found for program: %s',
                     soup.find('h1').text)
    finally:
        _LOGGER.info('No summary found nor program name')

    return "No summary"


async def async_set_summary(program):
    # todo do przerobienia ze scraper - podsumowanie
    '''
    Set a program's summary
    '''
    import aiohttp
    async with aiohttp.ClientSession() as session:
        resp = await session.get(program.get('url'))
        text = await resp.text()
        summary = extract_program_summary(text)
        program['summary'] = summary
        return program


async def async_get_program_guide(channel, no_cache=False, refresh_interval=4):
    # todo scraper
    """
    Get the program data for a channel
    """
    # print('async_get_program_guide channel', channel)

    chan = await async_determine_channel(channel)

    # print('#async_get_program_guide chan', chan)

    now = datetime.datetime.now()
    today = datetime.date.today()

    max_cache_age = datetime.timedelta(hours=refresh_interval)

    if not no_cache and 'guide' in _CACHE and _CACHE.get('guide').get(chan):
        cache = _CACHE.get('guide').get(chan)
        cache_age = cache.get('last_updated')
        if now - cache_age < max_cache_age:
            _LOGGER.debug('Found program guide in cache.')
            return cache.get('data')
        else:
            _LOGGER.debug('Found outdated program guide in cache. Update it.')
            _CACHE['guide'].pop(chan)

    chans = await async_get_channels()
    # print('async_get_program_guide chans ', chans)

    url = chans.get('data', {}).get(chan)

    if not url:
        _LOGGER.error('Could not determine URL for %s', chan)
        return
    soup = await _async_request_soup(url)
    programs = []

    ul_tag = soup.find('div', class_='lista').find('ul').find_all('li', class_=lambda x: 'rkl' not in x)

    # print(ul_tag)

    for prg_item in range(len(ul_tag)):

        try:
            prog_name = ul_tag[prg_item].find('a', class_='programInfo').find('span').text.strip()
            # nazwa programu
            # print(prog_name)
            prog_url = BASE_URL[:26] + ul_tag[prg_item].find('a', class_='programInfo')['href']
            # print(prog_url)

            if not prog_url:
                _LOGGER.warning('Failed to retrieve the detail URL for program %s. '
                                'The summary will be empty', prog_name)
            try:
                prog_type = ul_tag[prg_item]['class'][0]
                # print('prog_type', prog_type)

            except Exception:
                prog_type = ''
                # print('prog_type e', prog_type)
                # dla zakończenia programy nie ma typu programu
                _LOGGER.error('Exception occured while fetching the program genre')

            start_time = (
                datetime.datetime.strptime(ul_tag[prg_item].find('a', class_='programInfo').find('em').text.strip(),
                                           '%H:%M'))
            # print(start_time)

            try:

                stop_time = (datetime.datetime.strptime(
                    ul_tag[prg_item + 1].find('a', class_='programInfo').find('em').text.strip(), '%H:%M'))
                # print(stop_time)

            except Exception:

                stop_time = start_time + datetime.timedelta(hours=2)
                _LOGGER.error('Exception occured while fetching the program end')

            today = datetime.date.today()

            prog_start = datetime.datetime.combine(today, start_time.time())
            # print('prog_start', prog_start)

            prog_end = datetime.datetime.combine(today, stop_time.time())
            # print('prog_end', prog_end)

            soup = await _async_request_soup(prog_url)

            # obrazki są na stronie prgramu i trzeba jeszcze jedną soup
            try:
                prog_img = soup.find('div', attrs={'class': 'informacje'}).find('a')['content']
                # niektóre programy maja filmy zamiast zdjęcie

            except Exception:
                # if ( soup.find('div', attrs={'class': 'zdjecieGlowne'}).find('script', attrs={'class': 'XlinkEmbedScript'})):
                #     prog_img = ''
                #     _LOGGER.error('Exception occured while fetching the primary channel image')
                #
                # elif soup.find('div', attrs={'class': 'zdjecieGlowne'}).find('a')['href']:
                #     prog_img = soup.find('div', attrs={'class': 'zdjecieGlowne'}).find('a')['href']
                #
                # # inne maja zdjęcie pod inna klasa
                prog_img = ''
                _LOGGER.error('No channel image')

            # print(prog_img)
            programs.append(
                {'name': prog_name, 'type': prog_type, 'img': prog_img,
                 'url': prog_url, 'summary': None, 'start_time': prog_start,
                 'end_time': prog_end})

        except Exception as exc:
            _LOGGER.error('Exception occured while fetching the program guide for channel %s: %s', chan, exc)
            import traceback

            traceback.print_exc()

    # Set the program summaries asynchronously

    tasks = [async_set_summary(prog) for prog in programs]
    programs = await asyncio.gather(*tasks)

    if programs:
        if 'guide' not in _CACHE:
            _CACHE['guide'] = {}
        _CACHE['guide'][chan] = {'last_updated': now, 'data': programs}
    # print(programs)
    return programs


async def async_get_current_program(channel, no_cache=False):
    # todo scrap albo bez zmian bo pobiera dane z innych procedur
    '''
    Get the current program info
    '''
    chan = await async_determine_channel(channel)
    # print('async_get_current_program chan ', chan)

    guide = await async_get_program_guide(chan, no_cache)

    # print('async_get_current_program guide ', guide)

    if not guide:
        _LOGGER.warning('Could not retrieve TV program for %s', channel)
        # print('no guide')
        return
    now = datetime.datetime.now()
    for prog in guide:
        start = prog.get('start_time')
        # print('start', start)
        end = prog.get('end_time')
        if start < now < end:
            # print('async_get_current_program prog', prog)
            return prog


def _request_soup(*args, **kwargs):
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(_async_request_soup(*args, **kwargs))
    # print(res)
    return res


def get_channels(*args, **kwargs):
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(async_get_channels(*args, **kwargs))
    print('get_channels res', res)
    return res


def get_program_guide(*args, **kwargs):
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(async_get_program_guide(*args, **kwargs))
    print('get_program_guide res', res)
    return res


def get_current_program(*args, **kwargs):
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(async_get_current_program(*args, **kwargs))

    for key in res:
        print(key, res[key])
        # print('get_current_program res', res)
        # print(res['name'])
        # print(res['start_time'])
        # print(res['end_time'])

    return res


# get_program_guide('tvp3_krakow')

# get_current_program('tvp 3 Kraków')


get_remaining_time(get_current_program('PLANETE+'))
