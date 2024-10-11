#!/usr/bin/python
import xbmc
import xbmcplugin
import xbmcgui
import json
from datetime import datetime
from infotagger.listitem import ListItemInfoTag
import time
# from random import choice

JSON_MAP = {
    'episode_properties': [
        'title',
        'playcount',
        'season',
        'episode',
        'showtitle',
        'originaltitle',
        'plot',
        'votes',
        'file',
        'rating',
        'ratings',
        'userrating',
        'resume',
        'tvshowid',
        'firstaired',
        'art',
        'streamdetails',
        'runtime',
        'director',
        'writer',
        'cast',
        'dateadded',
        'lastplayed'
    ],

    'tvshow_properties': [
        'title',
        'studio',
        'year',
        'plot',
        'cast',
        'rating',
        'ratings',
        'userrating',
        'votes',
        'genre',
        'episode',
        'season',
        'runtime',
        'mpaa',
        'premiered',
        'playcount',
        'lastplayed',
        'sorttitle',
        'originaltitle',
        'art',
        'tag',
        'dateadded',
        'imdbnumber'
    ]
}

def logjson(msg):
    xbmc.log(msg=json.dumps(msg, sort_keys=True, indent=4, separators=(',', ': ')), level=xbmc.LOGINFO)

def logtext(msg):
    xbmc.log(msg=msg, level=xbmc.LOGINFO)

def getPath(li):
    return li['file']

def isFolder(li):
    return li['isFolder']

def set_plugincontent(id, content=None,category=None):
    if category:
        xbmcplugin.setPluginCategory(id, category)
    if content:
        xbmcplugin.setContent(id, content)

def buildListItem(iteminfo):
    watchedepisodes = iteminfo.pop('watchedepisodes', '')
    art = iteminfo.pop('art', '')
    cast = iteminfo.pop('cast', '')
    label = iteminfo.pop('label', '')

    if 'tvshowid' in iteminfo:
        isFolder = True
        iteminfo['mediatype'] = 'tvshow'
        iteminfo['dbid'] = iteminfo.pop('tvshowid', '')
        iteminfo['path'] = 'videodb://tvshows/titles/%s/' % iteminfo['dbid']
    if 'episodeid' in iteminfo:
        isFolder = False
        iteminfo['mediatype'] = 'episode'
        iteminfo['path'] = iteminfo.pop('file', '')
        iteminfo['premiered'] = iteminfo.pop('firstaired', '')
        iteminfo['dbid'] = iteminfo.pop('episodeid', '')
        iteminfo['tvshowtitle'] = iteminfo.pop('showtitle', '')

    streamdetails = iteminfo.pop('streamdetails', '')
    ratings = iteminfo.pop('ratings', '')
    resume = iteminfo.pop('resume', None)
    runtime = iteminfo.pop('runtime', '')

    li = xbmcgui.ListItem(label=label, path=iteminfo['path'], offscreen=True)
    li.setIsFolder(isFolder)
    li.setArt(art)

    info_tag = ListItemInfoTag(li, 'video')
    info_tag.set_info(iteminfo)
    info_tag.set_cast(cast)
    if resume is not None:
        info_tag._info_tag.setResumePoint(resume['position'],resume['total'])
    info_tag.set_stream_details(streamdetails)

    return li

def finalizeList(id, items, category=None, content=None):
    xbmcplugin.addDirectoryItems(id, [(item.getPath(), item, item.isFolder()) for item in items if item])
    xbmcplugin.endOfDirectory(handle=id)

    set_plugincontent(id, category=category, content=content)


def get_date(date_time):
    # Hack for broken embedded python
    # https://forum.kodi.tv/showthread.php?tid=112916
    # https://bugs.python.org/issue27400
    try:
        date_time_obj = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
    except TypeError:
        date_time_obj = datetime(*(time.strptime(date_time, '%Y-%m-%d %H:%M:%S')[0:6]))
    date_obj = date_time_obj.date()

    return str(date_obj)

def json_call(method, properties=None, sort=None, query_filter=None, limit=None, params=None, item=None, options=None, limits=None):
    json_string = {'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': {}}

    if properties is not None:
        json_string['params']['properties'] = properties

    if limit is not None:
        json_string['params']['limits'] = {'start': 0, 'end': int(limit)}

    if sort is not None:
        json_string['params']['sort'] = sort

    if query_filter is not None:
        json_string['params']['filter'] = query_filter

    if options is not None:
        json_string['params']['options'] = options

    if limits is not None:
        json_string['params']['limits'] = limits

    if item is not None:
        json_string['params']['item'] = item

    if params is not None:
        json_string['params'].update(params)

    jsonrpc_call = json.dumps(json_string)
    result = xbmc.executeJSONRPC(jsonrpc_call)
    result = json.loads(result)

    return result
