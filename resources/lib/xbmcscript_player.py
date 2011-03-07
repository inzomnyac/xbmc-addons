__script__ = "Cinema Experience"
__scriptID__ = "script.cinema.experience"
###########################################################
"""
    Video Playlist Module:
    - Assembles Video Playlist based on user settings
    - When playlist complete, calls xbmcscript_trivia.py to perform trivia and start playlist
"""
############################################################
# main imports
import sys
import os
import xbmcgui
import xbmc
import xbmcaddon
import traceback, threading, re

_A_ = xbmcaddon.Addon( __scriptID__ )
# language method
_L_ = _A_.getLocalizedString
# settings method
_S_ = _A_.getSetting


# set proper message
message = 32520

#pDialog = xbmcgui.DialogProgress()
#pDialog.create( __script__, _L_( message )  )
#pDialog.update( 0 )

from urllib import quote_plus
from random import shuffle, random

log_sep = "-"*70

BASE_CACHE_PATH = os.path.join( xbmc.translatePath( "special://profile" ), "Thumbnails", "Video" )
BASE_CURRENT_SOURCE_PATH = os.path.join( xbmc.translatePath( "special://profile/addon_data/" ), os.path.basename( _A_.getAddonInfo('path') ) )
BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( _A_.getAddonInfo('path'), 'resources' ) )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

from ce_playlist import _get_special_items
from ce_playlist import _get_queued_video_info

def _get_trailers( items, mpaa, genre, movie ):
    # return if not user preference
    if ( not items ):
        return []
    # trailer settings, grab them here so we don't need another _S_() object
    settings = { "trailer_amt_db_file":  xbmc.translatePath( _S_( "trailer_amt_db_file" ) ),
                      "trailer_folder":  xbmc.translatePath( _S_( "trailer_folder" ) ),
                      "trailer_rating": _S_( "trailer_rating" ),
                 "trailer_limit_query": _S_( "trailer_limit_query" ) == "true",
                   "trailer_play_mode": int( _S_( "trailer_play_mode" ) ),
                     "trailer_hd_only": _S_( "trailer_hd_only" ) == "true",
                     "trailer_quality": int( _S_( "trailer_quality" ) ),
              "trailer_unwatched_only": _S_( "trailer_unwatched_only" ) == "true",
                 "trailer_newest_only": _S_( "trailer_newest_only" ) == "true",
                       "trailer_count": ( 0, 1, 2, 3, 4, 5, 10, )[ int( _S_( "trailer_count" ) ) ],
                     "trailer_scraper": ( "amt_database", "amt_current", "local", )[ int( _S_( "trailer_scraper" ) ) ]
               }
    # get the correct scraper
    exec "from resources.scrapers.%s import scraper as scraper" % ( settings[ "trailer_scraper" ], )
    Scraper = scraper.Main( mpaa, genre, settings, movie )
    # fetch trailers
    trailers = Scraper.fetch_trailers()
    # return results
    return trailers

    
