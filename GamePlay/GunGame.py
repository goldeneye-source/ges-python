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
from Utils.GEWarmUp import GEWarmUp
from Utils.GEPlayerTracker import GEPlayerTracker
from Utils import GetPlayers, _
from GEUtil import Color
import GEPlayer, GEUtil, GEWeapon, GEMPGameRules, GEGlobal

# NOTE NOTE #
# When changing the weapon list, make sure you also change the classname list
# or the weapons will not register as proper kills for the player's level
#
# The classnames for the following weapons should be substituted:
# 	grenade -> npc_grenade
# 	rocket_launcher -> npc_rocket
# 	grenade_launcher -> npc_shell
# 	[remote|timed|proximity]mine -> npc_mine  ##(ALL MINES ARE THE SAME CLASSNAME)##
#

USING_API = GEGlobal.API_VERSION_1_1_0

# TODO: Make this a list of lists including ammo amt given at spawn
weapList = ["golden_pp7", "rocket_launcher", "moonraker", "rcp90", "auto_shotgun", "ar33", "phantom", "shotgun", "d5k", "cmag", "kf7", "sniper_rifle", "pp7", "grenade", "klobb"]
weapClassName = ["golden_pp7", "npc_rocket", "moonraker", "rcp90", "auto_shotgun", "ar33", "phantom", "shotgun", "d5k", "cmag", "kf7", "sniper_rifle", "pp7", "npc_grenade", "klobb"]
iMaxLevel = len( weapList ) - 1

