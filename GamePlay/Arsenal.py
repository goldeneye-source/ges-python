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
from Utils.GEWarmUp import GEWarmUp
from Utils.GEPlayerTracker import GEPlayerTracker
from Utils import GetPlayers, clamp, _
from random import shuffle
import GEUtil, GEMPGameRules as GERules, GEGlobal, GEPlayer, GEWeapon

# Arsenal
# Coded by Troy and Killer Monkey
# /////////////////////////// Scenario Data ///////////////////////////

USING_API = GEGlobal.API_VERSION_1_1_1

weaponList = [
    ( "weapon_golden_pp7", 50 ), ( "weapon_golden_gun", 20 ), ( "weapon_moonraker", 0 ), ( "weapon_silver_pp7", 50 ),
    ( "weapon_rcp90", 150 ), ( "weapon_ar33", 150 ), ( "weapon_auto_shotgun", 40 ), ( "weapon_cmag", 50 ), ( "weapon_phantom", 150 ),
    ( "weapon_shotgun", 40 ), ( "weapon_sniper_rifle", 75 ), ( "weapon_kf7", 150 ), ( "weapon_d5k", 150 ), ( "weapon_zmg", 150 ),
    ( "weapon_pp7", 50 ), ( "weapon_dd44", 50 ), ( "weapon_klobb", 150 ), ( "weapon_knife", 0 )
]

weaponListCopy = list( weaponList )
maxLevel = len( weaponList ) - 1

TR_ROUND = "round"
TR_LEVEL = "level"
TR_SPAWNED = "spawned"

