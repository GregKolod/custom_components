from urllib.request import urlopen
from bs4 import BeautifulSoup


def channel_scrapper(quote_page):
    page = urlopen(quote_page)
    soup = BeautifulSoup(page, 'html.parser')

    ul_tag = soup.find('ul', attrs={'class': 'stationItems'}).find_all('li')
    channel_list = []
    prgStart = ul_tag[0].find('em')
    # godzina startu programu - [0] bo pierwszy z listy bierzemy

    prgStop = ul_tag[1].find('em')
    # godzina zakończenie programu - [1] bo drugi listy bierzemy

    title = ul_tag[0].find('div', attrs={'class': 'detail'})
    # tytuł programu

    imgPrg = ul_tag[0].find('img')['src']
    # obraz programu - jak usunąc crop-100x63  to będzie full obraz

    chanLogo = soup.find('div', attrs={'class': 'stationTitle'}).find('img')['src']
    # logo kanału

    print(prgStart.text)
    print(prgStop.text)
    print(title.find('a').text)

    print(title.find('a')['href'])
    # link do programu

    print(imgPrg)

    print(chanLogo)

    return channel_list


shows = channel_scrapper('https://www.teleman.pl/program-tv/stacje/TVP-1')
