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
import GEEntity, GEWeapon, GEUtil

def EndMatch():
    '''
    This function bypasses calls to CanRoundEnd and CanMatchEnd.
    The map is changed after the round and match reports are shown.
    Successive calls to this function do nothing.
    '''

def EndRound( should_score=True, change_weapons=True ):
    '''
    This function bypasses calls to CanRoundEnd and CanMatchEnd.
    If should_score is False it will bypass round scoring and not
    show the after action report. If change_weapons is False then
    the current weapon set will not change for the next round.
    
    should_score -- Set whether this round should be scored
    change_weapons -- Set whether the weaponset should change
    '''

def GetTeam( index ):
    '''Get the team instance at the specified index'''
    return CTeam

def GetRadar():
    '''Get the radar manager instance'''
    return CGERadar

def GetTokenMgr():
    '''Get the token manager instance'''
    return CGETokenManager

def LockRound():
    '''Lock the round, does nothing unless you use IsRoundLocked()'''

def UnlockRound():
    '''Unlock the round, does nothing unless you use IsRoundLocked()'''

def IsRoundLocked():
    '''Check whether the round is locked'''
    return bool

def AllowRoundTimer( state ):
    '''Toggle whether to use the round timer or not.'''

def DisableWeaponSpawns():
    '''Disables all weapon spawners on the map.'''

def DisableAmmoSpawns():
    '''Disables all ammo spawners on the map.'''

def DisableArmorSpawns():
    '''Disables all armor spawners on the map.'''

def GetWeaponInSlot( slot ):
    '''Get the weapon id in the specified loadout slot'''
    return int

def GetWeaponLoadout( loadout_name=None ):
    '''
    Get a list of weapons in the specfied loadout. If no
    loadout is specified it returns the current loadout.

    loadout_name -- Name of the desired loadout, None for current (string)
    '''
    return []

def SetPlayerWinner( player ):
    '''Sets the given player as the winner of the round regardless of score.'''

def SetTeamWinner( team ):
    '''
    Sets the given team as the winner of the round regardless of score.
    Only useful when teamplay is active.

    team -- A team instance or team ID
    '''

def GetMatchTimeLeft():
    '''Get the remaining time left in the match (until map change).'''
    return float

def GetRoundTimeLeft():
    '''Get the remaining time in the current round.'''
    return float

def IsIntermission():
    '''Is the game in an intermission?'''
    return bool

def IsGameOver():
    '''Are we in the final intermission before map change?'''
    return bool

def IsTeamplay():
    '''Is teamplay active?'''
    return bool

def GetNumActivePlayers():
    '''
    Returns the number of players that are NOT spectating and have selected a character (i.e., not in pre-spawn).
    This number INCLUDES players in observer mode (i.e., blocked from respawning by the scenario)
    '''
    return int

def GetNumActiveTeamPlayers( team ):
    '''
    Returns the number of players that are NOT spectating and have selected a character (i.e., not in pre-spawn).
    This number INCLUDES players in observer mode (i.e., blocked from respawning by the scenario)
    
    team -- A team instance or team ID
    '''
    return int

def GetNumInRoundPlayers():
    '''
    Returns the number of players that are NOT spectating, have selected a character (i.e., not in pre-spawn),
    and are NOT blocked from respawning by the scenario.
    '''
    return int

def GetNumInRoundTeamPlayers( team ):
    '''
    Returns the number of players that are NOT spectating, have selected a character (i.e., not in pre-spawn),
    and are NOT blocked from respawning by the scenario.
    
    team -- A team instance or team ID
    '''
    return int

def GetNumAlivePlayers():
    '''
    Returns the number of players that are NOT an observer.
    '''
    return int

def SetExcludedCharacters( char_list ):
    '''
    Exclude characters from being shown on the character select panel.
    
    char_list -- Comma seperated list of character identities (ex. "006_mi6,bond,samedi")
    '''

def SetAllowTeamSpawns( state ):
    '''
    Toggle team spawns from being used.

    state -- bool
    '''

