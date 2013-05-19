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
from Utils import choice, clamp, plural, GetPlayers
from Utils.GEPlayerTracker import GEPlayerTracker
from GEUtil import Color
import GEEntity, GEPlayer, GEUtil, GEWeapon, GEMPGameRules, GEGlobal
import random
import GEGamePlay

USING_API = GEGlobal.API_VERSION_1_1_0
EP_SHOUT_COLOR = Color( 240, 200, 120, 170 )
LLD_DEBUG = False

def ep_forcerespawn():
	for j in range( 32 ):
		if GEPlayer.IsValidPlayerIndex( j ):
			GEPlayer.GetMPPlayer( j ).ForceRespawn()

def ep_goldeneye_handicap( hc ):
	return 2.0 ** ( float( hc ) / 3.0 )

def ep_id_by_entity( ent ):
	if ent != None:
		return GEEntity.GetUID( ent )
	return 0

def ep_loadout_slot( index ):
	weapon = GEMPGameRules.GetWeaponInSlot( index )
	if weapon != None:
		return GEWeapon.WeaponClassname( weapon ).lower()
	return "weapon_paintbrush"

def ep_playername_by_uid( uid ):
	player = ep_player_by_uid( uid )
	return player.GetPlayerName() if player else ""

def ep_player_by_uid( uid ):
	if uid != 0:
		return GEPlayer.ToMPPlayer( GEEntity.GetEntByUID( uid ) )
	return None

def ep_shout( msg ):
	GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, msg )
	GEUtil.HudMessage( None, msg, -1, -1, EP_SHOUT_COLOR, 2.0 )
	return msg

def ep_weapon_by_info( info ):
	weaponsurrogate = info.GetWeapon()
	if weaponsurrogate != None:
		weapon = GEWeapon.ToGEWeapon( weaponsurrogate )
		if weapon != None:
			return weapon.GetClassname().lower()
	return "weapon_paintbrush"

def ep_weightedselect_random( weightlist ):
	if type( weightlist ) is not list:
		raise TypeError( "Weights must be a list type" )

	totalweight = 0
	for x in weightlist:
		totalweight += x
	target = random.random() * float( totalweight )
	for i in range( len( weightlist ) ):
		target -= weightlist[i]
		if target <= 0:
			return i
	# Should never get here, but floats do happen
	return len( weightlist ) - 1

# ///////////////////////////////////////////////////////////////////////////////
# Globals for LALD
TR_INROUND = "inround"
TR_SPAWNED = "spawned"

