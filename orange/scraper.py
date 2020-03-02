from urllib.request import urlopen
from bs4 import BeautifulSoup
import datetime

BASE_URL = 'https://www.teleman.pl/program-tv/stacje/'

# pobiera dane o akulanym programie ze strony www.teleman.pl

def channel_scrapper(channel):
    page = urlopen(BASE_URL + channel)
   # page = urlopen(quote_page)
    soup = BeautifulSoup(page, 'html.parser')

    ul_tag = soup.find('ul', attrs={'class': 'stationItems'}).find_all('li')
    channel_list = []
    prog_start = ul_tag[0].find('em').text
    # godzina startu programu - [0] bo pierwszy z listy bierzemy

    prog_end = ul_tag[1].find('em').text
    # godzina zakończenie programu - [1] bo drugi listy bierzemy
    #TODO - zrobić sprawdzenia co robić jak nie można odnaleźć godziny + 2h

    title = ul_tag[0].find('div', attrs={'class': 'detail'}).find('a').text
    # tytuł programu

    prog_img = ul_tag[0].find('img')['src']
    # obraz programu - jak usunąc crop-100x63  to będzie full obraz

    chanLogo = soup.find('div', attrs={'class': 'stationTitle'}).find('img')['src']
    # logo kanału
    
    prog_genre = ul_tag[0].find('p', attrs={'class': 'genre'}).text
    #program typ
    
    
    print('Aktualny program', title)
    print(prog_start, prog_end)
  


    #print(title.find('a')['href'])
    # link do programu

    print(prog_img)

    print(chanLogo)
    # czas trwania programu - zamieniem na time, bo muszę wyrugowac date, a potem znowu na datetime żeby policzyc różnice
    start= (datetime.datetime.strptime(prog_start,'%H:%M')).time()
    stop = datetime.datetime.strptime(prog_end,'%H:%M')
    # dodaje godzine bo otrzymuje niewałaściwą
    teraz = (datetime.datetime.now()  + datetime.timedelta(hours=1))
    # tu znowu zmiana na datetime
    #TODO do spardzenie i jak bedzie z programem po północy?
    startd= datetime.datetime.combine(datetime.date.today(), start)
 
    progress = (teraz -  startd)

    print(progress.strftime('%H:%M'))

    return channel_list


# shows = channel_scrapper('https://www.teleman.pl/program-tv/stacje/TVP-1')
shows = channel_scrapper('TVP-1')