def ResetAllPlayerDeaths():
    '''Reset every players' death count'''

def ResetAllPlayersScores():
    '''Reset every players' score'''

def ResetAllTeamsScores():
    '''Reset every teams' score'''

class CTakeDamageInfo:
    def GetInflictor( self ):
        return GEEntity.CBaseEntity

    def GetAttacker( self ):
        return GEEntity.CBaseEntity

    def GetWeapon( self ):
        return GEEntity.CBaseEntity

    def GetDamage( self ):
        return float

    def GetDamageType( self ):
        return int

    def GetAmmoName( self ):
        return str

class CTeam:
    def GetRoundScore( self ):
        return int

    def SetRoundScore( self, score ):
        '''Sets the aboslute score for this round.'''

    def AddRoundScore( self, amount ):
        '''Adds amount to the current round's score'''

    def GetMatchScore( self ):
        '''Get the current match score.'''
        return int

    def SetMatchScore( self, score ):
        '''Sets the absolute score for the match.'''

    def AddMatchScore( self, amount ):
        '''Adds amount to the current match's score.'''

    def ResetMatchScore( self ):
        '''Sets the Match score to 0.'''

    def GetNumPlayers( self ):
        '''Return the number of players on this team.'''
        return int

    def GetName( self ):
        '''Get the team's printable name.'''
        return str

    def GetTeamNumber( self ):
        '''Get the team's number (ie. the team's id).'''
        return int

class CGERadar:
    def SetForceRadar( self, state ):
        '''Force the radar to be visible, or not.'''

    def SetPlayerRangeMod( self, player, multiplier ):
        '''
        Sets a multiplier on the given player's radar range.
        
        player -- The player to affect
        multiplier -- A value between 0 and 1.0
        '''

    def AddRadarContact( self, entity, type=0, always_visible=False, icon="", color=GEUtil.Color() ):
        '''
        Add a contact on the radar. This can be any entity.

        entity -- The entity to add to the radar

        Keyword Arguments:
          type -- The type of contact (GEGlobal.RADAR_TYPE_*)
          always_visible -- Show contact even if out of range
          icon -- Relative path to the icon to show on the radar
          color -- Color of this contact
        '''

    def DropRadarContact( self, entity ):
        '''
        Removes the given entity from the radar. Note that players
        cannot be removed and this function will simply remove any
        special parameters set for them.
        '''

    def IsRadarContact( self, entity ):
        '''Returns True is the entity is a contact on the radar.'''
        return bool

    def SetupObjective( self, entity, team_filter=GEGlobal.TEAM_NONE, token_filter="", text="", color=GEUtil.CColor(), min_dist=0, pulse=False ):
        '''
        Setup an on-screen objective icon. RADAR_TYPE_OBJECTIVE or RADAR_TYPE_TOKEN
        automatically become objectives, you can override the defaults with this
        function. Use the team_filter to restrict the icon by team number. Use
        token_filter to restrict the icon to those who hold the named token, put
        a ! in front of the name for the inverse. Text displays above the icon. Set
        min_dist to have icons fade out when the player is within this distance to
        the objective. Pulse causes the icon to pulse, useful to attract attention.
        
        entity -- Entity to make an objective

        Keyword Arguments:
          team_filter -- Team ID that can see this objective
          token_filter -- Token classname that a player must hold to see this objective
          text -- Text to display above the icon
          color -- Color of the icon
          min_dist -- Minimum viewable distance, useful to prevent griefing
          pulse -- Cause the icon to slowly pulse
        '''
        return

    def ClearObjective( self, entity ):
        '''Remove the given entity as an objective.'''

    def DropAllContacts( self ):
        '''Remove all contacts.'''

    def ListContactsNear( self, origin ):
        '''
        Returns a list of dicts that describe the contacts on 
        the radar within range of the origin given. Used mainly by
        the Ai code.

        Each returned dict has the following keys:
        {"ent_handle","origin","range","team","type","is_objective"}
        
        origin -- GEUtil.Vector
        '''
        return []

