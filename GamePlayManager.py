from GESFuncs import *
from GEGlobal import PY_BASE_DIR
import sys, reimport
import GEGamePlay
import GamePlay

class PYGamePlayManager( GEGamePlay.CGamePlayManager ):
	def __init__( self ):
		super( PYGamePlayManager, self ).__init__()
		reimport.reimport( GamePlay )

	def SetGamePlay( self, ident ):
		tmp = FindModule( GamePlay, ident )
		if not tmp:
			GEUtil.Warning( "Failed to find scenario %s!\n" % ident )
			return None
		else:
			ident = tmp
			module = "GamePlay.%s" % ident
			scenario = None

			try:
				# Try to load immediately, fallback to import if new class
				scenario = getattr( sys.modules[module], ident )()
				print "Loading scenario %s from cache" % ident
			except KeyError:
				try:
					RemoveCompiled( "%s\\GamePlay\\%s" % ( PY_BASE_DIR, ident ) )

					__import__( module, globals(), locals() )

					scenario = getattr( sys.modules[module], ident )()

					print "Loading scenario %s from disk" % ident

				except ImportError:
					PrintError( "Failed to load scenario %s\n" % ident )

			if scenario and not CheckAPI( sys.modules[module], GEGlobal.API_GP_VERSION ):
				GEUtil.Warning( "Scenario load FAILED due to API mismatch. Did you define USING_API?\n" )
				return None

			return scenario

pyGamePlayMangObj = None

def GetGamePlayManager():
	global pyGamePlayMangObj

	if not pyGamePlayMangObj:
		pyGamePlayMangObj = PYGamePlayManager()

	return pyGamePlayMangObj

def PurgeGamePlayManager():
	global pyGamePlayMangObj
	pyGamePlayMangObj = None

# If imported directly, create our manager object
if __name__ == '__main__':
	GetGamePlayManager()
