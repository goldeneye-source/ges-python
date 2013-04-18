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
from Utils import GetPlayers
from Utils.GEPlayerTracker import GEPlayerTracker
from GEUtil import Color, TraceOpt
import GEPlayer, GEUtil, GEWeapon, GEMPGameRules as GERules, GEGlobal as Glb
import random

USING_API = Glb.API_VERSION_1_1_0

class TokenSpawnTest( GEScenario ):
	MAX_TOKENS = 5
	MAX_CAPAREA = 5

	def __init__( self ):
		super( TokenSpawnTest, self ).__init__()

		self.TOKEN1 = "token_deathmatch";
		self.TOKEN2 = "token_custom1";

		self.pltracker = GEPlayerTracker( self )

		self.do_token_test = False
		self.token_count = 2
		self.token_next_time = 0
		self.token_do_increase = True

		self.EndRound = False
		self.EndMatch = True

	def Cleanup( self ):
		GEScenario.Cleanup( self )
		self.pltracker = None

	def GetPrintName( self ):
		return "Testing"

	def GetScenarioHelp( self, help_obj ):
		assert isinstance( help_obj, GEScenarioHelp )

		help_obj.SetInfo( "Testing the token system", "" )
		help_obj.SetDescription( "Tests of the token spawning system and various gameplay elements" )

	def GetGameDescription( self ):
		return "test"

	def GetTeamPlay( self ):
		return Glb.TEAMPLAY_TOGGLE

	def OnLoadGamePlay( self ):
		tokenmgr = GERules.GetTokenMgr()

		tokenmgr.SetupToken( self.TOKEN1, location=Glb.SPAWN_TOKEN, limit=self.token_count,
							glow_color=Color( 0, 255, 0, 120 ), respawn_delay=10 )

		tokenmgr.SetupToken( self.TOKEN2, location=Glb.SPAWN_TOKEN, limit=1,
							glow_color=Color( 0, 0, 255, 120 ), respawn_delay=10,
							world_model="models/weapons/goldengun/w_goldengun.mdl",
							view_model="models/weapons/goldengun/v_goldengun.mdl",
							print_name="Golden Gun" )

		tokenmgr.SetupCaptureArea( "cap1", 	limit=self.token_count, location=Glb.SPAWN_CAPAREA,
									rqd_token=self.TOKEN1, spread=1000, glow_color=Color( 0, 255, 0, 120 ) )

		tokenmgr.SetupCaptureArea( "cap2", limit=1, location=Glb.SPAWN_CAPAREA, spread=600 )

		GEUtil.AddDownloadable( "models\\weapons\\ammocrate.mdl" )

		self.EndRound = False
		self.EndMatch = True

	def OnRoundBegin( self ):
		self.token_count = 0
		self.token_next_time = 0

		GERules.ResetAllPlayersScores()

		self.InitProBar()

	def OnRoundEnd( self ):
		GERules.GetRadar().DropAllContacts()

	def OnPlayerSay( self, player, text ):
		assert isinstance( text, str )
		assert isinstance( player, GEPlayer.CGEMPPlayer )
		text = text.lower()

		if text == Glb.SAY_COMMAND1:
			player.ForceRespawn()
		elif text == Glb.SAY_COMMAND2:
			self.do_token_test = not self.do_token_test
			if self.do_token_test:
				GEUtil.ClientPrint( None, Glb.HUD_PRINTTALK, "^mToken Testing Enabled" )
			else:
				GEUtil.ClientPrint( None, Glb.HUD_PRINTTALK, "^mToken Testing Disabled" )
		elif text == "!endround":
			self.EndRound = not self.EndRound
			if self.EndRound:
				GEUtil.ClientPrint( None, Glb.HUD_PRINTTALK, "^mRound ending enabled" )
			else:
				GEUtil.ClientPrint( None, Glb.HUD_PRINTTALK, "^mRound ending disabled" )
		elif text == "!endmatch":
			self.EndMatch = not self.EndMatch
			if self.EndMatch:
				GEUtil.ClientPrint( None, Glb.HUD_PRINTTALK, "^mMatch ending enabled" )
			else:
				GEUtil.ClientPrint( None, Glb.HUD_PRINTTALK, "^mMatch ending disabled" )
		elif text == "!doendround":
			GERules.EndRound( True )
		elif text == "!doendmatch":
			GERules.EndMatch()
		elif text == "!message":
			GEUtil.PopupMessage( None, "Test Message 1", "This is a test of the popup message system!", None )
			GEUtil.PopupMessage( None, "Test Message 2", "This is a test of the popup message system!", "mwgg_goal" )
			GEUtil.PopupMessage( None, "Test Message 3", "#GES_GPH_ELIMINATED" )
		elif text == "!droptoken":
			weap = player.GetActiveWeapon()
			if weap and GERules.GetTokenMgr().IsValidToken( weap.GetClassname() ):
				GERules.GetTokenMgr().TransferToken( weap, None )
		elif text == "!te":
			GEUtil.CreateTempEnt( "ring", origin=player.GetAbsOrigin(), radius_start=110, radius_end=130,
								width=3, color=Color( 255, 0, 0, 120 ), framerate=10, amplitude=0.2 )
		elif text == "!dump":
			for plr in GetPlayers():
				r = random.random()
				if r < 0.5:
					self.pltracker.SetValue( plr, "testing", True )
				else:
					self.pltracker.SetValue( plr, "testing", False )

			self.pltracker.DumpData()
		elif text == "!msgtest":
			pos = GEUtil.Vector( player.GetAbsOrigin() )
			pos[2] += 20
			# This purposefully doesn't do anything
			player.SetAbsOrigin( pos )

			GEUtil.HudMessage( None, "%s\n^rRight^| Align" % player.GetSteamID(), -0.05, -1, Color( 255, 255, 255, 255 ) )
			GEUtil.HudMessage( None, "%s\n^cBottom^| Align" % pos, 0.05, -0.05, Color( 255, 255, 255, 255 ) )
		else:
			return False

		return True

	def CanRoundEnd( self ):
		if self.EndRound:
			GEUtil.HudMessage( None, "Round End Allowed", -1, -1, Color( 255, 255, 255, 255 ), 1.0, 0 )
		else:
			GEUtil.HudMessage( None, "Round End Blocked", -1, -1, Color( 255, 255, 255, 255 ), 1.0, 0 )

		return self.EndRound

	def CanMatchEnd( self ):
		if self.EndMatch:
			GEUtil.HudMessage( None, "Match End Allowed", -1, 0.6, Color( 255, 255, 255, 255 ), 1.0, 1 )
		else:
			GEUtil.HudMessage( None, "Match End Blocked", -1, 0.6, Color( 255, 255, 255, 255 ), 1.0, 1 )

		return self.EndMatch

	def OnPlayerConnect( self, player ):
		self.InitProBar()

	def OnPlayerKilled( self, victim, killer, weapon ):
		# what exactly got killed?
		if not victim:
			return

		# death by world
		if not killer:
			victim.IncrementScore( -1 )
			return

		if victim.GetIndex() == killer.GetIndex():
			killer.IncrementScore( -1 )
		elif GERules.IsTeamplay() and killer.GetTeamNumber() == victim.GetTeamNumber():
			killer.IncrementScore( -1 )
		else:
			GERules.GetTeam( killer.GetTeamNumber() ).IncrementRoundScore( 1 )
			killer.IncrementScore( 1 )

	def OnThink( self ):
		if self.do_token_test and GEUtil.GetTime() > self.token_next_time:
			if self.token_do_increase and self.token_count < self.MAX_TOKENS:
				self.token_count = self.token_count + 1
			elif not self.token_do_increase and self.token_count > 0:
				self.token_count = self.token_count - 1

			GERules.GetTokenMgr().SetupToken( self.TOKEN1, limit=self.token_count )
			GERules.GetTokenMgr().SetupCaptureArea( "cap1", limit=self.token_count )

			if self.token_do_increase and self.token_count == self.MAX_TOKENS:
				self.token_do_increase = False
			elif not self.token_do_increase and self.token_count <= 0:
				self.token_do_increase = True

			GEUtil.UpdateHudProgressBar( None, 0, self.token_count )
			GEUtil.ConfigHudProgressBar( None, 0, "Token #%i" % self.token_count, Color( 255, 0, 0, 255 ) )

			self.token_next_time = GEUtil.GetTime() + 1.0

	# ---------------------- #
	# CAPTURE AREA FUNCTIONS #
	# ---------------------- #
	def OnCaptureAreaSpawned( self, capture ):
		GERules.GetRadar().AddRadarContact( capture, Glb.RADAR_TYPE_OBJECTIVE, True, "sprites/hud/radar/capture_point", Color( 255, 255, 255, 255 ) )

	def OnCaptureAreaRemoved( self, area ):
		GERules.GetRadar().DropRadarContact( area )

	def OnCaptureAreaEntered( self, area, player, token ):
		GERules.GetTokenMgr().CaptureToken( token )
		print "Entered capture area " + area.GetGroupName() + "!"

	# --------------- #
	# TOKEN FUNCTIONS #
	# --------------- #
	def OnTokenSpawned( self, token ):
		assert isinstance( token, GEWeapon.CGEWeapon )

		if token.GetClassname() == self.TOKEN1:
			GERules.GetRadar().AddRadarContact( token, Glb.RADAR_TYPE_TOKEN, True, "", Color( 255, 255, 255, 100 ) )
		else:
			GERules.GetRadar().AddRadarContact( token, Glb.RADAR_TYPE_TOKEN, True, "", Color( 255, 0, 0, 100 ) )
			GERules.GetRadar().SetupObjective( token, Glb.TEAM_NONE, "", "", Color( 255, 0, 0, 120 ) )

	def OnTokenRemoved( self, token ):
		GERules.GetRadar().DropRadarContact( token )

	def OnTokenPicked( self, token, player ):
		GERules.GetRadar().DropRadarContact( token )

		if token.GetClassname() == self.TOKEN2:
			GEUtil.HudMessage( None, "Custom Token Picked!", -1, 0.7, Color( 255, 255, 255, 255 ), 1.0, 3 )

	def OnTokenDropped( self, token, player ):
		if token.GetClassname() == self.TOKEN2:
			GEUtil.HudMessage( None, "Custom Token Dropped!", -1, 0.75, Color( 255, 255, 255, 255 ), 1.0, 2 )

		if token.GetClassname() == self.TOKEN1:
			GERules.GetRadar().AddRadarContact( token, Glb.RADAR_TYPE_TOKEN, True, "", Color( 255, 255, 255, 100 ) )
		else:
			GERules.GetRadar().AddRadarContact( token, Glb.RADAR_TYPE_TOKEN, True, "", Color( 255, 0, 0, 100 ) )

	def OnTokenAttack( self, token, player, start, direction ):
		if token.GetClassname() == self.TOKEN1:
			return

		end = GEUtil.VectorMA( start, direction, 500.0 )
		hit = GEUtil.Trace( start, end, TraceOpt.PLAYER, player )

		if hit is not None:
			GEUtil.HudMessage( None, "Hit Player!", -1, 0.6, Color( 255, 255, 255, 255 ), 1.0, 1 )
			GERules.GetTokenMgr().TransferToken( token, hit )
			hit.WeaponSwitch( self.TOKEN2 )
			return

		hit = GEUtil.Trace( start, end, TraceOpt.CAPAREA, player )

		if hit is not None:
			GEUtil.HudMessage( None, "Hit Cap Area!", -1, 0.6, Color( 255, 255, 255, 255 ), 1.0, 1 )


	# ---------------- #
	# CUSTOM FUNCTIONS #
	# ---------------- #
	def InitProBar( self ):
		# opts = Glb.HUDPB_SHOWVALUE #| Glb.HUDPB_SHOWBAR
		# h = 15
		# w = 200
		# x = -1
		# y = 0.05
		opts = Glb.HUDPB_SHOWVALUE | Glb.HUDPB_VERTICAL | Glb.HUDPB_SHOWBAR
		h = 80
		w = 12
		x = 0.9
		y = -1
		GEUtil.InitHudProgressBar( None, 0, "Tokens:", opts, self.MAX_TOKENS, x, y, w, h, Color( 255, 0, 0, 180 ) );

