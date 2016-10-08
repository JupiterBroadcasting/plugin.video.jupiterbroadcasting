#!/usr/bin/env python
"""
Jupiter Broadcasting Kodi Addon
http://github.com/robloach/plugin.video.jupiterbroadcasting
"""

import sys, urllib, urllib2, re, xbmcplugin, xbmcgui, xbmcaddon, os
from BeautifulSoup import BeautifulStoneSoup

# local imports
import jb_shows

__settings__ = xbmcaddon.Addon(id='plugin.video.jupiterbroadcasting')
__language__ = __settings__.getLocalizedString

def categories(show_archived=False):
    """
    Load the available categories for Jupiter Broadcasting.
    """

    shows = {}
    # get shows
    if show_archived:
        shows = jb_shows.get_archived_shows()
    else:
        shows = jb_shows.get_active_shows()

    # translate shows
    shows = translate_shows(__language__, shows)
    sorted_shows = jb_shows.sort_shows(shows)


    quality = int(__settings__.getSetting("video_quality"))

    # Add the Live Stream if not showing archived shows
    if not show_archived:
        add_livestream()

    # Loop through each of the shows and add them as directories.
    iterator = 2
    for show in sorted_shows:
        item_name = show[0]
        data = show[1]

        # short circuit on archived shows
        if show_archived and not data['archived']:
            continue
        elif not show_archived and data['archived']:
            continue

        data['count'] = iterator
        iterator += 1

        # check if show is meta archive show
        if item_name == 'Archive':
            add_archive(item_name, data)
            continue


        # Check whether to use the high or low quality feed.
        feed = data['feed'] # High by default.
        if quality == 1:
            feed = data['feed-low']
        elif quality == 2:
            feed = data['feed-audio']
        data['image'] = __get_show_image_path(data)
        add_dir(item_name, feed, 1, data['image'], data)




def translate_shows(__language__, untranslated_shows):
    """
    Takes the raw show input and translates the name and plot
    """
    translated_shows = {}
    for show_name, data in untranslated_shows.items():
        data['plot'] = __language__(data['plot'])
        translated_shows[__language__(show_name)] = data

    return translated_shows


def index(name, url, page):
    """
    Presents a list of episodes within the given index page.
    """
    # Load the XML feed.
    data = urllib2.urlopen(url)

    # Parse the data with BeautifulStoneSoup, noting any self-closing tags.
    soup = BeautifulStoneSoup(
        data,
        convertEntities=BeautifulStoneSoup.XML_ENTITIES,
        selfClosingTags=['media:thumbnail', 'enclosure', 'media:content'])
    count = 1

    # Figure out where to start and where to stop the pagination.
    episodesperpage = int(float(__settings__.getSetting('episodes_per_page')))
    start = episodesperpage * int(page)
    currentindex = 0

    # Wrap in a try/catch to protect from broken RSS feeds.
    try:
        for item in soup.findAll('item'):
            # Set up the pagination properly.
            currentindex += 1
            if currentindex < start:
                # Skip this episode since it's before the page starts.
                continue
            if currentindex >= start + episodesperpage:
                # Add a go to next page link, and skip the rest of the loop.
                next_image = os.path.join(
                    __settings__.getAddonInfo('path'),
                    'resources',
                    'media',
                    'next.png')
                add_dir(
                    name=__language__(30300),
                    url=url,
                    mode=1,
                    iconimage=next_image,
                    info={},
                    page=page + 1)
                break

            # Load up the initial episode information.
            info = {}
            title = item.find('title')
            info['title'] = str(currentindex) + '. '
            if title:
                info['title'] += title.string
            info['tvshowtitle'] = name
            info['count'] = count
            count += 1 # Increment the show count.

            # Get the video enclosure.
            video = get_item_video(item, info)

            # Find the Date
            date = ''
            pubdate = item.find('pubDate')
            if pubdate != None:
                date = pubdate.string
                # strftime("%d.%m.%Y", item.updated_parsed)

            # Plot outline.
            summary = item.find('itunes:summary')
            if summary != None:
                info['plot'] = info['plotoutline'] = summary.string.strip()

            # Plot.
            get_item_description(item, info)

            # Author/Director.
            author = item.find('itunes:author')
            if author != None:
                info['director'] = author.string

            # Load the self-closing media:thumbnail data.
            thumbnail = ''
            mediathumbnail = item.findAll('media:thumbnail')
            if mediathumbnail:
                thumbnail = mediathumbnail[0]['url']
            elif name != __language__(30025) and name != __language__(30300):
                # Fall back to episode image
                shows = translate_shows(__language__, jb_shows.get_all_shows())
                thumbnail = __get_show_image_path(shows[name])

            # Add the episode link.
            add_link(info['title'], video, date, thumbnail, info)
    except:
        pass
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def add_livestream():
        livestream = int(__settings__.getSetting("live_stream"))
        live_url = ''
        if livestream == 0: # RTSP
            live_url = 'rtsp://jblive.videocdn.scaleengine.net/jb-live/play/jblive.stream'
        if livestream == 1: # RTMP
            live_url = 'rtmp://jblive.videocdn.scaleengine.net/jb-live/play/jblive.stream'
        elif livestream == 2: # HLS
            live_url = 'http://jblive.videocdn.scaleengine.net/jb-live/play/jblive.stream/playlist.m3u8'
        elif livestream == 3: # Audio
            live_url = 'http://jblive.fm'

        add_link(
            name=__language__(30010),
            url=live_url,
            date='',
            iconimage=os.path.join(
                __settings__.getAddonInfo('path'),
                'resources',
                'media',
                'jblive-tv.jpg'),
            info={
                'title': __language__(30010),
                'plot': __language__(30210),
                'genre': 'Technology',
                'count': 1
            }
        )

