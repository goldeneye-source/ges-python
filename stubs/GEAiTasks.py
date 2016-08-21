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
class TaskFail:
    NO_FAILURE = int
    NO_TARGET = int
    WEAPON_OWNED = int
    ITEM_NO_FIND = int
    NO_HINT_NODE = int
    SCHEDULE_NOT_FOUND = int
    NO_ENEMY = int
    NO_BACKAWAY_NODE = int
    NO_COVER = int
    NO_FLANK = int
    NO_SHOOT = int
    NO_ROUTE = int
    NO_ROUTE_GOAL = int
    NO_ROUTE_BLOCKED = int
    NO_ROUTE_ILLEGAL = int
    NO_WALK = int
    ALREADY_LOCKED = int
    NO_SOUND = int
    NO_SCENT = int
    BAD_ACTIVITY = int
    NO_GOAL = int
    NO_PLAYER = int
    NO_REACHABLE_NODE = int
    NO_AI_NETWORK = int
    BAD_POSITION = int
    BAD_PATH_GOAL = int
    STUCK_ONTOP = int
    ITEM_TAKEN = int

class Task:
    INVALID = int
    RESET_ACTIVITY = int
    WAIT = int
    ANNOUNCE_ATTACK = int
    WAIT_FACE_ENEMY = int
    WAIT_FACE_ENEMY_RANDOM = int
    WAIT_PVS = int
    SUGGEST_STATE = int
    TARGET_PLAYER = int
    MOVE_TO_TARGET_RANGE = int
    MOVE_AWAY_PATH = int
    GET_PATH_AWAY_FROM_BEST_SOUND = int
    GET_PATH_TO_ENEMY = int
    GET_PATH_TO_ENEMY_LKP = int
    GET_CHASE_PATH_TO_ENEMY = int
    GET_PATH_TO_ENEMY_LKP_LOS = int
    GET_PATH_TO_ENEMY_CORPSE = int
    GET_PATH_TO_PLAYER = int
    GET_PATH_TO_ENEMY_LOS = int
    GET_FLANK_RADIUS_PATH_TO_ENEMY_LOS = int
    GET_FLANK_ARC_PATH_TO_ENEMY_LOS = int
    GET_PATH_TO_RANGE_ENEMY_LKP_LOS = int
    GET_PATH_TO_TARGET = int
    GET_PATH_TO_HINTNODE = int
    STORE_LASTPOSITION = int
    CLEAR_LASTPOSITION = int
    STORE_POSITION_IN_SAVEPOSITION = int
    STORE_BESTSOUND_IN_SAVEPOSITION = int
    STORE_BESTSOUND_REACTORIGIN_IN_SAVEPOSITION = int
    REACT_TO_COMBAT_SOUND = int
    STORE_ENEMY_POSITION_IN_SAVEPOSITION = int
    GET_PATH_TO_LASTPOSITION = int
    GET_PATH_TO_SAVEPOSITION = int
    GET_PATH_TO_SAVEPOSITION_LOS = int
    GET_PATH_TO_RANDOM_NODE = int
    GET_PATH_TO_BESTSOUND = int
    GET_PATH_TO_BESTSCENT = int
    RUN_PATH = int
    WALK_PATH = int
    WALK_PATH_TIMED = int
    WALK_PATH_WITHIN_DIST = int
    WALK_PATH_FOR_UNITS = int
    RUN_PATH_FLEE = int
    RUN_PATH_TIMED = int
    RUN_PATH_FOR_UNITS = int
    RUN_PATH_WITHIN_DIST = int
    STRAFE_PATH = int
    CLEAR_MOVE_WAIT = int
    FACE_IDEAL = int
    FACE_REASONABLE = int
    FACE_PATH = int
    FACE_PLAYER = int
    FACE_ENEMY = int
    FACE_HINTNODE = int
    FACE_TARGET = int
    FACE_LASTPOSITION = int
    FACE_SAVEPOSITION = int
    FACE_AWAY_FROM_SAVEPOSITION = int
    RANGE_ATTACK1 = int
    RANGE_ATTACK2 = int
    MELEE_ATTACK1 = int
    MELEE_ATTACK2 = int
    RELOAD = int
    SPECIAL_ATTACK1 = int
    SPECIAL_ATTACK2 = int
    FIND_HINTNODE = int
    FIND_LOCK_HINTNODE = int
    CLEAR_HINTNODE = int
    LOCK_HINTNODE = int
    SOUND_ANGRY = int
    SOUND_DEATH = int
    SOUND_IDLE = int
    SOUND_WAKE = int
    SOUND_PAIN = int
    SOUND_DIE = int
    SET_ACTIVITY = int
    SET_SCHEDULE = int
    SET_FAIL_SCHEDULE = int
    SET_TOLERANCE_DISTANCE = int
    SET_ROUTE_SEARCH_TIME = int
    CLEAR_FAIL_SCHEDULE = int
    FIND_COVER_FROM_BEST_SOUND = int
    FIND_COVER_FROM_ENEMY = int
    FIND_LATERAL_COVER_FROM_ENEMY = int
    FIND_BACKAWAY_FROM_SAVEPOSITION = int
    FIND_NODE_COVER_FROM_ENEMY = int
    FIND_NEAR_NODE_COVER_FROM_ENEMY = int
    FIND_FAR_NODE_COVER_FROM_ENEMY = int
    FIND_COVER_FROM_ORIGIN = int
    DIE = int
    WAIT_RANDOM = int
    WAIT_INDEFINITE = int
    STOP_MOVING = int
    TURN_LEFT = int
    TURN_RIGHT = int
    WAIT_FOR_MOVEMENT = int
    WAIT_FOR_MOVEMENT_STEP = int
    WAIT_UNTIL_NO_DANGER_SOUND = int
    WEAPON_RUN_PATH = int
    ITEM_RUN_PATH = int
    USE_SMALL_HULL = int
    FALL_TO_GROUND = int
    WANDER = int
    FREEZE = int
    GATHER_CONDITIONS = int
    IGNORE_OLD_ENEMIES = int
    ADD_GESTURE_WAIT = int
    ADD_GESTURE = int
    CLEAR_GOAL = int
