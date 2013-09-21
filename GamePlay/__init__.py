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
from GEGamePlay import CBaseScenario, CScenarioHelp
import GEGlobal, GEEntity, GEPlayer, GEUtil, GEWeapon, GEMPGameRules

class GEScenarioHelp( CScenarioHelp ):
	pass

class GEScenario( CBaseScenario ):
	def __init__( self ):
		super( GEScenario, self ).__init__()
		self.ClearEventHooks()

	def __del__( self ):
		# Uncomment the below line to confirm that your python scenarios are being deleted!
		# GEUtil.Warning( "Python Scenario Deleted!\n" )
		pass

	# DO NOT OVERRIDE THESE FUNCTIONS
	def RegisterEventHook( self, hook, func ):
		if not self.__hooks.has_key( hook ):
			self.__hooks[hook] = []

		# Make sure we don't double register
		if self.__hooks[hook].count( func ) == 0:
			self.__hooks[hook].append( func )

	def CallEventHooks( self, hook, args=() ):
		if self.__hooks.has_key( hook ):
			for func in self.__hooks[hook]:
				func( *args )

	def ClearEventHooks( self ):
		self.__hooks = {}
	# END RESTRICTIONS


	def GetGameDescription( self ):
		raise NameError

	def GetPrintName( self ):
		raise NameError

	def GetTeamPlay( self ):
		return GEGlobal.TEAMPLAY_NONE

	def GetScenarioHelp( self, help_obj ):
		'''
		@type help_obj: GEGamePlay.CScenarioHelp
		'''
		pass

	def OnLoadGamePlay( self ):
		pass

	def OnUnloadGamePlay( self ):
		self.ClearEventHooks()

	def OnPlayerConnect( self, player ):
		pass

	def OnPlayerDisconnect( self, player ):
		pass

	def OnThink( self ):
		pass

	def OnCVarChanged( self, name, oldvalue, newvalue ):
		pass

	def OnRoundBegin( self ):
		"""Called after the world reloads and prior to players being spawned"""
		# Reset player's scores
		GEMPGameRules.ResetAllPlayersScores()

	def OnRoundEnd( self ):
		"""Called once the round time ends and prior to scoring calculations"""
		pass

	def OnPlayerSpawn( self, player ):
		"""Called when a player spawns into the game world (ie, not spectating)"""
		pass

	def OnPlayerObserver( self, player ):
		"""Called when a player enters observer mode"""
		pass

	def OnPlayerKilled( self, victim, killer, weapon ):
		"""Default Deathmatch style scoring"""
		if not victim:
			return

		if not killer or victim == killer:
			# World kill or suicide
			victim.AddRoundScore( -1 )
		elif GEMPGameRules.IsTeamplay() and killer.GetTeamNumber() == victim.GetTeamNumber():
			# Same-team kill
			GEMPGameRules.GetTeam( killer.GetTeamNumber() ).AddRoundScore( -1 )
			killer.AddRoundScore( -1 )
		else:
			# Normal kill
			GEMPGameRules.GetTeam( killer.GetTeamNumber() ).AddRoundScore( 1 )
			killer.AddRoundScore( 1 )

	def CanPlayerRespawn( self, player ):
		return True

	def CanPlayerChangeChar( self, player, ident ):
		return True

	def CanPlayerChangeTeam( self, player, oldteam, newteam ):
		return True

	def CanPlayerHaveItem( self, player, weapon ):
		return True

	def OnPlayerSay( self, player, text ):
		return False

	def ShouldForcePickup( self, player, entity ):
		return False

	def CalculateCustomDamage( self, victim, info, health, armor ):
		return health, armor

	def CanRoundEnd( self ):
		return True

	def CanMatchEnd( self ):
		return True

	def OnTokenSpawned( self, token ):
		pass

	def OnTokenRemoved( self, token ):
		pass

	def OnTokenPicked( self, token, player ):
		pass

	def OnTokenDropped( self, token, player ):
		pass

	def OnTokenAttack( self, token, player, position, direction ):
		pass

	def OnCaptureAreaSpawned( self, area ):
		pass

	def OnCaptureAreaRemoved( self, area ):
		pass

	def OnCaptureAreaEntered( self, area, player, token ):
		pass

	def OnCaptureAreaExited( self, area, player ):
		pass
