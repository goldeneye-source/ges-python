################ Copyright 2005-2016 Team GoldenEye: Source #################
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
from .Utils.GEWarmUp import GEWarmUp
from .Utils.GEPlayerTracker import GEPlayerTracker
from .Utils import GetPlayers, clamp, _
import GEUtil, GEMPGameRules as GERules, GEGlobal as Glb, GEPlayer, GEWeapon

# Arsenal
# Coded by Troy and Killer Monkey
# and completely ruined by E-S
# /////////////////////////// Scenario Data ///////////////////////////

USING_API = Glb.API_VERSION_1_2_0

maxLevel = 8

TR_LEVEL = "level" # Player's current level.
TR_LEVELKILLS = "levelkills" # How many kills the player has earned this level.
TR_SPAWNED = "spawned" # If the player has spawned in yet.

class Arsenal( GEScenario ):
    def __init__( self ):
        GEScenario.__init__( self )

        self.WaitingForPlayers = True
        self.weaponList = []

        self.warmupTimer = GEWarmUp( self )
        self.pltracker = GEPlayerTracker( self )

        # CVar Holders
        self.KillsPerLevel = 2 # How many kills it takes to advance to the next level
        self.LevelBoost = True # If players who joined late get boosted to the level of the player in last place.

    def GetPrintName( self ):
        return "#GES_GP_ARSENAL_NAME"

    def GetScenarioHelp( self, help_obj ):
        help_obj.SetDescription( "#GES_GP_ARSENAL_HELP" )

    def GetGameDescription( self ):
        return "Arsenal"

    def GetTeamPlay( self ):
        return Glb.TEAMPLAY_NONE

    def OnLoadGamePlay( self ):
        GEUtil.PrecacheSound( "GEGamePlay.Token_Drop_Enemy" ) # Used for final weapon.
        GEUtil.PrecacheSound( "GEGamePlay.Level_Up" ) # Plays when level is gained
        GEUtil.PrecacheSound( "GEGamePlay.Level_Down" ) # Plays when level is lost

        self.CreateCVar( "ar_lowestlevel", "1", "Give new players the lowest active player's level. (Use 0 to start new players at level 1)" )
        self.CreateCVar( "ar_warmuptime", "15", "The warmup time in seconds. (Use 0 to disable)" )
        self.CreateCVar( "ar_killsperlevel", "2", "How many kills is required to level up to the next weapon." )
        
        # Make sure we don't start out in wait time or have a warmup if we changed gameplay mid-match
        if GERules.GetNumActivePlayers() >= 2:
            self.WaitingForPlayers = False
            self.warmupTimer.StartWarmup(0)

        GERules.EnableSuperfluousAreas()
        GERules.EnableInfiniteAmmo()

    def OnUnloadGamePlay(self):
        super( Arsenal, self ).OnUnloadGamePlay()
        self.warmupTimer = None
        self.pltracker = None

    def OnCVarChanged( self, name, oldvalue, newvalue ):
        if name == "ar_killsperlevel":
            self.KillsPerLevel = int( newvalue )
        elif name == "ar_lowestlevel":
            if int( newvalue ) > 0:
                self.LevelBoost = True
            else:
                self.LevelBoost = False
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

        self.weaponList = [] #Clear our weapon list

        # Store all the current weaponset's weapons in a list for easy access.
        for i in range(0, 8):
            self.weaponList.append( GEWeapon.WeaponClassname(GERules.GetWeaponInSlot(i)) )

        # Reset all player's statistics 
        self.pltracker.SetValueAll( TR_LEVEL, 0 )
        self.pltracker.SetValueAll( TR_LEVELKILLS, 0 )

        for player in GetPlayers():
            self.ar_SetLevel( player, 0 )
            self.ar_SetKills( player, 0 )
            if player.GetTeamNumber() != Glb.TEAM_SPECTATOR:
                self.ar_PrintCurLevel( player )

    def OnPlayerConnect( self, player ):
        self.pltracker[player][TR_LEVEL] = 0
        self.pltracker[player][TR_LEVELKILLS] = 0
        self.pltracker[player][TR_SPAWNED] = False

    def OnPlayerSpawn( self, player ):
        if not self.WaitingForPlayers and not self.warmupTimer.IsInWarmup():
            if not self.pltracker[player][TR_SPAWNED]:
                if self.LevelBoost:
                    self.ar_SetLevel( player, self.ar_LowestLevel() ) # Give the player a calculated minimum level on their first spawn this round so they don't start behind.
                else:
                    self.ar_SetLevel( player, 0 ) # We still need to do this so we display the level intro text.

                self.pltracker[player][TR_SPAWNED] = True
            else: # If this isn't our first spawn, the SetLevel command isn't going to give us our weapon so we have to do it here.
                self.ar_GivePlayerWeapons( player )

        if player.IsInitialSpawn():
            GEUtil.PopupMessage( player, "#GES_GP_ARSENAL_NAME", "#GES_GPH_AR_GOAL" )

    def OnPlayerKilled( self, victim, killer, weapon ):
        if self.WaitingForPlayers or self.warmupTimer.IsInWarmup() or GERules.IsIntermission() or not victim:
            return

        kL = self.ar_GetLevel( killer )
        vL = self.ar_GetLevel( victim )

        # Convert projectile entity names to their corresponding weapon
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
            self.ar_IncrementKills( victim, -1 )
        else:
            # Normal kill
            if name == "weapon_slappers" or name == "player": # Slappers or killbind.
                self.ar_IncrementLevel( victim, -1 )
                if vL > 0:
                    self.ar_IncrementLevel( killer, 1 ) # Jump forward an entire level, keeping our kill count.
                    msg = _( "#GES_GP_GUNGAME_SLAPPED", victim.GetCleanPlayerName(), killer.GetCleanPlayerName() )
                    GEUtil.PostDeathMessage( msg )
                    GEUtil.EmitGameplayEvent( "ar_levelsteal", str( killer.GetUserID() ), str( victim.GetUserID() ), "", "", True ) #Acheivement event
                else:
                    msg = _( "#GES_GP_GUNGAME_SLAPPED_NOLOSS", killer.GetCleanPlayerName() )
                    GEUtil.PostDeathMessage( msg )
                    self.ar_IncrementKills( killer, 1 ) # We can't steal a whole level but we can at least get a kill.

                killer.SetArmor( int( Glb.GE_MAX_ARMOR ) )
            elif maxLevel == self.ar_GetLevel( killer ):
                self.ar_IncrementLevel( killer, 1 ) # Final level only needs one kill.
            else:
                self.ar_IncrementKills( killer, 1 )

        victim.StripAllWeapons() # This prevents the victim from dropping weapons, which might confuse players since there are no pickups.

    def OnThink( self ):
        #Check to see if we can get out of warmup
        if self.WaitingForPlayers and GERules.GetNumActivePlayers() > 1:
            self.WaitingForPlayers = False
            if not self.warmupTimer.HadWarmup():
                self.warmupTimer.StartWarmup( int( GEUtil.GetCVarValue( "ar_warmuptime" ) ), True )
            else:
                GERules.EndRound( False )

    # I'm not sure if this function is entirely neccecery now, since it was designed to stop people from picking up dropped weapons.
    # It's a good failsafe at least, since even if players no longer drop weapons on death there are other rare sources for them to get weapons from.
    # Like thrown throwing knives and explicity spawned weapons, which some community maps might give.
    def CanPlayerHaveItem( self, player, item ):
        weapon = GEWeapon.ToGEWeapon( item )
        if weapon:
            name = weapon.GetClassname().lower()
            pL = self.pltracker[player][TR_LEVEL]

            if name == "weapon_slappers":
                return True

            if len(self.weaponList) < pL:
                return True

            if len(self.weaponList) == pL:
                return name == "weapon_knife"

            if name == self.weaponList[pL]:
                return True

            return False

        return True

    def CanMatchEnd( self ):
        if GERules.IsIntermission() or GERules.GetNumActivePlayers() < 2: #We just finished a round or it's not possible to get kills.
            return True
        else:
            return False

