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
class Class:
    NONE = int
    PLAYER = int
    PLAYER_ALLY = int
    GES_BOT = int
    GES_GUARD = int
    GES_NONCOMBATANT = int

class Disposition:
    HATE = int
    FEAR = int
    LIKE = int
    NEUTRAL = int

class State:
    NO_SELECTION = int
    NONE = int
    IDLE = int
    ALERT = int
    COMBAT = int
    DEAD = int

class Level:
    EASY = int
    MEDIUM = int
    HARD = int
    UBER = int

class Goal:
    NONE = int
    ENEMY = int
    TARGET = int
    ENEMY_LKP = int
    SAVED_POSITION = int

class Path:
    NONE = int
    TRAVEL = int
    LOS = int
    COVER = int

class Capability:
    MOVE_GROUND = int
    MOVE_JUMP = int
    MOVE_FLY = int
    MOVE_CLIMB = int
    MOVE_SWIM = int
    MOVE_SHOOT = int
    SKIP_NAV_GROUND_CHECK = int
    USE = int
    USE_DOORS = int
    TURN_HEAD = int
    WEAPON_RANGE_ATTACK = int
    WEAPON_MELEE_ATTACK = int
    USE_WEAPONS = int
    ANIMATEDFACE = int
    USE_SHOT_REGULATOR = int
    FRIENDLY_DMG_IMMUNE = int
    SQUAD = int
    DUCK = int
    NO_HIT_PLAYER = int
    AIM_GUN = int
    NO_HIT_SQUADMATES = int

class Memory:
    CLEAR = int
    PROVOKED = int
    INCOVER = int
    SUSPICIOUS = int
    TASK_EXPENSIVE = int
    PATH_FAILED = int
    FLINCHED = int
    TOURGUIDE = int
    LOCKED_HINT = int
    TURNING = int
    TURNHACK = int
    HAD_ENEMY = int
    HAD_PLAYER = int
    HAD_LOS = int
    MOVED_FROM_SPAWN = int
    STUCK = int
    CUSTOM3 = int
    CUSTOM2 = int
    CUSTOM1 = int
