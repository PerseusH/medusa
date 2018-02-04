#! /usr/bin/env python
# encoding=utf-8


import requests
import time
import random
import json
from bs4 import BeautifulSoup


today = time.strftime('%Y-%m-%d', time.localtime())
GAMES_URL = 'https://www.zhibo8.cc/nba/json/%s.htm?key=%s' % (today, str(random.random()))


class NBAGames():
    def __init__(self):
        self.i = 0
        self.games = self.game_list()
        self.count = len(self.games)


    def __iter__(self):
        return self


    def next(self):
        if  self.i == self.count - 1:
            raise StopIteration
        else:
            self.i += 1
            return self.games[self.i]


    def parse_html(self, html):
        soup = BeautifulSoup(html, 'lxml')
        return soup
    
    
    def game_info(self, gid):
        ginfo = {}
    
        ginfo_url = 'https://news.zhibo8.cc/nba/%s/%s.htm' % (today, gid)
        gifo_soup = self.parse_html(self.download(ginfo_url).content)
        ginfo['title'] = gifo_soup.find('div', attrs={'class': 'title'}).h1.getText()
        ginfo['home_team'] = gifo_soup.find('div', attrs={'class': 'content'}).find_all('p')[3].getText()
        ginfo['visit_team'] = gifo_soup.find('div', attrs={'class': 'content'}).find_all('p')[4].getText()
    
        score_url = 'https://bifen4pc.qiumibao.com/json/%s/%s.htm' % (today, gid)
        score = self.download(score_url).json()
        sinfo = '%s %s:%s %s' % (
                score['home_team'],
                score['home_score'],
                score['visit_score'],
                score['visit_team']
                )
        ginfo['score'] = sinfo
    
        return ginfo
    
    
    def game_list(self):
        response = self.download(GAMES_URL).json()
        games = filter(lambda i: i['title'].startswith('NBA常规赛'), response['video_arr'])

        return [self.game_info(game['saishiid']) for game in games]


    def download(self, url):
        return requests.get(url)
    
    
def ec(s):
    return s.encode('utf-8')    


if __name__ == '__main__':
    for ginfo in Games():
        print ec(ginfo['title'])
        print ec(ginfo['score'])
        print ec(ginfo['brief1'])
        print ec(ginfo['brief2'])
        print '---------------------------------------------------------------------------------------'
