"""
 A Plugin to play videos shared at http://reeplay.it

 Written By BigBellyBilly
 bigbellybilly AT gmail DOT com	- bugs, comments, ideas ...

 Please don't alter or re-publish this script without authors persmission.
 Additional support may be found on xboxmediacenter forum.	

 - url = sys.argv[ 0 ]
 - handle = sys.argv[ 1 ]
 - params =  sys.argv[ 2 ]

"""

import xbmc, xbmcgui, xbmcplugin
import sys, os, os.path, traceback
from xml.sax.saxutils import unescape
from xml.sax.saxutils import escape
#from pprint import pprint

__plugin__ = "reeplay.it"
__scriptname__ = __plugin__
__author__ = 'BigBellyBilly [BigBellyBilly@gmail.com]'
__url__ = "http://code.google.com/p/xbmc-addons/"
__svn_url__ = "http://xbmc-addons.googlecode.com/svn/trunk/plugins/video/reeplay.it"
__date__ = '21-09-2009'
__version__ = '1.2a'
__svn_revision__ = "$Revision$"
__XBMC_Revision__ = "19001"
xbmc.output(__plugin__ + " Version: " + __version__ + " Date: " + __date__)

# check if build is special:// aware - set roots paths accordingly
XBMC_HOME = 'special://home'
XBMC_PROFILE = 'special://profile'
if not os.path.isdir(xbmc.translatePath(XBMC_HOME)):	# if fails to convert to Q:, old builds
	XBMC_HOME = 'Q:'
	XBMC_PROFILE = 'T:'

# Shared resources
DIR_HOME= os.getcwd().replace(';','')
DIR_RESOURCES = os.path.join( DIR_HOME, "resources" )
DIR_RESOURCES_LIB = os.path.join( DIR_RESOURCES, "lib" )
DIR_USERDATA = '/'.join( [XBMC_PROFILE, "plugin_data", "video", __plugin__] )
DIR_CACHE = xbmc.translatePath('/'.join( [ DIR_USERDATA, "cache"] ))
sys.path.insert(0, xbmc.translatePath(DIR_RESOURCES_LIB) )

# Load Language using xbmc builtin
try:
    # 'resources' now auto appended onto path
    __lang__ = xbmc.Language( xbmc.translatePath(DIR_HOME) ).getLocalizedString
except:
	xbmcgui.Dialog().ok("XBMC Language Error", "Install a newer XBMC build.", str( sys.exc_info()[ 1 ] ))

from bbbLib import *
import reeplayit

#################################################################################################################
class ReeplayitPlugin:
	""" main plugin class """

	# define param key names
	PARAM_TITLE = "title"
	PARAM_PLS_ID = 'plsid'
	PARAM_PLS_COUNT = 'plscount'
	PARAM_PLS_PAGE = 'plspage'
	PARAM_VIDEO_ID = 'videoid'
	PARAM_PLS_PLAYALL = 'plsplayall'
	PARAM_INFO = 'info'

	def __init__( self, *args, **kwargs ):
		log("> __init__()")

		if not sys.argv or len(sys.argv) < 3:
			xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=False)
			log("< __init__() too few argv args %s" % sys.argv)
			return

		# allow access to readme/changelog which dont rely on any settings
		elif ( sys.argv[ 2 ] ):
			paramDict = self._getParams()
			if paramDict.has_key(self.PARAM_INFO):
				fn = os.path.join( DIR_RESOURCES, paramDict[self.PARAM_INFO] )
				reeplayit.showTextFile(fn)
				return

		# load settings - ensuring all ok
		if not self.loadSettings():
			xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=False)
			log("< settings incomplete, exiting script")
			return

		log("script normal startup")
		# create a new lib instance using login details
		self.reeplayitLib = reeplayit.ReeplayitLib(self.settings.get(self.settings.SETTING_USER), \
												self.settings.get(self.settings.SETTING_PWD), \
												self.settings.get(self.settings.SETTING_PAGE_SIZE), \
												self.settings.get(self.settings.SETTING_VQ))


		if ( not sys.argv[ 2 ] ):
			ok = True
			# check XBMC min build date required
			if not checkBuildDate(__plugin__, "01-02-2009"):
				ok = False
			# check for svn update
			elif self.settings.get(self.settings.SETTING_CHECK_UPDATE):	# check for update ?
				if checkUpdate(False, False):
					ok = False

			if not ok:
				xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=False)
				return

			# new session clear cache of data and maybe videos
			deleteVideos = self.settings.get(self.settings.SETTING_DELETE_VIDEOS)
			reeplayit.deleteScriptCache(deleteVideos, deleteData=True)

			# get category
			self.getPlaylists()
		else:
			# extract URL params and act accordingly
			try:
