#!/usr/bin/env python
# coding: utf-8

from urllib.request import urlopen
from bs4 import BeautifulSoup
import aiohttp
import datetime
import asyncio
import logging
import re

_CACHE = {}
_LOGGER = logging.getLogger(__name__)

BASE_URL = 'https://www.telemagazyn.pl/'


# page = urlopen(BASE_URL)
# soup = BeautifulSoup(page, 'html.parser')

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
        print('_async_request_soup resp', resp)
        text = await resp.text()
        # text = resp
        return BeautifulSoup(text, 'html.parser')


def _request_soup(*args, **kwargs):
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(_async_request_soup(*args, **kwargs))
    # print(res)
    return res


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

    ul_tag = soup.find('div', class_='lista').find('ul').find_all('li', class_=lambda x: x not in ('rkl'))

    # wez wszystkie li ale bez reklam

    for prg_item in range(len(ul_tag)):

        try:
            prog_name = ul_tag[prg_item].find('a', class_='programInfo').find('span').text.strip()
            # nazwa programu
            print(prog_name)
            prog_url = BASE_URL[:26] + ul_tag[prg_item].find('a', class_='programInfo')['href']
            print(prog_url)
            # wywołać asyanchonicznie soupa
            if not prog_url:
                _LOGGER.warning('Failed to retrieve the detail URL for program %s. '
                                'The summary will be empty', prog_name)
            try:
                prog_type = ul_tag[prg_item]['class'][0]
                print('prog_type', prog_type)

            except Exception:
                prog_type = ''
                print('prog_type e', prog_type)
                # dla zakończenia programy nie ma typu programu
                _LOGGER.error('Exception occured while fetching the program genre')

            start_time = (
                datetime.datetime.strptime(ul_tag[prg_item].find('a', class_='programInfo').find('em').text.strip(),
                                           '%H:%M'))
            print(start_time)

            try:

                stop_time = (datetime.datetime.strptime(
                    ul_tag[prg_item + 1].find('a', class_='programInfo').find('em').text.strip(), '%H:%M'))
                print(stop_time)

            except Exception:

                stop_time = start_time + datetime.timedelta(hours=2)
                _LOGGER.error('Exception occured while fetching the program end')

            today = datetime.date.today()

            prog_start = datetime.datetime.combine(today, start_time.time())
            print('prog_start', prog_start)

            prog_end = datetime.datetime.combine(today, stop_time.time())
            print('prog_end', prog_end)

            try:
                # soup = await _async_request_soup(prog_url)
                page = urlopen(prog_url)
                soup = BeautifulSoup(page, 'html.parser')
                prog_img = soup.find('div', attrs={'class': 'zdjecieGlowne'}).find('a')['href']
                print(prog_img)
            #
            except Exception:
                prog_img = ''
                print(prog_img)
                _LOGGER.error('Exception occured while fetching the channel image')

            programs.append(
                {'name': prog_name, 'type': prog_type, 'img': prog_img,
                 'url': prog_url, 'summary': None, 'start_time': prog_start,
                 'end_time': prog_end})
        except Exception as exc:
            _LOGGER.error('Exception occured while fetching the program guide for channel %s: %s', chan, exc)
            import traceback

            traceback.print_exc()

    # Set the program summaries asynchronously

    # tasks = [async_set_summary(prog) for prog in programs]
    # programs = await asyncio.gather(*tasks)

    if programs:
        if 'guide' not in _CACHE:
            _CACHE['guide'] = {}
        _CACHE['guide'][chan] = {'last_updated': now, 'data': programs}
    # print(programs)
    return programs


def get_channels(*args, **kwargs):
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(async_get_channels(*args, **kwargs))
    # print('get_channels res', res)
    return res


def get_program_guide(*args, **kwargs):
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(async_get_program_guide(*args, **kwargs))
    # print('get_program_guide res', res)
    return res


def get_current_program(*args, **kwargs):
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(async_get_current_program(*args, **kwargs))
    # print('get_current_program res', res)
    return res


get_program_guide('tvp 1')
