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
import GEEntity

def ClientPrint( player_or_team, msg_dest, msg, param1="", param2="", param3="", param4="" ):
    '''
    Prints a message to the specified destination. Additional parameters will fill in localizable strings.

    Set 'player_or_team' to None to print to all players.
    Set 'msg_dest' to one of the GEGlobal.HUD_PRINT* entries.
    
    'param1' through 'param4' are used to fill in localization slots in 'msg', for example:
    "#LOCALIZE_THIS" might have a "%s1" parameter, set 'param1' to "spam" to fill it in!
    
    player_or_team -- GEPlayer.CGEPlayer or Team Number
    msg_dest -- int
    msg -- str
    param1 -- str
    param2 -- str
    param3 -- str
    param4 -- str
    '''

def HudMessage( player_or_team, msg, x, y, color=GEUtil.Color( 255, 255, 255, 255 ), hold_time=5.0, channel=-1 ):
    '''
    Post a message on the HUD using the specified styling
    Set player_or_team to None to print to all players
    
    X and Y values are floats and represent a percentage of the client's 
    screen size for positioning. They are agnostic to the actual screen size 
    as a result. To center the message use -1. To right-align or bottom-align 
    use 0 < value < -1 (eg -0.1).
    
    You can use the color hints defined here: http://wiki.geshl2.com/index.php/HudColor
    Use ^| to stop the custom color
    
    The 'channel' parameter can be any number from 1 to 5 to indicate a shared message
    channel that will overwrite any existing message to prevent text overlap. Leave it 
    undefined or set to -1 to use the rotating channels that will provide a new channel on
    each function call.
    
    player_or_team -- GEPlayer.CGEPlayer or Team Number
    msg -- str
    x -- float
    y -- float
    color -- GEUtil.Color
    holdtime -- float
    channel -- int
    '''

def PopupMessage( player_or_team, title, msg, image="" ):
    '''
    Create a Popup notice that will appear on the left side of the screen
    Set player_or_team to None to print to all players
    
    player_or_team -- GEPlayer.CGEPlayer or Team Number
    title -- str
    msg -- str
    image -- str
    '''

def Msg( msg ):
    '''
    Write a message to the console
    
    msg -- str
    '''
    
def DevMsg( msg ):
    '''
    Write a message to the console, "developer 1" must be enabled to see it!
    
    msg -- str
    '''

def Warning( msg ):
    '''
    Write a warning to the console
    
    msg -- str
    '''

def DevWarning( msg ):
    '''
    Write a warning to the console, "developer 1" must be enabled to see it!
    
    msg -- str
    '''

def ServerCommand( cmd ):
    '''
    Execute an arbitrary command on the server.
    e.g. - GEUtil.ServerCommand( "ge_endround\n" )
    
    Warning: It is preferred to use authed Python commands whenever possible!
    
    cmd -- str
    '''

def ClientCommand( player, cmd ):
    '''
    Execute an arbitrary command on designated player.
    e.g. - GEUtil.ClientCommand( player, "kill\n" )
    
    Warning: It is preferred to use authed Python commands whenever possible!
    
    player -- GEPlayer.CGEPlayer
    cmd -- str
    '''
    
def IsDedicatedServer():
    '''
    Are we running on a dedicated server?
    '''
    return bool
    
def IsLAN():
    '''
    Are we running on a LAN?
    '''
    return bool

''' Temporary Entity Definitions '''
class TempEnt:
    RING = int
    BEAM = int
    BEAM_FOLLOW = int
    DUST = int
    SMOKE = int
    SPARK = int

def CreateTempEnt( type, origin=Vector, **kwargs ):
    '''
    Create a Temporary Entity of the given type at the given origin and extended args.
    'origin' is required for all temp ents. BEAM also requires 'end', and BEAM_FOLLOW 
    requires 'entity'.
    
    List of acceptable kwargs entries:
    
    - RING: origin, delay, radius_start, radius_end, framerate, duration, width, amplitude, color, speed
    - BEAM: origin, end, delay, framerate, duration, width, width_end, fade_length, amplitude, color, speed
    - BEAM_FOLLOW: origin, entity, delay, duration, width, width_end, fade_length, color
    - DUST: origin, delay, direction, size, speed
    - SMOKE: origin, delay, size, framerate
    - SPARK: origin, delay, magnitude, direction, trail_length
    
    Example Usage:
        origin = player.GetEyePosition()
        GEUtil.CreateTempEnt( TempEnt.RING, origin, framerate = 15, duration = 0.6, 
            speed = 0, width=3.0, amplitude=0.00, radius_start=128.0, 
            radius_end=128.0, color=RingColor )
    
    type -- entry from GEUtil.TempEnt
    origin -- GEUtil.Vector
    '''

def EmitGameplayEvent( name, value1="", value2="", value3="", value4="", send_to_clients=False ):
    '''
    Emit a custom gameplay event with a name and string values. These events can
    be picked up by server plugins to do special actions in conjunction with your
    scenario.
    
    name -- str
    value1 -- str
    value2 -- str
    value3 -- str
    value4 -- str
    send_to_clients -- bool
    '''

