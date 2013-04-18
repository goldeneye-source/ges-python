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
from . import GEScenario
import GEEntity, GEPlayer, GEUtil, GEWeapon, GEMPGameRules, GEGlobal

USING_API = GEGlobal.API_VERSION_1_0_0

class MWGG( GEScenario ):
	def __init__( self ):
		super( MWGG, self ).__init__()

		self.GGClass = 'weapon_golden_gun'
		self.GGOwnerId = None

		self.GGGlow = GEUtil.CColor( 232, 180, 2, 64 )
		self.GGColor = GEUtil.CColor( 232, 180, 2, 255 )
		self.GGObjDrop = GEUtil.CColor( 232, 180, 2, 100 )
		self.GGObjHeld = GEUtil.CColor( 232, 180, 2, 230 )

	def GetPrintName( self ):
		return "#GES_GP_MWGG_NAME"

	def GetScenarioHelp( self, help_obj ):
		help_obj.SetDescription( "#GES_GP_MWGG_HELP" )

	def GetGameDescription( self ):
		return "MWGG"

	def GetTeamPlay( self ):
		return GEGlobal.TEAMPLAY_NONE

	def OnLoadGamePlay( self ):
		GEMPGameRules.GetTokenMgr().SetupToken( self.GGClass, limit=1, respawn_delay=20.0,
							location=GEGlobal.SPAWN_WEAPON | GEGlobal.SPAWN_SPECIALONLY,
							glow_color=self.GGGlow )

		GEMPGameRules.GetTokenMgr().SetGlobalAmmo( self.GGClass, 2 )
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
			if victim == self.GGOwnerId:
				GEUtil.EmitGameplayEvent( "mwgg_suicide", "%i" % victim.GetUserID() )
				GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "#GES_GP_MWGG_SUICIDE" )
				
			victim.AddRoundScore( -1 )
		else:
			# Regular kill
			if victim == self.GGOwnerId:
				GEUtil.EmitGameplayEvent( "mwgg_killed", "%i" % victim.GetUserID(), "%i" % killer.GetUserID() )
				GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "#GES_GP_MWGG_KILLED", killer.GetPlayerName() )
				
			GEUtil.Warning( "Player was killed\n!" )
			killer.AddRoundScore( 1 )

	def OnThink( self ):
		if self.GGOwnerId:
			GGPlayer = GEEntity.GetEntByUniqueId( self.GGOwnerId )
			if GGPlayer and GGPlayer.GetArmor() > 0:
				GGPlayer.SetMaxArmor( 0 )

	def OnTokenSpawned( self, token ):
		GEMPGameRules.GetRadar().AddRadarContact( token, GEGlobal.RADAR_TYPE_TOKEN, True, "ge_radar_gg" )
		GEMPGameRules.GetRadar().SetupObjective( token, GEGlobal.TEAM_NONE, "", "", self.GGObjDrop )

	def OnTokenPicked( self, token, player ):
		radar = GEMPGameRules.GetRadar()
		radar.DropRadarContact( token )
		radar.AddRadarContact( player, GEGlobal.RADAR_TYPE_PLAYER, True, "", self.GGColor )
		radar.SetupObjective( player, GEGlobal.TEAM_NONE, "", "", self.GGObjHeld )

		GEUtil.PlaySoundTo( player, "GEGamePlay.Token_Grab" )
		GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "#GES_GP_MWGG_PICKED", player.GetPlayerName() )
		GEUtil.EmitGameplayEvent( "mwgg_ggpickup", "%i" % player.GetUserID() )
		GEUtil.HudMessage( player, "#GES_GP_MWGG_HAVEGG", -1, 0.75, self.GGColor, 3.0 )

		radar.SetPlayerRangeMod( player, 0.5 )
		player.SetScoreBoardColor( GEGlobal.SB_COLOR_GOLD )
		self.GGOwnerId = GEEntity.GetUID( player )

	def OnTokenDropped( self, token, player ):
		radar = GEMPGameRules.GetRadar()
		radar.DropRadarContact( player )
		radar.AddRadarContact( token, GEGlobal.RADAR_TYPE_TOKEN, True, "ge_radar_gg" )
		radar.SetupObjective( token, GEGlobal.TEAM_NONE, "", "", self.GGObjDrop )

		GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "#GES_GP_MWGG_DROPPED", player.GetPlayerName() )
		player.SetScoreBoardColor( GEGlobal.SB_COLOR_NORMAL )
		self.GGOwnerId = None

	def OnTokenRemoved( self, token ):
		GEMPGameRules.GetRadar().DropRadarContact( token )
		GEMPGameRules.GetRadar().DropRadarContact( token.GetOwner() )
		self.GGOwnerId = None
