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
from GEAi import ActivityId
from . import BaseSchedule, Cond
from ..Tasks import Task

class EstablishLOFFallback( BaseSchedule ):
    def Build( self ):
        self.AddTask( Task.SET_ROUTE_SEARCH_TIME, 2 )
        self.AddTask( Task.GET_CHASE_PATH_TO_ENEMY )
        self.AddTask( Task.RUN_PATH_TIMED, 2 )
        self.AddTask( Task.WAIT_FOR_MOVEMENT )

        self.AddInterrupt( Cond.HEAR_DANGER )
        self.AddInterrupt( Cond.NEW_ENEMY )
        self.AddInterrupt( Cond.CAN_RANGE_ATTACK1 )
        self.AddInterrupt( Cond.CAN_MELEE_ATTACK1 )

class BotCombatFace( BaseSchedule ):
    def Build( self ):
        from . import Sched

        self.AddTask( Task.SET_FAIL_SCHEDULE, Sched.ESTABLISH_LINE_OF_FIRE )
        self.AddTask( Task.SET_ACTIVITY, ActivityId( "ACT_IDLE" ) )
        self.AddTask( Task.FACE_ENEMY )

        self.AddInterrupt( Cond.CAN_RANGE_ATTACK1 )
        self.AddInterrupt( Cond.CAN_MELEE_ATTACK1 )

        self.AddInterrupt( Cond.HEAR_DANGER )
        self.AddInterrupt( Cond.NEW_ENEMY )
        self.AddInterrupt( Cond.ENEMY_DEAD )
        self.AddInterrupt( Cond.ENEMY_WENT_NULL )

class BotRangeAttack1( BaseSchedule ):
    def Build( self ):
        from . import Sched

        self.AddTask( Task.FACE_ENEMY )
        self.AddTask( Task.STORE_LASTPOSITION )
        self.AddTask( Task.SET_TOLERANCE_DISTANCE, 24 )
        self.AddTask( Task.ANNOUNCE_ATTACK, 1 )
        self.AddTask( Task.SET_ROUTE_SEARCH_TIME, 1 )
        self.AddTask( Task.GET_PATH_TO_RANDOM_NODE, 512 )
        self.AddTask( Task.RUN_PATH_TIMED, 1 )
        self.AddTask( Task.RANGE_ATTACK1 )
        self.AddTask( Task.GET_PATH_TO_LASTPOSITION )
        self.AddTask( Task.RUN_PATH_TIMED, 1 )
        self.AddTask( Task.CLEAR_LASTPOSITION )

        self.AddInterrupt( Cond.NEW_ENEMY )
        self.AddInterrupt( Cond.ENEMY_DEAD )
        self.AddInterrupt( Cond.ENEMY_WENT_NULL )
        self.AddInterrupt( Cond.NO_PRIMARY_AMMO )
        self.AddInterrupt( Cond.HEAR_DANGER )
        self.AddInterrupt( Cond.WEAPON_SIGHT_OCCLUDED )

class BotSeekEnemy( BaseSchedule ):
    def Build( self ):
        from . import Sched
        self.AddTask( Task.SET_FAIL_SCHEDULE, Sched.IDLE_WANDER )
        self.AddTask( Task.SET_ROUTE_SEARCH_TIME, 2 )
        self.AddTask( Task.SET_TOLERANCE_DISTANCE, 128 )
        self.AddTask( Task.GES_FIND_ENEMY )
        self.AddTask( Task.GET_PATH_TO_TARGET )
        self.AddTask( Task.RUN_PATH_TIMED, 5.0 )

        self.AddInterrupt( Cond.SEE_ENEMY )
        self.AddInterrupt( Cond.NEW_ENEMY )
        self.AddInterrupt( Cond.ENEMY_DEAD )
        self.AddInterrupt( Cond.ENEMY_UNREACHABLE )
        self.AddInterrupt( Cond.ENEMY_WENT_NULL )

        self.AddInterrupt( Cond.LIGHT_DAMAGE )
        self.AddInterrupt( Cond.HEAVY_DAMAGE )
        self.AddInterrupt( Cond.HEAR_DANGER )
        self.AddInterrupt( Cond.GES_CLOSE_TO_WEAPON )

class BotTakeCoverFromEnemy( BaseSchedule ):
    def Build( self ):
        from . import Sched
        self.AddTask( Task.SET_FAIL_SCHEDULE, Sched.IDLE_WANDER )
        self.AddTask( Task.STOP_MOVING )
        self.AddTask( Task.WAIT, 0.1 )
        self.AddTask( Task.SET_TOLERANCE_DISTANCE, 24 )
        self.AddTask( Task.FIND_COVER_FROM_ENEMY )
        self.AddTask( Task.RUN_PATH )
        self.AddTask( Task.WAIT_FOR_MOVEMENT )
        self.AddTask( Task.FACE_ENEMY )

        self.AddInterrupt( Cond.HEAR_DANGER )
        self.AddInterrupt( Cond.NEW_ENEMY )
        self.AddInterrupt( Cond.ENEMY_DEAD )
        self.AddInterrupt( Cond.ENEMY_WENT_NULL )
        self.AddInterrupt( Cond.GES_NO_TARGET )