def PostDeathMessage( msg ):
    '''
    Post a message in the death notices [max length 128]
    
    msg -- str
    '''

def DebugDrawLine( start, end, r, g, b, no_depth_test, duration ):
    '''
    Mainly for visual debugging between two points
    
    start -- Vector
    end -- Vector
    r -- int
    g -- int
    b -- int
    no_depth_test -- bool
    duration -- float
    '''

def GetTime():
    '''
    Get the current server game time
    '''
    return float

def GetCVarValue( name ):
    '''
    Get the value of a console variable
    
    name -- str
    '''
    return str

def DistanceBetween( ent1, ent2 ):
    '''
    ent1 -- GEEntity.CBaseEntity
    ent2 -- GEEntity.CBaseEntity
    '''
    return float

def PrecacheSound( soundname ):
    '''
    soundname -- str
    '''

def PrecacheModel( model ):
    '''
    model -- str
    '''

def PrecacheParticleEffect( particle ):
    '''
    particle -- str
    '''

def AddDownloadable( file ):
    '''
    file -- str
    '''

def PlaySoundTo( dest, sound, dim_music=False ):
    '''
    Play a sound to the given destination. This can be a player, team number,
    or None which will play it to everyone. Set dim_music to True to dim the
    background music when this sound plays (default is False).
    
    `sound` can be a file path or a defined sound name.
    
    This sound is not attenuated in any way and is played such that only the 
    provided players can hear it.
    
    If using a direct .wav or .mp3, you can use modifiers in front of the sound
    to change it's behavior. NOTE: These must be present in the precache definition!!
    Example: PlaySoundTo( "@custom/custom_sound.wav" )
    
    @ -> Omni sound, plays the same on all speakers
    ) -> Spatialized stereo sound
    ^ -> Distance encoded sound
    
    dest -- GEPlayer.CGEPlayer or int or None
    sound -- str
    dim_music -- bool
    '''

def PlaySoundFrom( origin, sound, attenuation=0.8 ):
    '''
    Play a sound from the given origin. This can be a player or a vector.
    You can change how much the sound is attenuated by changing 'attenuation'.
    Closer to zero lets people hear the sound further away.
    Note: Gunfire has an attenuation of 0.27
    
    `sound` can be a file path or a defined sound name.
    
    If using a direct .wav or .mp3, you can use modifiers in front of the sound
    to change it's behavior. NOTE: These must be present in the precache definition!!
    Example: PlaySoundTo( "@custom/custom_sound.wav" )
    
    @ -> Omni sound, plays the same on all speakers
    ) -> Spatialized stereo sound
    ^ -> Distance encoded sound
    
    dest -- GEPlayer.CGEPlayer or GEUtil.Vector
    sound -- str
    attenuation -- double (0 -> 3.0)
    '''
    
def StopSound( dest, sound ):
    '''
    Stops a previously played sound by name. Simply pass in the same name as
    previously given and the sound will stop. Provide a player to `dest` to 
    stop the sound on that player only.
    
    dest -- GEPlayer.CGEPlayer or None
    sound -- str
    '''

def ParticleEffect( player, attachment, effect, follow ):
    '''
    player -- GEPlayer.CGEPlayer
    attachment -- str
    effect -- str
    follow -- bool
    '''

def ParticleEffectBeam( player, attachment, end, effect ):
    '''
    player -- GEPlayer.CGEPlayer
    attachment -- str
    end -- Vector
    effect -- str
    '''

def InitHudProgressBar( player_or_team, index, title=None, flags=0, max_value=0, x=-1, y=-1, wide=120, tall=60, color=GEUtil.Color(255,255,255,255), curr_value=0 ):
    '''
    Initiate a progress bar to show on a player's or teams' screen. There are a maximum of 8
    progress bars for each player. Use the index to indicate which bar you are initializing.
    Initializing with the same index as a previous bar completely overwrites the previous
    one. Set 'curr_value' to preventing having to call UpdateHudProgressBar directly after
    this function.
    
    Use UpdateHudProgressBar to update the value, color, or title, it uses  significantly 
    less network bandwidth than this function and prevents flickering.
    
    Set player_or_team to None to send to all players.
    
    player_or_team -- GEPlayer.CGEPlayer or Team Number
    index -- int
    title -- str
    flags -- int
    max_value -- float
    x -- float
    y -- float
    wide -- int
    tall -- int
    color -- GEUtil.Color
    curr_value -- float
    '''

def UpdateHudProgressBar( player_or_team, index, value=None, title=None, color=None ):
    '''
    Update an existing progress bar with a new value, title, and/or color
    
    Set player_or_team to None to send to all players
    
    player_or_team -- GEPlayer.CGEPlayer or Team Number
    index -- int
    value -- float
    title -- str
    color -- GEUtil.Color
    '''
    
def RemoveHudProgressBar( player_or_team, index ):
    '''
    Remove a progress bar from the designated player's screen
    
    Set player_or_team to None to send to all players
    
    player_or_team -- GEPlayer.CGEPlayer or Team Number
    index -- int
    '''

