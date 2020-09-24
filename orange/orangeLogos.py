#!/usr/bin/env python
# coding: utf-8
### scraper selenium orange

### Get tv logos id from Orange website

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import csv

chrome_options = Options()
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(options=chrome_options)

driver.get("https://www.orange.pl/view/pakiety-orange-tv")

# driver.find_element_by_id('rozwin_button').click()
# rozwiniecie listy wszystkich kanałów

channels = driver.find_elements_by_xpath('//*[@id="Container"]/li')

with open('orangeLogo.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csvLogo = csv.writer(csvfile, dialect='excel')

    for channel in range(1, len(channels) + 1):
        wwwLink = driver.find_element_by_xpath('//*[@id="Container"]/li[' + str(channel) + ']/div/span/img')
        logoId = wwwLink.get_attribute('src').split('/')[-1].split('-')[0]
        channelName = wwwLink.get_attribute('alt').strip()
        csvLogo.writerow([channel, channelName, logoId])

driver.close()
