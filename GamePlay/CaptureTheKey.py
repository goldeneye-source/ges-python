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
from GamePlay import GEScenario, GEScenarioHelp
from Utils import OppositeTeam, _
from Utils.GEOvertime import GEOvertime
from Utils.GETimer import EndRoundCallback, TimerTracker, Timer
from Utils.GEWarmUp import GEWarmUp
import GEEntity, GEPlayer, GEUtil, GEWeapon, GEMPGameRules as GERules, GEGlobal as Glb

USING_API = Glb.API_VERSION_1_1_0
FL_DEBUG = False

class Token:
	def __init__( self ):
		self.hent = GEEntity.EHANDLE( None )
		self.next_drop_time = 0

	def GetOwner( self ):
		if self.hent.Get():
			return self.hent.Get().GetPlayerOwner()
		else:
			return None

# -----------------------
# BEGIN CAPTURE THE KEY
#   CLASS DEFINITION
# -----------------------
class CaptureTheKey( GEScenario ):
	# Static Defines
	( PROBAR_MI6, PROBAR_JANUS, PROBAR_OVERRIDE ) = range( 1, 4 )
	( MSG_JANUS_CHANNEL, MSG_MI6_CHANNEL, MSG_MISC_CHANNEL ) = range( 3 )

	MSG_JANUS_YPOS 		 = 0.71
	MSG_MI6_YPOS 		 = 0.75
	MSG_MISC_YPOS 		 = 0.67

	OVERTIME_DELAY		 = 3.0

	CVAR_CAPOVERRIDE	 = "ctk_capture_override_time"
	CVAR_CAPPOINTS		 = "ctk_player_capture_points"
	CVAR_SPEEDMULT		 = "ctk_player_speed_mult"
	CVAR_WARMUP			 = "ctk_warmup_time"

	TOKEN_MI6 			 = 'token_mi6'
	TOKEN_JANUS 		 = 'token_janus'

	COLOR_NEUTRAL		 = GEUtil.Color( 220, 220, 220, 255 )

	COLOR_MI6_GLOW 		 = GEUtil.Color( 14, 139, 237, 200 )
	COLOR_MI6_RADAR 	 = GEUtil.Color( 94, 171, 231, 255 )
	COLOR_MI6_OBJ_COLD	 = GEUtil.Color( 94, 171, 231, 150 )
	COLOR_MI6_OBJ_HOT	 = GEUtil.Color( 94, 171, 231, 235 )

	COLOR_JANUS_GLOW 	 = GEUtil.Color( 224, 18, 18, 200 )
	COLOR_JANUS_RADAR 	 = GEUtil.Color( 206, 43, 43, 255 )
	COLOR_JANUS_OBJ_COLD = GEUtil.Color( 206, 43, 43, 150 )
	COLOR_JANUS_OBJ_HOT = GEUtil.Color( 206, 43, 43, 235 )

	( COLOR_RADAR, COLOR_OBJ_COLD, COLOR_OBJ_HOT ) = range( 3 )

	TAG = "[CTK]"

	def __init__( self ):
		super( CaptureTheKey, self ).__init__()
		# Create trackers and utilities
		self.warmupTimer = GEWarmUp( self )
		self.timerTracker = TimerTracker( self )
		self.overtime 	 = GEOvertime()

		# Initialize base elements
		self.game_tokens = { Glb.TEAM_MI6 : Token(), Glb.TEAM_JANUS : Token() }
		self.game_timers = {}

	def Cleanup( self ):
		super( CaptureTheKey, self ).Cleanup()
		self.game_timers = None
		self.warmupTimer = None
		self.timerTracker = None
		self.overtime = None

	def GetPrintName( self ):
		return "#GES_GP_CAPTUREKEY_NAME"

	def GetScenarioHelp( self, help_obj ):
		assert isinstance( help_obj, GEScenarioHelp )

		help_obj.SetInfo( "#GES_GPH_CTK_TAGLINE", "http://wiki.geshl2.com/Capture_The_Key" )
		help_obj.SetDescription( "#GES_GP_CAPTUREKEY_HELP" )

		pane = help_obj.AddPane( "ctk" )
		help_obj.AddHelp( pane, "ctk_objectives", "#GES_GPH_CTK_OBJECTIVES" )
		help_obj.AddHelp( pane, "ctk_radar", "#GES_GPH_CTK_RADAR" )

	def GetGameDescription( self ):
		return "Capture The Key"

	def GetTeamPlay( self ):
		return Glb.TEAMPLAY_ALWAYS

	def OnLoadGamePlay( self ):
		# Precache our models
		GEUtil.PrecacheModel( "models/gameplay/capturepoint.mdl" )

		# Ensure our sounds are precached
		GEUtil.PrecacheSound( "GEGamePlay.Overtime" )
		GEUtil.PrecacheSound( "GEGamePlay.Token_Grab" )
		GEUtil.PrecacheSound( "GEGamePlay.Token_Grab_Enemy" )
		GEUtil.PrecacheSound( "GEGamePlay.Token_Capture_Friend" )
		GEUtil.PrecacheSound( "GEGamePlay.Token_Capture_Enemy" )
		GEUtil.PrecacheSound( "GEGamePlay.Token_Drop_Friend" )
		GEUtil.PrecacheSound( "GEGamePlay.Token_Drop_Enemy" )

		# Setup our tokens
		tokenmgr = GERules.GetTokenMgr()

		# MI6 Team Token Definition
		tokenmgr.SetupToken( self.TOKEN_MI6, limit=1, team=Glb.TEAM_MI6,
							location=Glb.SPAWN_TOKEN | Glb.SPAWN_OTHERTEAM,
							glow_color=self.COLOR_MI6_GLOW, glow_dist=450.0,
							allow_switch=False, respawn_delay=20,
							view_model="models/weapons/tokens/v_briefcasetoken.mdl",
							world_model="models/weapons/tokens/w_briefcasetoken.mdl",
							print_name="#GES_GP_CTK_BRIEFCASE" )

		# Janus Team Token Definition
		tokenmgr.SetupToken( self.TOKEN_JANUS, limit=1, team=Glb.TEAM_JANUS,
							location=Glb.SPAWN_TOKEN | Glb.SPAWN_OTHERTEAM,
							glow_color=self.COLOR_JANUS_GLOW, glow_dist=450.0,
							allow_switch=False, respawn_delay=20,
							print_name="#GES_GP_CTK_KEY" )

		# Setup the capture areas
		tokenmgr.SetupCaptureArea( "capture_mi6", model="models/gameplay/capturepoint.mdl", skin=1,
								limit=1, location=Glb.SPAWN_CAPAREA | Glb.SPAWN_MYTEAM,
								rqd_token=self.TOKEN_MI6, rqd_team=Glb.TEAM_MI6 )

		tokenmgr.SetupCaptureArea( "capture_janus", model="models/gameplay/capturepoint.mdl", skin=2,
								limit=1, location=Glb.SPAWN_CAPAREA | Glb.SPAWN_MYTEAM,
								rqd_token=self.TOKEN_JANUS, rqd_team=Glb.TEAM_JANUS )

		# Reset variables
		self.game_inWaitTime	 = True
		self.game_inWarmup  	 = True
		self.game_inOvertime  	 = False
		self.game_inOvertimeDelay = False
		self.game_canFinishRound = True

		# Clear the timer list
		self.timerTracker.RemoveTimer()

		# Create the MI6 delay timer
		self.game_timers[Glb.TEAM_MI6] = self.timerTracker.CreateTimer( "ctk_mi6" )
		self.game_timers[Glb.TEAM_MI6].SetAgeRate( 1.2, 1.5 )
		self.game_timers[Glb.TEAM_MI6].SetUpdateCallback( self.ctk_OnTokenTimerUpdate, 0.1 )

		# Create the Janus delay timer
		self.game_timers[Glb.TEAM_JANUS] = self.timerTracker.CreateTimer( "ctk_janus" )
		self.game_timers[Glb.TEAM_JANUS].SetAgeRate( 1.2, 1.5 )
		self.game_timers[Glb.TEAM_JANUS].SetUpdateCallback( self.ctk_OnTokenTimerUpdate, 0.1 )

		# CVars
		self.CreateCVar( self.CVAR_CAPOVERRIDE, "5", "Sets the amount of seconds that a player has to stay on a capture point to capture if both tokens are held" )
		self.CreateCVar( self.CVAR_CAPPOINTS, "5", "Sets the amount of points a player recieves on token capture" )
		self.CreateCVar( self.CVAR_SPEEDMULT, "1.1", "Speed multiplier for a player holding a token [0.5 - 1.5]" )
		self.CreateCVar( self.CVAR_WARMUP, "20", "Seconds of warmup time before the match begins (set to 0 to disable)" )

		self.rules_overrideTime 	 = 5.0
		self.rules_playerCapPoints 	 = 5
		self.rules_speedMultiplier 	 = 1.1
		self.rules_warmupTime 		 = 20

		# Make sure we don't start out in wait time if we changed gameplay mid-match
		if GERules.GetNumActivePlayers() >= 2:
			self.game_inWaitTime = False

		GERules.GetRadar().SetForceRadar( True )

	def OnCVarChanged( self, name, oldvalue, newvalue ):
		if name == self.CVAR_CAPOVERRIDE:
			overridetime = float( newvalue )
			self.rules_overrideTime = 0 if overridetime < 0 else overridetime
		elif name == self.CVAR_CAPPOINTS:
			points = int( newvalue )
			self.rules_playerCapPoints = 0 if points < 0 else points
		elif name == self.CVAR_SPEEDMULT:
			self.rules_speedMultiplier = float( newvalue )
		elif name == self.CVAR_WARMUP:
			self.rules_warmupTime = int( newvalue )
			if self.warmupTimer.IsInWarmup():
				self.warmupTimer.StartWarmup( self.rules_warmupTime )
				if self.rules_warmupTime <= 0:
					GERules.EndRound( False )

	def OnRoundBegin( self ):
		GERules.ResetAllPlayersScores()

		# This makes sure players get a new set of bars on spawn
		self.game_inOvertime 	 = False
		self.game_canFinishRound = True

		if not self.game_inWaitTime and not self.warmupTimer.HadWarmup():
			self.warmupTimer.StartWarmup( self.rules_warmupTime )

	def CanRoundEnd( self ):
		if self.warmupTimer.IsInWarmup():
			return False

		# See if any tokens are picked, if so we postpone the ending
		# We can only break overtime if a token is dropped or captured
		if not self.game_inOvertime and not GERules.IsIntermission():
			mi6Score = GERules.GetTeam( Glb.TEAM_MI6 ).GetRoundScore() + GERules.GetTeam( Glb.TEAM_MI6 ).GetMatchScore()
			janusScore = GERules.GetTeam( Glb.TEAM_JANUS ).GetRoundScore() + GERules.GetTeam( Glb.TEAM_JANUS ).GetMatchScore()

			# Only go into overtime if our match scores are close and we have a token in hand
			if abs( mi6Score - janusScore ) <= 3 and ( self.ctk_IsTokenHeld( Glb.TEAM_MI6 ) or self.ctk_IsTokenHeld( Glb.TEAM_JANUS ) ):
				GEUtil.HudMessage( None, "#GES_GPH_OVERTIME_TITLE", -1, self.MSG_MISC_YPOS, self.COLOR_NEUTRAL, 4.0, self.MSG_MISC_CHANNEL )
				GEUtil.PopupMessage( None, "#GES_GPH_OVERTIME_TITLE", "#GES_GPH_OVERTIME" )
				GEUtil.EmitGameplayEvent( "ctk_overtime" )
				GEUtil.PlaySoundTo( None, "GEGamePlay.Overtime", True )
				self.game_inOvertime 	 = True
				self.game_inOvertimeDelay = False
				self.game_canFinishRound = False
				# Ensure overtime never lasts longer than 5 minutes
				self.overtime.StartOvertime( 300.0 )

		elif not self.game_inOvertimeDelay and not GERules.IsIntermission():
			# Exit overtime if a team is eliminated, awarding the other team a point
			if GERules.GetNumInRoundTeamPlayers( Glb.TEAM_MI6 ) == 0:
				GERules.GetTeam( Glb.TEAM_JANUS ).AddRoundScore( 1 )
				GEUtil.HudMessage( None, _( "#GES_GP_CTK_OVERTIME_SCORE", "Janus" ), -1, -1, self.COLOR_NEUTRAL, 5.0 )
				self.timerTracker.OneShotTimer( self.OVERTIME_DELAY, EndRoundCallback )
				self.game_inOvertimeDelay = True
			elif GERules.GetNumInRoundTeamPlayers( Glb.TEAM_JANUS ) == 0:
				GERules.GetTeam( Glb.TEAM_MI6 ).AddRoundScore( 1 )
				GEUtil.HudMessage( None, _( "#GES_GP_CTK_OVERTIME_SCORE", "MI6" ), -1, -1, self.COLOR_NEUTRAL, 5.0 )
				self.timerTracker.OneShotTimer( self.OVERTIME_DELAY, EndRoundCallback )
				self.game_inOvertimeDelay = True
			elif not self.overtime.CheckOvertime():
				# Overtime failsafe tripped, end the round now
				return True

		return self.game_canFinishRound

	def OnPlayerSpawn( self, player ):
		player.SetSpeedMultiplier( 1.0 )
		player.SetScoreBoardColor( Glb.SB_COLOR_NORMAL )

	def OnThink( self ):
		# Enter "wait time" if we only have 1 player
		if GERules.GetNumActivePlayers() < 2:
			# Check overtime fail safe
			if self.game_inOvertime:
				self.game_canFinishRound = True

			# Restart the round and count the scores if we were previously not in wait time
			if not self.game_inWaitTime:
				GERules.EndRound()

			self.warmupTimer.Reset()
			self.game_inWaitTime = True
			return

		# Restart the round (not counting scores) if we were in wait time
		if self.game_inWaitTime:
			GEUtil.HudMessage( None, "#GES_GP_GETREADY", -1, -1, GEUtil.CColor( 255, 255, 255, 255 ), 2.5 )
			GERules.EndRound( False )
			self.game_inWaitTime = False

	def OnPlayerKilled( self, victim, killer, weapon ):
		assert isinstance( victim, GEPlayer.CGEMPPlayer )
		assert isinstance( killer, GEPlayer.CGEMPPlayer )

		# In warmup? No victim?
		if self.warmupTimer.IsInWarmup() or not victim:
			return

		# death by world
		if not killer:
			victim.AddRoundScore( -1 )
			return

		victimTeam = victim.GetTeamNumber()
		killerTeam = killer.GetTeamNumber()

		if victim == killer or victimTeam == killerTeam:
			# Suicide or team kill
			killer.AddRoundScore( -1 )
		else:
			# Check to see if this was a kill against a token bearer (defense)
			if victim == self.game_tokens[victimTeam].GetOwner():
				clr_hint = '^i' if killerTeam == Glb.TEAM_MI6 else '^r'
				GEUtil.EmitGameplayEvent( "ctk_tokendefended", "%i" % killer.GetUserID(), "%i" % victim.GetUserID(), "%i" % victimTeam )
				GEUtil.PostDeathMessage( _( "#GES_GP_CTK_DEFENDED", clr_hint, killer.GetCleanPlayerName(), self.ctk_TokenName( victimTeam ) ) )
				killer.AddRoundScore( 2 )
			else:
				killer.AddRoundScore( 1 )

	def CanPlayerRespawn( self, player ):
		if self.game_inOvertime:
			GEUtil.PopupMessage( player, "#GES_GPH_ELIMINATED_TITLE", "#GES_GPH_ELIMINATED" )
			player.SetScoreBoardColor( Glb.SB_COLOR_ELIMINATED )
			return False

		return True

	def OnCaptureAreaSpawned( self, area ):
		team = area.GetTeamNumber()
		tknName = self.TOKEN_MI6 if team == Glb.TEAM_MI6 else self.TOKEN_JANUS

		GERules.GetRadar().AddRadarContact( area, Glb.RADAR_TYPE_OBJECTIVE, True, "sprites/hud/radar/capture_point", self.ctk_GetColor( team ) )
		GERules.GetRadar().SetupObjective( area, team, tknName, "#GES_GP_CTK_OBJ_CAPTURE", self.ctk_GetColor( team, self.COLOR_OBJ_HOT ), 0, True )

	def OnCaptureAreaRemoved( self, area ):
		GERules.GetRadar().DropRadarContact( area )

	def OnCaptureAreaEntered( self, area, player, token ):
		assert isinstance( area, GEEntity.CBaseEntity )
		assert isinstance( player, GEPlayer.CGEMPPlayer )
		assert isinstance( token, GEWeapon.CGEWeapon )

		if token is None:
			return

		# We don't delay capture in overtime
		if self.game_inOvertime:
			self.ctk_CaptureToken( token, player )
			return

		# If the other team has our token, we have to wait a set period
		tokenteam = token.GetTeamNumber()
		otherteam = OppositeTeam( player.GetTeamNumber() )

		if self.ctk_IsTokenHeld( otherteam ):
			timer = self.game_timers[tokenteam]
			if timer.state is Timer.STATE_STOP:
				GEUtil.InitHudProgressBar( player, self.PROBAR_OVERRIDE, "#GES_GP_CTK_CAPTURE_OVR", Glb.HUDPB_SHOWBAR, self.rules_overrideTime, -1, 0.6, 120, 16, GEUtil.CColor( 220, 220, 220, 240 ) )
			timer.Start( self.rules_overrideTime )
		else:
			self.ctk_CaptureToken( token, player )

	def OnCaptureAreaExited( self, area, player ):
		assert isinstance( area, GEEntity.CBaseEntity )
		assert isinstance( player, GEPlayer.CGEMPPlayer )

		tokenteam = player.GetTeamNumber()
		self.game_timers[tokenteam].Pause()

	def OnTokenSpawned( self, token ):
		tokenTeam = token.GetTeamNumber()

		GERules.GetRadar().AddRadarContact( token, Glb.RADAR_TYPE_TOKEN, True, "", self.ctk_GetColor( tokenTeam ) )
		GERules.GetRadar().SetupObjective( token, Glb.TEAM_NONE, "", self.ctk_TokenName( tokenTeam ), self.ctk_GetColor( tokenTeam, self.COLOR_OBJ_COLD ) )

		self.game_tokens[tokenTeam].hent = GEEntity.EHANDLE( token )

	def OnTokenPicked( self, token, player ):
		tokenTeam = token.GetTeamNumber()
		otherTeam = OppositeTeam( tokenTeam )

		self.game_tokens[tokenTeam].next_drop_time = GEUtil.GetTime() + 10.0

		GERules.GetRadar().DropRadarContact( token )
		GERules.GetRadar().AddRadarContact( player, Glb.RADAR_TYPE_PLAYER, True, "sprites/hud/radar/run", self.ctk_GetColor( player.GetTeamNumber() ) )
		GERules.GetRadar().SetupObjective( player, Glb.TEAM_NONE, "", self.ctk_TokenName( tokenTeam ), self.ctk_GetColor( tokenTeam, self.COLOR_OBJ_HOT ) )

		GEUtil.EmitGameplayEvent( "ctk_tokenpicked", "%i" % player.GetUserID(), "%i" % tokenTeam )

		# Token bearers move faster
		player.SetSpeedMultiplier( self.rules_speedMultiplier )
		player.SetScoreBoardColor( Glb.SB_COLOR_WHITE )

		msgFriend = _( "#GES_GP_CTK_PICKED_FRIEND", player.GetCleanPlayerName(), self.ctk_TokenName( tokenTeam ) )
		msgEnemy = _( "#GES_GP_CTK_PICKED_FOE", player.GetCleanPlayerName(), self.ctk_TokenName( tokenTeam ) )

		self.ctk_PostMessage( msgFriend, tokenTeam, tokenTeam )
		self.ctk_PostMessage( msgEnemy, otherTeam, tokenTeam )

		GEUtil.PlaySoundTo( tokenTeam, "GEGamePlay.Token_Grab", False )
		GEUtil.PlaySoundTo( otherTeam, "GEGamePlay.Token_Grab_Enemy", False )

	def OnTokenDropped( self, token, player ):
		tokenTeam = token.GetTeamNumber()
		otherTeam = OppositeTeam( tokenTeam )

		# Stop the override timer and force remove just in case
		self.game_timers[tokenTeam].Stop()
		GEUtil.RemoveHudProgressBar( player, self.PROBAR_OVERRIDE )

		GEUtil.EmitGameplayEvent( "ctk_tokendropped", "%i" % player.GetUserID(), "%i" % tokenTeam )

		GERules.GetRadar().AddRadarContact( token, Glb.RADAR_TYPE_TOKEN, True, "", self.ctk_GetColor( tokenTeam ) )
		GERules.GetRadar().SetupObjective( token, Glb.TEAM_NONE, "", self.ctk_TokenName( tokenTeam ), self.ctk_GetColor( tokenTeam, self.COLOR_OBJ_COLD ) )

		GERules.GetRadar().DropRadarContact( player )
		GERules.GetRadar().ClearObjective( player )

		player.SetSpeedMultiplier( 1.0 )
		player.SetScoreBoardColor( Glb.SB_COLOR_NORMAL )

		msg = _( "#GES_GP_CTK_DROPPED", player.GetCleanPlayerName(), self.ctk_TokenName( tokenTeam ) )

		self.ctk_PostMessage( msg, tokenTeam, tokenTeam )
		self.ctk_PostMessage( msg, otherTeam, tokenTeam )

		GEUtil.PlaySoundTo( tokenTeam, "GEGamePlay.Token_Drop_Friend", True )
		GEUtil.PlaySoundTo( otherTeam, "GEGamePlay.Token_Drop_Enemy", True )

	def OnTokenRemoved( self, token ):
		tokenTeam = token.GetTeamNumber()

		GERules.GetRadar().DropRadarContact( token )
		self.game_tokens[tokenTeam].hent = GEEntity.EHANDLE( None )

	def OnPlayerSay( self, player, text ):
		team = player.GetTeamNumber()
		# If the player issues !voodoo they will drop their token
		if text.lower() == "!voodoo" and team != Glb.TEAM_SPECTATOR:
			tokendef = self.game_tokens[team]
			if player == tokendef.GetOwner():
				if GEUtil.GetTime() >= tokendef.next_drop_time:
					GERules.GetTokenMgr().TransferToken( tokendef.hent.Get(), None )
				else:
					timeleft = max( 1, int( tokendef.next_drop_time - GEUtil.GetTime() ) )
					GEUtil.HudMessage( player, _( "#GES_GP_CTK_TOKEN_DROP", timeleft ), -1, self.MSG_MISC_YPOS, self.COLOR_NEUTRAL, 2.0, self.MSG_MISC_CHANNEL )
				return True

		return False