def VectorMA( start, direction, distance ):
    '''
    Multiply the start vector in the given direction by distance
    
    start -- Vector
    direction -- Vector
    distance -- float
    '''
    return Vector

class TraceOpt:
    PLAYER = int
    WORLD = int
    WEAPON = int
    TOKEN = int
    CAPAREA = int
    
def Trace( start, end, options, ignore_ent=None ):
    '''
    Perform a trace in the world, returns the entity that was hit by the trace,
    if any. Options are from GEUtil.TraceOpt and can be bitwise or'd to control
    what type of entities can be returned if hit.
    
    start -- Vector
    end -- Vector
    options -- int
    ignore_ent -- GEEntity.CBaseEntity
    '''
    return GEEntity.CBaseEntity

class Color:
    def __init__( self, color ):
        '''
        Copy another previously defined color directly
        
        color -- Color
        '''
        
    def __init__( self, raw ):
        '''
        Define a color by a raw integer value
        The bit order is 0x[AA][RR][GG][BB]
        
        Example: Color( 0xFF00FFFF ) == Color( 0, 255, 255, 255 ) 
        
        raw -- int
        '''
        
    def __init__( self, r, g, b, a=255 ):
        '''
        Define a color by RGBA values
        
        r -- int
        g -- int
        b -- int
        a -- int
        '''

    def __getitem__( self, item ):
        return float

    def __setitem__( self, item, value ):
        return

    def SetColor( self, r, g, b, a=0 ):
        '''
        r -- int
        g -- int
        b -- int
        a -- int
        '''

    def SetRawColor( self, color ):
        '''
        Sets the color using raw 32-bit number
        
        color -- int
        '''

    def GetRawColor( self ):
        return int

    def r( self ):
        return int

    def g( self ):
        return int

    def b( self ):
        return int

    def a( self ):
        return int

# This is deprecated
class CColor( Color ):
    pass

class QAngle:
    def __init__( self, x=0, y=0, z=0 ):
        '''
        x -- float
        y -- float
        z -- float
        '''

    def __getitem__( self, item ):
        return float

    def __setitem__( self, item, value ):
        return

    def Random( self, min_val, max_val ):
        '''
        min_val -- float
        max_val -- float
        '''

    def IsValid( self ):
        return bool

    def Invalidate( self ):
        return

    def Length( self ):
        return float

    def LengthSqr( self ):
        return float

    def __add__( self, other ):
        '''
        other -- QAngle
        '''
        return QAngle

    def __sub__( self, other ):
        '''
        other -- QAngle
        '''
        return QAngle

    def __div__( self, other ):
        '''
        other -- float
        '''
        return QAngle

    def __mult__( self, other ):
        '''
        other -- float
        '''
        return QAngle

class Vector:
    def __init__( self, x=0, y=0, z=0 ):
        '''
        x -- float
        y -- float
        z -- float
        '''

    def __getitem__( self, item ):
        return float

    def __setitem__( self, item, value ):
        return

    def Random( self, min_val, max_val ):
        '''
        min_val -- float
        max_val -- float
        '''

    def IsValid( self ):
        return bool

    def Invalidate( self ):
        return

    def Length( self ):
        return float

    def Length2D( self ):
        return float

    def LengthSqr( self ):
        return float

    def Length2DSqr( self ):
        return float

    def Zero( self ):
        return

    def Negate( self ):
        return

    def IsZero( self ):
        return bool

    def NormalizeInPlace( self ):
        return float

    def IsLengthGreaterThan( self, val ):
        '''
        val -- float
        '''
        return bool

    def IsLengthLessThan( self, val ):
        '''
        val -- float
        '''
        return bool

    def DistTo( self, other ):
        '''
        other -- Vector
        '''
        return float

    def DistToSqr( self, other ):
        '''
        other -- Vector
        '''
        return float

    def MulAdd( self, a, b, scalar ):
        '''
        a -- Vector
        b -- Vector
        scalar -- float
        '''

    def Dot( self, other ):
        '''
        other -- Vector
        '''
        return float

    def __eq__( self, other ):
        '''
        other -- Vector
        '''
        return bool

    def __add__( self, other ):
        '''
        other -- Vector
        '''
        return Vector

    def __sub__( self, other ):
        '''
        other -- Vector
        '''
        return Vector

    def __div__( self, other ):
        '''
        other -- float
        '''
        return Vector

    def __mult__( self, other ):
        '''
        other -- float
        '''
        return Vector

class CSound:
    def DoesSoundExpire( self ):
        return bool

    def SoundExpirationTime( self ):
        return float

    def GetSoundOrigin( self ):
        return Vector

    def GetSoundReactOrigin( self ):
        return Vector

    def FIsSound( self ):
        return bool

    def FIsScent( self ):
        return bool

    def IsSoundType( self, flags ):
        return bool

    def SoundType( self ):
        return int

    def SoundContext( self ):
        return int

    def SoundTypeNoContext( self ):
        return int

    def Volume( self ):
        return int

    def OccludedVolume( self ):
        return float
