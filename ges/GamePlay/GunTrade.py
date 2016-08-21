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
import math
import random
from GamePlay import GEScenario
from .Utils import GetPlayers, _
from .Utils.GEPlayerTracker import GEPlayerTracker
from random import shuffle
import GEPlayer, GEUtil, GEMPGameRules as GERules, GEGlobal as Glb, GEWeapon

USING_API = Glb.API_VERSION_1_2_0

# Organized by strength, in groups of 4.  Stronger weapons are higher.
weaponList = [
"weapon_golden_pp7", "weapon_golden_gun", "weapon_rocket_launcher", "weapon_grenade_launcher",
"weapon_moonraker",  "weapon_silver_pp7", "weapon_rcp90", "weapon_auto_shotgun",
"weapon_cmag", "weapon_ar33", "weapon_phantom", "weapon_shotgun",
"weapon_kf7", "weapon_knife_throwing", "weapon_sniper_rifle", "weapon_zmg",
"weapon_d5k_silenced",  "weapon_d5k", "weapon_pp7", "weapon_pp7_silenced",
"weapon_klobb", "weapon_knife", "weapon_dd44", "weapon_grenade" ]

TR_WEPINDEX = "wepindex" # Index of the weapon the player has on the list above.

class GunTrade( GEScenario ):
    
    def __init__( self ):
        GEScenario.__init__( self )

        self.indexQueue = [0] * 24
        self.pltracker = GEPlayerTracker( self )
    
    def GetPrintName( self ):
        return "#GES_GP_GT_NAME"

    def GetScenarioHelp( self, help_obj ):
        help_obj.SetDescription( "#GES_GP_GT_HELP" )

    def GetGameDescription( self ):
        if GERules.IsTeamplay():
            return "Team Gun Trade"
        else:
            return "Gun Trade"

    def GetTeamPlay( self ):
        return Glb.TEAMPLAY_TOGGLE

    def OnLoadGamePlay( self ):
        GEUtil.PrecacheSound( "GEGamePlay.Woosh" ) # Plays when level is lost
        GERules.EnableInfiniteAmmo()

    def OnUnloadGamePlay(self):
        super( GunTrade, self ).OnUnloadGamePlay()
        self.pltracker = None

    def OnRoundBegin( self ):
        GEScenario.OnRoundBegin( self )

        GERules.DisableWeaponSpawns()
        GERules.DisableAmmoSpawns()

        #Reorder the weapon index queue and then issue a unique weapon to each player.
        self.indexQueue = [0] * 24

        #Take all the player's weapons away so we don't get duplicates
        for player in GetPlayers():
            self.pltracker[player][TR_WEPINDEX] = -1

        for i in range(24):
            self.indexQueue[i] = i

        self.gt_QueueShuffle()

    def OnPlayerConnect( self, player ):
        self.pltracker[player][TR_WEPINDEX] = -1 # Give them an index of -1 so we know to give them a new weapons when they spawn.

    def OnPlayerDisconnect( self, player ):
        self.indexQueue.append( self.pltracker[player][TR_WEPINDEX] ) # Put their weapon back in the queue so we don't lose it.

    def OnPlayerSpawn( self, player ):
        if (self.pltracker[player][TR_WEPINDEX] == -1): # If we haven't been issued a weapon, pull one from the stack.
            self.gt_IssueWeapon( player )
        
        self.gt_SpawnWeapon( player )

        if player.IsInitialSpawn():
            GEUtil.PopupMessage( player, "#GES_GP_GT_NAME", "#GES_GPH_GT_GOAL" )

    def OnPlayerKilled( self, victim, killer, weapon ):
        # Let the base scenario behavior handle scoring so we can just worry about the gun swap mechanics.
        GEScenario.OnPlayerKilled( self, victim, killer, weapon )
        
        if not victim:
            return

        if killer and victim != killer:
            # Normal kill

            # Equip new weapons
            wepname = weapon.GetClassname().lower()

            if (wepname == "weapon_slappers" or wepname == "trigger_trap"): #Slapper kills replace the victim's weapon with a random new one.
                self.gt_SubSwapWeapon( killer, victim )
            elif wepname == "player" and self.gt_GetWeaponTierOfPlayer(victim) >= self.gt_GetWeaponTierOfPlayer(killer): #Killbind greifing protection, lower tiers are better.
                self.gt_SubSwapWeapon( killer, victim )
            else:
                self.gt_SwapWeapons( killer, victim ) #Normal swap.    

            #Killer ID, Victim ID, Weapon Killer Traded Away, Weapon Victim Traded Away
            GEUtil.EmitGameplayEvent( "gt_weaponswap" , str( killer.GetUserID()), str( victim.GetUserID() ), weaponList[ self.pltracker[victim][TR_WEPINDEX] ], weaponList[ self.pltracker[killer][TR_WEPINDEX] ], True )

            self.gt_SpawnWeapon( killer ) # Only killer gets their weapon right now.
            
            GEUtil.PlaySoundTo( victim, "GEGamePlay.Woosh" )
            GEUtil.PlaySoundTo( killer, "GEGamePlay.Woosh" )

        victim.StripAllWeapons() # Victim always loses their weapons so they never drop anything, as there are no weapon pickups in this mode.

    # This is used to make sure we can't pick up any weapons we're not supposed to.  Players shouldn't drop weapons in this
    # mode but it doesn't hurt to cut out other ways of getting weapons too.
    def CanPlayerHaveItem( self, player, item ):
        weapon = GEWeapon.ToGEWeapon( item )
        if weapon:
            name = weapon.GetClassname().lower()
            wI = self.pltracker[player][TR_WEPINDEX]

            if name == weaponList[wI] or name == "weapon_slappers":
                return True

            return False

        return True

