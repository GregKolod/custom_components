#!/usr/bin/env python
# coding: utf-8


from collections import OrderedDict
import aiohttp
import asyncio
import json
import logging
import requests
import time

from .epg import async_get_current_program as async_get_cprg
from fuzzywuzzy import process

from .channels import CHANNELS
from .keys import KEYS

_LOGGER = logging.getLogger(__name__)

__version__ = '0.0.4'


class LiveboxPlayTv(object):
    def __init__(self, hostname, port, timeout=3, refresh_frequency=60):
        from datetime import timedelta
        self.hostname = hostname
        self.port = port
        self.timeout = timeout

        self._cache_channel_img = {}
        self.refresh_frequency = timedelta(seconds=refresh_frequency)

    async def async_update(self):
        _LOGGER.debug("Refresh Orange API data")
        _data = None
        self._osd_context = None
        self._channel_id = None

        _datalivebox = await self.async_rq(10)

        if _datalivebox:
            res = _datalivebox["result"]["data"]

        _LOGGER.debug("self.async_rq %s", res)
        self._media_type = res.get('playedMediaType')
        self._media_state = res.get('playedMediaState')
        self._osd_contex = res.get('osdContext')
        self._media_position = res.get('playedMediaPosition')
        self._epg_id = res.get('playedMediaId')
        self._standby_state = res.get('activeStandbyState')
        self._timeshift_state = res.get('timeShiftingState')
        self._mac_address = res.get('macAddress')
        self._name = res.get('friendlyName')
        self._wol_support = res.get('wol_support')

        pass

    @property
    def standby_state(self):
        # return self.info.get('activeStandbyState') == '0'
        return self._standby_state == '0'

    @property
    def channel(self):
        return self.get_current_channel_name()

    @property
    def channel_img(self):
        return self.get_current_channel_image()

    @channel.setter
    def channel(self, value):
        self.set_channel(value)

    @property
    def epg_id(self):
        # return self.info.get('playedMediaId')
        return self._epg_id

    @epg_id.setter
    def epg_id(self, value):
        self.set_epg_id(value)

    @property
    def program(self):
        return self.get_current_program_name()

    @property
    def program_img(self):
        return self.get_current_program_image()

    @property
    def osd_context(self):
        return self._osd_contex

    @property
    def media_state(self):
        return self._media_state

    @property
    def media_position(self):
        # return self.info.get('playedMediaPosition')
        return self._media_position

    @property
    def media_type(self):
        return self._media_type
        # return self.info.get('playedMediaType')

    @property
    def timeshift_state(self):
        # return self.info.get('timeShiftingState')
        return self._timeshift_state

    @property
    def mac_address(self):
        # return self.info.get('macAddress')
        return self._mac_address

    @property
    def name(self):
        # return self.info.get('friendlyName')
        return self._name

    @property
    def wol_support(self):
        # return self.info.get('wolSupport') == '0'
        return self._wol_support == '0'

    @property
    def is_on(self):
        return self.standby_state

    @property
    def info(self):
        return self.get_info()

    # TODO
    @staticmethod
    def discover():
        pass

    def rq(self, operation, params=None):
        url = 'http://{}:{}/remoteControl/cmd'.format(self.hostname, self.port)
        get_params = OrderedDict({'operation': operation})
        if params:
            get_params.update(params)
            _LOGGER.debug('GET parameters: %s', get_params)
        resp = requests.get(url, params=get_params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    async def async_rq(self, operation, params=None):
        url = 'http://{}:{}/remoteControl/cmd'.format(self.hostname, self.port)
        get_params = OrderedDict({'operation': operation})
        if params:
            get_params.update(params)
            _LOGGER.debug('GET parameters: %s', get_params)
        async with aiohttp.ClientSession() as session:
            resp = await session.get(url, params=get_params)
            text = await resp.json()
            return text

    async def async_get_info(self):
        return await self.async_update()

    def state(self):
        return self.standby_state

    def turn_on(self):
        if not self.standby_state:
            self.press_key(key=KEYS['POWER'])
            time.sleep(2)
            self.press_key(key=KEYS['OK'])

    def turn_off(self):
        if self.standby_state:
            return self.press_key(key=KEYS['POWER'])

    @asyncio.coroutine
    def async_get_current_program(self):

        if self.channel and self.channel != 'N/A':
            return (yield from async_get_cprg(self.channel))

    @asyncio.coroutine
    def async_get_current_program_name(self):
        res = yield from self.async_get_current_program()
        if res:
            return res.get('name')

    @asyncio.coroutine
    def async_get_current_program_image(self):

        res = yield from self.async_get_current_program()
        if res:
            return res.get('img')
            # return resize_program_image(res.get('img'), img_size)

    def get_current_channel(self):
        # epg_id = self.info.get('playedMediaId')
        epg_id = self._epg_id
        _LOGGER.debug('epg id %s', epg_id)
        return self.get_channel_from_epg_id(epg_id)

    def get_current_channel_name(self):
        channel = self.get_current_channel()
        if channel is None:
            return
        channel_name = channel['name']
        if channel_name == 'N/A':
            # Unable to determine current channel, let's try something else to
            # get a string representing what's on screen
            # http://forum.eedomus.com/viewtopic.php?f=50&t=2914&start=40#p36721
            osd = self.osd_context  # Avoid multiple lookups
            if osd == 'Catchup':
                return 'Catchup'
            elif osd == 'AdvPlayer':
                return 'Replay'

        return channel_name

    def get_current_channel_image(self):
        channel = self.channel
        if self.channel == 'N/A':
            return
        return self.get_channel_image(channel=channel)

    def get_channel_image(self, channel, skip_cache=False):
        """Get the logo for a channel"""

        if not channel:
            _LOGGER.error('Channel is not set. Could not retrieve image.')
            return

        # Check if the image is in cache
        if channel in self._cache_channel_img and not skip_cache:
            img = self._cache_channel_img[channel]
            _LOGGER.debug('Cache hit: %s -> %s', channel, img)
            return img

        try:
            img_src = None
            for i in CHANNELS:
                if i['name'] == channel:
                    img_src = i['logo']
                    img = 'https://klient.orange.pl/tv-pakiety/channels/{}-logo.png'.format(img_src)
                    # Cache result
                    self._cache_channel_img[channel] = img
                    _LOGGER.debug('livebox get logo  %s -> %s', channel, img)
                    return img

        except PageError:
            _LOGGER.error('Could not fetch channel image for %s', channel)

    def get_channels(self):
        return CHANNELS

    def __update(self):
        # obsolate
        _LOGGER.info('Refresh Orange API data')
        url = 'http://lsm-rendezvous040413.orange.fr/API/?output=json&withChannels=1'
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    def get_channel_names(self, json_output=False):
        channels = [x['name'] for x in CHANNELS]
        return json.dumps(channels) if json_output else channels

    def get_channel_info(self, channel):
        # If the channel start with '#' search by channel number
        channel_index = None
        if channel.startswith('#'):
            channel_index = channel.split('#')[1]
        # Look for an exact match first
        for chan in CHANNELS:
            if channel_index:
                if chan['index'] == channel_index:
                    return chan
            else:
                if chan['name'].lower() == channel.lower():
                    return chan
        # Try fuzzy matching it that did not give any result
        chan = process.extractOne(channel, CHANNELS)[0]
        return chan

    def get_channel_epg_id(self, channel):
        return self.get_channel_info(channel)['epg_id']

    def get_channel_from_epg_id(self, epg_id):
        res = [c for c in CHANNELS if c['epg_id'] == epg_id]
        return res[0] if res else None

    def set_epg_id(self, epg_id):
        # The EPG ID needs to be 10 chars long, padded with '*' chars
        epg_id_str = str(epg_id).rjust(10, '*')
        _LOGGER.info('Tune to %s',
                     self.get_channel_from_epg_id(epg_id)['name'])
        _LOGGER.debug('EPG ID string: %s', epg_id_str)

        url = 'http://{}:{}/remoteControl/cmd?operation=09&epg_id={}&uui=1'. \
            format(self.hostname, self.port, epg_id_str)
        resp = requests.get(url, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def set_channel(self, channel):
        epg_id = self.get_channel_epg_id(channel)
        return self.set_epg_id(epg_id)

    def __get_key_name(self, key_id):
        for key_name, k_id in KEYS.items():
            if k_id == key_id:
                return key_name

    def press_key(self, key, mode=0):
        '''
        modes:
            0 -> simple press
            1 -> long press
            2 -> release after long press
        '''
        if isinstance(key, str):
            assert key in KEYS, 'No such key: {}'.format(key)
            key = KEYS[key]
        _LOGGER.info('Press key %s', self.__get_key_name(key))
        return self.rq('01', OrderedDict([('key', key), ('mode', mode)]))

    def volume_up(self):
        return self.press_key(key=KEYS['VOL+'])

    def volume_down(self):
        return self.press_key(key=KEYS['VOL-'])

    def mute(self):
        return self.press_key(key=KEYS['MUTE'])

    def channel_up(self):
        return self.press_key(key=KEYS['CH+'])

    def channel_down(self):
        return self.press_key(key=KEYS['CH-'])

    def play_pause(self):
        return self.press_key(key=KEYS['PLAY/PAUSE'])

    def play(self):
        if self.media_state == 'PAUSE':
            return self.play_pause()
        _LOGGER.debug('Media is already playing.')

    def pause(self):
        if self.media_state == 'PLAY':
            return self.play_pause()
        _LOGGER.debug('Media is already paused.')

    def event_notify(self):

        url = 'http://{}:{}/remoteControl/notifyEvent'.format(self.hostname,
                                                              self.port)
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()