class Main:
    # base paths
    
        
    def __init__( self ):
        self._play_mode = _S_( "trailer_play_mode" )
        self.number_of_features = int( _S_( "number_of_features") ) + 1
        self.playlistsize = xbmc.PlayList(xbmc.PLAYLIST_VIDEO).size()
        self._check_trailers()
        self._start()
        _A_.setSetting( id='trailer_play_mode', value='%d' % int( self._play_mode ) )
    
    def _check_trailers( self ):
        if int( _S_( "trailer_play_mode" ) ) == 1:
            path = os.path.join( BASE_CURRENT_SOURCE_PATH, "downloaded_trailers.txt" )
            if ( xbmc.executehttpapi( "FileExists(%s)" % ( path, ) ) == "<li>True" ):
                xbmc.log( "[script.cinema.experience] - File Exists: downloaded_trailers.txt", xbmc.LOGNOTICE )
                trailer_list = self._load_trailer_list()
                print "trailer_list"
                print trailer_list
                if trailer_list:
                    for trailer in trailer_list:
                        trailer_detail = self._load_trailer_nfo( trailer )
                        self.downloaded_trailers += trailer_detail
                else:
                    xbmc.log( "[script.cinema.experience] - Empty File: downloaded_trailers.txt", xbmc.LOGNOTICE )
                    _A_.setSetting( id='trailer_play_mode', value='%d' % 0 )
            else:
                xbmc.log( "[script.cinema.experience] - File Does Not Exists: downloaded_trailers.txt", xbmc.LOGNOTICE )
                _A_.setSetting( id='trailer_play_mode', value='%d' % 0 )
        else:
            pass
    
    def _load_trailer_list( self ):
        xbmc.log( "[script.cinema.experience] - Loading Downloaded Trailer List", xbmc.LOGNOTICE)
        try:
            # set base watched file path
            base_path = os.path.join( BASE_CURRENT_SOURCE_PATH, "downloaded_trailers.txt" )
            # open path
            usock = open( base_path, "r" )
            # read source
            trailer_list = eval( usock.read() )
            # close socket
            usock.close()
        except:
            trailer_list = []
        return trailer_list
    
    def _load_trailer_nfo( self, path ):
        '''
            id=trailer[ 0 ]
            path=trailer[ 2 ],
            genre=trailer[ 9 ],
            title=trailer[ 1 ],
            thumbnail=trailer[ 3 ],
            plot=trailer[ 4 ],
            runtime=trailer[ 5 ],
            mpaa=trailer[ 6 ],
            release_date=trailer[ 7 ],
            studio=trailer[ 8 ],
            director=trailer[ 11 ]
        '''
        try:
            path = os.path.splitext()[0] + ".nfo"
            print "path"
            print path
            usock = open( path, "r" )
            # read source
            xmlSource =  usock.read()
            # close socket
            usock.close()
        except:
            xmlSource = ""
        xmlSource = xmlSource.replace("\n    ","")
        # if only 
        xmlSource = xmlSource.replace('<movieinfo>','<movieinfo id="0">')
        # gather all trailer records <movieinfo>
        trailer = re.findall( '<movieinfo id="(.*?)"><title>(.*?)</title><quality>(.*?)</quality><runtime>(.*?)</runtime><releasedate>(.*?)</releasedate><mpaa>(.*?)</mpaa><genre>(.*?)</genre><studio>(.*?)</studio><director>(.*?)</director><cast>(.*?)</cast><plot>(.*?)</plot><thumb>(.*?)</thumb>', xmlSource )
        print "xmlSource"
        print xmlSource
        print "trailer"
        print trailer
        if not trailer:
            for item in trailer:
                new_trailer += item
        else:
            new_trailer=[]
        return new_trailer
        
    def _start( self ):
        try:
            # create the playlist
            self.playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
            # Check to see if multiple features have been set in settings
            # if multiple features is greater than 1(not a single feature) 
            # add the intermission videos and audio files for the 2, third, etc movies
            if self.playlistsize > 1:
                movie_titles = ""
                for feature_count in range (1, self.playlistsize + 1):
                    movie_title = self.playlist[ feature_count - 1 ].getdescription()
                    xbmc.log( "[script.cinema.experience] - Feature #%-2d - %s" % ( feature_count, movie_title ), xbmc.LOGNOTICE )
                    movie_titles = movie_titles + movie_title + "<li>"
                movie_titles = movie_titles.rstrip("<li>")
                if _S_( "voxcommando" ) == "true":
                    xbmc.executehttpapi( "Broadcast(<b>CElaunch." + str(self.playlistsize ) + "<li>" + movie_titles + "</b>;33000)" )             
                if ( int( _S_( "intermission_video") ) > 0 or _S_( "intermission_audio") or _S_( "intermission_ratings") ):
                    mpaa, audio, genre, movie = self._add_intermission_videos()
            # otherwise just build for a single video
            else:
                # get the queued video info
                movie_title = self.playlist[ 0 ].getdescription()
                if _S_( "voxcommando" ) == "true":
                    xbmc.executehttpapi( "Broadcast(<b>CElaunch<li>" + movie_title + "</b>;33000)" )
                xbmc.log( "[script.cinema.experience] - Feature - %s" % movie_title, xbmc.LOGNOTICE )
                mpaa, audio, genre, movie = _get_queued_video_info()
            self._create_playlist( mpaa, audio, genre, movie)
            # play the trivia slide show
        except:
            traceback.print_exc()
             
    def _add_intermission_videos( self ):
        xbmc.log( "[script.cinema.experience] - Adding intermission Video(s)", xbmc.LOGNOTICE )
        count = 0
        index_count = 1
        for feature in range( 1, self.playlistsize ):
            mpaa, audio, genre, movie = _get_queued_video_info( index_count )
            #count = index_count
            # add intermission video
            if ( int( _S_( "intermission_video") ) > 0 ):
                xbmc.log( "[script.cinema.experience] - Inserting intermission Video(s): %s" % _S_( "intermission_video" ), xbmc.LOGNOTICE )
                xbmc.log( "[script.cinema.experience] -     playlist Position: %d" % index_count, xbmc.LOGNOTICE )
                p_size = xbmc.PlayList(xbmc.PLAYLIST_VIDEO).size()
                xbmc.log( "[script.cinema.experience] -     p_size: %d" % p_size, xbmc.LOGNOTICE )
                _get_special_items(    playlist=self.playlist,
                                          items=( 0, 1, 1, 2, 3, 4, 5, )[ int( _S_( "intermission_video" ) ) ], 
                                           path=( xbmc.translatePath( _S_( "intermission_video_file" ) ), xbmc.translatePath( _S_( "intermission_video_folder" ) ), )[ int( _S_( "intermission_video" ) ) > 1 ],
                                          genre=_L_( 32612 ),
                                         writer=_L_( 32612 ),
                                          index=index_count
                                   )
                if xbmc.PlayList(xbmc.PLAYLIST_VIDEO).size() > p_size and int( _S_( "intermission_video" ) ) > 1: 
                    index_count = index_count + int( _S_( "intermission_video" ) ) - 1
                elif xbmc.PlayList(xbmc.PLAYLIST_VIDEO).size() > p_size and int( _S_( "intermission_video" ) ) == 1:
                    index_count += int( _S_( "intermission_video" ) )
            # get rating video
            if ( _S_( "enable_ratings" ) ) == "true"  and (_S_( "intermission_ratings") ) == "true":
                xbmc.log( "[script.cinema.experience] - Inserting Intermission Rating Video",xbmc.LOGNOTICE )
                xbmc.log( "[script.cinema.experience] -     playlist Position: %d" % index_count, xbmc.LOGNOTICE )
                p_size = xbmc.PlayList(xbmc.PLAYLIST_VIDEO).size()
                xbmc.log( "[script.cinema.experience] -     p_size: %d" % p_size, xbmc.LOGNOTICE )
                _get_special_items(    playlist=self.playlist,
                                          items=1 * ( _S_( "rating_videos_folder" ) != "" ),
                                           path=xbmc.translatePath( _S_( "rating_videos_folder" ) ) + mpaa + ".avi",
                                          genre=_L_( 32603 ),
                                         writer=_L_( 32603 ),
                                         index = index_count
                                   )
                if xbmc.PlayList(xbmc.PLAYLIST_VIDEO).size() > p_size:
                    index_count += 1
            # get Dolby/DTS videos
            if ( _S_( "enable_audio" ) ) == "true"  and (_S_( "intermission_audio") ) == "true":
                xbmc.log( "[script.cinema.experience] - Inserting Intermission Audio Format Video",xbmc.LOGNOTICE )
                xbmc.log( "[script.cinema.experience] -     playlist Position: %d" % index_count, xbmc.LOGNOTICE )
                p_size = xbmc.PlayList(xbmc.PLAYLIST_VIDEO).size()
                xbmc.log( "[script.cinema.experience] -     p_size: %d" % p_size, xbmc.LOGNOTICE )
                _get_special_items(    playlist=self.playlist,
                                          items=1 * ( _S_( "audio_videos_folder" ) != "" ),
                                          path = xbmc.translatePath( _S_( "audio_videos_folder" ) ) + { "dca": "DTS", "ac3": "Dolby", "dtsma": "DTSHD-MA", "dtshd_ma": "DTSHD-MA", "a_truehd": "Dolby TrueHD", "truehd": "Dolby TrueHD" }.get( audio, "Other" ) + xbmc.translatePath( _S_( "audio_videos_folder" ) )[ -1 ],
                                          genre=_L_( 32606 ),
                                         writer=_L_( 32606 ),
                                         index = index_count
                                   )
                # Move to the next feature + 1 - if we insert 2 videos, the next feature is 3 away from the first video, then prepare for the next intro(+1)
                # count = feature * 3 + 1
                if xbmc.PlayList(xbmc.PLAYLIST_VIDEO).size() > p_size:
                    index_count += 1
            index_count += 1 
        # return info from first movie in playlist                                        
        mpaa, audio, genre, movie = _get_queued_video_info( 0 )
        return mpaa, audio, genre, movie
        
    def _create_playlist( self, mpaa, audio, genre, movie ):
        # TODO: try to get a local thumb for special videos?
        xbmc.log( "[script.cinema.experience] - Building Cinema Experience Playlist",xbmc.LOGNOTICE )
        # get Dolby/DTS videos
        xbmc.log( "[script.cinema.experience] - Adding Audio Format Video",xbmc.LOGNOTICE )
        if ( _S_( "enable_audio" ) ) == "true" and ( _S_( "audio_videos_folder" ) ):
                _get_special_items(    playlist=self.playlist,
                                          items=1 * ( _S_( "audio_videos_folder" ) != "" ),
                                           path=xbmc.translatePath( _S_( "audio_videos_folder" ) ) + { "dca": "DTS", "ac3": "Dolby", "dtsma": "DTSHD-MA", "dtshd_ma": "DTSHD-MA", "a_truehd": "Dolby TrueHD", "truehd": "Dolby TrueHD"  }.get( audio, "Other" ) + xbmc.translatePath( _S_( "audio_videos_folder" ) )[ -1 ],
                                          genre=_L_( 32606 ),
                                         writer=_L_( 32606 ),
                                          index=0
                                   )
        # Add Countdown video
        xbmc.log( "[script.cinema.experience] - Adding Count Down Videos: %s Videos" % _S_( "countdown_video" ),xbmc.LOGNOTICE )
        _get_special_items(    playlist=self.playlist,
                                                items=( 0, 1, 1, 2, 3, 4, 5, )[ int( _S_( "countdown_video" ) ) ], 
                                                path=( xbmc.translatePath( _S_( "countdown_video_file" ) ), xbmc.translatePath( _S_( "countdown_video_folder" ) ), )[ int( _S_( "countdown_video" ) ) > 1 ],
                                                genre=_L_( 32611 ),
                                                writer=_L_( 32611 ),
                                                index=0
                                            )
        # get rating video
        xbmc.log( "[script.cinema.experience] - Adding Ratings Video",xbmc.LOGNOTICE )
        if ( _S_( "enable_ratings" ) ) == "true" :
            _get_special_items(    playlist=self.playlist,
                                                    items=1 * ( _S_( "rating_videos_folder" ) != "" ), 
                                                    path=xbmc.translatePath( _S_( "rating_videos_folder" ) ) + mpaa + ".avi",
                                                    genre=_L_( 32603 ),
                                                    writer=_L_( 32603 ),
                                                    index=0
                                                )
        # get feature presentation intro videos
        xbmc.log( "[script.cinema.experience] - Adding Feature Presentation Intro Videos: %s Videos" % _S_( "fpv_intro" ),xbmc.LOGNOTICE )
        _get_special_items(    playlist=self.playlist,
                                                items=( 0, 1, 1, 2, 3, 4, 5, )[ int( _S_( "fpv_intro" ) ) ], 
                                                path=( xbmc.translatePath( _S_( "fpv_intro_file" ) ), xbmc.translatePath( _S_( "fpv_intro_folder" ) ), )[ int( _S_( "fpv_intro" ) ) > 1 ],
                                                genre=_L_( 32601 ),
                                                writer=_L_( 32601 ),
                                                index=0
                                            )
        # get trailers
        xbmc.log( "[script.cinema.experience] - Retriving Trailers: %s Trailers" % _S_( "trailer_count" ),xbmc.LOGNOTICE )
        if not int( _S_( "trailer_play_mode" ) ) == 1:
            trailers = _get_trailers(  items=( 0, 1, 2, 3, 4, 5, 10, )[ int( _S_( "trailer_count" ) ) ],
                                        mpaa=mpaa,
                                       genre=genre,
                                       movie=movie
                                    )
        else:
            trailers = self.download_trailers
        # get coming attractions outro videos
        xbmc.log( "[script.cinema.experience] - Adding Coming Attraction Video: %s Videos" % _S_( "cav_outro" ),xbmc.LOGNOTICE )
        _get_special_items(    playlist=self.playlist,
                                                items=( 0, 1, 1, 2, 3, 4, 5, )[ int( _S_( "cav_outro" ) ) ] * ( len( trailers ) > 0 ), 
                                                path=( xbmc.translatePath( _S_( "cav_outro_file" ) ), xbmc.translatePath( _S_( "cav_outro_folder" ) ), )[ int( _S_( "cav_outro" ) ) > 1 ],
                                                genre=_L_( 32608 ),
                                                writer=_L_( 32608 ),
                                                index=0
                                            )
        # enumerate through our list of trailers and add them to our playlist
        xbmc.log( "[script.cinema.experience] - Adding Trailers: %s Trailers" % len( trailers ),xbmc.LOGNOTICE )
        for trailer in trailers:
            # get trailers
            _get_special_items(    playlist=self.playlist,
                                       items=1,
                                        path=trailer[ 2 ],
                                       genre=trailer[ 9 ] or _L_( 32605 ),
                                       title=trailer[ 1 ],
                                   thumbnail=trailer[ 3 ],
                                        plot=trailer[ 4 ],
                                     runtime=trailer[ 5 ],
                                        mpaa=trailer[ 6 ],
                                release_date=trailer[ 7 ],
                                      studio=trailer[ 8 ] or _L_( 32604 ),
                                      writer= _L_( 32605 ),
                                    director=trailer[ 11 ],
                                       index=0
                              )
        # get coming attractions intro videos
        xbmc.log( "[script.cinema.experience] - Adding Coming Attraction Intro Videos: %s Videos" % _S_( "cav_intro" ),xbmc.LOGNOTICE )
        _get_special_items(    playlist=self.playlist,
                                  items=( 0, 1, 1, 2, 3, 4, 5, )[ int( _S_( "cav_intro" ) ) ] * ( len( trailers ) > 0 ), 
                                   path=( xbmc.translatePath( _S_( "cav_intro_file" ) ), xbmc.translatePath( _S_( "cav_intro_folder" ) ), )[ int( _S_( "cav_intro" ) ) > 1 ],
                                  genre=_L_( 32600 ),
                                 writer=_L_( 32600 ),
                                  index=0
                           )
        # get movie theater experience intro videos
        xbmc.log( "[script.cinema.experience] - Adding Movie Theatre Intro Videos: %s Videos" % _S_( "mte_intro" ),xbmc.LOGNOTICE )
        _get_special_items(    playlist=self.playlist,
                                  items=( 0, 1, 1, 2, 3, 4, 5, )[ int( _S_( "mte_intro" ) ) ], 
                                   path=( xbmc.translatePath( _S_( "mte_intro_file" ) ), xbmc.translatePath( _S_( "mte_intro_folder" ) ), )[ int( _S_( "mte_intro" ) ) > 1 ],
                                  genre=_L_( 32607 ),
                                 writer=_L_( 32607 ),
                                  index=0
                          )
        # get trivia outro video(s)
        xbmc.log( "[script.cinema.experience] - Adding Trivia Outro Videos: %s Videos" % _S_( "trivia_outro" ),xbmc.LOGNOTICE )
        _get_special_items(    playlist=self.playlist,
                                  items=( 0, 1, 1, 2, 3, 4, 5, )[ int( _S_( "trivia_outro" ) ) ], 
                                   path=( xbmc.translatePath( _S_( "trivia_outro_file" ) ), xbmc.translatePath( _S_( "trivia_outro_folder" ) ), )[ int( _S_( "trivia_outro" ) ) > 1 ],
                                  genre=_L_( 32610 ),
                                 writer=_L_( 32610 ),
                                   index=0
                             #media_type="video/picture"
                                                )
        # get feature presentation outro videos
        xbmc.log( "[script.cinema.experience] - Adding Feature Presentation Outro Videos: %s Videos" % _S_( "fpv_outro" ),xbmc.LOGNOTICE )
        _get_special_items(    playlist=self.playlist,
                                  items=( 0, 1, 1, 2, 3, 4, 5, )[ int( _S_( "fpv_outro" ) ) ], 
                                   path=( xbmc.translatePath( _S_( "fpv_outro_file" ) ), xbmc.translatePath( _S_( "fpv_outro_folder" ) ), )[ int( _S_( "fpv_outro" ) ) > 1 ],
                                  genre=_L_( 32602 ),
                                 writer=_L_( 32602 ),
                                            )
        # get movie theater experience outro videos
        xbmc.log( "[script.cinema.experience] - Adding Movie Theatre Outro Videos: %s Videos" % _S_( "mte_outro" ),xbmc.LOGNOTICE )
        _get_special_items(    playlist=self.playlist,
                                  items=( 0, 1, 1, 2, 3, 4, 5, )[ int( _S_( "mte_outro" ) ) ], 
                                   path=( xbmc.translatePath( _S_( "mte_outro_file" ) ), xbmc.translatePath( _S_( "mte_outro_folder" ) ), )[ int( _S_( "mte_outro" ) ) > 1 ],
                                  genre=_L_( 32607 ),
                                 writer=_L_( 32607 ),
                                            )
        xbmc.log( "[script.cinema.experience] - Playlist Size: %s" % xbmc.PlayList(xbmc.PLAYLIST_VIDEO).size(), xbmc.LOGNOTICE )
        return