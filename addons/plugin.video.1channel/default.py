#1channel Plugin
import sys,urllib,urllib2,urlparse,re,base64
import xbmcgui, xbmcplugin, xbmcaddon, urlresolver
from BeautifulSoup import BeautifulSoup, SoupStrainer

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
try:
    from urlparse import parse_qs
except ImportError:
    #python 2.4 compatibility
    from cgi import parse_qs
    urlparse.parse_qs = parse_qs
args = urlparse.parse_qs(sys.argv[2][1:])

#PLUGIN CONSTANTS
plugin_id = 'plugin.video.1channel'
addon = xbmcaddon.Addon(id=plugin_id)

#COMMON PLUGIN FUNCTIONS
#subfolder url link
def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

#chrome web browser act a like
useragent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36'

def getURL(url):
        print '>>>>>1channel Plugin :: getURL :: url = '+url
        try:
            req = urllib2.Request(url)
            req.add_header('User-Agent', useragent)
            response = urllib2.urlopen(req)
            link=response.read()
            response.close()
        except urllib2.HTTPError, error:
            print 'Error reason: ', error
            return error.read()
        else:
            return link

mode = args.get('mode', None)
 
if mode is None:
    url = build_url({'mode': 'movies', 'foldername': 'Movies'})
    li = xbmcgui.ListItem('Movies', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    url = build_url({'mode': 'tv', 'foldername': 'TV'})
    li = xbmcgui.ListItem('TV', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'movies':
    url = build_url({'mode': 'search', 'foldername': 'Search for Movie', 'vidtype': 'movie'})
    li = xbmcgui.ListItem('Search for Movie', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    url = ''
    li = xbmcgui.ListItem('[COLOR yellow]>>>>>>>>>>Featured Movies<<<<<<<<<<[/COLOR]')
    li.setThumbnailImage('none')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    featuredmoviesurl = 'http://www.primewire.ag/index.php?sort=featured'
    data = getURL(featuredmoviesurl)
    strainer = SoupStrainer(attrs={'class':'index_container'})
    container = BeautifulSoup(data, parseOnlyThese=strainer)
    for movie in container.findAll(attrs={'class':'index_item index_item_ie'}):
        name = movie.a['title'].replace('Watch ','') 
        movieurl = 'http://www.primewire.ag' + movie.a['href']
        thumb = 'http:' + movie.a.img['src']
        url = build_url({'mode': 'streams', 'foldername': name.encode('ascii', 'ignore'), 'url': movieurl})
        li = xbmcgui.ListItem(name, iconImage='DefaultFolder.png')
        li.setThumbnailImage(thumb)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'tv':
    url = build_url({'mode': 'search', 'foldername': 'Search for TV Show', 'vidtype': 'tv'})
    li = xbmcgui.ListItem('Search for TV Show', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    url = ''
    li = xbmcgui.ListItem('[COLOR yellow]>>>>>>>>>>Featured TV Shows<<<<<<<<<<[/COLOR]')
    li.setThumbnailImage('none')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    featuredtvurl = 'http://www.primewire.ag/?tv=&sort=featured'
    data = getURL(featuredtvurl)
    strainer = SoupStrainer(attrs={'class':'index_container'})
    container = BeautifulSoup(data, parseOnlyThese=strainer)
    for tvshow in container.findAll(attrs={'class':'index_item index_item_ie'}):
        name = tvshow.a['title'].replace('Watch ','') 
        showurl = 'http://www.primewire.ag' + tvshow.a['href']
        thumb = 'http:' + tvshow.a.img['src']
        url = build_url({'mode': 'episodes', 'foldername': name.encode('ascii', 'ignore'), 'url': showurl})
        li = xbmcgui.ListItem(name, iconImage='DefaultFolder.png')
        li.setThumbnailImage(thumb)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'search':
    search = ''
    vidtype = args['vidtype'][0]
    keyboard = xbmc.Keyboard(search, '1channel Search')
    keyboard.doModal()
    if keyboard.isConfirmed():
        search = urllib.quote_plus(keyboard.getText())
        url = 'http://www.primewire.ag/index.php?search_keywords=' + search
        data = getURL(url)
        strainer = SoupStrainer(attrs={'class':'index_container'})
        container = BeautifulSoup(data, parseOnlyThese=strainer)
        for item in container.findAll(attrs={'class':'index_item index_item_ie'}):
            name = item.a['title'].replace('Watch ','') 
            vidurl = 'http://www.primewire.ag' + item.a['href']
            thumb = 'http:' + item.a.img['src']
            if vidtype == 'movie':
                vidmode = 'streams'
            else:
                vidmode = 'episodes'
            url = build_url({'mode': vidmode, 'foldername': name.encode('ascii', 'ignore'), 'url': vidurl})
            li = xbmcgui.ListItem(name, iconImage='DefaultFolder.png')
            li.setThumbnailImage(thumb)
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'episodes':
    showurl = args['url'][0]
    data = getURL(showurl)
    strainer = SoupStrainer(attrs={'class':'tv_container'})
    container = BeautifulSoup(data, parseOnlyThese=strainer)
    for season in container.findAll(attrs={'class':'show_season'}):
        seasonnumber = season['data-id']
        name = 'Season ' + seasonnumber
        url = ''
        li = xbmcgui.ListItem('[COLOR yellow]' + name + '[/COLOR]')
        li.setThumbnailImage('none')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

        for episode in season.findAll('div'):
            episodename = episode.a.contents[0] + episode.a.span.contents[0]
            episodeurl = 'http://www.primewire.ag' + episode.a['href']
            url = build_url({'mode': 'streams', 'foldername': episodename.encode('ascii', 'ignore'), 'url': episodeurl})
            li = xbmcgui.ListItem(episodename, iconImage='DefaultFolder.png')
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'streams':
    videopage = args['url'][0]
    data = getURL(videopage)
    soup = BeautifulSoup(data)
    for video in soup.findAll(href=re.compile("^/external.php")):
        try:
            name = video['title']
            videourl = video['href']
            encodeddomain = re.compile('domain=(.+?)&logged').findall(videourl)
            domain = base64.b64decode(encodeddomain[0])
            fullname = name + '  [' + domain + ']'
            url = build_url({'mode': 'play', 'foldername': fullname, 'url': videourl})
            li = xbmcgui.ListItem(fullname, iconImage='DefaultVideo.png')
            li.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
        except:
            pass
    
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'play':
    videourl = args['url'][0]
    encodedurl = re.compile('url=(.+?)&domain').findall(videourl)
    url = urlresolver.resolve(base64.b64decode(encodedurl[0]))
    listitem = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
