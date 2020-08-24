#!/usr/bin/env python
# coding: utf-8

from bs4 import BeautifulSoup
import aiohttp
import datetime
import asyncio
import logging

_CACHE = {}
_LOGGER = logging.getLogger(__name__)
BASE_URL = 'https://programtv.onet.pl'


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
    '''
    Check whether the current channel is correct. If not try to determine it
    using fuzzywuzzy
    '''
    from fuzzywuzzy import process
    channel_data = await async_get_channels()
    # print('async_determine_channel channel_data ', channel_data)

    # print(len(channel_data['data']))

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
        # print('async_determine_channel res', channel, res)
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

    soup = await _async_request_soup(BASE_URL + '/stacje')
    channels = {}
    tv_station = soup.find('ul', class_='channelList').find_all('li')

    for station in range(len(tv_station)):
        try:
            href = tv_station[station].find('a')['href']
            tvStationName = tv_station[station].find('a')['title']
            # print('nazwa_stacji', tvStationName)
            channels[tvStationName] = BASE_URL + href
            # print(station, ' nazwa_stacji channels', channels[tvStationName])

        except Exception as exc:
            _LOGGER.error('Exception occured while fetching the channel '
                          'list: %s', exc)
    if channels:
        _CACHE['channels'] = {'last_updated': now, 'data': channels}

        return _CACHE['channels']



def get_current_program_progress(program):
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


async def async_get_program_guide(channel, no_cache=False, refresh_interval=4):
    """
    Get the program data for a channel
    """
    # print('async_get_program_guide channel', channel)

    chan = await async_determine_channel(channel)

    # print('#async_get_program_guide chan', chan)

    now = datetime.datetime.now()
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

    ul_tag = soup.find('div', class_='emissions').find('ul').find_all('li')

    """ What the date today from EPG"""
    today_str = soup.find('div', class_='emissions').find('span', class_='date').find('span').text.strip()
    today = datetime.datetime.strptime(today_str, '%Y-%m-%d').date()

    # ul_tag2 = soup.find('div', class_='emissions').find('ul').find_all('li')
    #
    # print(ul_tag2[10].get_text())
    # print('------')
    # print(ul_tag2[10].name)
    # print(ul_tag2[10].attrs)
    # print('------')
    # print(ul_tag2[10].find(attrs={'class': ['hh07', 'fltrSerie']}))
    # print(ul_tag2[10].find_previous('li', class_=['hh07', 'fltrSerie']))

    for prg_item in range(len(ul_tag)):

        try:
            prog_name = ul_tag[prg_item].find('a').text.strip()
            # nazwa programu
            # print('prog_name' ,prog_name)

            prog_url = BASE_URL[:26] + ul_tag[prg_item].find('a')['href']

            # print('prog_url' , prog_url)

            if not prog_url:
                _LOGGER.warning('Failed to retrieve the detail URL for program %s. '
                                'The summary will be empty', prog_name)
            try:
                prog_type = ul_tag[prg_item].find('span', class_='type').text.strip()
                # print('prog_type', prog_type)

            except Exception:
                prog_type = ''
                # print('prog_type e', prog_type)
                # dla zakończenia programy nie ma typu programu
                _LOGGER.debug('Exception occured while fetching the program genre')

            try:
                prog_summary = ul_tag[prg_item].find('div', class_='titles').find('p').text.strip()
                # print('prog_summary ', prog_summary)

            except Exception:
                prog_summary = ''
                # print('prog_summary  e', prog_summary)
                _LOGGER.debug('Exception occured while fetching the program summary')

            start_time = (
                datetime.datetime.strptime(ul_tag[prg_item].find('span', class_='hour').text.strip(), '%H:%M'))
            # print('start_time' , start_time)

            try:

                stop_time = (datetime.datetime.strptime(
                    ul_tag[prg_item + 1].find('span', class_='hour').text.strip(), '%H:%M'))
                # print('stop_time', stop_time)

            except Exception:

                stop_time = start_time + datetime.timedelta(hours=2)
                _LOGGER.debug('Exception occured while fetching the program end')

            prog_start = datetime.datetime.combine(today, start_time.time())
            # print('prog_start', prog_start)

            """ is it next day?"""
            if start_time > stop_time:
                # print('nowa doba')
                today += datetime.timedelta(days=1)

            prog_end = datetime.datetime.combine(today, stop_time.time())
            # print('prog_end', prog_end)

            # obrazki są na stronie programu i trzeba jeszcze jedną soup
            try:

                url_soup = await _async_request_soup(prog_url)
                prog_img = 'http:' + url_soup.find('img', attrs={'class': 'lazyImg'})['data-original']
                if prog_img == 'http://ocdn.eu/program-tv-transforms/1/LCFktlEYWRtL2IzNzk5OGMwYTExODlhNWNmYzA4ZWY5OTQwNTllNTQ4N2Q3N2U2Y2RkMWVlMTIxMGU4NTRmYjdiYzllNmNmNjKRlQLNASwAwsM':
                    prog_img = ''
                    # print('Onet fake '+prog_img)
                    _LOGGER.debug('Fake ONET image')


            except Exception:
                prog_img = ''
                _LOGGER.debug('No channel image')

            # print(prog_img)
            # print(programs)
            programs.append(
                {'name': prog_name, 'type': prog_type, 'img': prog_img,
                 'url': prog_url, 'summary': prog_summary, 'start_time': prog_start,
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


async def async_get_current_program(channel, no_cache=False):
    """
    Get the current program info
    """
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
    # print('get_channels res', len(res['data']))
    # print('get_channels res', len(res['data']), res)

    return res


def get_program_guide(*args, **kwargs):
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(async_get_program_guide(*args, **kwargs))
    # print('get_program_guide res', res)
    print(res)
    # for key in range(len(res)):
    return res


def get_current_program(*args, **kwargs):
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(async_get_current_program(*args, **kwargs))
    #
    # print(res['name'])

    return res


get_program_guide('tvn')
# get_current_program('tvn')

# get_current_program_summary('tvn')