#				paramDict = self._getParams()
				if paramDict.has_key(self.PARAM_PLS_ID):
					title = unescape(paramDict[self.PARAM_TITLE])
					count = int(paramDict[self.PARAM_PLS_COUNT])
					page = int(paramDict.get(self.PARAM_PLS_PAGE,1))
					id = paramDict[self.PARAM_PLS_ID]
					self.getPlaylist(title, id, count, page)
				elif paramDict.has_key(self.PARAM_VIDEO_ID):
					title = unescape(paramDict[self.PARAM_TITLE])
					id = paramDict[self.PARAM_VIDEO_ID]
					self.getVideo(title, id)
				elif paramDict.has_key(self.PARAM_PLS_PLAYALL):
					id = paramDict[self.PARAM_PLS_PLAYALL]
					title = unescape(paramDict[self.PARAM_TITLE])
					count = int(paramDict[self.PARAM_PLS_COUNT])
					self.playPlaylist(title, id, count) 
				else:
					raise
			except:
				traceback.print_exc()
				messageOK("ERROR", str(sys.exc_info()[ 1 ]))
				xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=False)

		log("< __init__()")

	########################################################################################################################
	def loadSettings(self):
		""" Settings are set in the script, this is just to check all settings exist """
		log( "> loadSettings")

		self.settings = reeplayit.ReeplayitSettings()
		success = self.settings.check()
		if not success:
			# call settings menu - if xbmc builds has feature
			try:
				if ( os.environ.get( "OS", "n/a" ) == "xbox" ):
					xbmc.sleep( 2000 )
				xbmcplugin.openSettings(sys.argv[0])
				success = self.settings.check()
			except:
				# builtin missing from build - inform user to use ContextMenu for settings
				traceback.print_exc()
				messageOK(__lang__(0), __lang__(107))

		log( "< loadSettings() success=%s" % success)
		return success

	########################################################################################################################
	def callRestart(self):
		xbmc.executebuiltin("xbmc.ActivateWindow(videofiles,%s)" % sys.argv[0])

	########################################################################################################################
	def _getParams(self):
		""" extract params from argv[2] to make a dict (key=value) """
		paramDict = {}
		paramPairs=sys.argv[2][1:].split( "&" )
		for paramsPair in paramPairs:
			param = paramsPair.split('=')
			if len(param) == 2:
				paramDict[param[0]] = param[1]
			elif len(param) > 2:
				value = "=".join(param[1:]).replace('^','&')	# frig to avoid being split prematurely
				paramDict[param[0]] = value

		return paramDict

	########################################################################################################################
	def getPlaylists(self):
		""" Return a list of Playlists """
		log( "> getPlaylists()")
		ok = False
		try:
			sz = self.reeplayitLib.getPlaylists()
			if not sz:
				raise "Empty"

			for li in self.reeplayitLib.plsListItems:
				plsTitle = li.getLabel()
				plsId = li.getProperty(self.reeplayitLib.PROP_ID)
				plsCount = int(li.getProperty(self.reeplayitLib.PROP_COUNT))

				# context menu option - Play Playlist
				# use RunPlugin as its not creating a new dir - just doing an action
				menuCmd = "xbmc.RunPlugin(%s?%s=%s&%s=%s&%s=%s)" % (sys.argv[0], \
																self.PARAM_PLS_PLAYALL, plsId,
																self.PARAM_TITLE, plsTitle, \
																self.PARAM_PLS_COUNT, plsCount)
				li.addContextMenuItems([(__lang__(233) + ": "+plsTitle, menuCmd)])		# play pls
	
				li_url = "%s?%s=%s&%s=%s&%s=%s" % ( sys.argv[ 0 ], \
												self.PARAM_TITLE, plsTitle, \
												self.PARAM_PLS_ID, plsId, \
												self.PARAM_PLS_COUNT, plsCount )

				ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), \
							url=li_url, listitem=li, isFolder=True, totalItems=sz)
				if ( not ok ): break
		except "Empty":
			log("Empty raised")
			messageOK(__plugin__, __lang__(104))	# no pls found
			ok = False
		except:
			traceback.print_exc()
			messageOK("ERROR:", str(sys.exc_info()[ 1 ]))
			ok = False

		if ok:
			xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
			xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
			xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_SIZE )
			xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content="files" )

		xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok)
		log( "< getPlaylists() ok=%s" % ok)

	########################################################################################################################
	def getPlaylist(self, plsTitle, plsId, plsCount, plsPage=1):
		""" Discover a list of Categories within a Directory """
		log( "> getplaylist() plsId=%s plsCount=%s plsPage=%s" % (plsId,plsCount,plsPage))

		ok = False
		try:
			maxPages = self.reeplayitLib.getMaxPages( plsCount )
			isNextPage = (plsPage < maxPages)
			log("isNextPage=%s" % isNextPage)

			msg = "%s - %s %s" % (plsTitle, __lang__(219), plsPage)
			dialogProgress.create(__lang__(0), __lang__(217), msg) # DL playlist content
			self.reeplayitLib.set_report_hook(self.reeplayitLib.progressHandler, dialogProgress)

			videoCount = self.reeplayitLib.getPlaylist(plsId, page=plsPage)

			dialogProgress.close()
			if not videoCount: raise "Empty"

			if isNextPage:
				videoCount += 1
			if isNextPage:
				nextPage = plsPage+1
				title = "%s (%s/%s)" % (__lang__(221), plsPage+1, maxPages)
				
				li_url = "%s?%s=%s&%s=%s&%s=%s&%s=%s" % ( sys.argv[ 0 ], \
												self.PARAM_TITLE, escape(title), \
												self.PARAM_PLS_ID, plsId, \
												self.PARAM_PLS_COUNT, plsCount, \
												self.PARAM_PLS_PAGE, nextPage )

				tbn = os.path.join( DIR_RESOURCES, "next.png")
				li = xbmcgui.ListItem(title, "", tbn, tbn )
				ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), \
							url=li_url, listitem=li, isFolder=True, totalItems=videoCount)

			# for each video , extract info and store to a ListItem
			for li in self.reeplayitLib.videoListItems:
				videoTitle = li.getLabel()
				videoId = li.getProperty(self.reeplayitLib.PROP_ID)