class BotEngageEnemy( BaseSchedule ):
    def Build( self ):
        from . import Sched

        self.AddTask( Task.SET_FAIL_SCHEDULE, Sched.ESTABLISH_LINE_OF_FIRE )
        self.AddTask( Task.STORE_POSITION_IN_SAVEPOSITION )
        self.AddTask( Task.SET_ROUTE_SEARCH_TIME, 2 )
        self.AddTask( Task.SET_TOLERANCE_DISTANCE, 128 )
        self.AddTask( Task.GET_FLANK_RADIUS_PATH_TO_ENEMY_LOS, 250 )
        self.AddTask( Task.FACE_TARGET )
        self.AddTask( Task.WAIT_FOR_MOVEMENT )
        self.AddTask( Task.RUN_PATH_TIMED, 1.5 )

        self.AddInterrupt( Cond.HEAVY_DAMAGE )
        self.AddInterrupt( Cond.LIGHT_DAMAGE )
        self.AddInterrupt( Cond.HEAR_DANGER )

        self.AddInterrupt( Cond.ENEMY_DEAD )
        self.AddInterrupt( Cond.ENEMY_UNREACHABLE )
        self.AddInterrupt( Cond.ENEMY_WENT_NULL )
        self.AddInterrupt( Cond.NEW_ENEMY )

class BotPatrol( BaseSchedule ):
    def Build( self ):
        self.AddTask( Task.SET_ROUTE_SEARCH_TIME, 2 )
        self.AddTask( Task.GET_PATH_TO_RANDOM_NODE, 2048 )
        self.AddTask( Task.RUN_PATH_WITHIN_DIST, 256 )
        self.AddTask( Task.CLEAR_GOAL )
        self.AddTask( Task.GET_PATH_TO_RANDOM_NODE, 2048 )
        self.AddTask( Task.RUN_PATH_WITHIN_DIST, 256 )
        self.AddTask( Task.WAIT_RANDOM, 1.0 )

        self.AddInterrupt( Cond.HEAR_DANGER )
        self.AddInterrupt( Cond.HEAR_COMBAT )
        self.AddInterrupt( Cond.HEAR_BULLET_IMPACT )
        self.AddInterrupt( Cond.NEW_ENEMY )
        self.AddInterrupt( Cond.SEE_ENEMY )
        self.AddInterrupt( Cond.HEAVY_DAMAGE )
        self.AddInterrupt( Cond.LIGHT_DAMAGE )
        
class BotSeekWeapon( BaseSchedule ):
    def Build( self ):
        from . import Sched

        self.AddTask( Task.SET_FAIL_SCHEDULE, Sched.IDLE_WANDER )
        self.AddTask( Task.SET_ROUTE_SEARCH_TIME, 2 )
        self.AddTask( Task.SET_TOLERANCE_DISTANCE, 128 )
        self.AddTask( Task.GES_FIND_WEAPON, 0 )
        self.AddTask( Task.GET_PATH_TO_TARGET )
        self.AddTask( Task.RUN_PATH_TIMED, 10 )

        self.AddInterrupt( Cond.HEAR_BULLET_IMPACT )
        self.AddInterrupt( Cond.HEAR_DANGER )
        self.AddInterrupt( Cond.LIGHT_DAMAGE )
        self.AddInterrupt( Cond.HEAVY_DAMAGE )
        self.AddInterrupt( Cond.SEE_ENEMY )
        self.AddInterrupt( Cond.GES_NO_TARGET )
        self.AddInterrupt( Cond.NEW_ENEMY )

class BotSeekWeaponDetermined( BaseSchedule ):
    def Build( self ):
        from . import Sched

        self.AddTask( Task.SET_FAIL_SCHEDULE, Sched.IDLE_WANDER )
        self.AddTask( Task.SET_ROUTE_SEARCH_TIME, 2 )
        self.AddTask( Task.SET_TOLERANCE_DISTANCE, 48 )
        self.AddTask( Task.GES_FIND_WEAPON, 1 )
        self.AddTask( Task.GET_PATH_TO_TARGET )
        self.AddTask( Task.RUN_PATH_TIMED, 10 )

        self.AddInterrupt( Cond.HEAR_DANGER )
        self.AddInterrupt( Cond.GES_NO_TARGET )
        self.AddInterrupt( Cond.NEW_ENEMY )

