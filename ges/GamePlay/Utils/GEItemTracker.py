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
import GEEntity, GEAmmoCrate, GEPlayer, GEUtil
import GEGlobal as Glb
from GEGlobal import EventHooks
# This is a persistent tracker for ai that can
# store weapons/ammo/armor locations

class GEItemTracker:
    def __init__( self, parent ):
        if not hasattr( parent, 'RegisterEventHook' ):
            raise AttributeError( "Parent must be a Gameplay Scenario type!" )

        self.Clear()
        parent.RegisterEventHook( EventHooks.GP_WEAPONSPAWNED, self._WeaponSpawned )
        parent.RegisterEventHook( EventHooks.GP_WEAPONREMOVED, self._WeaponRemoved )
        parent.RegisterEventHook( EventHooks.GP_ARMORSPAWNED, self._ArmorSpawned )
        parent.RegisterEventHook( EventHooks.GP_ARMORREMOVED, self._ArmorRemoved )
        parent.RegisterEventHook( EventHooks.GP_AMMOSPAWNED, self._AmmoSpawned )
        parent.RegisterEventHook( EventHooks.GP_AMMOREMOVED, self._AmmoRemoved )


    def _WeaponSpawned( self, weapon ):
        if weapon == None:
            return

        assert isinstance( weapon, GEEntity.CGEWeapon )

        if weapon not in self.weapons:
            self.weapons.append(weapon)
        
        return

    def _WeaponRemoved( self, weapon ):
        if weapon == None:
            return

        assert isinstance( weapon, GEEntity.CGEWeapon )

        if weapon in self.weapons:
            self.weapons.remove(weapon)
        
        return

    def _ArmorSpawned( self, armor ):
        if armor == None:
            return

        assert isinstance( armor, GEEntity.CBaseEntity )

        if armor not in self.armorvests:
            self.armorvests.append(armor)
        
        return

    def _ArmorRemoved( self, armor ):
        if armor == None:
            return

        assert isinstance( armor, GEEntity.CBaseEntity )

        if armor in self.armorvests:
            self.armorvests.remove(armor)
        
        return

    def _AmmoSpawned( self, ammo ):
        if ammo == None:
            return

        assert isinstance( ammo, GEAmmoCrate.CGEAmmoCrate )

        if ammo not in self.ammocrates:
            self.ammocrates.append(ammo)
            if ammo.GetAmmoType() in WEAP_CRATE:
                self.weapons.append(ammo)
        
        return

    def _AmmoRemoved( self, ammo ):
        if ammo == None:
            return

        assert isinstance( ammo, GEAmmoCrate.CGEAmmoCrate )

        if ammo in self.ammocrates:
            self.ammocrates.remove(ammo)
            if ammo.GetAmmoType() in WEAP_CRATE:
                self.weapons.remove(ammo)
        
        return

    def Clear( self ):
        self.weapons = []
        self.ammocrates = []
        self.armorvests = []
        return

WEAP_CRATE = [ Glb.AMMO_TIMEDMINE, Glb.AMMO_PROXIMITYMINE, Glb.AMMO_REMOTEMINE, Glb.AMMO_TKNIFE, Glb.AMMO_GRENADE ]
