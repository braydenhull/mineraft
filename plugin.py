__author__ = 'brayden'

import feedparser
import urllib2
from bs4 import BeautifulSoup
import re

TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)

class getPlugin():
    def getGenericBukkitDevPluginInfo(self, pluginUrl):
        print "got this far!"
        returnInfoDict = {'versions': {'title': [], 'description': [], 'link': []}}
        feed = feedparser.parse(pluginUrl + 'files.rss')
        for entry in feed['entries']:
            returnInfoDict['versions']['title'].append(entry['title'])
            returnInfoDict['versions']['description'].append(remove_tags(entry['summary_detail']['value']))
            returnInfoDict['versions']['link'].append(entry['links'][0]['href'])
        # generate exception so I get memory footprint
        #doesnotexist[1]
        return returnInfoDict
    def getGenericBukkitDevPluginDownloadInformation(self, url):
        returnInfoDict = {'download': '', 'MD5': '', 'supportedCraftBukkit': []}
        request = urllib2.Request(url)
        webpage = BeautifulSoup(urllib2.urlopen(request).read())
        for link in webpage.find_all('a', href=re.compile('^http://dev.bukkit.org/media/files/')):
            returnInfoDict['download'] = link.get('href')
            break
        returnInfoDict['MD5'] = webpage.find("dt",text="MD5").findNextSiblings("dd")[0].string
        for tagContent in webpage.find('ul',{"class": "comma-separated-list"}).find_all('li'):
            returnInfoDict['supportedCraftBukkit'].append(tagContent.string)
        return returnInfoDict