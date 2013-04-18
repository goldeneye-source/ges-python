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
from GamePlay import GEScenario
import GEPlayer, GEUtil, GEMPGameRules as GERules, GEGlobal as Glb

USING_API = Glb.API_VERSION_1_1_0

class DeathMatch( GEScenario ):
	def GetPrintName( self ):
		return "#GES_GP_DEATHMATCH_NAME"

	def GetScenarioHelp( self, help_obj ):
		help_obj.SetDescription( "#GES_GP_DEATHMATCH_HELP" )

	def GetGameDescription( self ):
		if GERules.IsTeamplay():
			return "Team Deathmatch"
		else:
			return "Deathmatch"

	def GetTeamPlay( self ):
		return Glb.TEAMPLAY_TOGGLE

	def OnLoadGamePlay( self ):
		GERules.SetAllowTeamSpawns( False )
		self.CreateCVar( "dm_fraglimit", "0", "Enable frag limit for DeathMatch." )

	def OnThink( self ):
		fragLimit = int( GEUtil.GetCVarValue( "dm_fraglimit" ) )
		if fragLimit != 0:
			if GERules.IsTeamplay():

				teamJ = GERules.GetTeam( Glb.TEAM_JANUS );
				teamM = GERules.GetTeam( Glb.TEAM_MI6 );

				jScore = teamJ.GetRoundScore() + teamJ.GetMatchScore()
				mScore = teamM.GetRoundScore() + teamM.GetMatchScore()

				if jScore >= fragLimit or mScore >= fragLimit:
					GERules.EndMatch()
			else:
				for i in range( 32 ):

					if not GEPlayer.IsValidPlayerIndex( i ):
						continue

					player = GEPlayer.GetMPPlayer( i )

					if  ( player.GetMatchScore() + player.GetScore() ) >= fragLimit:
						GERules.EndMatch()
