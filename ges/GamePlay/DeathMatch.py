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
from .Utils import GetPlayers
import GEPlayer, GEUtil, GEMPGameRules as GERules, GEGlobal as Glb

USING_API = Glb.API_VERSION_1_1_1

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
        # Frag limit checks
        frag_limit = int( GEUtil.GetCVarValue( "dm_fraglimit" ) )
        if frag_limit != 0:
            if GERules.IsTeamplay():
                # Check if Janus or MI6 team has reached the frag limit
                team_janus = GERules.GetTeam( Glb.TEAM_JANUS );
                team_mi6 = GERules.GetTeam( Glb.TEAM_MI6 );

                janus_score = team_janus.GetRoundScore() + team_janus.GetMatchScore()
                mi6_score = team_mi6.GetRoundScore() + team_mi6.GetMatchScore()

                # If either Janus or MI6 reached the frag limit, immediately end the match
                if janus_score >= frag_limit or mi6_score >= frag_limit:
                    GERules.EndMatch()
            else:
                # Check if any player has reached the frag limit
                for player in GetPlayers():
                    player_score = player.GetMatchScore() + player.GetScore()
                    if player_score >= frag_limit:
                        GERules.EndMatch()