# ---------------------------
# GAMEPLAY SPECIFIC FUNCTIONS
# ---------------------------


    # We shuffle the weapon indexes this way to make sure that there's roughly an even destribution of the different
    # weapon strengths in play at any given time.  Since this que controls the weapons coming into play, having it be a controlled
    # mix means there will typically be a nice destribution of weapon strengths getting substituted in.
    # Won't be perfect with higher playercounts if a bunch of a given strength of weapon gets knocked out, but that's the name of the game.
    # If someone decides to get rid of all the weak/strong weapons then they'll have to deal with an oversaturated queue.

    # Shuffle kind of sucks since stuff like 123443211234 can happen, but it should do the job well enough.
    
    def gt_QueueShuffle( self ):
        holdingList = [ [],[],[],[],[],[] ]

        entries = len(self.indexQueue)

        # Sort the indexes into seperate lists based on their strength
        for i in range(entries):
            holdingList[math.floor(self.indexQueue[i] / 4)].append(self.indexQueue[i])

        self.indexQueue = [] # Wipe the index queue now that all of our data is in the holding list

        viablelists = [] # Lists ordered by weapon strength that still have one weapon in them
        unchosenlists = [] # Lists that haven't been chosen this shuffle
    
        # Get the lists that actually have anything in them.
        for i in range(6):
            if holdingList[i]:
                viablelists.append(i)
            
        for i in range(24):
            if not unchosenlists: # If unchosenlists is empty, refill it with all the lists that still have entries
                unchosenlists = list(viablelists)

            
            pickedlist = random.choice(unchosenlists) # Pick a random list we haven't used yet
            unchosenlists.remove(pickedlist) # This is just to make sure we get a decent mix of catagories
            
            pickedindex = random.choice(holdingList[pickedlist]) # Pick a random weapon from that list
            holdingList[pickedlist].remove(pickedindex) # Then remove that weapon from the list so we don't pick it again
            
            if not holdingList[pickedlist]: # If this list no longer has anything in it, it's not viable anymore
                viablelists.remove(pickedlist)
            
            self.indexQueue.append(pickedindex) # Finally add it back to our index que

    # Get the strength rating of the player's weapon.
    def gt_GetWeaponTierOfPlayer( self, player ):
        if not player:
            return -1

        return math.floor(self.pltracker[player][TR_WEPINDEX] / 4)

    # Give the player a weapon from the queue and add their existing one to the queue if they have one, then return it.
    def gt_IssueWeapon( self, player ):
        if not player:
            return

        if (self.pltracker[player][TR_WEPINDEX] != -1):
            self.indexQueue.append( self.pltracker[player][TR_WEPINDEX] )

        self.pltracker[player][TR_WEPINDEX] = self.indexQueue.pop(0) #Pull the index at the bottom of the queue and give it to the player.

        return self.pltracker[player][TR_WEPINDEX]

    # Actually give the player their weapon.
    def gt_SpawnWeapon( self, player ):
        if not player:
            return

        player.StripAllWeapons()
        player.GiveNamedWeapon( "weapon_slappers", 0 )
        player.GiveNamedWeapon( weaponList[ self.pltracker[player][TR_WEPINDEX] ], 800 ) # We don't care about ammo because it is infinite.
        player.WeaponSwitch( weaponList[ self.pltracker[player][TR_WEPINDEX] ] )

    # Swap weapons
    def gt_SwapWeapons( self, player1, player2 ):
        if not player1 or not player2:
            return

        index1 = self.pltracker[player1][TR_WEPINDEX]

        self.pltracker[player1][TR_WEPINDEX] = self.pltracker[player2][TR_WEPINDEX]
        self.pltracker[player2][TR_WEPINDEX] = index1

    # Swap weapons and substitute in a new one for player1, telling the players what got swapped.
    def gt_SubSwapWeapon( self, player1, player2 ):
        if not player1 or not player2:
            return

        self.gt_SwapWeapons( player1, player2 )
        oldwep = self.pltracker[player1][TR_WEPINDEX]
        newwep = self.gt_IssueWeapon( player1 )
        msg = _( "#GES_GP_GT_SWAP", GEWeapon.WeaponPrintName(weaponList[oldwep]), GEWeapon.WeaponPrintName(weaponList[newwep]) )
        GEUtil.PostDeathMessage( msg )
