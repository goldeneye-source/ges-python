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
import GEUtil, GEMPGameRules as GERules, GEGlobal as Glb
from GEGlobal import EventHooks

# These are in seconds
PREROUND_END_DELAY = 3.5

NOTICE_INTERVAL_LONG = 15.0
NOTICE_INTERVAL_SHORT = 10.0
NOTICE_INTERVAL_TINY = 0.9

CHAN_TIMER = 4

COLOR_TIMER = GEUtil.CColor( 255, 255, 255, 255 )
COLOR_GETREADY = GEUtil.CColor( 255, 255, 255 )

class GEWarmUp:
    def __init__( self, parent ):
        if not hasattr( parent, 'RegisterEventHook' ):
            raise AttributeError( "Parent must be a Gameplay Scenario type!" )

        parent.RegisterEventHook( EventHooks.GP_THINK, self._think )
        parent.RegisterEventHook( EventHooks.GP_PLAYERCONNECT, self._player_connect )

        self.keep_weaponset = False
        self.Reset()

    def IsInWarmup( self ):
        if self.time_endround:
            return True
        return self.in_warmup

    def HadWarmup( self ):
        return self.had_warmup

    def StartWarmup( self, duration=30.0, endround_if_no_warmup=False, keep_weaponset=False ):
        now = GEUtil.GetTime()
        if duration > 0:
            self.time_endwarmup = now + duration
            self.time_nextnotice = duration
            self.keep_weaponset = keep_weaponset
            self.in_warmup = True
            GEUtil.InitHudProgressBar( None, CHAN_TIMER, "#GES_GP_INWARMUP", Glb.HUDPB_TITLEONLY, x=-1, y=.02 )
            GEUtil.EmitGameplayEvent( "ges_startwarmup" )
            return True
        elif endround_if_no_warmup:
            self.keep_weaponset = keep_weaponset
            self.EndWarmup()
            return True
        else:
            # Just pass through...
            self.had_warmup = True
            self.in_warmup = False
            return False

    def EndWarmup( self ):
        self.Reset()
        self.time_endround = GEUtil.GetTime() + PREROUND_END_DELAY
        # Tell us to get ready
        GEUtil.RemoveHudProgressBar( None, CHAN_TIMER )
        GEUtil.HudMessage( None, "#GES_GP_GETREADY", -1, -1, COLOR_GETREADY, PREROUND_END_DELAY + 3.0, CHAN_TIMER )

    def SetKeepWeaponset( self, state ):
        self.keep_weaponset = state

    def Reset( self ):
        self.had_warmup = False
        self.in_warmup = False
        self.time_endround = 0
        self.time_endwarmup = 0
        self.time_nextnotice = 0

    def _player_connect( self, player ):
        if self.in_warmup:
            GEUtil.InitHudProgressBar( None, CHAN_TIMER, "#GES_GP_INWARMUP", Glb.HUDPB_TITLEONLY, x=-1, y=.02 )

    def _calc_next_notice( self, time_left ):
        if time_left > 30:
            # Round to the next 5-divisible number
            return max( 5.0 * round( ( time_left - NOTICE_INTERVAL_LONG ) / 5.0 ), 30.0 )
        elif time_left <= 30 and time_left > 10:
            # Show the notice every 10 seconds after we hit 30 seconds
            return max( time_left - NOTICE_INTERVAL_SHORT, 10.0 )
        else:
            # Show every second after that
            return max( time_left - NOTICE_INTERVAL_TINY, 0 )

    def _think( self ):
        # Don't worry about this if we are done
        if self.had_warmup:
            return

        now = GEUtil.GetTime()

        if self.in_warmup and now < self.time_endwarmup:
            time_left = self.time_endwarmup - now
            if time_left <= self.time_nextnotice:
                # Let everyone know how much time is left
                GEUtil.HudMessage( None, "#GES_GP_WARMUP\r%0.0f sec" % time_left, -1, 0.75, COLOR_TIMER, 3.0, CHAN_TIMER )
                # Calculate the time to the next notice
                self.time_nextnotice = self._calc_next_notice( time_left )

        elif self.in_warmup and now >= self.time_endwarmup:
            # Notify players that warmup is now over
            self.EndWarmup()

        elif self.time_endround and now >= self.time_endround:
            # This completes our warmup
            self.time_endround = 0
            self.had_warmup = True
            GERules.EndRound( False, self.keep_weaponset )
            GEUtil.EmitGameplayEvent( "ges_endwarmup" )
