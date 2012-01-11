import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmcaddon
from time import strftime
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup

__settings__ = xbmcaddon.Addon(id='plugin.video.jupiterbroadcasting')
__language__ = __settings__.getLocalizedString

def CATEGORIES():
    # List all the shows.
    shows = {}
    shows[__language__(30006)] = {
        'feed': 'http://feeds2.feedburner.com/AllJupiterVideos?format=xml',
        'image': 'http://images2.wikia.nocookie.net/__cb20110118004527/jupiterbroadcasting/images/2/24/JupiterBadgeGeneric.jpg',
        'plot': __language__(30013),
        'genre': 'Technology'
    }
    shows[__language__(30000)] = {
        'feed': 'http://feeds.feedburner.com/computeractionshowvideo?format=xml',
        'image': 'http://www.jupiterbroadcasting.com/images/LAS-VIDEO.jpg',
        'plot': 'The Linux Action Show covers the latest news in free and open source software, especially Linux.',
        'genre': 'Technology'
    }
    shows[__language__(30001)] = {
        'feed': 'http://feeds2.feedburner.com/jupiterbeeristasty-hd?format=xml',
        'image': 'http://www.jupiterbroadcasting.com/images/beeristasty/BeerisTasty-iTunesBadgeHD.png',
        'plot': 'Finding interesting combinations of food and beer.',
        'genre': 'Technology'
    }
    shows[__language__(30002)] = {
        'feed': 'http://feeds.feedburner.com/stokedhd?format=xml',
        'image': 'http://www.jupiterbroadcasting.com/images/STOked-BadgeHD.png',
        'plot': 'All the news about Star Trek Online you would ever need.',
        'genre': 'Technology'
    }
    shows[__language__(30003)] = {
        'feed': 'http://feeds.feedburner.com/lotsovideo?format=xml',
        'image': 'http://www.jupiterbroadcasting.com/images/LOTSOiTunesVideo144.jpg',
        'plot': 'Video games, reviews and coverage.',
        'genre': 'Technology'
    }
    shows[__language__(30004)] = {
        'feed': 'http://feeds.feedburner.com/jupiternitehd?format=xml',
        'image': 'http://www.jupiterbroadcasting.com/images/JANBADGE-LVID.jpg',
        'plot': 'Jupiter Broadcasting hooliganisms covered in front of a live audience on the intertubes.',
        'genre': 'Technology'
    }
    shows[__language__(30005)] = {
        'feed': 'http://feeds.feedburner.com/ldf-video?format=xml',
        'image': 'http://www.jupiterbroadcasting.com/images/LDF-FullStill144x139.jpg',
        'plot': 'Bryan takes a peek into alien life.',
        'genre': 'Technology'
    }
    shows[__language__(30007)] = {
        'feed': 'http://feeds.feedburner.com/MMOrgueHD?format=xml',
        'image': 'http://www.jupiterbroadcasting.com/images/MMOrgueBadgeHD144.jpg',
        'plot': 'The MMOrgue is a show presented by Jeremy about Massively Multiplayer Online (MMO) games.',
        'genre': 'Technology'
    }
    shows[__language__(30008)] = {
        'feed': 'http://feeds.feedburner.com/techsnaphd?format=xml',
        'image': 'http://images3.wikia.nocookie.net/jupiterbroadcasting/images/d/d6/Techsnapcenter.jpg',
        'plot': 'TechSNAP is a show about technology news hosted by Chris Fisher and Allan Jude which records live on Thursdays and is released on the following Monday.',
        'genre': 'Technology'
    }
    shows[__language__(30009)] = {
        'feed': 'http://feeds.feedburner.com/scibytehd?format=xml',
        'image': 'http://www.jupiterbroadcasting.com/images/SciByteBadgeHD.jpg',
        'plot': 'SciByte is a show about science topics presented by Heather and Jeremy.',
        'genre': 'Science'
    }
    shows[__language__(30011)] = {
        'feed': 'http://blip.tv/fauxshow/rss/itunes',
        'image': 'http://a.images.blip.tv/FauxShow-300x300_show_image205.png',
        'plot': 'The FauxShow is not a real show, but a social experience. Unlike most of the shows on the network, the FauxShow has no defined subject and the topic varies week to week.',
        'genre': 'Humour'
    }

    # Add Jupiter Broadcasting Live via the RTMP stream
    addLink(__language__(30010), 'rtsp://videocdn-us.geocdn.scaleengine.net/jblive/jblive.stream', '', 'http://images2.wikia.nocookie.net/__cb20110118004527/jupiterbroadcasting/images/2/24/JupiterBadgeGeneric.jpg', {
      'title': __language__(30010),
      'plot': __language__(30012),
      'genre': 'Technology',
      'count': 1
    })

    # Loop through each of the shows and add them as directories.
    x = 2
    for name, data in shows.iteritems():
        data['count'] = x
        x = x + 1
        addDir(name, data['feed'], 1, data['image'], data)

def INDEX(name, url):
    data = urllib2.urlopen(url)
    soup = BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.XML_ENTITIES)
    count = 1
    # Wrap in a try/catch to protect from borken RSS feeds.
    try:
        for item in soup.findAll('item'):
            # Load up the initial episode information.
            info = {}
            title = item.find('title')
            info['title'] = str(count) + '. '
            if (title):
                info['title'] += title.string
            info['tvshowtitle'] = name
            info['count'] = count
            count += 1 # Increment the show count.

            # Get the video enclosure.
            video = ''
            enclosure = item.find('enclosure')
            if (enclosure != None):
                video = enclosure.get('href')
                if (video == None):
                    video = enclosure.get('url')
                if (video == None):
                    video = ''
                size = enclosure.get('length')
                if (size != None):
                    info['size'] = int(size)

            # TODO: Parse the date correctly.
            date = ''
            pubdate = item.find('pubDate')
            if (pubdate != None):
                date = pubdate.string
                # strftime("%d.%m.%Y", item.updated_parsed)

            # Plot outline.
            summary = item.find('itunes:summary')
            if (summary != None):
                info['plot'] = info['plotoutline'] = summary.string.strip()

            # Plot.
            description = item.find('description')
            if (description != None):
                # Attempt to strip the HTML tags.
                try:
                    info['plot'] = re.sub(r'<[^>]*?>', '', description.string)
                except:
                    info['plot'] = description.string

            # Author/Director.
            author = item.find('itunes:author')
            if (author != None):
                info['director'] = author.string

            # TODO: Get the thumbnails to load correctly.
            thumbnail = ''
            mediathumbnail = item.findAll('media:thumbnail')
            for thumb in mediathumbnail:
                thumbnail = thumb.get('url')
                if (thumbnail == None):
                    thumbnail = ''
                else:
                    break

            # Add the episode link.
            addLink(info['title'], video, date, thumbnail, info)
    except:
       pass

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

# Info takes Plot, date, size
def addLink(name, url, date, iconimage, info):
        ok=True
        liz=xbmcgui.ListItem(name, date, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setInfo( type="video", infoLabels=info )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addDir(name, url, mode, iconimage, info):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True
    info["Title"] = name
    liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels=info)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

params=get_params()
url=None
name=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

if mode==None or url==None or len(url)<1:
        print ""
        CATEGORIES()

elif mode==1:
        print ""+url
        INDEX(name, url)


xbmcplugin.endOfDirectory(int(sys.argv[1]))
