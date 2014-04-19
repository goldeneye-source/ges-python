################ copyright 2005-2013 team goldeneye: source #################
#
# this file is part of goldeneye: source's python library.
#
# goldeneye: source's python library is free software: you can redistribute 
# it and/or modify it under the terms of the gnu general public license as 
# published by the free software foundation, either version 3 of the license, 
# or(at your option) any later version.
#
# goldeneye: source's python library is distributed in the hope that it will 
# be useful, but without any warranty; without even the implied warranty of
# merchantability or fitness for a particular purpose.  see the gnu general 
# public license for more details.
#
# you should have received a copy of the gnu general public license
# along with goldeneye: source's python library.
# if not, see <http://www.gnu.org/licenses/>.
#############################################################################
import GEEntity

def ToGEWeapon( entity ):
    '''
    entity -- GEEntity.CBaseEntity
    '''
    return CGEWeapon

def WeaponAmmoType( weap_name_or_id ):
    '''
    Gets the ammo name for the given weapon id or classname
    
    weap_name_or_id -- int or str
    '''
    return str

def WeaponClassname( weap_id ):
    '''
    Gets the class name for the given weapon id
    
    weap_id -- int
    '''
    return str

def WeaponPrintName( weap_name_or_id ):
    '''
    Gets the print name for the given weapon id or classname
    
    weap_name_or_id -- int or str
    '''
    return str

def WeaponInfo( weap_name_or_id, owner=none ):
    '''
    Retrieve the info for the particular weapon id or classname.
    Returned dict keys may include:
        id, classname, printname, weight, damage
        uses_clip, clip_size, clip_def,
        viewmodel, worldmodel, penetration, melee
        ammo_type, ammo_max, ammo_count (only if owner is supplied)
        
    weap_name_or_id -- int or str
    owner -- GEPlayer.CBaseCombatCharacter
    '''
    return {}

class CGEWeapon( GEEntity.CBaseEntity ):
    def GetWeight( self ):
        '''
        This is a measure of the "desirabiity" of the weapon
        and ranges from 0 to 6
        '''
        return int

    def GetPrintName( self ):
        return str

    def IsMeleeWeapon( self ):
        return bool

    def IsExplosiveWeapon( self ):
        return bool

    def IsAutomaticWeapon( self ):
        return bool

    def IsThrownWeapon( self ):
        return bool

    def CanHolster( self ):
        '''
        Are we allowed to switch away from this weapon?
        '''
        return bool

    def HasAmmo( self ):
        return bool

    def UsesAmmo( self ):
        return bool

    def GetAmmoType( self ):
        return str

    def GetAmmoCount( self ):
        '''
        Only works if a player is holding this weapon
        Returns the player's ammo count associated with this weapon
        '''
        return int

    def SetAmmoCount( self, amount ):
        '''
        Only works if a player is holding this weapon
        Sets the player's absolute ammo count associated with this weapon
        
        amount -- int
        '''
        return

    def GetMaxAmmoCount( self ):
        '''
        Returns the maximum amount of ammo that can be held
        '''
        return int

    def GetClip( self ):
        '''
        Returns the amount of ammo left before reload
        '''
        return int

    def GetMaxClip( self ):
        '''
        Returns the amount of ammo in one full reload
        '''
        return int

    def GetDefaultClip( self ):
        '''
        Returns the amount of ammo given at pickup
        '''
        return int

    def GetDamage( self ):
        return int

    def GetWeaponId( self ):
        return int

    def GetWeaponSlot( self ):
        return int

    def SetSkin( self, skin ):
        '''
        Sets the skin of the world and view model of the weapon
        
        skin -- int
        '''
        pass