class LiveAndLetDie( GEScenario ):
	HELPID_BOND = -1
	HELPID_BARON = -1

	def __init__( self ):
		super( LiveAndLetDie, self ).__init__()
		self.lld_declare_scenario_data()
		self.lld_declare_baron_data()
		self.pltracker = GEPlayerTracker( self )

	def Cleanup( self ):
		super( LiveAndLetDie, self ).Cleanup()
		self.pltracker = None

	def GetGameDescription( self ):
		return "Live and Let Die"

	def GetPrintName( self ):
		return "#GES_GP_LALD_NAME"

	def GetTeamPlay( self ):
		return GEGlobal.TEAMPLAY_NONE

	def GetScenarioHelp( self, help_obj ):
		assert isinstance( help_obj, GEGamePlay.CScenarioHelp )

		help_obj.SetInfo( "#GES_GPH_LALD_TAGLINE", "http://wiki.geshl2.com/index.php/Live_and_Let_Die" )
		help_obj.SetDescription( "#GES_GP_LALD_HELP" )

		pane = help_obj.AddPane( "bond" )
		help_obj.AddHelp( pane, "mwgg_goal", "#GES_GPH_LALD_ASBOND_GG" )
		help_obj.AddHelp( pane, "lald_bond_win", "#GES_GPH_LALD_ASBOND_WIN" )
		self.HELPID_BOND = pane

		pane = help_obj.AddPane( "baron" )
		help_obj.AddHelp( pane, "", "#GES_GP_LALD_AREBARON" )
		help_obj.AddHelp( pane, "lald_baron_win", "#GES_GPH_LALD_ASBARON" )
		help_obj.AddHelp( pane, "lald_baron_voodoo", "#GES_GPH_LALD_VOODOO" )
		self.HELPID_BARON = pane

		help_obj.SetDefaultPane( self.HELPID_BOND )

	def OnLoadGamePlay( self ):
		self.CVAR_BLOODLUST = "lald_bloodlust"
		self.CreateCVar( self.CVAR_BLOODLUST, "1", "Enable or disable Baron Samedi recovering Voodoo through use of his machete." )

		tokenmgr = GEMPGameRules.GetTokenMgr()
		tokenmgr.SetupToken( self.TOKEN_AUG_ENTITY, limit=1, respawn_delay=20.0,
							location=GEGlobal.SPAWN_WEAPON, glow_color=self.AURA_AUG )
		tokenmgr.SetGlobalAmmo( self.TOKEN_AUG_ENTITY )

		GEUtil.PrecacheSound( "GEGamePlay.Token_Chime" )
		GEUtil.PrecacheSound( "GEGamePlay.Baron_Voodoo" )
		GEUtil.PrecacheSound( "GEGamePlay.Baron_Flawless" )
		GEUtil.PrecacheSound( "GEGamePlay.Baron_EpicFail" )
		GEUtil.PrecacheParticleEffect( "ge_baron_teleport" )

		GEMPGameRules.SetExcludedCharacters( "samedi" )

	def OnCVarChanged( self, cvar, previous, current ):
		if cvar == self.CVAR_BLOODLUST:
			self.lld_baron_update_voodoobar()

	def OnPlayerConnect( self, player ):
		self.pltracker[player][TR_INROUND] = False

	def OnPlayerDisconnect( self, player ):
		if self.lld_player_isbaron( player ):
			self.lld_embaron_randomly()

	def OnRoundBegin( self ):
		GEScenario.OnRoundBegin( self )
		self.lld_disembaron()
		self.lld_zot_round()
		self.lld_authorize_everyone()

	def OnRoundEnd( self ):
		GEMPGameRules.GetRadar().DropAllContacts()

		# Describe default win type based on result
		endtype = "bondwin" if self.result == self.RESULT_BONDWIN else "baronwin"
		baronid = self.lld_Baron().GetUserID() if ( self.lld_Baron() ) else -1
		bondid = self.aug_holder.GetUserID() if ( self.aug_holder ) else -1

		if self.result == self.RESULT_BARONWIN and self.bounty >= 4 and self.baron_stats_hitbyaug == 0:
			GEUtil.PlaySoundTo( None, "GEGamePlay.Baron_Flawless", True )
			endtype = "baronflawless"
		elif self.result == self.RESULT_BONDWIN and self.bounty >= 4 and self.baron_frags == 0:
			GEUtil.PlaySoundTo( None, "GEGamePlay.Baron_EpicFail", True )
			endtype = "bondflawless"

		GEUtil.EmitGameplayEvent( "lald_roundend", endtype, "%i" % baronid, "%i" % bondid )

	def OnPlayerSpawn( self, player ):
		assert isinstance( player, GEPlayer.CGEMPPlayer )

		self.lld_progress()
		self.lld_costume_failsafe( player )

		if self.lld_player_isbaron( player ):
			self.lld_baron_spawn( player )
			if self.baron_health_cache >= 0:
				player.SetHealth( clamp( self.baron_health_cache, 0, 160 ) )
				self.baron_health_cache = -1
		else:
			player.SetSpeedMultiplier( 1.0 )
			player.SetScoreBoardColor( GEGlobal.SB_COLOR_NORMAL )
			if not self.pltracker[player][TR_INROUND]:
				if self.gamestate >= self.GAMESTATE_SHUT:
					GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "#GES_GP_NOJOIN", player.GetPlayerName() )
					player.SetScoreBoardColor( GEGlobal.SB_COLOR_ELIMINATED )
				else:
					self.lld_authorize_player( player )

	def OnPlayerKilled( self, victim, killer, weapon ):
		if victim == None:
			return
		if self.baron_uid != 0 and self.lld_player_isbaron( victim ):
# Baron died
			if killer == None or victim == killer:
				self.lld_eliminateplayer( victim )
				self.lld_misix_jackpot()
			elif not self.pltracker[self.baron_uid][TR_INROUND]:
				killer.AddRoundScore( self.bounty )
		else:
