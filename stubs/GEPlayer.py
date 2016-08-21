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
import GEEntity, GEWeapon

def IsValidPlayerIndex( index ):
    '''Check if this index is a valid player.'''
    return bool

class CBaseCombatCharacter( GEEntity.CBaseEntity ):
    def GetHealth( self ):
        return int

    def SetHealth( self, health ):
        '''Set the health of this character.'''

    def GetSkin( self ):
        return int

    def GetActiveWeapon( self ):
        return GEWeapon.CGEWeapon

    def HasWeapon( self, weapon ):
        '''
        Check if the player has the weapon in question.
        You can pass in a valid weapon id, weapon classname, 
        or weapon entity
        
        weapon -- int, str, or GEWeapon.CGEWeapon
        '''
        return bool

    def WeaponSwitch( self, weapon ):
        '''
        Switch to the given weapon. You can pass in a valid weapon id,
        weapon classname, or weapon entity this entity owns
        
        weapon -- int, str, or GEWeapon.CGEWeapon
        '''
        return bool

    def GetAmmoCount( self, weapon_or_ammo ):
        '''
        Returns the amount of ammo held by the player. This function
        can be called with weapon_or_ammo set to a weapon entity,
        weapon id, or ammo name (see GEGlobal).
        
        weapon_or_ammo -- int, str, or GEWeapon.CGEWeapon
        '''
        return int

    def GetHeldWeapons( self ):
        '''Returns a list of weapon entities held by the player.'''
        return []

    def GetHeldWeaponIds( self ):
        '''Returns a list of weapon ids held by the player.'''
        return []

def ToCombatCharacter( ent ):
    '''
    Convert the given entity to a CBaseCombatCharacter.
    Returns None if not possible.
    '''
    return CBaseCombatCharacter

class CGEPlayer( CBaseCombatCharacter ):
    def GetFrags( self ):
        '''Get the number of absolute kills.'''
        return int

    def GetDeaths( self ):
        '''Get the number of deaths.'''
        return int

    def AddDeathCount( self, amount ):
        '''Add amount to the death count.'''

    def GetArmor( self ):
        return int

    def GetHealth( self ):
        return int

    def ResetDeathCount( self ):
        return

    def CommitSuicide( self ):
        '''Force the player to commit suicide, counts against them.'''

    def GetPlayerName( self ):
        '''Get the player's name (includes color hints)'''
        return str

    def GetPlayerID( self ):
        '''Get the player's id (useful for event messages)'''
        return int

    def GetSteamID( self ):
        '''
        Get the player's Steam ID. If they are on LAN or offline this will ALWAYS
        return "STEAM_ID_PENDING". Use this for identification carefully.
        
        NOTE: Bots don't have a Steam ID!!
        '''
        return str

    def IsDead( self ):
        return bool

    def IsObserver( self ):
        return bool

    def GetMaxArmor( self ):
        return int

    def SetMaxArmor( self ):
        return int

    def GetMaxHealth( self ):
        return int

    def SetMaxHealth( self ):
        return int

    def SetArmor( self, armor ):
        pass

    def GetPlayerModel( self ):
        '''Identity of the player's character.'''
        return str

    def SetPlayerModel( self, character, skin ):
        '''
        Set the player's character & skin explicitly 
        
        character -- string
        skin -- int
        '''
        pass

    def SetDamageMultiplier( self, multiplier ):
        '''
        Multiplier for damage inflicted by this player.
        
        multiplier -- A value between 0 and 200
        '''
        pass

    def SetSpeedMultiplier( self, multiplier ):
        '''
        Multiplier for the player's speed.
        
        multiplier -- A value between 0.5 and 1.5
        '''
        pass

    def SetScoreBoardColor( self, scoreboard_color ):
        '''
        Sets the color of the player's name in the scoreboard.
        
        color -- A selection from GEGlobal.SB_COLOR_*
        '''
        pass

    def StripAllWeapons( self ):
        '''Take all weapons and ammo from the player.'''

    def SetHat( self, hat, canshoot ):
        '''
        Set and respawn the player's hat
        
        hat - model path to the hat model
        canshoot - can the hat be shot off?
        '''
        pass

    def KnockOffHat( self, remove=False ):
        '''
        Knock off the player's hat
        
        remove - delete the hat instead of just knocking it off
        '''
        pass

    def MakeInvisible( self ):
        '''
        Make the player invisible
        '''
        pass

    def MakeVisible( self ):
        '''
        Make the player visible
        '''
        pass

    def GetAimDirection( self ):
        '''
        Returns a vector pointing in the direction the player is aiming.

        NOTE: Currently does not work for bots!
        '''
        return GEUtil.Vector

    def GetEyePosition( self ):
        '''Returns the absolute position of the player's eyes.'''
        return GEUtil.Vector

    def GiveNamedWeapon( self, classname, ammo_amt, strip_ammo=False ):
        '''
        Give this player the specified weapon and ammo.

        If strip_ammo is True it will only give ammo_amt to the player and not
        the default clip ammo of the weapon
        
        classname -- string
        ammo_amt -- int
        strip_ammo -- boolean
        '''
        pass