class CGETokenManager:
    def SetupToken( self, classname, **kwargs ):
        '''
        Set up a new or existing token based on the supplied classname.
        
        classname -- Token classname to use

        Keyword Arguments:
          limit -- Maximum number to spawn (default 0)
          team  -- Associated team (default GEGlobal.TEAM_NONE)
          skin  -- Skin to use for the token model (default 0)
          location -- Spawn locations to use OR'd together (default GEGlobal.SPAWN_PLAYER)
          glow_color -- Color of the glow effect (default No Glow)
          glow_dist -- Maximum distance of the glow effect (default 350.0)
          view_model -- Viewmodel to use for this token (default "models/weapons/tokens/v_keytoken.mdl")
          world_model -- Worldmodel to use for this token (default "models/weapons/tokens/w_keytoken.mdl")
          print_name -- Human readable name for this token (default "#GE_TOKEN")
          allow_switch -- Allow holstering this token when held (default True)
          damage_mod -- Damage multiplier from the default token damage (default 1.0)
          respawn_delay -- Delay before this token is respawned when dropped (default 10.0)
        '''

    def IsValidToken( self, classname ):
        '''Check if this classname is associated with a token definition.'''
        return bool

    def RemoveToken( self, classname ):
        '''Remove any token definition associated with this classname.'''

    def RemoveTokenEnt( self, token, adjust_limit=True ):
        '''
        Removes the actual token entity from the world. Unless specified, 
        the token limit will be reduced by 1 and no replacement will be
        spawned.
        
        token -- The token entity to remove (GEWeapon.CGEWeapon)
        adjust_limit -- Adjust the token definition limit?
        '''

    def TransferToken( self, token, to_player ):
        '''
        Transfer a token from one player to another, set
        to_player to None to drop the token on the ground.
        
        token -- The token entity to transfer (GEWeapon.CGEWeapon)
        to_player -- The player to transfer to, or None to drop (GEPlayer.CGEPlayer)
        '''

    def GetTokens( self, classname ):
        '''Returns a list of all token entities associated with the given classname.'''
        return []

    def CaptureToken( self, token ):
        '''Removes the given token from play without affecting the token limit.'''

    def SetupCaptureArea( self, name, **kwargs ):
        '''
        Set up a new or existing capture area with the given name.

        name -- Name of the capture area group
        
        Keyword Arguments:
          limit -- Maximum number to spawn (default 0)
          model -- Model to use for the capture area (default "models/gameplay/capturepoint.mdl")
          skin  -- Skin to use for the capture area model (default 0)
          location -- Spawn locations to use OR'd together (default GEGlobal.SPAWN_PLAYER)
          glow_color -- Color of the glow effect (default No Glow)
          glow_dist -- Maximum distance of the glow effect (default 350.0)
          rqd_token -- Token required to trigger "OnCaptureAreaEntered/Exited" (default None)
          rqd_team -- Team that can trigger "OnCaptureAreaEntered/Exited" (default None)
          radius -- Radius of the capture area trigger (default 32.0)
          spread -- Minimum distances between these capture areas (default 500.0)
        '''

    def RemoveCaptureArea( self, name ):
        '''Removes the named capture area definition.'''

    def SetGlobalAmmo( self, classname, amount=-1 ):
        '''
        Set global ammo to be give at every ammo spawner. The ammo given
        is based on weapon classname. Set the amount to -1 to use 1/2 
        the normal crate amount.
        
        classname -- Weapon classname to determine what ammo to give
        amount -- Amount of ammo to give (default -1)
        '''

    def RemoveGlobalAmmo( self, classname ):
        '''
        Removes the global ammo definition based on the given
        weapon classname.

        classname -- Weapon classname to determine what ammo to remove
        '''

class CGECaptureArea( GEEntity.CBaseEntity ):
    def GetGroupName( self ):
        '''Get the group name that this capture area was spawned under.'''
        return str
