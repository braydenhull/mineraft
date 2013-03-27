__author__ = 'brayden'

import urllib2
import json

class getServer():
    def getRecommendedBukkitInfo(self):
        request = urllib2.Request('http://dl.bukkit.org/api/1.0/downloads/projects/craftbukkit/artifacts/rb/?_accept=application%2Fjson')
        buildList = json.loads(urllib2.urlopen(request).read())
        return buildList
    def getBetaBukkitInfo(self):
        request = urllib2.Request('http://dl.bukkit.org/api/1.0/downloads/projects/craftbukkit/artifacts/beta/?_accept=application%2Fjson')
        buildList = json.loads(urllib2.urlopen(request).read())
        return buildList
    def getDevBukkitInfo(self):
        request = urllib2.Request('http://dl.bukkit.org/api/1.0/downloads/projects/craftbukkit/artifacts/dev/?_accept=application%2Fjson')
        buildList = json.loads(urllib2.urlopen(request).read())
        return buildList