class Arsenal( GEScenario ):
    def __init__( self ):
        GEScenario.__init__( self )

        self.WaitingForPlayers = True
        self.RoundNumber = 0
        self.notice_WaitingForPlayers = 0

        self.warmupTimer = GEWarmUp( self )
        self.pltracker = GEPlayerTracker( self )

        # CVar Holders
        self.RoundLimit = 3
        self.RandomWeapons = False

    def GetPrintName( self ):
        return "#GES_GP_ARSENAL_NAME"

    def GetScenarioHelp( self, help_obj ):
        help_obj.SetDescription( "#GES_GP_ARSENAL_HELP" )

    def GetGameDescription( self ):
        return "Arsenal"

    def GetTeamPlay( self ):
        return GEGlobal.TEAMPLAY_NONE

    def OnLoadGamePlay( self ):
        global weaponList

        GEUtil.PrecacheSound( "GEGamePlay.Token_Drop_Enemy" )
        GEUtil.PrecacheSound( "GEGamePlay.Token_Grab" )
        GEUtil.PrecacheSound( "GEGamePlay.Token_Grab_Enemy" )

        self.CreateCVar( "ar_lowestlevel", "1", "Give new players the lowest active player's level. (Use 0 to start new players at level 1)" )
        self.CreateCVar( "ar_warmuptime", "20", "The warmup time in seconds. (Use 0 to disable)" )
        self.CreateCVar( "ar_numrounds", "3", "The number of rounds that should be played per map. (Use 0 to play until time runs out, Max is 10)" )
        self.CreateCVar( "ar_randomweapons", "0", "Randomize the weapons every round." )

        # Make sure we don't start out in wait time if we changed gameplay mid-match
        if GERules.GetNumActivePlayers() >= 2:
            self.WaitingForPlayers = False

        # Restore the default weapon list
        if weaponList != weaponListCopy:
            weaponList = list( weaponListCopy )

    def OnUnloadGamePlay( self ):
        GEScenario.OnUnloadGamePlay( self )
        self.warmupTimer = None
        self.pltracker = None

    def OnCVarChanged( self, name, oldvalue, newvalue ):
        global weaponList

        if name == "ar_numrounds":
            # Clamp the roundlimit
            val = clamp( int( newvalue ), 0, 10 )
            if val != self.RoundLimit:
                if self.RoundNumber > val and val > 0:
                    GERules.EndMatch()
                self.RoundLimit = val
        elif name == "ar_randomweapons":
            val = int( newvalue )
            if val == 0 and self.RandomWeapons:
                self.RandomWeapons = False
                weaponList = list( weaponListCopy )
                if not GERules.IsIntermission():
                    GERules.EndRound()
            elif val != 0 and not self.RandomWeapons:
                self.RandomWeapons = True
                if not GERules.IsIntermission():
                    GERules.EndRound()
        elif name == "ar_warmuptime":
            if self.warmupTimer.IsInWarmup():
                val = int( newvalue )
                self.warmupTimer.StartWarmup( val )
                if val <= 0:
                    GERules.EndRound( False )

    def OnRoundBegin( self ):
        GEScenario.OnRoundBegin( self )

        GERules.AllowRoundTimer( False )
        GERules.DisableWeaponSpawns()
        GERules.DisableAmmoSpawns()
        GERules.DisableArmorSpawns()

        if self.RandomWeapons:
            shuffle( weaponList )

        for player in GetPlayers():
            self.SetLevel( player, 0 )
            self.pltracker[player][TR_ROUND] = True
            if player.GetTeamNumber() != GEGlobal.TEAM_SPECTATOR:
                self.PrintCurLevel( player )

        if not self.WaitingForPlayers and not self.warmupTimer.IsInWarmup():
            self.RoundNumber += 1

    def OnRoundEnd( self ):
        if self.RoundNumber == self.RoundLimit and self.RoundLimit > 0:
            GERules.EndMatch()

    def OnPlayerConnect( self, player ):
        self.SetLevel( player, 0 )
        self.pltracker[player][TR_ROUND] = True
        self.pltracker[player][TR_SPAWNED] = False

    def OnPlayerSpawn( self, player ):
        if not self.WaitingForPlayers and not self.warmupTimer.IsInWarmup():
            if not self.pltracker[player][TR_SPAWNED] and int( GEUtil.GetCVarValue( "ar_lowestlevel" ) ) != 0:
                self.SetLevel( player, self.LowestLevel() )

            if self.pltracker[player][TR_ROUND] and self.RoundLimit > 0:
                if self.RoundNumber < self.RoundLimit:
                    GEUtil.HudMessage( player, _( "#GES_GP_AR_ROUNDCOUNT", self.RoundNumber, self.RoundLimit ), -1, 0.02, GEUtil.Color( 170, 170, 170, 220 ), 3.5 )
                else:
                    GEUtil.HudMessage( player, "#GES_GP_AR_FINALROUND", -1, 0.02, GEUtil.Color( 206, 43, 43, 255 ), 3.5 )

                self.pltracker[player][TR_ROUND] = False

        self.GivePlayerWeapons( player )
        self.pltracker[player][TR_SPAWNED] = True

        if player.IsInitialSpawn():
            GEUtil.PopupMessage( player, "#GES_GP_ARSENAL_NAME", "#GES_GPH_AR_GOAL" )

    def OnPlayerKilled( self, victim, killer, weapon ):
        if self.WaitingForPlayers or self.warmupTimer.IsInWarmup() or not victim:
            return

        kL = self.GetLevel( killer )
        vL = self.GetLevel( victim )

        name = weapon.GetClassname().lower()
        if name.startswith( "npc_" ):
            if name == "npc_grenade":
                name = "weapon_grenade"
            elif name == "npc_rocket":
                name = "weapon_rocket_launcher"
            elif name == "npc_shell":
                name = "weapon_grenade_launcher"
            elif name == "npc_mine_remote":
                name = "weapon_remotemine"
            elif name == "npc_mine_timed":
                name = "weapon_timedmine"
            elif name == "npc_mine_proximity":
                name = "weapon_proximitymine"

        if not killer or victim == killer:
            # World kill or suicide
            if vL > 0:
                self.IncrementLevel( victim, -1 )
                GEUtil.PlaySoundTo( victim, "GEGamePlay.Token_Drop_Enemy" )
                GEUtil.EmitGameplayEvent( "ar_levelchange", str( victim.GetUserID() ), str( vL + 1 ), "suicide" )
        elif name == weaponList[kL][0] or name == "weapon_knife" or name == "weapon_slappers":
            # Normal kill
            if name == "weapon_knife" and vL > 0:
                self.IncrementLevel( victim, -1 )
                GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "#GES_GP_GUNGAME_KNIFED", victim.GetCleanPlayerName() )
                GEUtil.PlaySoundTo( victim, "GEGamePlay.Token_Drop_Enemy" )
                GEUtil.EmitGameplayEvent( "ar_levelchange", str( victim.GetUserID() ), str( vL + 1 ), "knifed" )
            elif name == "weapon_slappers":
                if vL > 0:
                    self.IncrementLevel( victim, -1 )
                    GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "#GES_GP_GUNGAME_SLAPPED", victim.GetCleanPlayerName(), killer.GetCleanPlayerName() )
                    GEUtil.PlaySoundTo( victim, "GEGamePlay.Token_Drop_Enemy" )
                    GEUtil.EmitGameplayEvent( "ar_levelchange", str( victim.GetUserID() ), str( vL + 1 ), "slapped" )
                else:
                    GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "#GES_GP_GUNGAME_SLAPPED_NOLOSS", victim.GetCleanPlayerName(), killer.GetCleanPlayerName() )

                killer.SetArmor( int( GEGlobal.GE_MAX_ARMOR ) )

            self.IncrementLevel( killer, 1 )
            GEUtil.EmitGameplayEvent( "ar_levelchange", str( killer.GetUserID() ), str( self.GetLevel( killer ) + 1 ) )

            if self.GetLevel( killer ) < maxLevel:
                GEUtil.PlaySoundTo( killer, "GEGamePlay.Token_Grab" )
            elif self.GetLevel( killer ) == maxLevel:
                GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "#GES_GP_AR_FINALWEAPON", killer.GetCleanPlayerName() )
                GEUtil.PlaySoundTo( killer, "GEGamePlay.Token_Grab_Enemy" )

            if self.GetLevel( killer ) <= maxLevel:
                self.PrintCurLevel( killer )
                self.GivePlayerWeapons( killer )
            elif not GERules.IsIntermission():
                GERules.EndRound()

    def OnThink( self ):
        # Check for insufficient player count
        if GERules.GetNumActivePlayers() < 2:
            if not self.WaitingForPlayers:
                self.notice_WaitingForPlayers = 0
                GERules.EndRound()
            elif GEUtil.GetTime() > self.notice_WaitingForPlayers:
                GEUtil.HudMessage( None, "#GES_GP_WAITING", -1, -1, GEUtil.Color( 255, 255, 255, 255 ), 2.5, 1 )
                self.notice_WaitingForPlayers = GEUtil.GetTime() + 12.5

            self.warmupTimer.Reset()
            self.WaitingForPlayers = True
            return
        elif self.WaitingForPlayers:
            self.WaitingForPlayers = False
            if not self.warmupTimer.HadWarmup():
                self.warmupTimer.StartWarmup( int( GEUtil.GetCVarValue( "ar_warmuptime" ) ), True )
            else:
                GERules.EndRound( False )

    def CanPlayerHaveItem( self, player, item ):
        weapon = GEWeapon.ToGEWeapon( item )
        if weapon:
            name = weapon.GetClassname().lower()
            pL = self.pltracker[player][TR_LEVEL]

            if pL > maxLevel:
                return True

            if name == weaponList[pL][0] or name == "weapon_knife" or name == "weapon_slappers":
                return True

            return False

        return True

    def OnPlayerSay( self, player, text ):
        if text.lower() == GEGlobal.SAY_COMMAND1:
            self.PrintWeapons( player )
            return True

        return False

