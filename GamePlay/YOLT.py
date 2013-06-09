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
from .Utils import GetPlayers
from .Utils.GEPlayerTracker import GEPlayerTracker
from GEUtil import Color
import GEUtil, GEMPGameRules as GERules, GEGlobal as Glb

USING_API = Glb.API_VERSION_1_1_0

TR_ELIMINATED = "eliminated"
TR_SPAWNED = "spawned"

CLR_MI6_BOUNTY = Color( 100, 184, 234, 220 )
CLR_JANUS_BOUNTY = Color( 206, 43, 43, 255 )
CLR_DM_BOUNTY = Color( 170, 170, 170, 220 )

# For some odd reason, you only live twice...
class YOLT( GEScenario ):
	def __init__( self ):
		GEScenario.__init__( self )

		self.pltracker = GEPlayerTracker( self )

		self.game_inWaitTime = False
		self.game_bounty_orig = None
		self.game_bounty = None

	def GetTeamPlay( self ):
		return Glb.TEAMPLAY_TOGGLE

	def Cleanup( self ):
		GEScenario.Cleanup( self )
		self.pltracker = None

	def GetPrintName( self ):
		return "#GES_GP_YOLT_NAME"

	def GetScenarioHelp( self, help_obj ):
		help_obj.SetDescription( "#GES_GP_YOLT_HELP" )

	def GetGameDescription( self ):
		if GERules.IsTeamplay():
			return "Team YOLT"
		else:
			return "YOLT"

	def OnLoadGamePlay( self ):
		if GERules.GetNumActivePlayers() < 2:
			self.game_inWaitTime = True

	def OnPlayerConnect( self, player ):
		self.pltracker[player][TR_SPAWNED] = False
		self.pltracker[player][TR_ELIMINATED] = True

	def OnPlayerDisconnect( self, player ):
		if GERules.IsRoundLocked() and self.yolt_IsInPlay( player ):
			self.yolt_DecreaseBounty( player )

	def CanPlayerChangeTeam( self, player, oldTeam, newTeam ):
		if GERules.IsRoundLocked():
			if self.yolt_IsInPlay( player ):
				self.yolt_DecreaseBounty( player )

			if oldTeam == Glb.TEAM_SPECTATOR:
				GEUtil.PopupMessage( player, "#GES_GPH_CANTJOIN_TITLE", "#GES_GPH_CANTJOIN" )
			else:
				GEUtil.PopupMessage( player, "#GES_GPH_ELIMINATED_TITLE", "#GES_GPH_ELIMINATED" )

		# Changing teams will automatically eliminate you
		self.pltracker[player][TR_ELIMINATED] = True

		return True

	def OnPlayerSpawn( self, player ):
		# Update our tracker variables
		self.pltracker[player][TR_SPAWNED] = True
		self.pltracker[player][TR_ELIMINATED] = False

		if player.IsInitialSpawn():
			# Simple help message
			GEUtil.PopupMessage( player, "#GES_GP_YOLT_NAME", "#GES_GPH_YOLT_GOAL" )

	def OnPlayerObserver( self, player ):
		# Init the tracking bars
		self.yolt_InitObserverBars( player )

	def OnRoundBegin( self ):
		super( YOLT, self ).OnRoundBegin()

		# Remove latent bars
		GEUtil.RemoveHudProgressBar( None, 0 )
		GEUtil.RemoveHudProgressBar( None, 1 )

		GERules.UnlockRound()
		GERules.GetRadar().SetForceRadar( False )

		self.game_bounty_orig = None
		self.game_bounty = None

	def OnPlayerKilled( self, victim, killer, weapon ):
		# Execute default DM scoring behavior
		GEScenario.OnPlayerKilled( self, victim, killer, weapon )

		if not victim:
			return

		if not self.game_inWaitTime and victim.GetDeaths() >= 2:
			# Lock the round (if not done already)
			GERules.LockRound()

			# Tell everyone who was eliminated
			GEUtil.ClientPrint( None, Glb.HUD_PRINTTALK, "#GES_GP_YOLT_ELIMINATED", victim.GetPlayerName() )
			# Tell plugins who was eliminated
			GEUtil.EmitGameplayEvent( "yolt_eliminated", str( victim.GetUserID() ), str( killer.GetUserID() if killer else -1 ) )
			# Tell the victim they are eliminated
			GEUtil.PopupMessage( victim, "#GES_GPH_ELIMINATED_TITLE", "#GES_GPH_ELIMINATED" )

			# Decrease the bounty, eliminate the victim
			self.yolt_DecreaseBounty( victim )

	def OnThink( self ):
		# If less than 2 players enter "wait mode"
		if GERules.GetNumActivePlayers() < 2:
			if not self.game_inWaitTime:
				GERules.EndRound()

			self.game_inWaitTime = True
			return

		# If we get here and we are in "wait mode" than we have enough players to play!
		if self.game_inWaitTime:
			self.game_inWaitTime = False
			GEUtil.HudMessage( None, "#GES_GP_GETREADY", -1, -1, Color( 255, 255, 255, 255 ), 2.5 )
			GERules.EndRound( False )

	def CanPlayerRespawn( self, player ):
		if GERules.IsRoundLocked() and self.pltracker[player][TR_ELIMINATED]:
			player.SetScoreBoardColor( Glb.SB_COLOR_ELIMINATED )
			return False

		player.SetScoreBoardColor( Glb.SB_COLOR_NORMAL )
		return True

	def yolt_InitBounty( self ):
		if self.game_bounty_orig:
			# We are already init'd
			return

		if GERules.IsTeamplay():
			mi6_count = GERules.GetNumInRoundTeamPlayers( Glb.TEAM_MI6 )
			janus_count = GERules.GetNumInRoundTeamPlayers( Glb.TEAM_JANUS )
			# Team bounty is a list: [mi6, janus]
			self.game_bounty_orig = [ mi6_count, janus_count ]

			# Display the bounty progress bars (note color and values are swapped since these are "foes")
			GEUtil.InitHudProgressBar( Glb.TEAM_MI6_NO_OBS, 0, "#GES_GP_FOES", Glb.HUDPB_SHOWVALUE, janus_count, -1, 0.02, 0, 10, CLR_JANUS_BOUNTY )
			GEUtil.InitHudProgressBar( Glb.TEAM_JANUS_NO_OBS, 0, "#GES_GP_FOES", Glb.HUDPB_SHOWVALUE, mi6_count, -1, 0.02, 0, 10, CLR_MI6_BOUNTY )
		else:
			# DM bounty is just a number
			self.game_bounty_orig = GERules.GetNumInRoundPlayers()
			# We subtract 1 here to account for the local player (prevents "1 / X" at win)
			GEUtil.InitHudProgressBar( Glb.TEAM_NO_OBS, 0, "#GES_GP_FOES", Glb.HUDPB_SHOWVALUE, self.game_bounty_orig - 1, -1, 0.02, 0, 10, CLR_DM_BOUNTY )

		# Copy our origin into the tracker
		self.game_bounty = self.game_bounty_orig

		# Initialize observer bars
		self.yolt_InitObserverBars( Glb.TEAM_OBS )

	def yolt_DecreaseBounty( self, victim ):
		# Init the bounty if needed
		if not self.game_bounty_orig:
			self.yolt_InitBounty()

		# Mark the victim as eliminated
		self.pltracker[victim][TR_ELIMINATED] = True

		if GERules.IsTeamplay():
			# Team bounty is ( mi6, janus )
			if victim.GetTeamNumber() == Glb.TEAM_MI6:
				self.game_bounty[0] -= 1
			else:
				self.game_bounty[1] -= 1

			# Update non-observers (note the reversal of scores)
			GEUtil.UpdateHudProgressBar( Glb.TEAM_MI6_NO_OBS, 0, self.game_bounty[1] )
			GEUtil.UpdateHudProgressBar( Glb.TEAM_JANUS_NO_OBS, 0, self.game_bounty[0] )

			# Update observers
			GEUtil.UpdateHudProgressBar( Glb.TEAM_OBS, 0, self.game_bounty[0] )
			GEUtil.UpdateHudProgressBar( Glb.TEAM_OBS, 1, self.game_bounty[1] )
		else:
			# DM bounty is just a number
			self.game_bounty -= 1
			# We subtract 1 here to account for the local player (prevents "1 / X" at win)
			GEUtil.UpdateHudProgressBar( Glb.TEAM_NO_OBS, 0, self.game_bounty - 1 )
			# Update observers, we don't subtract 1 anymore
			GEUtil.UpdateHudProgressBar( Glb.TEAM_OBS, 0, self.game_bounty )

		# Check if we have a winner
		self.yolt_CheckWin()

	def yolt_CheckWin( self ):
		if not self.game_bounty:
			return

		if GERules.IsTeamplay():
			# Default no winner
			winner = None
			if self.game_bounty[0] <= 0:
				# MI6 has no bounty, Janus won
				winner = GERules.GetTeam( Glb.TEAM_JANUS )
			elif self.game_bounty[1] <= 0:
				# Janus has no bounty, MI6 won
				winner = GERules.GetTeam( Glb.TEAM_MI6 )
			elif self.game_bounty[0] == 1 and self.game_bounty[1] == 1:
				# When we are down to 1 player on each team, force show the radar
				GERules.GetRadar().SetForceRadar( True )

			if winner:
				winner.AddMatchScore( 5 )
				GERules.SetTeamWinner( winner )
				GERules.EndRound()
		else:
			# DM uses a number
			if self.game_bounty <= 1:
				# There is only 1 player left, find who that is
				for player in GetPlayers():
					if self.yolt_IsInPlay( player ):
						GERules.SetPlayerWinner( player )
						break
				# Round is over
				GERules.EndRound()
			elif self.game_bounty == 2:
				GERules.GetRadar().SetForceRadar( True )

	def yolt_InitObserverBars( self, player ):
		# We don't init if there is no bounty
		if not self.game_bounty:
			return

		# Remove latent bars
		GEUtil.RemoveHudProgressBar( player, 0 )
		GEUtil.RemoveHudProgressBar( player, 1 )

		# Initialize and update
		if GERules.IsTeamplay():
			GEUtil.InitHudProgressBar( player, 0, "##TEAM_MI6: ", Glb.HUDPB_SHOWVALUE, self.game_bounty_orig[0], 0.35, 0.14, 0, 10, CLR_MI6_BOUNTY, self.game_bounty[0] )
			GEUtil.InitHudProgressBar( player, 1, "##TEAM_JANUS: ", Glb.HUDPB_SHOWVALUE, self.game_bounty_orig[1], 0.5, 0.14, 0, 10, CLR_JANUS_BOUNTY, self.game_bounty[1] )
		else:
			GEUtil.InitHudProgressBar( player, 0, "#GES_GP_FOES", Glb.HUDPB_SHOWVALUE, self.game_bounty_orig, -1, 0.14, 0, 10, CLR_DM_BOUNTY, self.game_bounty )

	def yolt_IsInPlay( self, player ):
		try:
			return player.GetTeamNumber() != Glb.TEAM_SPECTATOR 	\
					and self.pltracker[player][TR_SPAWNED] 			\
					and not self.pltracker[player][TR_ELIMINATED]
		except KeyError:
			pass
