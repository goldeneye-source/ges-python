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
from GEUtil import Color
import GEEntity, GEUtil, GEMPGameRules, GEGlobal

USING_API = GEGlobal.API_VERSION_1_1_1

class MWGG( DeathMatch ):
    gg_glow_color = Color( 232, 180, 2, 64 )
    gg_owner_color = Color( 232, 180, 2, 255 )
    gg_dropped_color = Color( 232, 180, 2, 100 )
    gg_held_color = Color( 232, 180, 2, 230 )

    def __init__( self ):
        super( MWGG, self ).__init__()

        self.gg_classname = "weapon_golden_gun"
        self.gg_owner = None

    def GetPrintName( self ):
        return "#GES_GP_MWGG_NAME"

    def GetScenarioHelp( self, help_obj ):
        help_obj.SetDescription( "#GES_GP_MWGG_HELP" )

    def GetGameDescription( self ):
        return "MWGG"

    def GetTeamPlay( self ):
        return GEGlobal.TEAMPLAY_NONE

    def OnLoadGamePlay( self ):
        super( MWGG, self ).OnLoadGamePlay()
        GEMPGameRules.GetTokenMgr().SetupToken( self.gg_classname, limit=1, respawn_delay=20.0,
                            location=GEGlobal.SPAWN_WEAPON | GEGlobal.SPAWN_SPECIALONLY,
                            glow_color=self.gg_glow_color )

        GEMPGameRules.GetTokenMgr().SetGlobalAmmo( self.gg_classname, 2 )
        GEMPGameRules.GetRadar().SetForceRadar( True )

    def OnPlayerSpawn( self, player ):
        player.SetMaxArmor( int( GEGlobal.GE_MAX_ARMOR ) )
        player.SetScoreBoardColor( GEGlobal.SB_COLOR_NORMAL )

        if player.IsInitialSpawn():
            GEUtil.PopupMessage( player, "#GES_GPH_OBJECTIVE", "#GES_GPH_MWGG_GOAL", "mwgg_goal" )

    def OnPlayerKilled( self, victim, killer, weapon ):
        if not victim:
            return

        if not killer or victim == killer:
            # Death by world or suicide
            if victim == self.gg_owner:
                GEUtil.EmitGameplayEvent( "mwgg_suicide", str( victim.GetUserID() ) )
                GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "#GES_GP_MWGG_SUICIDE" )

            victim.AddRoundScore( -1 )
        else:
            # Regular kill
            if victim == self.gg_owner:
                GEUtil.EmitGameplayEvent( "mwgg_killed", str( victim.GetUserID() ), str( killer.GetUserID() ) )
                GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "#GES_GP_MWGG_KILLED", killer.GetCleanPlayerName() )

            killer.AddRoundScore( 1 )

    def OnThink( self ):
        if self.gg_owner:
            gg_player = GEEntity.GetEntByUID( self.gg_owner )
            if gg_player and gg_player.GetArmor() > 0:
                gg_player.SetMaxArmor( 0 )

    def OnTokenSpawned( self, token ):
        GEMPGameRules.GetRadar().AddRadarContact( token, GEGlobal.RADAR_TYPE_TOKEN, True, "ge_radar_gg" )
        GEMPGameRules.GetRadar().SetupObjective( token, GEGlobal.TEAM_NONE, "", "", self.gg_dropped_color )

    def OnTokenPicked( self, token, player ):
        radar = GEMPGameRules.GetRadar()
        radar.DropRadarContact( token )
        radar.AddRadarContact( player, GEGlobal.RADAR_TYPE_PLAYER, True, "", self.gg_owner_color )
        radar.SetupObjective( player, GEGlobal.TEAM_NONE, "", "", self.gg_held_color )

        GEUtil.PlaySoundTo( player, "GEGamePlay.Token_Grab" )
        GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "#GES_GP_MWGG_PICKED", player.GetCleanPlayerName() )
        GEUtil.EmitGameplayEvent( "mwgg_ggpickup", str( player.GetUserID() ) )
        GEUtil.HudMessage( player, "#GES_GP_MWGG_HAVEGG", -1, 0.75, self.gg_owner_color, 3.0 )

        radar.SetPlayerRangeMod( player, 0.5 )
        player.SetScoreBoardColor( GEGlobal.SB_COLOR_GOLD )
        self.gg_owner = player.GetUID()

    def OnTokenDropped( self, token, player ):
        radar = GEMPGameRules.GetRadar()
        radar.DropRadarContact( player )
        radar.AddRadarContact( token, GEGlobal.RADAR_TYPE_TOKEN, True, "ge_radar_gg" )
        radar.SetupObjective( token, GEGlobal.TEAM_NONE, "", "", self.gg_dropped_color )

        GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "#GES_GP_MWGG_DROPPED", player.GetCleanPlayerName() )
        player.SetScoreBoardColor( GEGlobal.SB_COLOR_NORMAL )
        self.gg_owner = None

    def OnTokenRemoved( self, token ):
        GEMPGameRules.GetRadar().DropRadarContact( token )
        GEMPGameRules.GetRadar().DropRadarContact( token.GetOwner() )
        self.gg_owner = None
