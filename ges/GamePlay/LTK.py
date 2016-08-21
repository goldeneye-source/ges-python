################ Copyright 2005-2016 Team GoldenEye: Source #################
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
from .DeathMatch import DeathMatch
from .Utils import GetPlayers
import GEPlayer, GEUtil, GEMPGameRules as GERules, GEGlobal as Glb

USING_API = Glb.API_VERSION_1_2_0

# LTK is just deathmatch with no armor, a high damage multiplier, and popout help.
class LTK( DeathMatch ):
    def GetPrintName( self ):
        return "#GES_GP_LTK_NAME"

    def GetScenarioHelp( self, help_obj ):
        help_obj.SetDescription( "#GES_GP_LTK_HELP" )

    def GetGameDescription( self ):
        if GERules.IsTeamplay():
            return "Team LTK"
        else:
            return "LTK"

    def OnLoadGamePlay( self ):
        super( LTK, self ).OnLoadGamePlay()
        self.ltk_SetDamageMultiplier( 1000 )
        GERules.SetSpawnInvulnTime( 0, True )
        
    def OnPlayerConnect( self, player ):
        player.SetDamageMultiplier( 1000 )

    def OnPlayerSpawn( self, player ):
        if player.IsInitialSpawn():
            GEUtil.PopupMessage( player, "#GES_GP_LTK_NAME", "#GES_GPH_LTK_GOAL" )

    def OnRoundBegin( self ):
        super( LTK, self ).OnRoundBegin()
        GERules.DisableArmorSpawns()

    def ltk_SetDamageMultiplier( self, amount ):
        for player in GetPlayers():
            player.SetDamageMultiplier( amount )
