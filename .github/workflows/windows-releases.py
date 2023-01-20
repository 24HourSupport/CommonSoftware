from urllib.request import urlopen
import json
from datetime import datetime
import time
url = "https://endoflife.date/api/windows.json"
response = urlopen(url)
list_of_releases = list()
data_json = json.loads(response.read())
for release in data_json:
    if ('(w)' in release['cycle'].lower()) or (('(e)' not in release['cycle'].lower()) and ('lts' not in release['cycle'].lower()) and ('iot' not in release['cycle'].lower())):
        list_of_releases.append(release)
releases = {'consumer' : {'11':[],'10':[]}} 
# We don't care about anything earlier than Windows 10, as those users are told to fuck off in AutoDDU.
# Reason for the consumer dict is because I plan on adding LTSC/Server handling in the future. 
for majorrelease in releases['consumer']:
    list_of_minor_releases = {}
    for minorrelease in list_of_releases:
        if minorrelease['cycle'][:len(majorrelease)] == majorrelease:
            # Reason the item is a list is so we can easily add stuff to it in the future without breaking compatibility with AutoDDU.
            list_of_minor_releases[minorrelease['buildID'][minorrelease['buildID'].rfind('.')+1:]] = [time.mktime(datetime.strptime(minorrelease['releaseDate'], '%Y-%m-%d').timetuple())]
    
    list_of_minor_releases = dict(sorted(list_of_minor_releases.items(), reverse=True))
    releases['consumer'][majorrelease] = list_of_minor_releases

# This just concerns validation, I don't wanna have a bad day in the future
# this at least protects against obvious issues

# As of January 20 2023 all these releases should be present, if any isn't we assume something went wrong. 
known_valid_releases = {'consumer': {'11': {'22621': [1663646400.0], '22000': [1633320000.0]}, '10': {'19045': [1666065600.0], '19044': [1637038800.0], '19043': [1621310400.0], '19042': [1603166400.0], '19041': [1590552000.0], '18363': [1573534800.0], '18362': [1567051200.0], '17763': [1542085200.0], '17134': [1525060800.0], '16299': [1508212800.0], '15063': [1491883200.0], '14393': [1470110400.0], '10586': [1447131600.0], '10240': [1438142400.0]}}}

for known_consumer_release in known_valid_releases['consumer']:
    for known_minor_release in known_valid_releases['consumer'][known_consumer_release]:
        if int(known_valid_releases['consumer'][known_consumer_release][known_minor_release][0]) not in list( range(int(releases['consumer'][known_consumer_release][known_minor_release][0])-4233600,int(releases['consumer'][known_consumer_release][known_minor_release][0])+4233600)):
            raise Exception('Something changed dates beyond a week??')

# Makes sure nothing happens like a release is more than 48 hours in the future

for known_consumer_release in releases['consumer']:
    for known_minor_release in releases['consumer'][known_consumer_release]:
        # 2014 to current day plus 48 hours
        if releases['consumer'][known_consumer_release][known_minor_release][0] not in list( range(1390243593,int(time.time()))):
            raise Exception('We got a release before Windows 10 was released or more than 48 hours in the future')
import os
if os.path.exists("WindowsReleases_v2.json"):
  os.remove("WindowsReleases_v2.json")
with open('WindowsReleases_v2.json', 'w') as fp:
    json.dump(releases, fp)
