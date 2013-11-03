################ Copyright 2005-2013 Team GoldenEye: Source #################
#
# This file is part of GoldenEye: Source's Python Library.
#
# GoldenEye: Source's Python Library is free software: you can redistribute
# it and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the License,
# or(at your option) any later version.
#
# GoldenEye: Source's Python Library is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GoldenEye: Source's Python Library.
# If not, see <http://www.gnu.org/licenses/>.
#############################################################################
from GESFuncs import *
from GEGlobal import PY_BASE_DIR
import sys
import GEGamePlay, GEUtil
import GamePlay

class PYGamePlayManager( GEGamePlay.CGamePlayManager ):
    def __init__( self ):
        super( PYGamePlayManager, self ).__init__()

        import reimport
        reimport.reimport( GamePlay )

    def LoadScenario( self, scenario_name ):
        found_scenario = FindModule( GamePlay, scenario_name )
        if not found_scenario:
            GEUtil.Warning( "Failed to find scenario %s!\n" % scenario_name )
            return None
        else:
            # Assign the found scenario to ensure we have the right case
            scenario_name = found_scenario
            module = "GamePlay.%s" % scenario_name
            scenario = None

            try:
                # Try to load immediately, fallback to import if new class
                scenario = getattr( sys.modules[module], scenario_name )()
                print "Loading scenario %s from cache" % scenario_name
            except KeyError:
                try:
                    RemoveCompiled( "%s\\GamePlay\\%s" % ( PY_BASE_DIR, scenario_name ) )
                    
                    __import__( module, globals(), locals() )

                    scenario = getattr( sys.modules[module], scenario_name )()

                    print "Loading scenario %s from disk" % scenario_name

                except ImportError:
                    PrintError( "Failed to load scenario %s\n" % scenario_name )

            if scenario and not CheckAPI( sys.modules[module], GEGlobal.API_GP_VERSION ):
                GEUtil.Warning( "Scenario load FAILED due to API mismatch.\n" )
                return None

            return scenario

pyGamePlayMangObj = None

def GetManager():
    global pyGamePlayMangObj

    if not pyGamePlayMangObj:
        pyGamePlayMangObj = PYGamePlayManager()

    return pyGamePlayMangObj

def PurgeManager():
    global pyGamePlayMangObj
    pyGamePlayMangObj = None
