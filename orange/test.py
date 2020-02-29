#!/usr/bin/env python
# coding: utf-8
from channels import CHANNELS

img_src = None


def obraz(channel):
    for i in CHANNELS:
        if i['index'] == str(channel):
            img_src = i['logo']
        img = 'https://klient.orange.pl/tv-pakiety/channels/{}-logo.png'.format(img_src)
        print(img)


return

obraz(2)

# for i in CHANNELS:
#     if i['index'] == '10':
#         img_src = i['logo']
#         print(img_src)
#

#     img_src = i['logo']
#
#
#     img = 'https://klient.orange.pl/tv-pakiety/channels/{}-logo.png'.format(img_src)
#     print(i['name'], i['index'])
#
# print({'epg_id': '14117', 'index': '49', 'name': 'Nickelodeon', 'logo': '1489064592'}['logo'])
#
#
# print(CHANNELS[1])
