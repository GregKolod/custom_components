#!/usr/bin/env python
# coding: utf-8

import logging
import urllib.request
import xml.etree.ElementTree as ET
import datetime
from pprint import pprint
import re

_CACHE = {}
_LOGGER = logging.getLogger(__name__)
BASE_URL = 'https://epg.ovh/pl.xml'

# tree = ET.parse('pl.xml')

# myroot = tree.getroot()
dataFormat = '%Y%m%d%H%M%S  %z'
today = datetime.date.today()
programs = []


def get_program_guide(channel):
    response = urllib.request.urlopen(BASE_URL).read()
    tree = ET.fromstring(response)

    for progDetails in tree.findall('programme'):
        if progDetails.attrib['channel'] == channel and \
                datetime.datetime.strptime(progDetails.attrib['start'], dataFormat).date() == today:

            name = progDetails.find('title').text.strip()

            try:
                summary = progDetails.find('desc').text.strip()
            except Exception:
                summary = ''

            try:
                img = progDetails.find('icon').attrib['src']
            except Exception:
                img = ''

            start_time = datetime.datetime.strptime(progDetails.attrib['start'], dataFormat).time()
            end_time = datetime.datetime.strptime(progDetails.attrib['stop'], dataFormat).time()

            latestType = len(progDetails.findall('category')) - 1

            type = progDetails.findall('category')[latestType].text.strip()

            try:
                epizod = progDetails.find('episode-num').text
                series = re.match(r'([Ss](\d+))?([Ee](\d+))?(\/(\d+))?', epizod)
                season = series.group(2)
                episode = series.group(4)

            except Exception:
                season = ''
                episode = ''

            programs.append(
                {'name': name, 'season': season, 'episode': episode, 'type': type, 'img': img, 'url': '',
                 'summary': summary, 'start_time': start_time,
                 'end_time': end_time})

            # print(start_time, end_time)
            # print(name)
            # print(type)
            # print(summary)
            # print(epizod)
            # print(img)
    now = datetime.datetime.now()
    if programs:
        if 'guide' not in _CACHE:
            _CACHE['guide'] = {}
        _CACHE['guide'][channel] = {'last_updated': now, 'data': programs}
    pprint(programs)
    return programs


get_program_guide("TVN")

for element in tree.findall('channel'):
    kanal = element.find('display-name').text
    icon = element.find('icon').attrib['src']
    print(kanal, icon)