#				videoLink = li.getProperty(self.reeplayitLib.PROP_URL)
#				print videoTitle, videoId#, videoLink

				li_url = "%s?%s=%s&%s=%s" % ( sys.argv[ 0 ], \
												self.PARAM_VIDEO_ID, videoId, \
												self.PARAM_TITLE, escape(videoTitle) )

				ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), \
							url=li_url, listitem=li, isFolder=False, totalItems=videoCount)
				if ( not ok ): break
		except "Empty":
			log("Empty raised")
		except:
			traceback.print_exc()
			messageOK("ERROR:", str(sys.exc_info()[ 1 ]))

#		dialogProgress.close()
		if not ok:
			messageOK(__plugin__, __lang__(105), plsTitle)	# no video
		else:
			xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
			xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
			xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )
			xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content="movies" )

		xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok )
		log( "< getPlaylist() ok=%s" % ok)

	############################################################################################################
	def getVideo(self, videoTitle, videoId):
		""" Discover media link from video content """

		log( "> getVideo() videoId=%s" % (videoId))
		source = ''
		try:
			dialogProgress.create(__lang__(0), videoTitle)
			self.reeplayitLib.set_report_hook(self.reeplayitLib.progressHandler, dialogProgress)
			source, li = self.reeplayitLib.getVideo(id=videoId, \
										title=videoTitle, \
										stream=self.settings.get(self.settings.SETTING_STREAM_VIDEO))
			if source and li:
				playMedia(source, li)
			dialogProgress.close()
		except:
			source = ""
			traceback.print_exc()
			messageOK("ERROR:", str(sys.exc_info()[ 1 ]))

		log( "< getVideo()")

	########################################################################################################################
	def playPlaylist(self, plsTitle, plsId, plsCount):
		""" Discover a list of Categories within a Directory """ 
		log( "> playPlaylist() plsId=%s plsCount=%s" % (plsId,plsCount))
		ok = False

		try:
			# delete existing data docs as were now getting every video in pls, not by pagesize
			reeplayit.deleteScriptCache(deleteVideos=False, deleteData=True)

			dialogProgress.create(__lang__(0), __lang__(217), plsTitle) # DL playlist content
			self.reeplayitLib.set_report_hook(self.reeplayitLib.progressHandler, dialogProgress)

			# get all videos in playlist
			videoCount = self.reeplayitLib.getPlaylist(plsId, pageSize=plsCount)

			if not videoCount: raise "Empty"

			# create a playlist and add items to it
			xbmcPlaylist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
			xbmcPlaylist.clear()

			streamVideo = self.settings.get(self.settings.SETTING_STREAM_VIDEO)
			for idx in range(videoCount):
				source, li = self.reeplayitLib.getVideo(idx, stream=streamVideo)
				if source and li:
