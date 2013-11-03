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
from Ai import PYBaseNPC, AiSystems
from . import Memory
from ..Schedules import Cond
import GEEntity, GEPlayer, GEWeapon, GEUtil, GEGlobal as Glb
from GEGlobal import EventHooks

class Weight:
    WORST, BAD, LOW, MEDIUM, HIGH, BEST = range( 6 )

class WeaponManager:
    WEAPON_EFFICIENCY = 1.0

    def __init__( self, parent ):
        assert isinstance( parent, PYBaseNPC )
        if not isinstance( parent, PYBaseNPC ):
            raise TypeError( "Memory initialized on a non-NPC, aborting" )

        self._weapons = []
        self._npc = parent
        self.param_callback = None
        self.time_to_next_weaponcheck = 0
        self.debug = False

        parent.RegisterEventHook( EventHooks.AI_GATHERCONDITIONS, self.GatherConditions )

    def GatherConditions( self ):
        curr_weap = self._npc.GetActiveWeapon()

        # Check to see if we can/should switch weapons
        if self._npc.HasCondition( Cond.NO_PRIMARY_AMMO ) or GEUtil.GetTime() >= self.time_to_next_weaponcheck:
            if self.param_callback:
                params = self.param_callback()
                weap_id = self.GetBestWeapon( **params )
            else:
                weap_id = self.GetBestWeapon()

            # Did we choose a new weapon?
            if not curr_weap or ( weap_id and weap_id != curr_weap.GetWeaponId() ):
                # Switch weapons and give a good delay before we try again
                self._npc.WeaponSwitch( weap_id )
                self.time_to_next_weaponcheck = GEUtil.GetTime() + 5.0
            else:
                # Normal delay, maybe we'll pickup a new one or some ammo!
                self.time_to_next_weaponcheck = GEUtil.GetTime() + self.WEAPON_EFFICIENCY

        # Weapon gathering checks
        self._npc.ClearCondition( Cond.BETTER_WEAPON_AVAILABLE )
        weap_mems = self._npc.GetSystem( AiSystems.MEMORY ).FindMemoriesByType( Memory.TYPE_WEAPON )
        for m in weap_mems:
            assert isinstance( m, Memory.Memory )
            try:
                # Should we signal to go for this weapon?
                if m.GetConfidence() > 0.3 and type( m.data ) is dict and m.data["weight"] >= curr_weap.GetWeight() and not self._npc.HasWeapon( m.data["id"] ):
                    if self._npc.GetAbsOrigin().DistTo( m.location ) < 1024:
                        self._npc.SetCondition( Cond.GES_CLOSE_TO_WEAPON )
                    self._npc.SetCondition( Cond.BETTER_WEAPON_AVAILABLE )
                    break
            except:
                pass

    def GetBestWeapon( self, melee_bonus=0, explosive_bonus=0, thrown_bonus=0 ):
        # Get all the NPC's held weapons
        self._weapons = self._npc.GetHeldWeaponIds()

        # Get the easy cases out of the way first
        if len( self._weapons ) == 0:
            if self.debug:
                print "[WeaponManager] ERROR - Best weapon called with no weapons in set"
            return None
        elif len( self._weapons ) == 1:
            return self._weapons[0]

        # Choose the base weapon hierarchy based on our enemy location to us
        if self._npc.HasCondition( Cond.GES_ENEMY_CLOSE ):
            base_list = WEAP_SHORT_RANGE
        elif self._npc.HasCondition( Cond.GES_ENEMY_FAR ):
            base_list = WEAP_LONG_RANGE
        else:
            base_list = WEAP_MID_RANGE

        # Generate a list a weapons based on our conditions
        weap_list = []
        for weap in base_list:
            # we only pull out weapons that we currently hold
            if weap not in self._weapons:
                continue

            # Base weight will decrease as we go down our list of weapons
            weight = len( base_list ) - len( weap_list )

            info = GEWeapon.WeaponInfo( int( weap ), self._npc.GetNPC() )
            if info["ammo_count"] > 0:
                # Bonus points for the number of clips of ammo we have
                if info["uses_clip"]:
                    weight += min( 3, float( info["ammo_count"] ) / info["clip_size"] )
                else:
                    weight += min( 3, info["ammo_count"] )
            elif weap != Glb.WEAPON_MOONRAKER and not info["melee"]:
                # Weapons with no ammo are not even considered
                continue

            if info["melee"]:
                weight += melee_bonus
            if weap in WEAP_EXPLOSIVES:
                weight += explosive_bonus
            if weap in WEAP_THROWN:
                weight += thrown_bonus

            weap_list.append( ( weap, weight ) )

        weap_sort = lambda x, y: cmp( y[1], x[1] )
        weap_list.sort( weap_sort )

        if self.debug and len( weap_list ) > 0:
            print ""
            for weap, weight in weap_list:
                print "%s given %.1f" % ( GEWeapon.WeaponClassname( weap ), weight )
            print ""

        if len( weap_list ) > 0 and weap_list[0][1] > 0:
            return weap_list[0][0]
        else:
            if self.debug:
                print "[WeaponManager] No weapons found to switch to!"

            return None

