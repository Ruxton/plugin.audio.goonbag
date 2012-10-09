'''
    goonbag.com XBMC Plugin
    Copyright (C) 2011 Greg Tangey

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import xbmc, xbmcplugin, xbmcgui, xbmcaddon
from BeautifulSoup import BeautifulSoup
import urllib, urllib2, cgi
import re

# DEBUG
DEBUG = True

def log(description):
  if DEBUG:
    xbmc.log("[ADD-ON] '%s v%s': %s" % (__plugin__, __version__, description), xbmc.LOGNOTICE)

__addon__ = xbmcaddon.Addon()
__plugin__ = __addon__.getAddonInfo('name')
__version__ = __addon__.getAddonInfo('version')
__icon__ = __addon__.getAddonInfo('icon')
__language__ = __addon__.getLocalizedString

i18n = __language__

pluginUrl = sys.argv[0]
pluginHandle = int(sys.argv[1])
pluginQuery = sys.argv[2]

BASE_URL = 'http://www.goonbag.com'

STREAMS = [
    {
      "name": "live",
      "title": i18n(30003),
      "url": "http://gbr.goonhost.net:8000/",
      "thumb": "http://live.goonbag.com/images/01chan.jpg"
    },
    {
      "name": "aa247",
      "title": i18n(30004),
      "url": "http://gbr.goonhost.net:8002/",
      "thumb": "http://live.goonbag.com/images/01chan.jpg"
    },
    {
      "name": "classics",
      "title": i18n(30005),
      "url": "http://gbr.goonhost.net:8004/",
      "thumb": "http://live.goonbag.com/images/01chan.jpg"
    }
]

def stream_info(url):
  log('stream_info() Checking if '+url+' is up..')
  request = urllib2.Request(url)
  request.add_header('Icy-MetaData','1')
  opener = urllib2.build_opener()

  data=opener.open(request)
  headers=True
  resp={}

  log('stream_info() reading headers')
  while headers:
    line = data.readline()
    arr = line.split(':',1)
    if arr.__len__() > 1:
      resp[arr[0]]=arr[1].rstrip("\r\n")
      if arr[0] == "icy-metaint":
        interval = int(arr[1])

    if line=="\r\n":
      headers=False

  ## metadata read
  # data.read(interval)
  # len=ord(data.read(1))*16
  log('stream_info() returning '+str(resp))
  return resp

def add_stream(name, title, thumb, comment, stream_url):
    streamInfo = stream_info(stream_url)
    if streamInfo.has_key('icy-pub'):
      log('add_stream() stream '+name+' is online')
      title = title + " ("+i18n(30001)+")"
    else:
      log('add_stream() stream '+name+' is offline')
      title = title + " ("+i18n(30002)+")"

    listitem = xbmcgui.ListItem(title, iconImage=thumb, thumbnailImage=thumb)
    infoLabels = {'title': title, 'artist': i18n(30000), 'comment': comment}
    listitem.setInfo('music', infoLabels)
    url = pluginUrl + '?mode=play&stream_url=' + stream_url + '&thumb=' + thumb + '&title=' + title + '&name=' + name
    xbmcplugin.addDirectoryItem(pluginHandle, url, listitem, isFolder=False)


query = cgi.parse_qs(pluginQuery[1:])

for key, value in query.items():
    query[key] = value[0]
query['mode'] = query.get('mode', '')
if query['mode'] == 'play':
    listitem = xbmcgui.ListItem(query['name'], iconImage=query['thumb'], thumbnailImage=query['thumb'])
    infoLabels = {'title': query['title'], 'artist': i18n(30000), 'Size': 64}
    listitem.setInfo('music', infoLabels)
    app = query['stream_url']
    xbmc.Player().play(app, listitem)

else:
    for show in STREAMS:
        comment = ''
        stream_url = show['url']
        add_stream(show['name'], show['title'], show['thumb'], comment, stream_url)
    xbmcplugin.endOfDirectory(pluginHandle)