#						url = li.getProperty(self.reeplayitLib.PROP_URL)
					xbmcPlaylist.add(source, li)
				else:
					break	# http error, so stop processing more videos

			dialogProgress.close()

			# play all in xbmc pls
			log("Playlist size=%d" % xbmcPlaylist.size())
			if xbmcPlaylist.size() <= 0: raise "Empty"

			if xbmcgui.Dialog().yesno(__lang__(0), __lang__(234), "","", __lang__(236), __lang__(235)):
				xbmcPlaylist.shuffle()
			playMedia(xbmcPlaylist)
		except "Empty":
			log("Empty raised")
			messageOK(__lang__(0), __lang__(105))		# no videos
		except:
			handleException()

		dialogProgress.close()
		log( "< playPlaylist()")


######################################################################################
def checkUpdate( silent=False, notifyNotFound=False):
	log( "> checkUpdate() silent=%s" % silent)

	updated = False
	import update
	up = update.UpdatePlugin(__lang__, __plugin__, "video")
	version = up.getLatestVersion(silent)
	log("Current Version: %s Tag Version: %s" % (__version__,version))
	if version and version != "-1":
		if __version__ < version:
			if xbmcgui.Dialog().yesno( __lang__(0), \
								"%s %s %s." % ( __lang__(1006), version, __lang__(1002) ), \
								__lang__(1003 )):
				up.makeBackup()
				up.issueUpdate(version)
				updated = True
		elif notifyNotFound:
			dialogOK(__lang__(0), __lang__(1000))
#	elif not silent:
#		dialogOK(__lang__(0), __lang__(1030))				# no tagged ver found

	del up
	log( "< checkUpdate() updated=%s" % updated)
	return updated

#######################################################################################################################    
# BEGIN !
#######################################################################################################################
makeDir(DIR_USERDATA) 
makeDir(DIR_CACHE)

try:
	# check language loaded
	xbmc.output( "__lang__ = %s" % __lang__ )
	myplugin = ReeplayitPlugin()
	del myplugin
except:
	handleException()

# clean up on exit
moduleList = ['bbbLib', 'reeplayit']
for m in moduleList:
	try:
		del sys.modules[m]
		xbmc.output(__plugin__ + " del sys.module=%s" % m)
	except: pass

# remove other globals
try:
	del dialogProgress
except: pass
#sys.modules.clear()