# /////////////////////////// Utility Functions ///////////////////////////

    def GetLevel( self, player ):
        if not player:
            return -1

        return self.pltracker[player][TR_LEVEL]

    def SetLevel( self, player, lvl ):
        if not player:
            return

        self.pltracker[player][TR_LEVEL] = lvl
        player.SetScore( lvl + 1 )

    def IncrementLevel( self, player, amt ):
        self.SetLevel( player, self.pltracker[player][TR_LEVEL] + amt )

    def PrintCurLevel( self, player ):
        if not player:
            return

        lvl = self.GetLevel( player )

        name = GEWeapon.WeaponPrintName( weaponList[lvl][0] )
        GEUtil.ClientPrint( player, GEGlobal.HUD_PRINTTALK, "#GES_GP_GUNGAME_LEVEL", str( lvl + 1 ), name )

    def GivePlayerWeapons( self, player ):
        if not player or player.IsDead():
            return

        player.StripAllWeapons()

        player.GiveNamedWeapon( "weapon_slappers", 0 )
        player.GiveNamedWeapon( "weapon_knife", 0 )

        weap = weaponList[self.GetLevel( player )]

        if weap[0] != "weapon_slappers" and weap[0] != "weapon_knife":
            player.GiveNamedWeapon( weap[0], weap[1] )

        player.WeaponSwitch( weap[0] )

    def LowestLevel( self ):
        listing = []
        for i in range( 32 ):
            player = GEPlayer.GetMPPlayer( i )
            if player and player.GetTeamNumber() != GEGlobal.TEAM_SPECTATOR and self.pltracker[player][TR_SPAWNED]:
                listing.append( self.GetLevel( player ) )

        if len( listing ) == 0:
            return 0

        return min( listing )

    def PrintWeapons( self, player ):
        if not player:
            return

        curr_level = self.GetLevel( player )
        # Players above the max level don't see anything
        if curr_level > maxLevel:
            return

        # Players at the max level see this message only
        if curr_level == maxLevel:
            GEUtil.PopupMessage( player, "#GES_GP_ARSENAL_NAME", "You are on the final level!" )
            return

        # Start with the player's current level
        arWeapons = "Current level %i: #%s\n" % ( curr_level + 1, GEWeapon.WeaponPrintName( weaponList[curr_level][0] ) )

        # Output up to the next 4 weapons for this player, not including the final weapon
        count = 0
        for i in range( curr_level + 1, maxLevel ):
            count += 1
            arWeapons += "Level %i: #%s\n" % ( i + 1, GEWeapon.WeaponPrintName( weaponList[i][0] ) )
            if count == 4:
                break

        # Tack on the final weapon
        if curr_level >= maxLevel - 5:
            arWeapons += "Final level %i: #%s\n" % ( len( weaponList ), GEWeapon.WeaponPrintName( weaponList[-1][0] ) )
        else:
            arWeapons += "\nFinal level %i: #%s\n" % ( len( weaponList ), GEWeapon.WeaponPrintName( weaponList[-1][0] ) )

        # Finally show the message to the requesting player
        GEUtil.PopupMessage( player, "#GES_GP_ARSENAL_NAME", arWeapons )