class BotSeekAmmo( BaseSchedule ):
    def Build( self ):
        from . import Sched

        self.AddTask( Task.SET_FAIL_SCHEDULE, Sched.IDLE_WANDER )
        self.AddTask( Task.SET_ROUTE_SEARCH_TIME, 2 )
        self.AddTask( Task.SET_TOLERANCE_DISTANCE, 48 )
        self.AddTask( Task.GES_FIND_AMMO, 1 )
        self.AddTask( Task.GET_PATH_TO_TARGET )
        self.AddTask( Task.RUN_PATH_TIMED, 10 )

        self.AddInterrupt( Cond.HEAR_BULLET_IMPACT )
        self.AddInterrupt( Cond.HEAR_DANGER )
        self.AddInterrupt( Cond.LIGHT_DAMAGE )
        self.AddInterrupt( Cond.HEAVY_DAMAGE )
        self.AddInterrupt( Cond.SEE_ENEMY )
        self.AddInterrupt( Cond.GES_NO_TARGET )
        self.AddInterrupt( Cond.NEW_ENEMY )

class BotSeekAmmoDetermined( BaseSchedule ):
    def Build( self ):
        from . import Sched

        self.AddTask( Task.SET_FAIL_SCHEDULE, Sched.IDLE_WANDER )
        self.AddTask( Task.SET_ROUTE_SEARCH_TIME, 2 )
        self.AddTask( Task.SET_TOLERANCE_DISTANCE, 48 )
        self.AddTask( Task.GES_FIND_AMMO, 1 )
        self.AddTask( Task.GET_PATH_TO_TARGET )
        self.AddTask( Task.RUN_PATH_TIMED, 10 )

        self.AddInterrupt( Cond.HEAR_DANGER )
        self.AddInterrupt( Cond.GES_NO_TARGET )
        self.AddInterrupt( Cond.NEW_ENEMY )

class BotSeekArmor( BaseSchedule ):
    def Build( self ):
        from . import Sched

        self.AddTask( Task.SET_FAIL_SCHEDULE, Sched.IDLE_WANDER )
        self.AddTask( Task.SET_ROUTE_SEARCH_TIME, 2 )
        self.AddTask( Task.SET_TOLERANCE_DISTANCE, 48 )
        self.AddTask( Task.GES_FIND_ARMOR, 2048 )
        self.AddTask( Task.GET_PATH_TO_TARGET )
        self.AddTask( Task.RUN_PATH_TIMED, 10 )

        self.AddInterrupt( Cond.HEAR_BULLET_IMPACT )
        self.AddInterrupt( Cond.HEAR_DANGER )
        self.AddInterrupt( Cond.LIGHT_DAMAGE )
        self.AddInterrupt( Cond.HEAVY_DAMAGE )
        self.AddInterrupt( Cond.GES_ENEMY_CLOSE )
        self.AddInterrupt( Cond.GES_NO_TARGET )
        self.AddInterrupt( Cond.GES_CAN_NOT_SEEK_ARMOR )
        self.AddInterrupt( Cond.NEW_ENEMY )

class BotSeekArmorDetermined( BaseSchedule ):
    def Build( self ):
        from . import Sched

        self.AddTask( Task.SET_FAIL_SCHEDULE, Sched.IDLE_WANDER )
        self.AddTask( Task.SET_ROUTE_SEARCH_TIME, 2 )
        self.AddTask( Task.SET_TOLERANCE_DISTANCE, 48 )
        self.AddTask( Task.GES_FIND_ARMOR, 2048 )
        self.AddTask( Task.GET_PATH_TO_TARGET )
        self.AddTask( Task.RUN_PATH_TIMED, 10 )

        self.AddInterrupt( Cond.HEAR_DANGER )
        self.AddInterrupt( Cond.GES_NO_TARGET )
        self.AddInterrupt( Cond.GES_CAN_NOT_SEEK_ARMOR )
        self.AddInterrupt( Cond.NEW_ENEMY )

class BotSeekToken( BaseSchedule ):
    def Build( self ):
        from . import Sched

        self.AddTask( Task.SET_FAIL_SCHEDULE, Sched.IDLE_WANDER )
        self.AddTask( Task.SET_ROUTE_SEARCH_TIME, 2 )
        self.AddTask( Task.SET_TOLERANCE_DISTANCE, 48 )
        self.AddTask( Task.GES_FIND_TOKEN )
        self.AddTask( Task.GET_PATH_TO_TARGET )
        self.AddTask( Task.ITEM_RUN_PATH, 8 )

        self.AddInterrupt( Cond.NEW_ENEMY )
        self.AddInterrupt( Cond.HEAR_DANGER )
        self.AddInterrupt( Cond.GES_ENEMY_CLOSE )
        self.AddInterrupt( Cond.LIGHT_DAMAGE )
        self.AddInterrupt( Cond.HEAVY_DAMAGE )
        self.AddInterrupt( Cond.GES_NO_TARGET )

