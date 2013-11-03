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
from .DeathMatch import DeathMatch
import GEPlayer, GEUtil, GEMPGameRules, GEGlobal

USING_API = GEGlobal.API_VERSION_1_1_1

class LTK( DeathMatch ):
    def GetPrintName( self ):
        return "#GES_GP_LTK_NAME"

    def GetScenarioHelp( self, help_obj ):
        help_obj.SetDescription( "#GES_GP_LTK_HELP" )

    def GetGameDescription( self ):
        if GEMPGameRules.IsTeamplay():
            return "Team LTK"
        else:
            return "LTK"

    def OnLoadGamePlay( self ):
        super( LTK, self ).OnLoadGamePlay()
        self.ltk_SetDamageMultiplier( 1000 )

    def OnPlayerConnect( self, player ):
        player.ltk_SetDamageMultiplier( 1000 )

    def OnPlayerSpawn( self, player ):
        if player.IsInitialSpawn():
            GEUtil.PopupMessage( player, "#GES_GP_LTK_NAME", "#GES_GPH_LTK_GOAL" )

    def OnRoundBegin( self ):
        super( LTK, self ).OnRoundBegin()
        GEMPGameRules.DisableArmorSpawns()

    def ltk_SetDamageMultiplier( self, amount ):
        for i in range( 32 ):
            if GEPlayer.IsValidPlayerIndex( i ):
                GEPlayer.GetMPPlayer( i ).SetDamageMultiplier( amount )