WEAP_EXPLOSIVES = [ Glb.WEAPON_GRENADE, Glb.WEAPON_GRENADE_LAUNCHER, Glb.WEAPON_PROXIMITYMINE,
    Glb.WEAPON_REMOTEMINE, Glb.WEAPON_TIMEDMINE, Glb.WEAPON_ROCKET_LAUNCHER ]

WEAP_THROWN = [ Glb.WEAPON_GRENADE, Glb.WEAPON_PROXIMITYMINE, Glb.WEAPON_REMOTEMINE, Glb.WEAPON_TIMEDMINE, Glb.WEAPON_KNIFE_THROWING ]

WEAP_SHORT_RANGE = [
    Glb.WEAPON_GOLDENPP7, Glb.WEAPON_GOLDENGUN, Glb.WEAPON_AUTO_SHOTGUN, Glb.WEAPON_MOONRAKER,
    Glb.WEAPON_SILVERPP7, Glb.WEAPON_COUGAR_MAGNUM, Glb.WEAPON_SHOTGUN, Glb.WEAPON_RCP90,
    Glb.WEAPON_AR33, Glb.WEAPON_PHANTOM, Glb.WEAPON_SNIPER_RIFLE, Glb.WEAPON_DD44, Glb.WEAPON_KNIFE,
    Glb.WEAPON_ZMG, Glb.WEAPON_D5K, Glb.WEAPON_KF7, Glb.WEAPON_D5K_SILENCED, Glb.WEAPON_ROCKET_LAUNCHER,
    Glb.WEAPON_GRENADE_LAUNCHER, Glb.WEAPON_PP7, Glb.WEAPON_PP7_SILENCED, Glb.WEAPON_KNIFE_THROWING,
    Glb.WEAPON_GRENADE, Glb.WEAPON_KLOBB, Glb.WEAPON_SLAPPERS, Glb.WEAPON_TIMEDMINE, Glb.WEAPON_PROXIMITYMINE
]

WEAP_MID_RANGE = [
    Glb.WEAPON_GOLDENPP7, Glb.WEAPON_GOLDENGUN, Glb.WEAPON_MOONRAKER, Glb.WEAPON_SILVERPP7,
    Glb.WEAPON_COUGAR_MAGNUM, Glb.WEAPON_AUTO_SHOTGUN, Glb.WEAPON_ROCKET_LAUNCHER, Glb.WEAPON_GRENADE_LAUNCHER,
    Glb.WEAPON_RCP90, Glb.WEAPON_SNIPER_RIFLE, Glb.WEAPON_AR33, Glb.WEAPON_PHANTOM, Glb.WEAPON_SHOTGUN,
    Glb.WEAPON_DD44, Glb.WEAPON_ZMG, Glb.WEAPON_D5K, Glb.WEAPON_KF7, Glb.WEAPON_D5K_SILENCED, Glb.WEAPON_PP7,
    Glb.WEAPON_PP7_SILENCED, Glb.WEAPON_KNIFE_THROWING, Glb.WEAPON_GRENADE, Glb.WEAPON_KLOBB,
    Glb.WEAPON_TIMEDMINE, Glb.WEAPON_PROXIMITYMINE, Glb.WEAPON_KNIFE, Glb.WEAPON_SLAPPERS
]

WEAP_LONG_RANGE = [
    Glb.WEAPON_GOLDENPP7, Glb.WEAPON_GOLDENGUN, Glb.WEAPON_SILVERPP7, Glb.WEAPON_MOONRAKER,
    Glb.WEAPON_COUGAR_MAGNUM, Glb.WEAPON_SNIPER_RIFLE, Glb.WEAPON_RCP90, Glb.WEAPON_AR33,
    Glb.WEAPON_ROCKET_LAUNCHER, Glb.WEAPON_PP7, Glb.WEAPON_D5K, Glb.WEAPON_PP7_SILENCED,
    Glb.WEAPON_D5K_SILENCED, Glb.WEAPON_KF7, Glb.WEAPON_PHANTOM, Glb.WEAPON_AUTO_SHOTGUN,
    Glb.WEAPON_SHOTGUN, Glb.WEAPON_DD44, Glb.WEAPON_ZMG, Glb.WEAPON_GRENADE, Glb.WEAPON_KLOBB,
    Glb.WEAPON_KNIFE_THROWING, Glb.WEAPON_GRENADE_LAUNCHER, Glb.WEAPON_PROXIMITYMINE,
    Glb.WEAPON_TIMEDMINE, Glb.WEAPON_KNIFE, Glb.WEAPON_SLAPPERS
]
