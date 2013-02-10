from GamePlay import GEScenario
from GamePlay.Utils.GEWarmUp import GEWarmUp
from GamePlay.Utils.GETimer import *
import GEEntity, GEPlayer, GEUtil, GEWeapon, GEMPGameRules, GEGlobal
import random

USING_API = GEGlobal.API_VERSION_1_0_0

# TODO:
#	1. Hacker transfer on change team / disconnect
#

def getPlayerFromUID( uid ):
	if not uid:
		return None

	plr = GEEntity.GetEntByUID( uid )
	if plr is not None and isinstance( plr, GEPlayer.CGEMPPlayer ):
		return plr
	else:
		return None


class LaunchCode( GEScenario ):
	# ------------------ #
	#  GLOBAL CONSTANTS  #
	# ------------------ #
	JANUS_HACKER_COSTUME = "boris"
	MI6_HACKER_COSTUME = "female_scientist"

	MIN_PLAYERS = 2
	LOW_PLAYER_NOTICE_INTERVAL = 10.0

	TOOL_CLASSNAME	 = "token_custom1"
	TOOL_WMODEL	 = "models/weapons/tokens/w_keytoken.mdl"
	TOOL_VMODEL	 = "models/weapons/tokens/v_keytoken.mdl"

	COLOR_INFO	 = GEUtil.CColor( 240, 200, 120, 170 )
	COLOR_NOTICE	 = GEUtil.CColor( 240, 200, 120, 170 )
	COLOR_RADAR_MI6	 = GEUtil.CColor( 94, 171, 231, 255 )
	COLOR_RADAR_JANUS = GEUtil.CColor( 206, 43, 43, 255 )

	TAG = "[LaunchCode]"

	DEFAULT_PARAMS = {
	    # Hacker Variables
		"hacker_notice"		: 0,
		"hacker_playerUID"	: None,
		"hacker_oldCostume" : "",
		"hacker_oldSkin"	: 0,
		"hacker_switched"	: False,
		"hacker_hasTool"	: False,
		"hacker_hasWeapon"	: False,

		# Game Variables
		"game_startTime"	: GEUtil.GetTime(),
		"game_hackersWin"	: False,
	    "game_tool"			: None,
		"game_lastTerminalUID" : None,
		"game_currTerminalUID" : None,
	}

	# ---------------- #
	#  CORE FUNCTIONS  #
	# ---------------- #

	def __init__( self ):
		super( LaunchCode, self ).__init__()
		self.warmUpTimer = GEWarmUp( self )
		self.timerTracker = TimerTracker( self )
		self.__debug = False
		# Defining some vars
		self.game_terminals = {}
		self.team_hacker = None
		self.team_preventor = None

	def Cleanup( self ):
		super( LaunchCode, self ).Cleanup()
		self.timer_endRound = None
		self.timer_hacking = None
		self.warmUpTimer = None
		self.timerTracker = None

	def GetPrintName( self ):
		return "Launch Code"

	def GetScenarioHelp( self, help_obj ):
		pass

	def GetGameDescription( self ):
		return "Launch Code"

	def GetTeamPlay( self ):
		return GEGlobal.TEAMPLAY_ALWAYS

	def OnLoadGamePlay( self ):
		# Precache our custom items
		GEUtil.PrecacheModel( "models/gameplay/capturepoint.mdl" )

		# Clear the timer list
		self.timerTracker.RemoveTimer()

		# Create the hacking timer
		self.timer_hacking = self.timerTracker.CreateTimer( "hack" )
		self.timer_hacking.SetAgeRate( 0.75, 2.0 )
		self.timer_hacking.SetUpdateCallback( self.lc_OnHackTimer )
		# Delay of End Round timer
		self.timer_endRound = self.timerTracker.CreateTimer( "endround" )
		self.timer_endRound.SetUpdateCallback( self.lc_OnEndRoundTimer )

		# Setup all our vars
		self.lc_InitRound()

		# Reset the some vars
		self.game_terminals = {}
		self.team_hacker = None
		self.team_preventor = None
		self.game_roundCount = 0

		# Enable team spawns
		GEMPGameRules.SetAllowTeamSpawns( True )

		GEMPGameRules.GetTokenMgr().SetupCaptureArea( "terminals", model="models/gameplay/capturepoint.mdl",
													limit=4, radius=32, location=GEGlobal.SPAWN_PLAYER )

		self.CreateCVar( "lc_warmup", "30", "Warmup time before the match begins" )
		self.CreateCVar( "lc_hackerboost", "1", "Allow the hacker to gain an ego-boost" )
		self.CreateCVar( "lc_hackertool", "1", "Allow the Insta-Hack tool" )
		self.CreateCVar( "lc_hacktime", "15", "Base number of seconds to hack a terminal" )

	def OnRoundBegin( self ):
		GEMPGameRules.GetRadar().SetForceRadar( True )
		GEMPGameRules.ResetAllPlayersScores()
		self.game_roundCount += 1

		self.lc_DerobeHacker()
		self.lc_InitRound()
		self.lc_ChooseHacker()
		self.lc_CreateHackingTool()

	def OnRoundEnd( self ):
		GEMPGameRules.GetRadar().DropAllContacts()

		if self.lc_HavePlayers() and not self.game_hackersWin:
			pTeam = GEMPGameRules.GetTeam( self.team_preventor )
			GEMPGameRules.SetTeamWinner( pTeam )
			for t in self.game_terminals.values():
				if not t["hacked"]:
					pTeam.IncrementRoundScore( 1 )

	def OnPlayerSpawn( self, player ):
		# Properly arm the hacker
		if self.hacker_playerUID == player.GetUID():
			self.lc_ArmHacker()
			if self.hacker_notice < 3:
				self.hacker_notice += 1
				GEUtil.HudMessage( player, "You are the hacker, hack the terminals by standing next to them", -1, -1, self.COLOR_NOTICE, 5.0, 2 )

	def OnPlayerKilled( self, victim, killer, weapon ):
		if victim is None:
			return

		if victim.GetUID() == self.hacker_playerUID:
			self.hacker_hasWeapon = False
			if self.team_preventor:
				GEMPGameRules.GetTeam( self.team_preventor ).IncrementRoundScore( 1 )

		if killer and victim != killer:
			killer.IncrementScore( 1 )
		else:
			victim.IncrementScore( -1 )

	def OnCaptureAreaSpawned( self, area ):
		aUID = area.GetUID()
		self.game_terminals[aUID] = { "hacked" : False }

		GEMPGameRules.GetRadar().AddRadarContact( area, GEGlobal.RADAR_TYPE_TOKEN, True, "sprites/hud/radar/capture_point", self.lc_GetHackerTeamColor() )

	def OnCaptureAreaRemoved( self, area ):
		aUID = area.GetUID()
		if self.game_terminals.has_key( aUID ):
			del self.game_terminals[aUID]

		GEMPGameRules.GetRadar().DropRadarContact( area )

	def OnCaptureAreaEntered( self, area, player, token ):
		aUID = area.GetUID()
		if not self.game_terminals.has_key( aUID ) or self.game_terminals[aUID]["hacked"]:
			return

		if player.GetUID() == self.hacker_playerUID:
			if self.timer_hacking.state is Timer.STATE_STOP or self.game_lastTerminalUID != area.GetUID():
				GEUtil.InitHudProgressBar( None, 1, "Hack Progress:", 1, 10.0, -1, 0.75, 120, 15, GEUtil.CColor( 220, 220, 220, 240 ) )

			self.game_lastTerminalUID = aUID
			self.game_currTerminalUID = aUID
			self.timer_hacking.Start( 10.0 )

	def OnCaptureAreaExited( self, area, player ):
		if player.GetUID() == self.hacker_playerUID:
			self.timer_hacking.Pause()
			self.game_currTerminalUID = None

	def CanPlayerChangeChar( self, player, ident ):
		if player == None:
			return False

		if ident == self.JANUS_HACKER_COSTUME or ident == self.MI6_HACKER_COSTUME:
			GEUtil.HudMessage( player, "You cannot impersonate the hacker!", -1, 0.1, self.COLOR_INFO, 2.0 )
			return False

		elif player.GetUID() == self.hacker_playerUID:
			if self.lc_CanHackerSwitch():
				self.lc_ChooseHacker()
				self.lc_ArmHacker()
				return True
			else:
				GEUtil.HudMessage( player, "You cannot switch from the hacker!", -1, 0.1, self.COLOR_INFO, 2.0 )
				return False

		return True

	def CanPlayerHaveItem( self, player, item ):
		name = item.GetClassname()

		if player.GetUID() == self.hacker_playerUID:
			# The hacker can only pickup armor
			if name.startswith( "item_armorvest" ):
				return True
			elif name == "weapon_slappers" or name == self.TOOL_CLASSNAME:
				return True
			elif name == "weapon_dd44" and not self.hacker_hasWeapon:
				self.hacker_hasWeapon = True
				return True

			return False
		else:
			if name == self.TOOL_CLASSNAME:
				return False

			return True

	def OnTokenSpawned( self, token ):
		GEMPGameRules.GetRadar().AddRadarContact( token, GEGlobal.RADAR_TYPE_TOKEN, True )

	def OnTokenRemoved( self, token ):
		GEMPGameRules.GetRadar().DropRadarContact( token )

	def OnTokenPicked( self, token, player ):
		self.hacker_hasTool = True
		GEUtil.PlaySoundToPlayer( player, "GEGamePlay.Token_Grab" )
		GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, self.TAG + " The hacker picked up the Insta-Hack" )
		GEUtil.HudMessage( self.team_hacker, "The hacker has the Insta-Hack, protect them at all costs!", -1, 0.65, self.COLOR_NOTICE, 4.0, 1 )
		GEUtil.HudMessage( self.team_preventor, "Warning! The hacker has the Insta-Hack!!", -1, 0.65, self.COLOR_NOTICE, 4.0, 1 )
		GEUtil.PlaySoundToTeam( self.team_hacker, "GEGamePlay.Token_Grab" )
		GEUtil.PlaySoundToTeam( self.team_preventor, "GEGamePlay.Token_Grab_Enemy" )
		GEMPGameRules.GetRadar().DropRadarContact( token )

	def OnTokenDropped( self, token, player ):
		self.hacker_hasTool = False
		GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, self.TAG + " The Insta-Hack has been destroyed" )
		GEUtil.HudMessage( None, "The Insta-Hack has been destroyed!", -1, 0.65, self.COLOR_NOTICE, 4.0, 1 )
		GEUtil.PlaySoundToPlayer( None, "GEGamePlay.Token_Drop_Friend" )
		GEMPGameRules.GetTokenMgr().RemoveTokenType( self.TOOL_CLASSNAME )

	def OnThink( self ):
		if self.game_lowPlayers:
			if self.lc_HavePlayers():
				# We have enough players, start the warmup period
				self.warmUpTimer.StartWarmup( float( GEUtil.GetCVarValue( "lc_warmup" ) ) )
				self.game_lowPlayers = False
				self.lc_DerobeHacker()
			elif GEUtil.GetTime() >= self.game_lowPlayersNotice:
				# Notify anyone in the serve that we don't have enough players
				GEUtil.HudMessage( None, "Not enough players, please wait...", -1, -1, self.COLOR_NOTICE, self.LOW_PLAYER_NOTICE_INTERVAL / 4.0 )
				self.game_lowPlayersNotice = GEUtil.GetTime() + self.LOW_PLAYER_NOTICE_INTERVAL

		elif not self.lc_HavePlayers():
			# Put us back into low player state
			self.warmUpTimer.Reset()
			self.game_lowPlayers = True
			self.game_lowPlayersNotice = 0
			self.lc_DerobeHacker()

	def CanPlayerChangeTeam( self, player, oldteam, newteam ):
		# The hacker cannot change teams
		if player.GetUID() == self.hacker_playerUID:
			GEUtil.HudMessage( player, "You cannot change teams as the hacker!", -1, -1, GEUtil.CColor( 255, 255, 255, 255 ), 3.0 )
			return False

		return True

	def OnPlayerDisconnect( self, player ):
		# If the hacker disconnects we must choose a new one
		if player.GetUID() == self.hacker_playerUID:
			self.lc_ChooseHacker( True )

	def OnPlayerSay( self, player, text ):
		# TODO: Remove me on release
		if text == "!debug":
			self.__debug = not self.__debug
			if self.__debug:
				GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, self.TAG + "Debugging Enabled" )
			else:
				GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, self.TAG + "Debugging Disabled" )

			return True

		elif text == "!voodoo":
			if player.GetUID() == self.hacker_playerUID and self.hacker_hasTool and self.game_currTerminalUID:
				self.lc_OnHackCompleted()
				self.timer_hacking.Stop()
				GEMPGameRules.GetTokenMgr().RemoveTokenType( self.TOOL_CLASSNAME )
				return True

		return False


	# ------------------ #
	#  CUSTOM FUNCTIONS  #
	# ------------------ #

	def lc_InitRound( self ):
		# Hacker Variables
		self.hacker_notice = 0
		self.hacker_playerUID = None
		self.hacker_oldCostume = ""
		self.hacker_oldSkin = 0
		self.hacker_switched = False
		self.hacker_hasTool = False
		self.hacker_hasWeapon = False

		# Game Variables
		self.game_startTime = GEUtil.GetTime()
		self.game_hackersWin = False
		self.game_lastTerminalUID = None
		self.game_currTerminalUID = None
		self.game_tool = None

		# Reset Timers
		self.timerTracker.ResetTimer()

		# Check for low player counts
		self.game_lowPlayersNotice = 0
		if not self.lc_HavePlayers():
			self.game_lowPlayers = True
		else:
			self.game_lowPlayers = False

		# Setup Teams
		if self.team_hacker:
			# Swap the teams
			tmp = self.team_hacker
			self.team_hacker = self.team_preventor
			self.team_preventor = tmp
		else:
			# First time? Pick a random team
			self.team_hacker = random.choice( [GEGlobal.TEAM_MI6, GEGlobal.TEAM_JANUS] )
			if self.team_hacker == GEGlobal.TEAM_JANUS:
				self.team_preventor = GEGlobal.TEAM_MI6
			else:
				self.team_preventor = GEGlobal.TEAM_JANUS

	def lc_ChooseHacker( self, force=False ):
		if not self.team_hacker:
			self.lc_ErrorShout( "Hacker assignment attempted before team chosen!" )
			return

		# Enumerate the number of eligable players
		players = self.lc_ListPlayers( self.team_hacker, self.hacker_playerUID )

		if self.hacker_playerUID:
			if len( players ) > 1 and ( force or self.lc_CanHackerSwitch() ):
				self.lc_DebugShout( "Hacker being switched" )
				self.lc_DerobeHacker()
				self.lc_EnrobeHacker( random.choice( players ) )
				self.hacker_switched = True

		elif len( players ) > 0:
			self.lc_DebugShout( "New hacker being selected" )
			self.lc_DerobeHacker()
			self.lc_EnrobeHacker( random.choice( players ) )
			self.hacker_switched = False

	def lc_CanHackerSwitch( self ):
		timeIn = GEUtil.GetTime() - self.game_startTime;
		plrCount = GEMPGameRules.GetNumActiveTeamPlayers( self.team_hacker )
		if self.hacker_playerUID and plrCount > 1 and not self.hacker_switched and timeIn < 15.0:
			return True
		return False

	def lc_CreateHackingTool( self ):
		mgr = GEMPGameRules.GetTokenMgr()
		mgr.SetupToken( self.TOOL_CLASSNAME, limit=1, location=GEGlobal.SPAWN_AMMO,
					allow_switch=True, glow_color=GEUtil.CColor( 80, 80, 80, 255 ), glow_dist=500.0 )

	def lc_EnrobeHacker( self, uid ):
		player = getPlayerFromUID( uid )
		if player is not None:
			model = self.MI6_HACKER_COSTUME
			if player.GetTeamNumber() == GEGlobal.TEAM_JANUS:
				model = self.JANUS_HACKER_COSTUME

			# Store away his old costume and set him as the hacker
			self.hacker_oldCostume = player.GetPlayerModel()
			self.hacker_oldSkin = player.GetSkin()
			player.SetPlayerModel( model, 0 )
			# Add me to the radar as always visible
			GEMPGameRules.GetRadar().AddRadarContact( player, GEGlobal.RADAR_TYPE_PLAYER, True, "sprites/hud/radar/run", GEUtil.CColor( 255, 180, 225, 170 ) )
			# Reset notices
			self.hacker_notice = 0
			self.hacker_playerUID = uid

	def lc_DerobeHacker( self ):
		player = getPlayerFromUID( self.hacker_playerUID )
		if player is not None:
			# Revert back to the old costume
			player.SetPlayerModel( self.hacker_oldCostume, self.hacker_oldSkin )
			player.StripAllWeapons()
			player.GiveDefaultWeapons()
			GEMPGameRules.GetRadar().DropRadarContact( player )

		self.hacker_playerUID = None

	def lc_ArmHacker( self, onlyAmmo=False ):
		player = getPlayerFromUID( self.hacker_playerUID )
		if player is not None:
			if onlyAmmo:
				player.GiveAmmo( GEGlobal.AMMO_9MM, 16 )
			else:
				self.hacker_hasWeapon = False
				player.StripAllWeapons()
				player.GiveNamedWeapon( "weapon_slappers", 0 )
				player.GiveNamedWeapon( "weapon_dd44", 14 ) # DD44 starts w/ 10 bullets: 8|16
				player.SetArmor( int( GEGlobal.GE_MAX_ARMOR ) )

	def lc_OnHackTimer( self, timer, update_type ):
		assert isinstance( timer, Timer )

		if update_type is Timer.UPDATE_FINISH:
			# Complete the hack
			self.lc_OnHackCompleted()

		elif update_type is Timer.UPDATE_STOP:
			GEUtil.RemoveHudProgressBar( None, 1 )
			# Reset the terminal usage since we abandoned our current effort
			self.game_lastTerminalUID = self.game_currTerminalUID = None

		elif update_type is Timer.UPDATE_RUN:
			GEUtil.UpdateHudProgressBar( None, 1, timer.GetCurrentTime() )

	def lc_OnHackCompleted( self ):
		GEMPGameRules.GetTeam( self.team_hacker ).IncrementRoundScore( 1 )
		GEMPGameRules.GetRadar().DropRadarContact( GEEntity.GetEntByUID( self.game_lastTerminalUID ) )

		GEUtil.PlaySoundToTeam( self.team_hacker, "GEGameplay.Token_Capture_Friend", True )
		GEUtil.PlaySoundToTeam( self.team_preventor, "GEGamePlay.Token_Capture_Enemy", True )
		GEUtil.HudMessage( None, "The hacker has taken over a terminal!", -1, -1, self.COLOR_NOTICE, 2.0, 2 )

		self.game_terminals[self.game_lastTerminalUID]["hacked"] = True
		self.game_lastTerminalUID = self.game_currTerminalUID = None

		self.lc_CheckHackerWin()

	def lc_OnEndRoundTimer( self, timer, update_type ):
		if update_type is Timer.UPDATE_FINISH:
			GEMPGameRules.EndRound()

	def lc_CheckHackerWin( self ):
		for t in self.game_terminals.values():
			if not t["hacked"]:
				return

		# If we made it here, hackers won! End the round
		self.game_hackersWin = True
		hTeam = GEMPGameRules.GetTeam( self.team_hacker )
		GEMPGameRules.SetTeamWinner( hTeam )
		hTeam.IncrementRoundScore( len( self.game_terminals ) )
		# End the round in 3 seconds (this should be a variable in EndRound(...))
		self.timer_endRound.Start( 3.0 )

	def lc_GetHackerTeamColor( self ):
		if self.team_hacker == GEGlobal.TEAM_MI6:
			return self.COLOR_RADAR_MI6
		else:
			return self.COLOR_RADAR_JANUS

	def lc_ListPlayers( self, team, ignore=None ):
		list = []
		for j in range( 32 ):
			if GEPlayer.IsValidPlayerIndex( j ):
				player = GEPlayer.GetMPPlayer( j )
				if player.GetTeamNumber() == team and player.GetUID() != ignore:
					list.append( player.GetUID() )
		return list

	def lc_HavePlayers( self ):
		if GEMPGameRules.GetNumActivePlayers() >= self.MIN_PLAYERS:
			return True
		return False

	def lc_DebugShout( self, msg ):
		if self.__debug:
			GEUtil.Msg( self.TAG + msg + "\n" )

	def lc_ErrorShout( self, msg ):
		if self.__debug:
			GEUtil.Warning( self.TAG + msg + "\n" )
