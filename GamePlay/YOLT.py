from . import GEScenario
from GamePlay.Utils.GEPlayerTracker import GEPlayerTracker
import GEEntity, GEPlayer, GEUtil, GEWeapon, GEMPGameRules, GEGlobal

USING_API = GEGlobal.API_VERSION_1_0_0

#For some odd reason, you only live twice...
class YOLT( GEScenario ):
	TR_ELIMINATED = "eliminated";
	TR_SPAWNED = "spawned";

	def __init__( self ):
		GEScenario.__init__( self )

		self.waitingForPlayers = False
		self.radarSet = False
		self.dmBounty = 0
		self.mi6Bounty = 0
		self.janusBounty = 0
		self.pltracker = GEPlayerTracker( self )

	def GetTeamPlay( self ):
		return GEGlobal.TEAMPLAY_TOGGLE

	def Cleanup( self ):
		GEScenario.Cleanup( self )
		self.pltracker = None

	def GetPrintName( self ):
		return "#GES_GP_YOLT_NAME"

	def GetScenarioHelp( self, help_obj ):
		help_obj.SetDescription( "#GES_GP_YOLT_HELP" )

	def GetGameDescription( self ):
		if GEMPGameRules.IsTeamplay():
			return "Team YOLT"
		else:
			return "YOLT"

	def OnPlayerConnect( self, player ):
		self.pltracker.SetValue( player, self.TR_SPAWNED, False )
		if GEMPGameRules.IsRoundLocked():
			# Immediately eliminate the player if the round is locked
			self.pltracker.SetValue( player, self.TR_ELIMINATED, True )

	def OnPlayerDisconnect( self, player ):
		if GEMPGameRules.IsRoundLocked() and player.GetDeaths() < 2 and player.GetTeamNumber() != GEGlobal.TEAM_SPECTATOR:
			self.UpdatePlayerBounty( player )

	def CanPlayerChangeTeam( self, player, oldTeam, newTeam ):
		if GEMPGameRules.IsRoundLocked():
			if  self.IsInPlay( player ) and oldTeam != GEGlobal.TEAM_SPECTATOR:
				self.UpdatePlayerBounty( player )
			elif oldTeam == GEGlobal.TEAM_SPECTATOR:
				GEUtil.PopupMessage( player, "#GES_GPH_CANTJOIN_TITLE", "#GES_GPH_CANTJOIN", "", 5.0, False )
			else:
				GEUtil.PopupMessage( player, "#GES_GPH_ELIMINATED_TITLE", "#GES_GPH_ELIMINATED", "", 5.0, False )

			# Changing teams will automatically eliminate you
			self.pltracker.SetValue( player, self.TR_ELIMINATED, True )

		return True

	def OnPlayerSpawn( self, player ):
		# Record us as "spawned"
		if player.GetTeamNumber() != GEGlobal.TEAM_SPECTATOR:
			self.pltracker.SetValue( player, self.TR_SPAWNED, True )

		if player.IsInitialSpawn():
			# If we spawned mid-round let them know why they can't play
			if not self.IsInPlay( player ):
				GEUtil.PopupMessage( player, "#GES_GPH_CANTJOIN_TITLE", "#GES_GPH_CANTJOIN" )

			GEUtil.PopupMessage( player, "#GES_GP_YOLT_NAME", "#GES_GPH_YOLT_GOAL" )

	def OnRoundBegin( self ):
		self.radarSet = False;
		GEMPGameRules.GetRadar().SetForceRadar( False );

		self.dmBounty = 0
		self.mi6Bounty = 0
		self.janusBounty = 0

		for i in range( 32 ):
			if not GEPlayer.IsValidPlayerIndex( i ):
				continue
			self.pltracker.SetValue( GEPlayer.GetMPPlayer( i ), self.TR_ELIMINATED, False )

		GEMPGameRules.UnlockRound();
		GEMPGameRules.ResetAllPlayerDeaths();
		GEMPGameRules.ResetAllPlayersScores();

	def OnRoundEnd( self ):
		GEMPGameRules.GetRadar().DropAllContacts()
		GEUtil.RemoveHudProgressBar( None, 0 )

	def OnPlayerKilled( self, victim, killer, weapon ):
		GEScenario.OnPlayerKilled( self, victim, killer, weapon )

		if not victim:
			return

		if not self.waitingForPlayers and victim.GetDeaths() >= 2:
			GEMPGameRules.LockRound()
			GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "#GES_GP_YOLT_ELIMINATED", victim.GetPlayerName() )
			GEUtil.EmitGameplayEvent( "yolt_eliminated", "%i" % victim.GetUserID(), "%i" % ( killer.GetUserID() if killer else -1 ) )
			GEUtil.PopupMessage( victim, "#GES_GPH_ELIMINATED_TITLE", "#GES_GPH_ELIMINATED" )

			# Officially eliminate the player
			self.pltracker.SetValue( victim, self.TR_ELIMINATED, True )
			# Initialize the bounty (if we need to)
			self.InitializePlayerBounty()
			# Update the bounty
			self.UpdatePlayerBounty( victim )

	def OnThink( self ):
		if GEMPGameRules.GetNumActivePlayers() < 2:
			GEMPGameRules.UnlockRound()
			self.waitingForPlayers = True
			return

		if self.waitingForPlayers:
			self.waitingForPlayers = False
			GEUtil.HudMessage( None, "#GES_GP_GETREADY", -1, -1, GEUtil.CColor( 255, 255, 255, 255 ), 2.5 )
			GEMPGameRules.EndRound( False )

		#Check to see if the round is over!
		if GEMPGameRules.IsTeamplay():
			#check to see if each team has a player...
			iMI6Players = []
			iJanusPlayers = []

			for i in range( 32 ):
				if not GEPlayer.IsValidPlayerIndex( i ):
					continue

				player = GEPlayer.GetMPPlayer( i )
				if self.IsInPlay( player ):
					if player.GetTeamNumber() == GEGlobal.TEAM_MI6:
						iMI6Players.append( player )
					elif player.GetTeamNumber() == GEGlobal.TEAM_JANUS:
						iJanusPlayers.append( player )

			numMI6Players = len( iMI6Players )
			numJanusPlayers = len( iJanusPlayers )

			if numMI6Players == 0 and numJanusPlayers == 0:
				GEMPGameRules.EndRound()

			elif numMI6Players == 0 and numJanusPlayers > 0:
				janus = GEMPGameRules.GetTeam( GEGlobal.TEAM_JANUS )
				janus.IncrementMatchScore( 5 )
				GEMPGameRules.SetTeamWinner( janus )
				GEMPGameRules.EndRound()

			elif numMI6Players > 0 and numJanusPlayers == 0:
				mi6 = GEMPGameRules.GetTeam( GEGlobal.TEAM_MI6 )
				mi6.IncrementMatchScore( 5 )
				GEMPGameRules.SetTeamWinner( mi6 )
				GEMPGameRules.EndRound()

			elif not self.radarSet and numMI6Players == 1 and numJanusPlayers == 1:
				#Add the two players as always visible on the radar
				radar = GEMPGameRules.GetRadar()
				radar.SetForceRadar( True )
				radar.AddRadarContact( iMI6Players[0], GEGlobal.RADAR_TYPE_PLAYER, True )
				radar.AddRadarContact( iJanusPlayers[0], GEGlobal.RADAR_TYPE_PLAYER, True )
				self.radarSet = True
		else:
			#Check to see if more than one player is around
			iPlayers = []

			for i in range( 32 ):
				if not GEPlayer.IsValidPlayerIndex( i ):
					continue

				player = GEPlayer.GetMPPlayer( i )
				if self.IsInPlay( player ):
					iPlayers.append( player )

			numPlayers = len( iPlayers )

			if numPlayers == 0:
				#This shouldn't happen, but just in case it does we don't want to overflow the vector...
				GEMPGameRules.EndRound()
			if numPlayers == 1:
				GEMPGameRules.SetPlayerWinner( iPlayers[0] )
				GEMPGameRules.EndRound()
			elif not self.radarSet and numPlayers == 2:
				#Add the two players as always visible on the radar
				radar = GEMPGameRules.GetRadar()
				radar.SetForceRadar( True )
				radar.AddRadarContact( iPlayers[0], GEGlobal.RADAR_TYPE_PLAYER, True )
				radar.AddRadarContact( iPlayers[1], GEGlobal.RADAR_TYPE_PLAYER, True )
				self.radarSet = True

	def CanPlayerRespawn( self, player ):
		if self.pltracker.GetValue( player, self.TR_ELIMINATED ) and GEMPGameRules.IsRoundLocked():
			player.SetScoreBoardColor( GEGlobal.SB_COLOR_ELIMINATED )
			return False

		player.SetScoreBoardColor( GEGlobal.SB_COLOR_NORMAL )
		return True

	def InitializePlayerBounty( self ):
		if GEMPGameRules.IsTeamplay() and self.mi6Bounty == 0 and self.janusBounty == 0:
			self.mi6Bounty = GEMPGameRules.GetNumInRoundTeamPlayers( GEGlobal.TEAM_MI6 )
			self.janusBounty = GEMPGameRules.GetNumInRoundTeamPlayers( GEGlobal.TEAM_JANUS )

			GEUtil.InitHudProgressBar( GEGlobal.TEAM_MI6, 0, "Foes: ", GEGlobal.HUDPB_SHOWVALUE, self.janusBounty, -1, 0.02, 0, 10, GEUtil.CColor( 206, 43, 43, 255 ) )
			GEUtil.InitHudProgressBar( GEGlobal.TEAM_JANUS, 0, "Foes: ", GEGlobal.HUDPB_SHOWVALUE, self.mi6Bounty, -1, 0.02, 0, 10, GEUtil.CColor( 100, 184, 234, 220 ) )

		elif not GEMPGameRules.IsTeamplay() and self.dmBounty == 0:
			self.dmBounty = GEMPGameRules.GetNumInRoundPlayers() - 1
			GEUtil.InitHudProgressBar( None, 0, "Foes: ", GEGlobal.HUDPB_SHOWVALUE, self.dmBounty, -1, 0.02, 0, 10, GEUtil.CColor( 170, 170, 170, 220 ) )

	def UpdatePlayerBounty( self, victim ):
		if GEMPGameRules.IsTeamplay():
			if victim.GetTeamNumber() == GEGlobal.TEAM_JANUS:
				self.janusBounty -= 1
			else:
				self.mi6Bounty -= 1

			GEUtil.UpdateHudProgressBar( GEGlobal.TEAM_MI6, 0, self.janusBounty )
			GEUtil.UpdateHudProgressBar( GEGlobal.TEAM_JANUS, 0, self.mi6Bounty )
		else:
			self.dmBounty -= 1

			# Remember, we take 1 off to account for the local player
			GEUtil.UpdateHudProgressBar( None, 0, self.dmBounty )

	def IsInPlay( self, player ):
		return player.GetTeamNumber() != GEGlobal.TEAM_SPECTATOR and self.pltracker.GetValue( player, self.TR_SPAWNED ) and not self.pltracker.GetValue( player, self.TR_ELIMINATED )
