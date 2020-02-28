#!/usr/bin/env python
# coding: utf-8
from channels import CHANNELS

img_src = None
for i in CHANNELS:
    img_src = i['logo']

    img = 'https://klient.orange.pl/tv-pakiety/channels/{}-logo.png'.format(img_src)
    print(i['name'], img)
