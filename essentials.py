__author__ = 'brayden'

import sys
import urllib2
import json

class Essentials():
    def getInfo(self, version):
        teamCityBuildIds = {'Release': 'bt3', 'Pre-Release': 'bt9', 'Development': 'bt2', 'GroupManager': 'bt10'} # I can get this sort of info manually but it'd take some hacky URL parsing and is liable to break so I feel this is better
        # The compiled list of everything that should be needed for Essentials. this is quite a lot of info though but I don't want to have to call this function more than once
        # Build artifacts is unfilled as I don't know why I put it there
        essInfo = {'buildVersions': {'id': [],'version': []}, 'buildArtifacts': [], 'buildType': teamCityBuildIds[version]}
        try:
            buildTypeId = teamCityBuildIds[version]
            print buildTypeId
        except IndexError:
            print("Version string given is not known.")
            sys.exit(1)
        request = urllib2.Request('http://ess.ementalo.com/guestAuth/app/rest/buildTypes/id:' + buildTypeId + '/builds', headers={"Accept": "application/json"})
        buildList = json.loads(urllib2.urlopen(request).read())
        print buildList
        print "Versions available: "
        for build in buildList['build']:
            print(build)
            print("Essentials stable " + build['number'] + " is available.")
            essInfo['buildVersions']['version'].append(build['number'])
            essInfo['buildVersions']['id'].append(build['id'])
        return essInfo

    def getDownload(self, buildTypeId, buildId, edition):
        if edition ==  'Extra':
            fileName = 'Essentials-extra.zip'
        elif edition == 'Full':
            fileName = 'Essentials-full.zip'
        elif edition == 'Core':
            fileName = 'Essentials.zip'
        elif edition == 'GroupManager':
            fileName = 'Essentials-gm.zip'
        else:
            print "Edition was not valid, options are: Extra, Full, Core or GroupManager."
            print "Setting Edition to Core as a contingency"
            fileName = 'Essentials.zip'
        url = 'http://ess.ementalo.com/repository/download/' + buildTypeId + '/' + str(buildId) + ':id/' + fileName + '?guest=1' # If you don't do ?guest=1 it'll not work properly!
        return url, fileName