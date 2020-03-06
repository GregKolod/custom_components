#!/usr/bin/env python
# coding: utf-8


from urllib.request import urlopen
from bs4 import BeautifulSoup
import aiohttp
import datetime
import asyncio
import logging
import re

BASE_URL = 'https://www.teleman.pl/program-tv/stacje/'


async def _async_request_soup(url):
    '''
    Perform a GET web request and return a bs4 parser
    '''
    _LOGGER.debug('GET %s', url)
    async with aiohttp.ClientSession() as session:
        resp = await session.get(url)
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
    if not channel_data:
        _LOGGER.error('No channel data. Cannot determine requested channel.')
        return
    channels = [c for c in channel_data.get('data', {}).keys()]
    if channel in channels:
        return channel
    else:
        res = process.extractOne(channel, channels)[0]
        _LOGGER.debug('No direct match found for %s. Resort to guesswork.'
                      'Guessed %s', channel, res)
        return res


async def async_get_channels(no_cache=False, refresh_interval=4):
    # TODO wstawić kod ze scraper.py
    '''
    Get channel list and corresponding urls
    '''
    # Check cache
    now = datetime.datetime.now()
    max_cache_age = datetime.timedelta(hours=refresh_interval)
    if not no_cache and 'channels' in _CACHE:
        cache = _CACHE.get('channels')
        cache_age = cache.get('last_updated')
        if now - cache_age < max_cache_age:
            _LOGGER.debug('Found channel list in cache.')
            return cache
        else:
            _LOGGER.debug('Found outdated channel list in cache. Update it.')
            _CACHE.pop('channels')
    soup = await _async_request_soup(BASE_URL + '/plan.html')
    # TODO wstawić kod ze scraper.py do base_url dodać nazwe kanału z channel.py
    channels = {}

    for li_item in soup.find_all('li'):
        try:
            child = li_item.findChild()
            if not child or child.name != 'a':
                continue
            href = child.get('href')
            if not href or not href.startswith('/programme/chaine'):
                continue
            channels[child.get('title')] = BASE_URL + href
        except Exception as exc:
            _LOGGER.error('Exception occured while fetching the channel '
                          'list: %s', exc)
    if channels:
        _CACHE['channels'] = {'last_updated': now, 'data': channels}
        return _CACHE['channels']


def resize_program_image(img_url, img_size=300):
    # TODO nie wiem po co to w teleman sa dwa rozmiary
    '''
    Resize a program's thumbnail to the desired dimension
    '''
    match = re.match(r'.+/(\d+)x(\d+)/.+', img_url)
    if not match:
        _LOGGER.warning('Could not compute current image resolution of %s',
                        img_url)
        return img_url
    res_x = int(match.group(1))
    res_y = int(match.group(2))
    # aspect_ratio = res_x / res_y
    target_res_y = int(img_size * res_y / res_x)
    return re.sub(
        r'{}x{}'.format(res_x, res_y),
        r'{}x{}'.format(img_size, target_res_y),
        img_url)


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
