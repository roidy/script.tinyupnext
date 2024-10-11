#!/usr/bin/python

import xbmcplugin
import xbmcgui
import xbmcaddon
import urllib.parse as urlparse
from helpers import *
import sys

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')



class Main:
    def __init__(self):
        self.li = list()
        self.flist = list()

        self.id = int(sys.argv[1])

        self.sort_lastplayed = {'order': 'descending', 'method': 'lastplayed'}
        self.sort_playcount = {'order': 'ascending', 'method': 'playcount'}

        path = sys.argv[2]
        try:
            args = path[1:]
            self.params = dict(urlparse.parse_qsl(args))
        except Exception:
            self.params = {}

        self.info = self.params.get('info', '')
        if self.info:
            if self.info.lower() == 'inprogress':
                self.inprogress()
        else:
            self.listing()

    def listing(self):
        # Inprogress TV
        list_item = xbmcgui.ListItem(label="Inprogress TV", offscreen=True)
        info_tag = ListItemInfoTag(list_item, 'video')
        info_tag.set_info({'title': 'Inprogress TV', 'mediatype': 'video'})
        list_item.setArt({'icon': 'DefaultFolder.png',
                         'thumb': 'DefaultFolder.png'})
        self.li.append(("plugin://script.tinyupnext/?info=inprogress", list_item, True))

        set_plugincontent(self.id, content='videos')
        xbmcplugin.addDirectoryItems(self.id, self.li)
        xbmcplugin.endOfDirectory(handle=self.id)

    #
    # Next episode or inprogress
    #
    def inprogress(self):
        # Get Inprogress shows
        json_query = json_call('VideoLibrary.GetInprogressTVShows',
                            properties=JSON_MAP['tvshow_properties'],
                            sort=self.sort_lastplayed
                            )
        try:
            json_query = json_query['result']['tvshows']
        except Exception:
            pass
        else:
            for show in json_query:
                # Get next episode
                json_query = json_call('VideoLibrary.GetEpisodes',
                                    properties=JSON_MAP['episode_properties'],
                                    sort=self.sort_playcount,
                                    params={'tvshowid': int(
                                        show['tvshowid'])},
                                    limit='1'
                                    )

                try:
                    episode = json_query['result']['episodes'][0]
                    episode['lastplayed'] = show['lastplayed']
                    episode['studio'] = show['studio']
                    episode['genre'] = show['genre']
                    episode['mpaa'] = show['mpaa']
                    episode['mediatype'] = 'episode'
                    self.li.append(episode)
                except Exception:
                    pass

        self.li.sort(key=lambda item: item['lastplayed'], reverse=True)

        for item in self.li:
            li = buildListItem(item)
            self.flist.append(li)

        finalizeList(id=self.id, items=self.flist,
                     category='inprogress', content='mixed')

if __name__ == '__main__':
    Main()