class GunGame( GEScenario ):
	TR_SHOWROUND = "gground"
	TR_LEVEL = "gglevel"
	TR_WASINPLAY = "ggwasinplay"
	TR_ACTIVE = "ggactive"
	TR_WEAPSGIVEN = "ggweapons"

	def __init__( self ):
		super( GunGame, self ).__init__()

		self.warmupTimer = GEWarmUp( self )
		self.notice_WaitingForPlayers = 0
		self.WaitingForPlayers = True

		self.StartedGame = False
		self.RoundsPlayed = 0
		self.PlayerStartLevel = 0
		self.pltracker = GEPlayerTracker( self )

		# CVar Holders
		self.RoundLimit = 2

	def Cleanup( self ):
		GEScenario.Cleanup( self )
		self.pltracker = None
		self.warmupTimer = None

	def GetPrintName( self ):
		return "#GES_GP_GUNGAME_NAME"

	def GetScenarioHelp( self, help_obj ):
		help_obj.SetDescription( "#GES_GP_GUNGAME_HELP" )

	def GetGameDescription( self ):
		return "GunGame"

	def GetTeamPlay( self ):
		return GEGlobal.TEAMPLAY_NONE

	def OnLoadGamePlay( self ):
		self.CreateCVar( "gg_avglevel", "0", "Give new players average level on join" )
		self.CreateCVar( "gg_warmup", "20", "The warm up time in seconds (Use 0 to disable warmup)" )
		self.CreateCVar( "gg_numrounds", "2", "This is the number of rounds that should be played. Use -1 for unlimited rounds per match. Max is 10." )

		# Make sure we don't start out in wait time if we changed gameplay mid-match
		if GEMPGameRules.GetNumActivePlayers() >= 2:
			self.WaitingForPlayers = False

	def OnCVarChanged( self, name, oldvalue, newvalue ):
		if name == "gg_numrounds":
			val = int( newvalue )
			val = -1 if val < -1 else val
			val = 10 if val > 10 else val
			self.RoundLimit = val

	def OnRoundBegin( self ):
		GEScenario.OnRoundBegin( self )

		GEMPGameRules.AllowRoundTimer( False )

		GEMPGameRules.DisableWeaponSpawns()
		GEMPGameRules.DisableAmmoSpawns()
		GEMPGameRules.DisableArmorSpawns()

		leadLevel = -1
		leadPlayer = None
		tie = False

		for player in GetPlayers():
			self.SetLevel( player, self.PlayerStartLevel )
			pL = self.GetLevel( player )

			if player.GetTeamNumber() != GEGlobal.TEAM_SPECTATOR:
				if pL > leadLevel:
					leadLevel = pL
					leadPlayer = player
					tie = False
				elif pL == leadLevel:
					tie = True

				self.pltracker.SetValue( player, self.TR_ACTIVE, True )
				self.pltracker.SetValue( player, self.TR_WASINPLAY, True )

				self.SetLevel( player, pL )
				self.PrintCurLevel( player )
				self.GivePlayerWeapons( player )
			else:
				# Ensure we start as "not in play"
				self.pltracker.SetValue( player, self.TR_WASINPLAY, False )

		if leadPlayer and leadLevel > 0 and leadLevel < iMaxLevel:
			if tie:
				GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "#GES_GP_GUNGAME_LEADER_TIE", str( leadLevel + 1 ) )
			else:
				GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "#GES_GP_GUNGAME_LEADER", player.GetPlayerName(), str( leadLevel + 1 ) )

		if not self.WaitingForPlayers and not self.warmupTimer.HadWarmup():
			if not self.warmupTimer.StartWarmup( int( GEUtil.GetCVarValue( "gg_warmup" ) ) ):
				self.RoundsPlayed += 1
		elif not self.WaitingForPlayers:
			self.RoundsPlayed += 1

	def OnRoundEnd( self ):
		for player in GetPlayers():
			self.pltracker.SetValue( player, self.TR_SHOWROUND, True )
			self.pltracker.SetValue( player, self.TR_WEAPSGIVEN, False )

	def OnPlayerConnect( self, player ):
		self.SetLevel( player, -1 )
		self.pltracker.SetValue( player, self.TR_ACTIVE, False )
		self.pltracker.SetValue( player, self.TR_SHOWROUND, True )
		self.pltracker.SetValue( player, self.TR_WASINPLAY, False )
		self.pltracker.SetValue( player, self.TR_WEAPSGIVEN, False )

	def OnPlayerSpawn( self, player ):
		self.GivePlayerWeapons( player )
		self.SetLevel( player, self.GetLevel( player ) )

		if player.IsInitialSpawn():
			GEUtil.PopupMessage( player, "#GES_GP_GUNGAME_NAME", "#GES_GPH_GUNGAME_GOAL" )

		if self.pltracker.GetValue( player, self.TR_SHOWROUND ):
			if not self.warmupTimer.IsInWarmup() and not self.WaitingForPlayers and self.RoundLimit > 0:
				self.pltracker.SetValue( player, self.TR_SHOWROUND, False )

				if self.RoundsPlayed < self.RoundLimit:
					GEUtil.HudMessage( player, _( "#GES_GP_GUNGAME_ROUNDCOUNT", self.RoundsPlayed, self.RoundLimit ), -1, 0.60, Color( 255, 255, 255, 255 ), 3.5 )
				else:
					GEUtil.HudMessage( player, "#GES_GP_GUNGAME_FINALROUND", -1, 0.60, Color( 206, 43, 43, 255 ), 3.5 )

	def CanPlayerChangeTeam( self, player, oldTeam, newTeam ):
		# If we were never in play give them starting level
		if not self.pltracker.GetValue( player, self.TR_WASINPLAY ):
			if GEUtil.GetCVarValue( "gg_avglevel" ) != "0":
				self.SetLevel( player, self.AvgLevel() )
			else:
				self.SetLevel( player, self.PlayerStartLevel )

		return True

	def OnPlayerKilled( self, victim, killer, weapon ):
		if self.WaitingForPlayers or self.warmupTimer.IsInWarmup():
			return

		# what exactly got killed?
		if not victim:
			return

		# Reset the victim getting their loadout
		self.pltracker.SetValue( victim, self.TR_WEAPSGIVEN, False )

		# death by world
		if not killer or not weapon:
			self.IncrementLevel( victim, -1 )
			return

		kId = killer.GetIndex()
		vId = victim.GetIndex()

		kL = self.GetLevel( killer )
		vL = self.GetLevel( victim )

		weapName = weapon.GetClassname().replace( 'weapon_', '' ).lower()

		if vId == kId:
			# Suicide drops our level
			self.IncrementLevel( killer, -1 )

		elif weapName == weapClassName[kL] or weapName == "knife" or weapName == "slappers":
			if weapName == "knife" and vL > 0:
				self.IncrementLevel( victim, -1 )
				GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "#GES_GP_GUNGAME_KNIFED", victim.GetCleanPlayerName() )
				GEUtil.EmitGameplayEvent( "gg_levelchange", "%i" % victim.GetUserID(), "%i" % ( self.GetLevel( victim ) + 1 ), "knifed" )

			if weapName == "slappers":
				if vL > 0:
					self.IncrementLevel( victim, -1 )
					GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "#GES_GP_GUNGAME_SLAPPED", victim.GetCleanPlayerName(), killer.GetCleanPlayerName() )
					GEUtil.EmitGameplayEvent( "gg_levelchange", "%i" % victim.GetUserID(), "%i" % ( self.GetLevel( victim ) + 1 ), "slapped" )
				else:
					GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "#GES_GP_GUNGAME_SLAPPED_NOLOSS", victim.GetCleanPlayerName(), killer.GetCleanPlayerName() )

				killer.SetArmor( int( GEGlobal.GE_MAX_ARMOR ) )

			self.IncrementLevel( killer, 1 )
			GEUtil.EmitGameplayEvent( "gg_levelchange", "%i" % killer.GetUserID(), "%i" % ( self.GetLevel( killer ) + 1 ) )

			if self.GetLevel( killer ) > iMaxLevel:
				GEMPGameRules.SetPlayerWinner( killer )
				if self.RoundLimit == -1 or self.RoundsPlayed < self.RoundLimit:
					GEMPGameRules.EndRound()
				else:
					GEMPGameRules.EndMatch()
			else:
				self.PrintCurLevel( killer )
				self.GivePlayerWeapons( killer )

	def OnThink( self ):
		# Check for insufficient player count
		if GEMPGameRules.GetNumActivePlayers() < 2:
			if not self.WaitingForPlayers:
				self.notice_WaitingForPlayers = 0
				GEMPGameRules.EndRound()
			elif GEUtil.GetTime() > self.notice_WaitingForPlayers:
				GEUtil.HudMessage( None, "#GES_GP_WAITING", -1, -1, GEUtil.Color( 255, 255, 255, 255 ), 2.5, 1 )
				self.notice_WaitingForPlayers = GEUtil.GetTime() + 12.5

			self.warmupTimer.Reset()
			self.WaitingForPlayers = True
			return
		elif self.WaitingForPlayers:
			self.WaitingForPlayers = False
			if not self.warmupTimer.HadWarmup():
				self.warmupTimer.StartWarmup( int( GEUtil.GetCVarValue( "gg_warmup" ) ), True )
				if self.warmupTimer.inWarmUp:
					GEUtil.EmitGameplayEvent( "gg_startwarmup" )
			else:
				GEMPGameRules.EndRound( False )

	def CanPlayerHaveItem( self, player, item ):
		weapon = GEWeapon.ToGEWeapon( item )
		if weapon:
			# Allow the default loadout to be given to the player before GivePlayerWeapons() is called
			if not self.pltracker.GetValue( player, self.TR_WEAPSGIVEN ):
				return True

			name = weapon.GetClassname().replace( 'weapon_', '' ).lower()

			pL = self.pltracker.GetValue( player, self.TR_LEVEL )

			if pL < 0 or pL > iMaxLevel:
				return True

			if  name == weapList[pL] or name == "knife" or name == "slappers":
				return True

			return False

		return True

	def OnPlayerSay( self, player, text ):
		if text == "!level":
			self.PrintCurLevel( player )
			return True

		elif text == "!weapons":
			self.PrintWeapons( player )
			return True

		elif text == "!commands":
			self.PrintCommands( player )
			return True

		return False