#-------------------#
# Utility Functions #
#-------------------#

	def ctk_GetColor( self, team, color_type=0 ):
		if team == Glb.TEAM_JANUS:
			if color_type == CaptureTheKey.COLOR_RADAR:
				return self.COLOR_JANUS_RADAR
			elif color_type == CaptureTheKey.COLOR_OBJ_COLD:
				return self.COLOR_JANUS_OBJ_COLD
			else:
				return self.COLOR_JANUS_OBJ_HOT
		elif team == Glb.TEAM_MI6:
			if color_type == CaptureTheKey.COLOR_RADAR:
				return self.COLOR_MI6_RADAR
			elif color_type == CaptureTheKey.COLOR_OBJ_COLD:
				return self.COLOR_MI6_OBJ_COLD
			else:
				return self.COLOR_MI6_OBJ_HOT
		else:
			return self.COLOR_NEUTRAL

	def ctk_CaptureToken( self, token, holder ):
		assert isinstance( token, GEWeapon.CGEWeapon )
		assert isinstance( holder, GEPlayer.CGEMPPlayer )

		tokenTeam = token.GetTeamNumber()
		otherTeam = OppositeTeam( tokenTeam )

		GERules.GetRadar().DropRadarContact( token )
		GERules.GetRadar().DropRadarContact( holder )

		holder.SetSpeedMultiplier( 1.0 )
		holder.SetScoreBoardColor( Glb.SB_COLOR_NORMAL )

		# Check overtime requirements
		if self.game_inOvertime:
			if not self.game_inOvertimeDelay:
				self.game_inOvertimeDelay = True
				self.timerTracker.OneShotTimer( self.OVERTIME_DELAY, EndRoundCallback )
			else:
				# We already scored in overtime, ignore this
				return

		# Capture the token and give the capturing team points
		GERules.GetTokenMgr().CaptureToken( token )

		# Make sure our timer goes away
		self.game_timers[tokenTeam].Stop()
		GEUtil.RemoveHudProgressBar( holder, self.PROBAR_OVERRIDE )

		# Give points if not in warmup
		if not self.warmupTimer.IsInWarmup():
			GERules.GetTeam( tokenTeam ).AddRoundScore( 1 )
			holder.AddRoundScore( self.rules_playerCapPoints )
			GEUtil.EmitGameplayEvent( "ctk_tokencapture", "%i" % holder.GetUserID(), "%i" % tokenTeam )

		GEUtil.PlaySoundTo( tokenTeam, "GEGamePlay.Token_Capture_Friend", True )
		GEUtil.PlaySoundTo( otherTeam, "GEGamePlay.Token_Capture_Enemy", True )

		msg = _( "#GES_GP_CTK_CAPTURE", holder.GetCleanPlayerName(), self.ctk_TokenName( tokenTeam ) )
		self.ctk_PostMessage( msg )

		GEUtil.PostDeathMessage( msg )

	def ctk_OnTokenTimerUpdate( self, timer, update_type ):
		assert isinstance( timer, Timer )

		tokenTeam = Glb.TEAM_MI6 if ( timer.GetName() == "ctk_mi6" ) else Glb.TEAM_JANUS
		otherTeam = OppositeTeam( tokenTeam )

		time = timer.GetCurrentTime()
		holder = self.game_tokens[tokenTeam].GetOwner()

		if holder is not None:
			if update_type == Timer.UPDATE_FINISH:
				token = self.game_tokens[tokenTeam].hent.Get()
				if token is not None:
					self.ctk_CaptureToken( token, holder )

			elif update_type == Timer.UPDATE_STOP:
				GEUtil.RemoveHudProgressBar( holder, self.PROBAR_OVERRIDE )

			elif update_type == Timer.UPDATE_RUN:
				GEUtil.UpdateHudProgressBar( holder, self.PROBAR_OVERRIDE, time )

				# Check to see if the other team dropped their token mid-capture
				if not self.ctk_IsTokenHeld( otherTeam ):
					timer.Finish()

	def ctk_IsTokenHeld( self, team ):
		return self.game_tokens[team].GetOwner() != None

	def ctk_PostMessage( self, msg, to_team=Glb.TEAM_NONE, from_team=Glb.TEAM_NONE ):
		if from_team == Glb.TEAM_JANUS:
			channel = self.MSG_JANUS_CHANNEL
			ypos = self.MSG_JANUS_YPOS
		elif from_team == Glb.TEAM_MI6:
			channel = self.MSG_MI6_CHANNEL
			ypos = self.MSG_MI6_YPOS
		else:
			channel = self.MSG_MISC_CHANNEL
			ypos = self.MSG_MISC_YPOS

		if to_team == Glb.TEAM_NONE:
			GEUtil.HudMessage( None, msg, -1, ypos, self.ctk_GetColor( from_team ), 5.0, channel )
		else:
			GEUtil.HudMessage( to_team, msg, -1, ypos, self.ctk_GetColor( from_team ), 5.0, channel )

	def ctk_TokenName( self, team ):
		return "#GES_GP_CTK_OBJ_JANUS" if team == Glb.TEAM_MI6 else "#GES_GP_CTK_OBJ_MI6"