def add_archive(name, info):
    info['Title'] = name
    info['image'] = os.path.join(
        __settings__.getAddonInfo('path'), info['image'])
    uri = sys.argv[0] + '?url=' + urllib.quote_plus('archiveFolder') + '&mode=' + str(2)
    uri += '&name=' + urllib.quote_plus(name) + '&page=' + str(0)

    liz = xbmcgui.ListItem(name, iconImage=info['image'], thumbnailImage=info['image'])
    liz.setInfo(type='video', infoLabels=info)
    xbmcplugin.addDirectoryItem(
        handle=int(sys.argv[1]),
        url=uri,
        listitem=liz,
        isFolder=True)

def get_item_description(item, info):
    description = item.find('description')
    if description != None:
        # Attempt to strip the HTML tags.
        try:
            info['plot'] = re.sub(r'<[^>]*?>', '', description.string)
        except:
            info['plot'] = description.string

def get_item_video(item, info):
    enclosure = item.find('enclosure')
    if enclosure != None:
        video = enclosure.get('href')
        if video == None:
            video = enclosure.get('url')
        if video == None:
            video = ''
        size = enclosure.get('length')
        if size != None:
            info['size'] = int(size)
    return video

def get_params():
    """
    Retrieves the current existing parameters from XBMC.
    """
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if params[len(params)-1] == '/':
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param

# Info takes Plot, date, size
def add_link(name, url, date, iconimage, info):
    """
    Adds a link to XBMC's list of options.
    """
    liz = xbmcgui.ListItem(
        name,
        date,
        iconImage=iconimage,
        thumbnailImage=iconimage)
    liz.setProperty('IsPlayable', 'true')
    liz.setInfo(type='Video', infoLabels=info)
    return xbmcplugin.addDirectoryItem(
        handle=int(sys.argv[1]),
        url=url,
        listitem=liz,
        isFolder=False)

def add_dir(name, url, mode, iconimage, info, page=0):
    """
    Adds a directory item to XBMC's list of options.
    """
    uri = sys.argv[0] + '?url=' + urllib.quote_plus(url) + '&mode=' + str(mode)
    uri += '&name=' + urllib.quote_plus(name) + '&page=' + str(page)
    info['Title'] = name
    liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setInfo(type='video', infoLabels=info)
    return xbmcplugin.addDirectoryItem(
        handle=int(sys.argv[1]),
        url=uri,
        listitem=liz,
        isFolder=True)

def __get_show_image_path(data):
    """
    Returns os path for show image
    """
    image_path = os.path.join(
        __settings__.getAddonInfo('path'),
        'resources',
        'media',
        data['image'])

    return image_path

PARAMS = get_params()
URL = None
NAME = None
MODE = None
PAGE = None

try:
    URL = urllib.unquote_plus(PARAMS["url"])
except:
    pass
try:
    NAME = urllib.unquote_plus(PARAMS["name"])
except:
    pass
try:
    MODE = int(PARAMS["mode"])
except:
    pass
try:
    PAGE = int(PARAMS["page"])
except:
    PAGE = 0

if MODE == None or URL == None or len(URL) < 1:
    categories()
elif MODE == 1:
    index(NAME, URL, PAGE)
elif MODE == 2:
    categories(show_archived=True)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