# Player died
			if killer == None or victim == killer:
	# Eliminated by suicide, penalized
				self.lld_eliminateplayer( victim )
				victim.AddRoundScore( -self.lld_num_inround_players() + 1 )
				baronid = self.lld_Baron().GetUserID() if ( self.lld_Baron() ) else -1
				GEUtil.EmitGameplayEvent( "lald_eliminated", "%i" % victim.GetUserID(), "%i" % baronid, "suicide" )
			elif self.lld_player_isbaron( killer ):
				killer.AddRoundScore( 1 )
				self.baron_frags += 1
				self.lld_eliminateplayer( victim )
				baronid = self.lld_Baron().GetUserID() if ( self.lld_Baron() ) else -1
				GEUtil.EmitGameplayEvent( "lald_eliminated", "%i" % victim.GetUserID(), "%i" % baronid, "baronkill" )

	def CanPlayerChangeTeam( self, player, oldalliance, newalliance ):
		if newalliance == GEGlobal.TEAM_SPECTATOR:
			# The Baron cannot change to spectator!
			if self.lld_player_isbaron( player ):
				GEUtil.HudMessage( player, "#GES_GP_LALD_AREBARON", -1, 0.1, EP_SHOUT_COLOR, 3.0 )
				return False

			# Eliminate a player who attempts to grief
			if self.gamestate == self.GAMESTATE_SHUT:
				self.lld_eliminateplayer( player )
		else:
			if self.gamestate <= self.GAMESTATE_OPEN:
				self.lld_authorize_everyone()
				if self.baron_uid == 0 or not self.lld_Baron():
					self.lld_embaron_randomly()

		return True

	def OnPlayerSay( self, player, text ):
		assert isinstance( player, GEPlayer.CGEMPPlayer )
		if not player:
			return

		text = text.lower()

		if text == GEGlobal.SAY_COMMAND1:
			if self.lld_player_isbaron( player ):
				self.lld_baron_usevoodoo()
			else:
				GEUtil.HudMessage( player, "#GES_GP_LALD_NOTBARON", -1, -1, EP_SHOUT_COLOR, 2.0 )
			return True
		elif text == GEGlobal.SAY_COMMAND2:
			if player.GetTeamNumber() == GEGlobal.TEAM_SPECTATOR:
				GEUtil.ClientPrint( player, GEGlobal.HUD_PRINTTALK, "#GES_GP_NORANK" )
			else:
				rank = GEMPGameRules.GetNumActivePlayers()
				myscore = player.GetMatchScore()
				for i in range( 32 ):
					other_plr = GEPlayer.GetMPPlayer( i )
					if other_plr and other_plr.GetMatchScore() < myscore:
						rank -= 1
				GEUtil.ClientPrint( player, GEGlobal.HUD_PRINTTALK, "#GES_GP_RANK", rank, GEMPGameRules.GetNumActivePlayers() )

			return True

		elif LLD_DEBUG:
			if text == "!baron":
				Baron = self.lld_Baron()
				if Baron != None:
					GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "%d/%d, Baron: %s, Level %d" % ( Baron.GetHealth(), Baron.GetArmor(), ep_playername_by_uid( self.baron_uid ), self.baron_level ) )
				else:
					GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "There is no Baron Samedi." )
				return True
			if text == "!status" or text == "!state":
				ep_shout( "Playercount: %d/%d, Bounty: %d, State: %d, Result: %d, Denoue: %d" % ( GEMPGameRules.GetNumActivePlayers(), GEMPGameRules.GetNumActivePlayers(), self.bounty, self.gamestate, self.result, self.denouement ) )
				return True
			if text == "!embaron":
				self.lld_embaron_randomly()
				return True
			if text == "!embaron_me":
				self.lld_embaron( ep_id_by_entity( player ) )
				return True
			if text == "!levelup":
				self.lld_baron_levelup()
				self.lld_baron_givearsenel()
				return True
			if text == "!turbo":
				player.SetSpeedMultiplier( 1.5 )
				return True
			if text == "!!voodoo":
				self.lld_baron_usevoodoo()
				return True

		return False

	def CanPlayerChangeChar( self, player, ident ):
		if self.lld_player_isbaron( player ) and self.override_disembaron == 0:
			GEUtil.HudMessage( player, "#GES_GP_LALD_AREBARON", -1, 0.1, EP_SHOUT_COLOR, 3.0 )
			return ident == self.BARON_COSTUME_BARON

		if ident == self.BARON_COSTUME_BARON:
			GEUtil.HudMessage( player, "#GES_GP_LALD_IMPBARON", -1, 0.1, EP_SHOUT_COLOR, 2.0 )
			return False

		return True

	def CanPlayerHaveItem( self, player, item ):
		# The Baron can only have his alloted weapons
		if self.lld_player_isbaron( player ):
			return item.GetClassname().lower() == self.BARON_MACHETE or self.lld_baron_validweapon( item )

		return True

	def CanPlayerRespawn( self, player ):
		if player:
			if self.pltracker[player][TR_INROUND] or self.gamestate <= self.GAMESTATE_SUSPENDED:
				return True
			else:
				player.SetScoreBoardColor( GEGlobal.SB_COLOR_ELIMINATED )
				return False
		return False

	def OnThink( self ):
		if self.hack_voodoodelay == 1:
			self.lld_baron_usevoodoo()

		if self.baron_uid != 0 and self.baron_voodoo_recharge > 0:
			self.baron_voodoo_recharge -= 1
			self.lld_baron_update_voodoobar()

		num_plrs = GEMPGameRules.GetNumActivePlayers()
		if self.gamestate == self.GAMESTATE_SUSPENDED:
			if num_plrs > 1:
				self.lld_round_resume()
		elif self.gamestate == self.GAMESTATE_SHUT:
			if num_plrs < 2:
				self.gamestate = self.GAMESTATE_INACTIVE
		elif self.gamestate == self.GAMESTATE_INACTIVE:
			if num_plrs > 1:
				ep_forcerespawn()
				self.lld_round_begin()

		if self.denouement > 0:
			self.denouement -= 1
			if self.denouement == 0:
				GEMPGameRules.EndRound( True )
				self.denouement = -1

	def OnTokenSpawned( self, token ):
		GEMPGameRules.GetRadar().AddRadarContact( token, GEGlobal.RADAR_TYPE_TOKEN, True, self.RADAR_AUG_ICON )
		color = self.RADAR_SCARAMANGA
		color[3] = 120.0
		GEMPGameRules.GetRadar().SetupObjective( token, GEGlobal.TEAM_NONE, "", "", color )

	def OnTokenPicked( self, token, player ):
		self.aug_holder = player
		self.lld_progress()
		player.SetScoreBoardColor( GEGlobal.SB_COLOR_GOLD )

		radar = GEMPGameRules.GetRadar()
		radar.DropRadarContact( token )
		radar.AddRadarContact( player, GEGlobal.RADAR_TYPE_PLAYER, True, "", self.RADAR_SCARAMANGA )
		radar.SetupObjective( player, GEGlobal.TEAM_NONE, "", "", self.RADAR_SCARAMANGA )

		GEUtil.PlaySoundTo( player, "GEGamePlay.Token_Grab" )
		GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "#GES_GP_MWGG_PICKED", player.GetPlayerName() )
		GEUtil.HudMessage( player, "#GES_GP_MWGG_HAVEGG", -1, 0.75, self.RADAR_SCARAMANGA, 3.0 )
		GEUtil.EmitGameplayEvent( "lald_ggpickup", "%i" % player.GetUserID() )

	def OnTokenDropped( self, token, player ):
		self.aug_holder = None
		self.lld_progress()

		radar = GEMPGameRules.GetRadar()
		radar.DropRadarContact( player )
		radar.AddRadarContact( token, GEGlobal.RADAR_TYPE_TOKEN, True, self.RADAR_AUG_ICON )
		color = self.RADAR_SCARAMANGA
		color[3] = 120.0
		radar.SetupObjective( token, GEGlobal.TEAM_NONE, "", "", color )

		GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "#GES_GP_MWGG_DROPPED", player.GetPlayerName() )

	def OnTokenRemoved( self, token ):
		GEMPGameRules.GetRadar().DropRadarContact( token )
		GEMPGameRules.GetRadar().DropRadarContact( token.GetOwner() )

	def CalculateCustomDamage( self, victim, info, health, armour ):
		impact = health + armour

		killer = GEPlayer.ToMPPlayer( info.GetAttacker() )
		if victim == None:
			return health, armour
		if killer == None or victim == killer:
			if self.lld_player_isbaron( victim ):
				armour = 0
				health = impact
			return health, armour
		if self.lld_player_isbaron( victim ) and killer != None:
			if ep_weapon_by_info( info ) == "weapon_golden_gun":
