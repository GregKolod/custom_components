#!/usr/bin/env python
# coding: utf-8

from bs4 import BeautifulSoup
import aiohttp
import datetime
import asyncio
import logging

_CACHE = {}
_LOGGER = logging.getLogger(__name__)
BASE_URL = 'https://wnet.fm/ramowka/'

today = datetime.date.today()


async def _async_request_soup(url):
    '''
    Perform a GET web request and return a bs4 parser
    '''

    _LOGGER.debug('GET %s', url)

    async with aiohttp.ClientSession() as session:
        resp = await session.get(url)
        text = await resp.text()
        return BeautifulSoup(text, 'html.parser')


async def async_get_weekdays():
    soup = await _async_request_soup(BASE_URL)
    week_day = []
    days = soup.find('div', class_='entry-content').find_all('h2')
    current_day = datetime.datetime.today().weekday()

    try:
        week_day = days[current_day].find('a')['href']

    except Exception as exc:
        _LOGGER.error('Exception occured while fetching the weekdays list: %s', exc)

    return week_day


async def async_get_program_guide():
    """
    Get the program data for a day
    """
    url = await async_get_weekdays()
    soup = await _async_request_soup(url)

    programs = []
    content = soup.find('div', class_='entry-content').find_all('h4')

    for prg_item in range(len(content)):
        try:
            prog_start_tmp, prog_name = content[prg_item].text.strip().split(' – ')
            if prog_start_tmp.find(':') == -1:
                prog_start_tmp += ':00'

            # prog_start = datetime.datetime.strptime(prog_start_tmp, '%H:%M')

            prog_start = datetime.datetime.combine(today, datetime.datetime.strptime(prog_start_tmp, '%H:%M').time())

            try:
                prog_end_tmp = content[prg_item + 1].text.strip().split(' – ')[0]

                if prog_end_tmp.find(':') == -1:
                    prog_end_tmp += ':00'

                # prog_end = datetime.datetime.strptime(prog_end_tmp, '%H:%M')

                prog_end = datetime.datetime.combine(today, datetime.datetime.strptime(prog_end_tmp, '%H:%M').time())

            except Exception:

                prog_end_tmp = prog_start + datetime.timedelta(hours=2)
                _LOGGER.debug('Exception occured while fetching the program end')

            programs.append(
                {'name': prog_name, 'start_time': prog_start, 'end_time': prog_end})



        except Exception as exc:
            _LOGGER.error('Exception occured while fetching the program guide for channel %s', exc)
            import traceback

            traceback.print_exc()

    now = datetime.datetime.now()

    if programs:
        if 'guide' not in _CACHE:
            _CACHE['guide'] = {}
        _CACHE['guide'] = {'last_updated': now, 'data': programs}
    # print(programs)
    return programs


def get_current_program(no_cache=False):
    """
    Get the current program info
    """

    guide = get_program_guide()

    # print('async_get_current_program guide ', guide)

    now = datetime.datetime.now()
    for prog in guide:
        start = prog.get('start_time')
        # print('start', start)
        end = prog.get('end_time')
        if start < now < end:
            print(prog['name'])
            return prog


def _request_soup(*args, **kwargs):
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(_async_request_soup(*args, **kwargs))
    return res


def get_weekdays():
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(async_get_weekdays())
    # print(res)
    return res


def get_program_guide():
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(async_get_program_guide())
    # print(res)
    return res


# print (datetime.datetime.today().weekday())
# get_weekdays()
# get_program_guide()

get_current_program()
