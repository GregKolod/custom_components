# import voluptuous as vol
# import homeassistant.helpers.config_validation as cv
# from homeassistant.components.sensor import (PLATFORM_SCHEMA)
# from homeassistant.helpers.entity import async_generate_entity_id

from homeassistant.helpers.entity import Entity

import datetime
import logging
from urllib.request import urlopen
from bs4 import BeautifulSoup

__version__ = '0.1'

_LOGGER = logging.getLogger(__name__)

today = datetime.date.today()
_CACHE = {}

BASE_URL = 'https://wnet.fm/ramowka/'


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    add_entities([WnetEpg()])


class WnetEpg(Entity):
    """The class for this sensor"""

    def __init__(self):
        self._state = None

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def name(self):
        """Return the name of the sensor"""
        return 'Wnet EPG'

    @property
    def icon(self):
        """Return the icon of the sensor"""
        return 'mdi:radio'

    def update(self):
        self._state = get_current_program()


def request_soup(url):
    '''
    Perform a GET web request and return a bs4 parser
    '''
    text = urlopen(url)
    return BeautifulSoup(text, 'html.parser')


def get_weekdays():
    soup = request_soup(BASE_URL)
    week_day = []
    days = soup.find('div', class_='entry-content').find_all('h2')
    current_day = datetime.datetime.today().weekday()
    try:
        week_day = days[current_day].find('a')['href']
    except Exception as exc:
        _LOGGER.error('Exception occured while fetching the weekdays list: %s', exc)
    # print(week_day)
    return week_day


def get_program_guide():
    """
    Get the program data for a day
    """
    url = get_weekdays()
    soup = request_soup(url)

    programs = []
    content = soup.find('div', class_='entry-content').find_all('h4')

    for prg_item in range(len(content)):
        try:
            prog_start_tmp, prog_name = content[prg_item].text.strip().split(' – ', 1)
            if prog_start_tmp.find(':') == -1:
                prog_start_tmp += ':00'

            prog_start = datetime.datetime.combine(today, datetime.datetime.strptime(prog_start_tmp, '%H:%M').time())

            try:
                prog_end_tmp = content[prg_item + 1].text.strip().split(' – ', 1)[0]

                if prog_end_tmp.find(':') == -1:
                    prog_end_tmp += ':00'

                prog_end = datetime.datetime.combine(today, datetime.datetime.strptime(prog_end_tmp, '%H:%M').time())

            except Exception:

                prog_end = prog_start + datetime.timedelta(hours=2)
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
    return programs


def get_current_program(no_cache=False):
    """
    Get the current program info
    """
    guide = get_program_guide()
    now = datetime.datetime.now()

    for prog in guide:
        start = prog.get('start_time')
        end = prog.get('end_time')
        if start < now < end:
            _LOGGER.debug('program name', prog['name'])
            print(prog)
            return prog['name']
    prog = 'brak programu'
    return prog
