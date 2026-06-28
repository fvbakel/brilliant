#!/usr/bin/env python3

import sys
import time
import urllib.parse
from collections import deque
import re

import requests
from bs4 import BeautifulSoup

# ----------------------------------------------------------------------
# Configuratie
# ----------------------------------------------------------------------
TIMEOUT = 10               # seconden per request
SLEEP_BETWEEN_REQUESTS = 0.2  # korte pauze om de server niet te overbelasten
USER_AGENT = "Mozilla/5.0"


class ClubResult:

    def __init__(self,home_club_index, away_club_index:int,date:str,home:int,away:int):
        self.home_club_index =home_club_index
        self.away_club_index =away_club_index
        self.date = date
        self.home = home
        self.away = away

class Compitition:

    def __init__(self):
        self.clubs:list[str] = []
        self.day:str = ''
        self.level:int = 0
        self.results:list[ClubResult] = []

def fetch(url):
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, allow_redirects=True,
                                timeout=TIMEOUT, headers=headers, stream=True)
        return resp
    except requests.RequestException as e:
        return None, str(e)


def extract_data(html):
    compitition = Compitition()
    soup = BeautifulSoup(html, "html.parser")

    title = soup.find('meta', attrs={'property':r'og:title'})
    klasse_match = re.search(r'(Zondag|Zaterdag) (\d)e klasse',title['content'])
    compitition.day = klasse_match.groups()[0]
    compitition.level = klasse_match.groups()[1]
    
    table = soup.find('table', class_='matrix table table-sm table-striped')
    rows = table.select('table tr')

    dates = {}
    home_club_index = -1
    for row in rows:
        th_club = row.find('th', class_='club')
        td_dates = row.find_all('td', attrs={'data-date': True})

        if len(td_dates) > 0:
            club_text = th_club.get_text(strip=True)
            
            club_name = re.sub(r'^\d+\.\s*', '', club_text)
            compitition.clubs.append(club_name)
            home_club_index += 1 
            for index,td_date in enumerate(td_dates):
                if th_club and td_date:               
                    date_attr = td_date['data-date']
                    outcome = td_date.text
                    groups = re.findall(r'^(\d+) - (\d+)', outcome)
                    if len(groups) == 1:
                        home,away = groups[0]
                    
                    away_club_index = index
                    if away_club_index >= home_club_index:
                        away_club_index += 1
                    date = dates[date_attr]
                    print(f"{club_name},{date},{outcome},{home},{away}")
                    compitition.results.append(ClubResult(home_club_index,away_club_index,date,home,away))
        else:
            td_dates = th_club.find_all('option')
            for td_date in td_dates:
                if td_date['value'] != '':
                    dates[td_date['value']] = td_date.text

    return compitition

def write_results(compitition:Compitition):
    file_name = "output.csv"
    with open(file_name, 'w') as file:
        for result in compitition.results:
            home_club =compitition.clubs[result.home_club_index]
            away_club = compitition.clubs[result.away_club_index]
            file.write(f"{compitition.day},{compitition.level},{home_club},{away_club},{result.date},{result.home},{result.away}\n")

def save_url(html):
    file_name = "data_sample.html"

    with open(file_name, 'w') as file:
        file.write(html)

def read_from_file():
    file_name = "data_sample.html"
    with open(file_name, 'r') as file:
        file_content = file.read()
    return file_content


def main():
    url = 'https://www.hollandsevelden.nl/competities/2025-2026/zuid-1/zo/5a/'
    # html = fetch(url)
    #htm_text = html.text
    # save_url(html_text)
    html_text = read_from_file()
    compitition = extract_data(html_text)
    write_results(compitition)

    


if __name__ == "__main__":
    main()