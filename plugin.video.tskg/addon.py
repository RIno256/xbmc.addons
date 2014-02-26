# -*- coding: utf-8 -*-
import os
import urllib
import urllib2
import re
import sys
import json

import xbmcaddon
from xbmcswift2 import Plugin

__addon__ = xbmcaddon.Addon(id='plugin.video.tskg')
sys.path.append(
    os.path.join(__addon__.getAddonInfo('path'), 'resources', 'lib'))

plugin = Plugin()

useragent = "|User-Agent=Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3"
nodetmp = "/tmp/node"


def getEpisode(episode):
    query_args = {'action': 'getEpisodeJSON', 'episode': episode}
    data = urllib.urlencode(query_args)
    request = urllib2.Request('http://www.ts.kg/ajax', data)
    response = urllib2.urlopen(request)
    episode_data = json.loads(response.read())
    return episode_data['file']


def GetHTML(url):
    headers = {'User-Agent': useragent, 'Content-Type':
               'application/x-www-form-urlencoded'}
    conn = urllib2.urlopen(urllib2.Request(url, urllib.urlencode({}), headers))
    html = conn.read()
    conn.close()
    return html


@plugin.route('/')
def index():
    serials_category = [
        # {'label': 'Новинки', 'path': plugin.url_for('show_new', new='new')},
        {'label': 'Зарубежные сериалы (открытые)', 'path': plugin.url_for(
            'show_serial', category='serials')},
        {'label': 'Зарубежные сериалы (закрытые)', 'path': plugin.url_for(
            'show_serial', category='closed')},
        {'label': 'Британские', 'path':
            plugin.url_for('show_serial', category='UK')},
        {'label': 'Корейские', 'path':
            plugin.url_for('show_serial', category='kor')},
        {'label': 'Российские', 'path':
            plugin.url_for('show_serial', category='russerials')},
        {'label': 'Аниме на русском', 'path':
            plugin.url_for('show_serial', category='anime')},
        {'label': 'Аниме на японском', 'path':
            plugin.url_for('show_serial', category='animej')},
        {'label': 'Мультсериалы', 'path':
            plugin.url_for('show_serial', category='mults')},
        {'label': 'Для детей', 'path':
            plugin.url_for('show_serial', category='kids')},
        {'label': 'Зарубежные ТВ-шоу', 'path':
            plugin.url_for('show_serial', category='tvshows')},
        {'label': 'Российские ТВ-шоу', 'path':
            plugin.url_for('show_serial', category='rushows')},
        {'label': '5 канал - Документальные', 'path':
            plugin.url_for('show_serial', category='5doc')},
        {'label': '5 канал - Развлекательные', 'path':
            plugin.url_for('show_serial', category='rushows')},
    ]
    return serials_category


# @plugin.route('/service/<new>/')
# def show_new(new):
#     newseries = GetHTML('http://www.ts.kg/')
#     rawseries_urls = re.compile(
#         'a href="(.+?)" class="blink"').findall(newseries)
#     series_labels = re.compile('rel="tooltip">(.+?)</a></td>').findall(
#         newseries)
#     newseries_urls = []
#     for rawseries_url in rawseries_urls:
#         if rawseries_url.find('ts.kg') > -1:
#             newseries_urls.append(rawseries_url)

#     counter = 0;
#     newseries_items = []
#     for newseries_url in newseries_urls:
#         if newseries_url[-1].isdigit():
#             fixed_url = getEpisode + useragent
#         else:
#             fixed_url = getEpisode + useragent
#         newseries_items.append(
#             {'label': series_labels[counter], 'path': fixed_url, 'is_playable': True, })
#         counter += 1
#     return newseries_items


@plugin.route('/<category>/')
def show_serial(category):
    url = "http://www.ts.kg/%s/" % category
    serials = GetHTML(url)
    genre_links = re.compile(
        'a href="(.+?)"><img src="(.+?)" title="(.+?)" alt="(.+?)"/><span class="caption">').findall(serials)
    serials_items = []
    for serial, img, title, alt in genre_links:
        serials_items.append(
            {'label': title, 'path': plugin.url_for('show_seasons', serial=serial), 'thumbnail': img})
    return serials_items


@plugin.route('/category/<serial>/')
def show_seasons(serial):
    seasons = GetHTML(serial)
    img = re.compile(
        '<img class="serial_cover" src="(.+?)"').findall(seasons)[0]
    seasons_numbers = re.compile(
        '<ul class="breadcrumb" id="season-(.+?)">').findall(seasons)
    seasons_items = []
    for season in seasons_numbers:
        label = 'Сезон %s' % season
        seasons_items.append(
            {'label': label, 'path': plugin.url_for('show_series', serial=serial, season=season), 'thumbnail': img})
    return seasons_items


@plugin.route('/category/<serial>/<season>/')
def show_series(serial, season):
    series = GetHTML(serial)
    img = re.compile(
        '<img class="serial_cover" src="(.+?)"').findall(series)[0]
    regx = '<ul class="breadcrumb" id="season-%s">(.+?)</ul>' % season
    season_html = re.compile(regx, re.DOTALL).findall(series)[0]
    series_list = re.compile(
        '<a class="episode_link"(.+?)episode="(.+?)">(.+?)</a>').findall(season_html)
    series_items = []
    for tmp, episode, series_number in series_list:
        fixed_url = getEpisode(episode)
        series_items.append(
            {'label': 'Эпизод ' + series_number, 'path': fixed_url, 'is_playable': True, 'thumbnail': img})
    return series_items

if __name__ == '__main__':
    plugin.run()