# /////////////////////////// Utility Functions ///////////////////////////

    # Returns the given player's level
    def ar_GetLevel( self, player ):
        if not player:
            return -1

        return self.pltracker[player][TR_LEVEL]

    # Set the given player's level to the given amount and give them their weapon.
    def ar_SetLevel( self, player, lvl ):
        if not player:
            return

        oldlvl = self.pltracker[player][TR_LEVEL]
        self.pltracker[player][TR_LEVEL] = lvl
        player.SetScore( lvl + 1 ) # Correcting for the fact that "level 1" is actually 0 in the code, 2 is 1, 3 is 2, etc.
        GEUtil.EmitGameplayEvent( "ar_levelchange", str( player.GetUserID() ), str( lvl ) )

        # Play effects, but only if we actually changed level.  Also avoids playing effects on first spawn since starting level
        # is 0 and setlevel is called with 0 on first spawn.  With minimum level above 0 it will play effects, but it should.
        if lvl != oldlvl and lvl <= maxLevel:
            if self.ar_GetLevel( player ) == maxLevel: # Final level gets a special sound and announces to everyone.
                msg = _( "#GES_GP_AR_FINALWEAPON", player.GetCleanPlayerName() )
                GEUtil.PostDeathMessage( msg )
                GEUtil.PlaySoundTo( player, "GEGamePlay.Token_Grab_Enemy" )
            elif lvl > oldlvl: # Gained a level
                GEUtil.PlaySoundTo( player, "GEGamePlay.Level_Up" )
            else: # Lost a level.
                GEUtil.PlaySoundTo( player, "GEGamePlay.Level_Down" )


        # Give weapons and print level.
        if lvl <= maxLevel: # Can't give weapons if we're somehow past the max level.
            self.ar_PrintCurLevel( player )
            self.ar_GivePlayerWeapons( player )         
        elif not GERules.IsIntermission(): # In fact, if we are, we just won!
            GEUtil.EmitGameplayEvent( "ar_completedarsenal", str( player.GetUserID()), "", "", "", True ) #Used for acheivements so we have to send to clients
            GERules.EndRound()
            

    # Set the given player's level kills to the given amount.
    # Some minimal handling of advancing to other levels with killcount increments other than 1, but the gamemode never uses this so if you
    # want to modify it to use higher killcount increments for things it might be worth buffing up these functions a bit.
    def ar_SetKills( self, player, kills ):
        if not player:
            return
        
        if ( kills >= self.KillsPerLevel ):
            self.ar_IncrementLevel( player, 1 )
            self.pltracker[player][TR_LEVELKILLS] = 0
        elif (kills < 0):
            self.ar_IncrementLevel( player, -1 )
            self.pltracker[player][TR_LEVELKILLS] = max(self.KillsPerLevel + kills, 0) # Kills is negative here so we're using it to correct previous level killcount.      
        else:
            self.pltracker[player][TR_LEVELKILLS] = kills # No level advancement, just complete the request as asked.
            msg = _( "#GES_GP_GUNGAME_KILLS", str(self.KillsPerLevel - kills) ) # We didn't increment a level which would have caused a level advancement message.
            GEUtil.HudMessage( player, msg, -1, 0.71, GEUtil.Color( 220, 220, 220, 255 ), 1.5, 2 ) # So give a killcount message instead.

    # Advance the given player's level by the given amount.
    def ar_IncrementLevel( self, player, amt ):
        if (self.pltracker[player][TR_LEVEL] + amt > 0): # Make sure there's enough levels to take off
            self.ar_SetLevel( player, self.pltracker[player][TR_LEVEL] + amt )
        else:
            self.ar_SetKills( player, 0 ) # If we can't take off a level we'll just take all of their kills.
            self.ar_SetLevel( player, 0 ) # and set them to the lowest level, just in case someone changed the design of the mode and expected to take off 2 or more.

    # Advance the given player's level kills by the given amount.
    def ar_IncrementKills( self, player, amt ):
        self.ar_SetKills( player, self.pltracker[player][TR_LEVELKILLS] + amt )

    # Present a HUD message with the player's current level
    def ar_PrintCurLevel( self, player ):
        if not player:
            return

        lvl = self.ar_GetLevel( player )

        if lvl < maxLevel:
            name = GEWeapon.WeaponPrintName( self.weaponList[lvl] )
        else:
            name = "Hunting Knife"

        msg = _( "#GES_GP_GUNGAME_LEVEL", str( lvl + 1 ), name )
        GEUtil.HudMessage( player, msg, -1, 0.71, GEUtil.Color( 220, 220, 220, 255 ), 3.0, 2 )

    # Give player their level specific weapon and the slappers
    def ar_GivePlayerWeapons( self, player ):
        if not player or player.IsDead() or len(self.weaponList) < 7:
            return

        player.StripAllWeapons()

        player.GiveNamedWeapon( "weapon_slappers", 0 ) # We only ever have slappers and the weapon of our level

        lvl = self.ar_GetLevel( player )

        if maxLevel > lvl:
            weap = self.weaponList[lvl]
        else:
            weap = "weapon_knife" # Last level is always the knife.

        if weap != "weapon_slappers":
            player.GiveNamedWeapon( weap, 800 ) # We use infinite ammo so who cares about exact ammo amounts

        player.WeaponSwitch( weap )

    # Calculate the minimum level for players joining in late.
    def ar_LowestLevel( self ):
        listing = []
        for i in range( 32 ):
            player = GEPlayer.GetMPPlayer( i )
            if player and player.GetTeamNumber() != Glb.TEAM_SPECTATOR and self.pltracker[player][TR_SPAWNED]:
                listing.append( self.ar_GetLevel( player ) )

        if len( listing ) == 0:
            return 0

        return min( listing ) # The bottom might not be level 1 but we still start at the bottom.
