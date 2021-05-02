from homeassistant.helpers.entity import Entity

import datetime
import logging
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

__version__ = '0.1'

_LOGGER = logging.getLogger(__name__)

today = datetime.date.today()

_CACHE = {}

SCAN_INTERVAL = datetime.timedelta(seconds=60)

# BASE_URL = 'http://krakow.pios.gov.pl/stan-srodowiska/komunikat-pylkowy/'
BASE_URL = 'http://www.ptzca.pl/index.php?option=com_ptzca_pylki'


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    add_entities([Alergie()])


class Alergie(Entity):
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
        return 'Alergie'

    @property
    def icon(self):
        """Return the icon of the sensor"""
        return 'mdi:radio'

    def update(self):
        _LOGGER.debug('update zrobiony')
        self._state = get_current_message()


def request_soup(url):
    '''
    Perform a GET web request and return a bs4 parser
    '''
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    text = urlopen(req)
    return BeautifulSoup(text, 'html.parser')


def get_message_date():
    """
    Get the message date
    """
    soup = request_soup(BASE_URL)
    message_date = soup.find('div', id='data').text
    return message_date


def get_message():
    """
    Get the program data for a day
    """
    soup = request_soup(BASE_URL)
    message = soup.find('div', id='tekst').text
    return message


def get_details():
    """
    Get the taksons details
    """
    details = []
    soup = request_soup(BASE_URL)
    taksons = soup.find('div', id='tabela').find_all('div', class_='wiersz')

    for i in range(len(taksons)):
        takson = taksons[i].find('div', class_='takson').text
        wartosc = taksons[i].find('div', class_='wartosc').text
        prognoza = taksons[i].find('div', class_='tekst').text.strip()
        details.append({'takson': takson, 'wartosc': wartosc, 'prognoza': prognoza})

    return details




