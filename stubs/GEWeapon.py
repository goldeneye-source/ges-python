################ copyright 2005-2016 team goldeneye: source #################
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
import geentity

def togeweapon( entity ):
    '''
    entity -- geentity.cbaseentity
    '''
    return cgeweapon

def weaponammotype( weap_name_or_id ):
    '''
    gets the ammo name for the given weapon id or classname
    
    weap_name_or_id -- int or str
    '''
    return str

def weaponclassname( weap_id ):
    '''
    gets the classname for the given weapon id
    
    weap_id -- int
    '''
    return str

def weaponprintname( weap_name_or_id ):
    '''
    gets the print name for the given weapon id or classname
    
    weap_name_or_id -- int or str
    '''
    return str

def weaponinfo( weap_name_or_id, owner=none ):
    '''
    retrieve the info for the particular weapon id or classname.
    dict keys may include:
        id, classname, printname, weight, damage
        uses_clip, clip_size, clip_def,
        viewmodel, worldmodel, penetration, melee
        ammo_type, ammo_max, ammo_count (only if owner is supplied)
        
    weap_name_or_id -- int or str
    owner -- geplayer.cbasecombatcharacter
    '''
    return {}

class cgeweapon( geentity.cbaseentity ):
    def getweight( self ):
        '''
        this is a measure of the "desirabiity" of the weapon
        and ranges from 0 to 6
        '''
        return int

    def getprintname( self ):
        return str

    def ismeleeweapon( self ):
        return bool

    def isexplosiveweapon( self ):
        return bool

    def isautomaticweapon( self ):
        return bool

    def isthrownweapon( self ):
        return bool

    def canholster( self ):
        '''
        are we allowed to switch away from this weapon?
        '''
        return bool

    def hasammo( self ):
        return bool

    def usesammo( self ):
        return bool

    def getammotype( self ):
        return str

    def getammocount( self ):
        '''
        only works if a player is holding me, gets their ammo held
        '''
        return int

    def setammocount( self, amount ):
        '''
        only works if a player is holding me, sets their absolute ammo count
        
        amount -- int
        '''
        return

    def getmaxammocount( self ):
        '''
        returns the maximum amount of ammo that can be held
        '''
        return int

    def getclip( self ):
        '''
        returns the amount of ammo left before reload
        '''
        return int

    def getmaxclip( self ):
        '''
        returns the amount of ammo in one full reload
        '''
        return int

    def getdefaultclip( self ):
        '''
        returns the amount of ammo given at pickup
        '''
        return int

    def getdamage( self ):
        return int

    def getweaponid( self ):
        return int

    def getweaponslot( self ):
        return int

    def setskin( self, skin ):
        '''
        sets the skin of the world and view model of the weapon
        
        skin -- int
        '''
        pass