#-------------------#
# Utility Functions #
#-------------------#

	def GetLevel( self, player ):
		if not player:
			return -1
		return self.pltracker.GetValue( player, self.TR_LEVEL )

	def SetLevel( self, player, lvl ):
		if not player:
			return
		# Bound us!
		lvl = 0 if lvl < 0 else lvl

		# Set Level
		self.pltracker.SetValue( player, self.TR_LEVEL, lvl )
		# Set Score
		player.SetScore( lvl + 1 )

	def IncrementLevel( self, player, amt ):
		self.SetLevel( player, self.pltracker.GetValue( player, self.TR_LEVEL ) + amt )

	def PrintCurLevel( self, player ):
		lvl = self.GetLevel( player )
		if not player or lvl > iMaxLevel:
			return

		if lvl >= 0:
			weapName = GEWeapon.WeaponPrintName( "weapon_%s" % weapList[lvl] )
			GEUtil.ClientPrint( player, GEGlobal.HUD_PRINTTALK, "%s1 %s2", "^lLevel %i: ^y" % ( lvl + 1 ), "%s" % ( weapName ) )

		else:
			GEUtil.ClientPrint( player, GEGlobal.HUD_PRINTTALK, "^lYou are not in play" )


	def GivePlayerWeapons( self, player ):
		if not player:
			return

		lvl = self.GetLevel( player )
		if player.IsDead() or lvl < 0 or lvl > iMaxLevel:
			return

		player.StripAllWeapons()

		player.GiveNamedWeapon( "weapon_slappers", 0 )
		player.GiveNamedWeapon( "weapon_knife", 0 )

		curWeap = "weapon_%s" % weapList[lvl]

		if lvl != iMaxLevel + 1:
			if curWeap == "weapon_grenade":
				player.GiveNamedWeapon( curWeap, 1 )
			else:
				player.GiveNamedWeapon( curWeap, 90 )

			player.WeaponSwitch( curWeap )

		self.pltracker.SetValue( player, self.TR_WEAPSGIVEN, True )

	def AvgLevel( self ):
		level = 0
		count = 0

		for i in range( 32 ):
			if not GEPlayer.IsValidPlayerIndex( i ):
				continue
			player = GEPlayer.GetMPPlayer( i )

			if player.GetTeamNumber() != GEGlobal.TEAM_SPECTATOR and self.GetLevel( player ) != -1:
				level = level + self.GetLevel( player )
				count += 1

		if count == 0:
			return 0

		return int( level / count )

	def PrintWeapons( self, player ):
		if not player:
			return

		GEUtil.ClientPrint( player, GEGlobal.HUD_PRINTTALK, "^l----------------------------------------------------" )
		GEUtil.ClientPrint( player, GEGlobal.HUD_PRINTTALK, "         GunGame Weapons Order" )
		GEUtil.ClientPrint( player, GEGlobal.HUD_PRINTTALK, "^l----------------------------------------------------" )

		for i in range( iMaxLevel ):
			GEUtil.ClientPrint( player, GEGlobal.HUD_PRINTTALK, "%i: %s" % ( i + 1, weapList[i].replace( '_', ' ' ).capitalize() ) )

		GEUtil.ClientPrint( player, GEGlobal.HUD_PRINTTALK, "^l----------------------------------------------------" )

	def PrintCommands( self, player ):
		if not player:
			return

		GEUtil.ClientPrint( player, GEGlobal.HUD_PRINTTALK, "^l-------------------------------------" )
		GEUtil.ClientPrint( player, GEGlobal.HUD_PRINTTALK, "Type !level for current level" )
		GEUtil.ClientPrint( player, GEGlobal.HUD_PRINTTALK, "Type !weapons for weapon order" )
		GEUtil.ClientPrint( player, GEGlobal.HUD_PRINTTALK, "^l-------------------------------------" )