class CGEMPPlayer( CGEPlayer ):
    def GetRoundScore( self ):
        return int

    def SetRoundScore( self, score ):
        pass

    def AddRoundScore( self, amount ):
        pass

    def ResetRoundScore( self ):
        return

    def GetMatchScore( self ):
        return int

    def SetMatchScore( self, score ):
        pass

    def AddMatchScore( self, amount ):
        pass

    def SetDeaths( self, deaths ):
        pass

    def ForceRespawn( self ):
        '''
        Forces the player to find a new spawn spot, does not count
        negatively against their score like a suicide would.
        '''

    def ChangeTeam( self, team, forced=False ):
        '''
        Change the player's team. If forced it will not count against the player's score.
        
        team -- int
        forced -- boolean
        '''

    def GetCleanPlayerName( self ):
        '''Return the player's name without color hints, useful for on-screen notifications'''
        return str

    def IsInitialSpawn( self ):
        '''Is this the first spawn for the player in the match?'''
        return bool

    def SetInitialSpawn( self, state ):
        '''Explicitly set the next spawn for this player as initial.'''
        
    def IsInRound( self ):
        '''
        NOT spectating, have selected a character (i.e., not in pre-spawn),
        and are NOT blocked from respawning by the scenario.
        '''
        return bool
        
    def IsActive( self ):
        '''
        NOT an observer or spectating.
        '''
        return bool
        
    def IsPreSpawn( self ):
        '''
        Joined server and have NOT selected a character.
        '''
        return bool

    def GiveDefaultWeapons( self ):
        '''Gives the player the default weapon loadout as if they spawned.'''

    def GiveAmmo( self, ammo_name, amount, suppress_sound=False ):
        '''
        ammo_name -- string
        amount -- int
        suppress_sound -- boolean
        '''
        pass

def ToMPPlayer( ent_or_uid ):
    '''
    Returns an MP Player instance if supplied an entity instance or player's unique id.
    Returns None if conversion fails or entity does not exist.

    ent -- GEEntity.CBaseEntity or Unique ID of player
    '''
    return CGEMPPlayer

def GetMPPlayer( index ):
    '''
    Returns an MP Player instance if supplied a valid player entity index (1 -> maxplayers).
    Return None if the player does not exist.

    index -- int
    '''
    return CGEMPPlayer

class CGEBotPlayer( CGEMPPlayer ):
    def GiveNamedWeapon( self, classname, ammo_amt, strip_ammo=False ):
        '''
        classname -- string
        ammo_amt -- int
        strip_ammo -- boolean
        '''
        pass

    def ChangeTeam( self, team, forced=False ):
        '''
        team -- int
        forced -- boolean
        '''
        pass

    def StripAllWeapons( self ):
        return