# Baron is hit with AuG
				self.baron_stats_hitbyaug += 1
				armour = 0
				health = impact * 0.02
				if health >= victim.GetHealth():
					self.lld_eliminateplayer( victim )
			else:
				if impact >= victim.GetArmor():
# Baron is not eliminated, but is zeroed-out.
					self.baron_health_cache = victim.GetHealth() + self.BARON_SPAWN_RECOVER
# TODO: Maybe move this to On Killed?
					self.lld_baron_levelup()
					self.baron_voodoo += choice( GEUtil.GetCVarValue( self.CVAR_BLOODLUST ) != "0", self.BARON_VOODOO_BLOODLUST_LEAD, 0 )
					health = victim.GetHealth()
					armour = victim.GetArmor()
					return health, armour
				else:
# Baron is armor-damaged by player.
					health = 0
					armour = impact
					return health, armour

		elif killer != None:
			if self.lld_player_isbaron( killer ):
# Player hit by Baron, test for bloodlust.
				if ep_weapon_by_info( info ) == self.BARON_MACHETE:
					self.lld_baron_voodoo_recover( impact )

		return health, armour

	def lld_round_begin( self ):
		self.gamestate = self.GAMESTATE_OPEN
		self.aug_holder = None
		self.lld_authorize_everyone()
		self.lld_baron_initialize()
		self.lld_embaron_randomly()
		self.lld_progress()

	def lld_round_resume( self ):
		self.gamestate = self.GAMESTATE_OPEN
		self.lld_authorize_everyone()
		ep_shout( "Resuming round." )

	def lld_zot_round( self ):
		self.gamestate = self.GAMESTATE_INACTIVE
		self.result = self.RESULT_NONE
		self.denouement = -1
		self.bounty = 0

	def lld_authorize_everyone( self ):
		if self.gamestate <= self.GAMESTATE_OPEN:
			self.bounty = 0
			self.pltracker.SetValueAll( TR_INROUND, False )

			for plr in GetPlayers():
				if plr.GetTeamNumber() != GEGlobal.TEAM_SPECTATOR:
					self.pltracker[plr][TR_INROUND] = True
					self.bounty += 1

			self.lld_baron_speedamp()

	def lld_authorize_player( self, player ):
		self.pltracker[player][TR_INROUND] = True
		self.bounty += 1

	def lld_num_inround_players( self ):
		return self.pltracker.CountValues( TR_INROUND, True )

	def lld_eliminateplayer( self, player ):
		if self.gamestate == self.GAMESTATE_OPEN:
			self.lld_authorize_everyone()
			self.gamestate = self.GAMESTATE_SHUT

		if self.gamestate == self.GAMESTATE_SHUT and player != None:
			if self.pltracker.GetValue( player, TR_INROUND ):
				GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "#GES_GP_YOLT_ELIMINATED", player.GetPlayerName() )
				GEUtil.PopupMessage( player, "#GES_GPH_ELIMINATED_TITLE", "#GES_GPH_ELIMINATED" )
				self.pltracker.SetValue( player, TR_INROUND, False )
				player.SetScoreBoardColor( GEGlobal.SB_COLOR_ELIMINATED )
				self.lld_result_test()
			self.lld_baron_speedamp()
		self.lld_progress()

	def lld_Baron( self ):
		if self.baron_uid != 0:
			return ep_player_by_uid( self.baron_uid )
		return None

	def lld_baron_damageamp( self ):
		if self.baron_uid != 0:
			baron = self.lld_Baron()
			assert isinstance( baron, GEPlayer.CGEMPPlayer )
			if baron == None:
				return 0
			if self.baron_level < self.BARON_WEAPON_LIMIT:
				baron.SetDamageMultiplier( 1.0 )
				return 0
			else:
				amp = self.lld_baron_damagefactor()
				baron.SetDamageMultiplier( amp )
				return int( amp * 100.0 - 100.0 )
		return 0

	def lld_baron_damagefactor( self ):
		if self.baron_uid != 0 and self.baron_level >= self.BARON_WEAPON_LIMIT:
			amp = ep_goldeneye_handicap( ( self.baron_level - self.BARON_WEAPON_LIMIT ) * self.BARON_HANDICAP_RATE )
			amp = clamp( amp, 1.0, 21.0 )
			return amp
		return 1.0

	def lld_baron_givearsenel( self ):
		if self.baron_uid == 0:
			return
		Baron = self.lld_Baron()
		if Baron != None:
			Baron.StripAllWeapons()
			Baron.GiveNamedWeapon( self.BARON_MACHETE, 1 )
			arsenelquality = self.lld_baron_weaponlevel()
			while arsenelquality > 0:
				arsenelquality -= 1
				thisgun = ep_loadout_slot( arsenelquality )
				if thisgun != "weapon_golden_gun":
					Baron.GiveNamedWeapon( thisgun, self.BARON_SPAWN_AMMO )

	def lld_baron_initialize( self ):
		self.baron_voodoo = self.BARON_VOODOO_DEFAULT
		self.baron_level = 1
		self.baron_frags = 0
		self.baron_voodoo_recharge = 0
		self.baron_stats_hitbyaug = 0

	def lld_baron_levelup( self ):
		self.baron_level = clamp( self.baron_level + 1, 1, self.BARON_LEVEL_MAX )
		if self.baron_level <= self.BARON_WEAPON_LIMIT:
			GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, plural( self.baron_level, "#GES_GP_LALD_WEAPON" ), str( self.baron_level ) )
		else:
			GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "#GES_GP_LALD_DAMAGE", str( self.lld_baron_damageamp() ) )

	def lld_baron_remove_voodoobar( self ):
		if self.baron_uid != 0:
			Baron = self.lld_Baron()
			if Baron != None:
				GEUtil.RemoveHudProgressBar( Baron, 0 )
				GEUtil.RemoveHudProgressBar( Baron, 1 )

	def lld_baron_spawn( self, player ):
		self.lld_baron_speedamp()
		self.lld_baron_damageamp()
		self.lld_baron_givearsenel()
		if player != None:
			player.SetArmor( self.BARON_SPAWN_ARMOR )
			if self.baron_health_cache >= 0:
				player.SetHealth( max( self.BARON_SPAWN_RECOVER, self.baron_health_cache ) )

	def lld_baron_speedamp( self ):
		if self.baron_uid == 0:
			return
		Baron = self.lld_Baron()
		if Baron == None:
			return
		players = self.lld_num_inround_players();
		factor = clamp( ( 20.0 / ( float( players ) + 14.5 ) ) ** 0.5, 0.91, 1.1 )
		Baron.SetSpeedMultiplier( factor )

	def lld_baron_update_voodoobar( self ):
		HUD_WIDTH = 80
		if self.baron_uid != 0:
			Baron = self.lld_Baron()
			if Baron == None:
				return
			if self.baron_voodoo_recharge == 0:
				inflate = choice( GEUtil.GetCVarValue( self.CVAR_BLOODLUST ) != "0", 0, self.BARON_VOODOO_COST - 1 )
				width = choice( GEUtil.GetCVarValue( self.CVAR_BLOODLUST ) != "0", self.BARON_VOODOO_MAX, self.BARON_VOODOO_DEFAULT + inflate )
				casts = self.lld_baron_voodoo_castsremaining()
				if casts > 0:
					barcolor = choice( self.baron_voodoo + inflate < self.BARON_VOODOO_MAX, self.BARON_PROGRESS_NORMAL, self.BARON_PROGRESS_FULL )
					GEUtil.InitHudProgressBar( Baron, 1, "%s\r%i" % ( self.CAPTION_VOODOO, casts ), GEGlobal.HUDPB_SHOWBAR, 1, -1, .72, 0, 0, barcolor )
					GEUtil.InitHudProgressBar( Baron, 0, "", GEGlobal.HUDPB_SHOWBAR, width, -1, .76, HUD_WIDTH, 10, barcolor )
				else:
					GEUtil.InitHudProgressBar( Baron, 1, self.CAPTION_EXHAUSTED, GEGlobal.HUDPB_SHOWBAR, 1, -1, .72, 0, 0, self.BARON_PROGRESS_EXHAUSTED )
					GEUtil.InitHudProgressBar( Baron, 0, "", GEGlobal.HUDPB_SHOWBAR, width, -1, .76, HUD_WIDTH, 10, self.BARON_PROGRESS_EXHAUSTED )
					inflate = 0
				GEUtil.UpdateHudProgressBar( Baron, 0, float( self.baron_voodoo + inflate ) )
			else:
				if self.baron_voodoo_recharge >= self.BARON_VOODOO_RECHARGE - 1:
					GEUtil.InitHudProgressBar( Baron, 1, choice( self.baron_voodoo > 0, self.CAPTION_REFRACTORY, self.CAPTION_EXHAUSTED ), GEGlobal.HUDPB_SHOWBAR, 1, -1, .72, 0, 0, self.BARON_PROGRESS_EXHAUSTED )
					GEUtil.InitHudProgressBar( Baron, 0, "", GEGlobal.HUDPB_SHOWBAR, self.BARON_VOODOO_RECHARGE - 1, -1, .76, HUD_WIDTH, 10, self.BARON_PROGRESS_EXHAUSTED )
				GEUtil.UpdateHudProgressBar( Baron, 0, self.baron_voodoo_recharge )


	def lld_baron_usevoodoo( self ):
		if self.baron_uid != 0:
			Baron = self.lld_Baron()
			if Baron == None:
				return False
			if self.baron_voodoo_recharge == 0 and self.result == self.RESULT_NONE and Baron.IsDead() == False:
				if self.baron_voodoo > 0:
					if self.hack_voodoodelay == 0:
						self.hack_voodoodelay = 1
						GEUtil.ParticleEffect( Baron, "eyes", "ge_baron_teleport", False )
						return
					self.hack_voodoodelay = 0
					self.baron_voodoo = max( 0, self.baron_voodoo - self.BARON_VOODOO_COST )
					self.baron_voodoo_recharge = self.BARON_VOODOO_RECHARGE
					self.baron_health_cache = Baron.GetHealth() + self.BARON_SPAWN_RECOVER
					self.lld_baron_levelup()
					Baron.ForceRespawn()
					self.lld_baron_update_voodoobar()
					GEUtil.PlaySoundTo( None, "GEGamePlay.Baron_Voodoo", True )
					return True
				else:
					GEUtil.HudMessage( self.lld_Baron(), "#GES_GP_LALD_NOPOWER", -1, -1, EP_SHOUT_COLOR, 2.0 )
		return False

	def lld_baron_validweapon( self, weapon ):
		if weapon == None:
			return False
		wname = weapon.GetClassname().lower()
		if wname != "weapon_golden_gun":
			for j in range( self.lld_baron_weaponlevel() ):
				if wname == ep_loadout_slot( j ):
					return True
		return False

	def lld_baron_voodoo_castsremaining( self ):
		return int( int( self.baron_voodoo + self.BARON_VOODOO_COST - 1 ) / self.BARON_VOODOO_COST )

	def lld_baron_weaponlevel( self ):
		if self.baron_level > 0:
			return clamp( self.baron_level, 1, self.BARON_WEAPON_LIMIT )
		return 0

	def lld_costume_failsafe( self, player ):
		if player == None:
			return
		if self.lld_player_isbaron( player ):
			if player.GetPlayerModel() != self.BARON_COSTUME_BARON:
				player.SetPlayerModel( self.BARON_COSTUME_BARON, 0 )
		else:
			if player.GetPlayerModel() == self.BARON_COSTUME_BARON:
				player.SetPlayerModel( self.BARON_COSTUME_DEFAULT, 0 )

	def lld_baron_voodoo_recover( self, damage ):
		if GEUtil.GetCVarValue( self.CVAR_BLOODLUST ) == "0":
			return
		casts = self.lld_baron_voodoo_castsremaining()
		self.baron_voodoo += choice( damage >= 80, self.BARON_VOODOO_BLOODLUST_BODY, self.BARON_VOODOO_BLOODLUST_LIMB )
		self.baron_voodoo = clamp( self.baron_voodoo, 0, self.BARON_VOODOO_MAX )
		self.lld_baron_update_voodoobar()
		if casts < self.lld_baron_voodoo_castsremaining():
			if self.baron_uid != 0:
				Baron = self.lld_Baron()
				if Baron != None:
					GEUtil.PlaySoundTo( Baron, "GEGamePlay.Token_Chime" )

	def lld_declare_baron_data( self ):
		self.BARON_MACHETE = 'weapon_knife'
		self.BARON_COSTUME_DEFAULT = "bond"
		self.BARON_COSTUME_BARON = "samedi"
		self.BARON_HANDICAP_RATE = 0.5
		self.BARON_LEVEL_MAX = 35
		self.BARON_PROGRESS_FULL = Color( 180, 225, 255, 170 )
		self.BARON_PROGRESS_NORMAL = Color( 240, 200, 120, 170 )
		self.BARON_PROGRESS_EXHAUSTED = Color( 240, 120, 120, 170 )
		self.BARON_SPAWN_AMMO = 86
		self.BARON_SPAWN_ARMOR = int( GEGlobal.GE_MAX_ARMOR * 5 / 8 )
		self.BARON_SPAWN_RECOVER = int( GEGlobal.GE_MAX_HEALTH / 4 )
		self.BARON_SPAWN_HEALTH = self.BARON_SPAWN_RECOVER
		self.BARON_WEAPON_LIMIT = 8
		self.BARON_VOODOO_BLOODLUST_LEAD = 0
		self.BARON_VOODOO_BLOODLUST_LIMB = 1
		self.BARON_VOODOO_BLOODLUST_BODY = 2
		self.BARON_VOODOO_COST = 7
		self.BARON_VOODOO_DEFAULT = self.BARON_VOODOO_COST * 2 + 1
		self.BARON_VOODOO_MAX = self.BARON_VOODOO_DEFAULT + self.BARON_VOODOO_COST
		self.BARON_VOODOO_RECHARGE = 40
		self.baron_uid = 0
		self.baron_previous_uid = 0
		self.baron_level = 0
		self.baron_voodoo = 0
		self.baron_frags = 0
		self.baron_voodoo_recharge = 0
		self.baron_health_cache = -1
		self.baron_costume_cache = self.BARON_COSTUME_DEFAULT
		self.baron_costume_cache_skin = 0

	def lld_declare_scenario_data( self ):
		self.AURA_AUG = Color( 244, 192, 11, 64 )
		self.RADAR_AUG_ICON = "ge_radar_gg"
		self.RADAR_BARON_ICON = "sprites/hud/radar/baron"
		self.RADAR_SCARAMANGA = Color( 232, 180, 2, 255 )
		self.TOKEN_AUG_ENTITY = 'weapon_golden_gun'
		self.RESULT_NONE = 0
		self.RESULT_BONDWIN = 1
		self.RESULT_BARONWIN = 2
		self.CAPTION_EXHAUSTED = "#GES_GP_LALD_NOVOODOO"
		self.CAPTION_VOODOO = "#GES_GP_LALD_VOODOO"
		self.CAPTION_REFRACTORY = "#GES_GP_LALD_WAITVOODOO"
		self.DENOUEMENT_SHORT = 17
		self.DENOUEMENT_LONG = self.DENOUEMENT_SHORT * 2
		self.GAMESTATE_INACTIVE = 5
		self.GAMESTATE_SUSPENDED = 15
		self.GAMESTATE_OPEN = 25
		self.GAMESTATE_SHUT = 35
		self.GAMESTATE_ENDOFROUND = 45
		self.PROGRESS_YLOC = .02
		self.gamestate = self.GAMESTATE_INACTIVE
		self.override_disembaron = 0
		self.denouement = -1
		self.bounty = 0
		self.result = self.RESULT_NONE
		self.hack_voodoodelay = 0
		self.aug_holder = None

	def lld_declarewinner_baron( self ):
		self.gamestate = self.GAMESTATE_ENDOFROUND
		self.result = self.RESULT_BARONWIN
		ep_shout( "#GES_GP_LALD_BARONWINS" )
		self.denouement = self.DENOUEMENT_LONG
		baron = self.lld_Baron()
		baron.AddRoundScore( self.bounty - 1 - baron.GetScore() )

	def lld_declarewinner_misix( self ):
		self.gamestate = self.GAMESTATE_ENDOFROUND
		self.result = self.RESULT_BONDWIN
		self.denouement = self.DENOUEMENT_SHORT
		ep_shout( "#GES_GP_LALD_BARONLOSES" )

	def lld_embaron( self, uid ):
		if uid != 0:
			self.lld_disembaron()
			self.baron_uid = uid

			Baron = self.lld_Baron()
			if Baron != None:
				self.baron_costume_cache = Baron.GetPlayerModel() if Baron.GetPlayerModel() != self.BARON_COSTUME_BARON else self.BARON_COSTUME_DEFAULT
				self.baron_costume_cache_skin = Baron.GetSkin()
				Baron.SetPlayerModel( self.BARON_COSTUME_BARON, 0 )
				self.lld_baron_update_voodoobar()
				GEMPGameRules.GetRadar().DropRadarContact( Baron )
				GEMPGameRules.GetRadar().AddRadarContact( Baron, GEGlobal.RADAR_TYPE_PLAYER, True, self.RADAR_BARON_ICON )
				# Only the GG Holder can see the baron's objective icon
				GEMPGameRules.GetRadar().SetupObjective( Baron, GEGlobal.TEAM_NONE, self.TOKEN_AUG_ENTITY, "", Color( 255, 255, 255, 100 ), 300 )
				self.lld_baron_spawn( Baron )
				Baron.SetScoreBoardColor( GEGlobal.SB_COLOR_WHITE )
				# Baron specific help
				if not self.pltracker.GetValue( Baron, "baronhelp" ):
					self.ShowScenarioHelp( Baron, self.HELPID_BARON )
					self.pltracker.SetValue( Baron, "baronhelp", True )

	def lld_disembaron( self ):
		baron = self.lld_Baron()
		if baron != None:
			# This override prevents the costume control from blocking the still-Baron-UID player from reverting.
			self.override_disembaron = 1
			baron.SetPlayerModel( self.baron_costume_cache, self.baron_costume_cache_skin )
			self.override_disembaron = 0
			self.baron_costume_cache = self.BARON_COSTUME_DEFAULT
			self.baron_costume_cache_skin = 0
			self.lld_baron_remove_voodoobar()
			GEMPGameRules.GetRadar().DropRadarContact( baron )
			baron.SetDamageMultiplier( 1.0 )
			baron.SetScoreBoardColor( GEGlobal.SB_COLOR_NORMAL )

		self.baron_previous_uid = self.baron_uid
		self.baron_uid = 0

	def lld_embaron_randomly( self ):
		if self.lld_num_inround_players() < 2:
			return
		self.lld_disembaron()

		players = self.pltracker.GetPlayers( TR_INROUND, True )
		prospect_uid = 0
		while prospect_uid == 0:
			choice = random.choice( players )
			if choice != self.baron_previous_uid:
				prospect_uid = choice.GetUID()

		self.lld_embaron( prospect_uid )

	def lld_misix_jackpot( self ):
		for player in GetPlayers():
			if self.pltracker[player][TR_INROUND]:
				player.AddRoundScore( self.bounty )

	def lld_player_isbaron( self, player ):
		return self.baron_uid != 0 and self.baron_uid == ep_id_by_entity( player )

	def lld_progress( self ):
		if self.gamestate != self.GAMESTATE_SHUT and self.gamestate != self.GAMESTATE_OPEN:
			GEUtil.RemoveHudProgressBar( None, 3 )
		else:
			barcolor = choice( self.aug_holder != None, self.BARON_PROGRESS_NORMAL, self.BARON_PROGRESS_FULL )
			GEUtil.InitHudProgressBar( None, 3, "#GES_GP_FOES", GEGlobal.HUDPB_SHOWVALUE, self.bounty - 1, -1, self.PROGRESS_YLOC, 0, 10, barcolor )
			playerslessone = self.lld_num_inround_players() - 1
			if playerslessone > 1:
				GEUtil.UpdateHudProgressBar( None, 3, playerslessone )
			elif playerslessone == 1:
				GEUtil.InitHudProgressBar( None, 3, "#GES_GP_SHOWDOWN", GEGlobal.HUDPB_SHOWBAR, self.bounty - 1, -1, self.PROGRESS_YLOC, 0, 10, barcolor )
			else:
				GEUtil.RemoveHudProgressBar( None, 3 )

	def lld_result_test( self ):
		if ( self.gamestate == self.GAMESTATE_OPEN or self.gamestate == self.GAMESTATE_SHUT ) and self.result == self.RESULT_NONE:
			if self.baron_uid != 0:
				if not self.pltracker[self.baron_uid][TR_INROUND]:
					self.lld_declarewinner_misix()
				elif self.lld_num_inround_players() == 1:
					self.lld_declarewinner_baron()
