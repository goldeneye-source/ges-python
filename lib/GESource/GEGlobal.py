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
# Static defines for the python API's
API_VERSION_1_0_0 = str
API_VERSION_1_1_0 = str
API_VERSION_1_1_1 = str

# Current API version (INTERNAL USE ONLY)
API_AI_VERSION = str
API_GP_VERSION = str

# Defined on game run
PY_BASE_DIR = str

# Functions that can be hooked for callbacks
class EventHooks:
    GP_THINK = int
    GP_PLAYERCONNECT = int
    GP_PLAYERDISCONNECT = int
    GP_PLAYERSPAWN = int
    GP_PLAYEROBSERVER = int
    GP_PLAYERKILLED = int
    GP_PLAYERTEAM = int
    GP_ROUNDBEGIN = int
    GP_ROUNDEND = int

    AI_ONSPAWN = int
    AI_ONLOOKED = int
    AI_ONLISTENED = int
    AI_PICKUPITEM = int
    AI_GATHERCONDITIONS = int
    AI_SELECTSCHEDULE = int
    AI_SETDIFFICULTY = int

# Standard Say Commands (for use in OnPlayerSay)
SAY_COMMAND1 = "!voodoo"
SAY_COMMAND2 = "!gesrocks"

# Teams
TEAM_NONE = int
TEAM_SPECTATOR = int
TEAM_MI6 = int
TEAM_JANUS = int

#
# These are meta teams for better filtering of messages
#
TEAM_OBS = int
# All observers and spectators (regardless of team)
TEAM_NO_OBS = int
# All players that are NOT observers or spectators (regardless of team)
TEAM_MI6_OBS = int
# Only MI6 observers and spectators
TEAM_MI6_NO_OBS = int
# Only MI6 team members that are NOT observers (no spectators)
TEAM_JANUS_OBS = int
# Only Janus observers and spectators
TEAM_JANUS_NO_OBS = int
# Only Janus team members that are NOT observers (no spectators)

# Teamplay allowance
TEAMPLAY_NONE = int
TEAMPLAY_ALWAYS = int
TEAMPLAY_TOGGLE = int

# For use with GEMPGameRules.CTokenManager functions
SPAWN_AMMO = int
SPAWN_WEAPON = int
SPAWN_TOKEN = int
SPAWN_CAPAREA = int
SPAWN_PLAYER = int
SPAWN_MYTEAM = int
SPAWN_OTHERTEAM = int
SPAWN_SPECIALONLY = int

# Weapon ID's
WEAPON_NONE = int
WEAPON_PP7 = int
WEAPON_PP7_SILENCED = int
WEAPON_DD44 = int
WEAPON_SILVERPP7 = int
WEAPON_GOLDENPP7 = int
WEAPON_COUGAR_MAGNUM = int
WEAPON_GOLDENGUN = int
WEAPON_SHOTGUN = int
WEAPON_AUTO_SHOTGUN = int
WEAPON_KF7 = int
WEAPON_KLOBB = int
WEAPON_ZMG = int
WEAPON_D5K = int
WEAPON_D5K_SILENCED = int
WEAPON_RCP90 = int
WEAPON_AR33 = int
WEAPON_PHANTOM = int
WEAPON_SNIPER_RIFLE = int
WEAPON_KNIFE_THROWING = int
WEAPON_GRENADE_LAUNCHER = int
WEAPON_ROCKET_LAUNCHER = int
WEAPON_MOONRAKER = int
WEAPON_TIMEDMINE = int
WEAPON_REMOTEMINE = int
WEAPON_PROXIMITYMINE = int
WEAPON_GRENADE = int
WEAPON_SLAPPERS = int
WEAPON_KNIFE = int
WEAPON_MAX = int

# Ammo names
AMMO_9MM = str
AMMO_RIFLE = str
AMMO_BUCKSHOT = str
AMMO_MAGNUM = str
AMMO_GOLDENGUN = str
AMMO_PROXIMITYMINE = str
AMMO_TIMEDMINE = str
AMMO_REMOTEMINE = str
AMMO_TKNIFE = str
AMMO_GRENADE = str
AMMO_ROCKET = str
AMMO_SHELL = str

# For use with GEUtil.ClientPrint
HUD_PRINTNOTIFY = int
HUD_PRINTCONSOLE = int
HUD_PRINTTALK = int
HUD_PRINTCENTER = int

# Default Max Armor/Health
GE_MAX_ARMOR = int
GE_MAX_HEALTH = int

# For use with GEUtil.InitHUDProgressBar
HUDPB_TITLEONLY = int
HUDPB_SHOWBAR = int
HUDPB_SHOWVALUE = int
HUDPB_VERTICAL = int

# For use with GEMPGameRules.CRadar
RADAR_TYPE_DEFAULT = int
RADAR_TYPE_PLAYER = int
RADAR_TYPE_TOKEN = int
RADAR_TYPE_OBJECTIVE = int

RADAR_ALWAYSVIS = bool
RADAR_NORMVIS = bool

# For use with CGEPlayer.SetScoreboardColor
SB_COLOR_NORMAL = int
SB_COLOR_GOLD = int
SB_COLOR_WHITE = int
SB_COLOR_ELIMINATED = int

# Sound constants
SOUND_PRIORITY_VERY_LOW = int
SOUND_PRIORITY_LOW = int
SOUND_PRIORITY_NORMAL = int
SOUND_PRIORITY_HIGH = int
SOUND_PRIORITY_VERY_HIGH = int
SOUND_PRIORITY_HIGHEST = int

SOUND_NONE = int
SOUND_COMBAT = int
SOUND_WORLD = int
SOUND_PLAYER = int
SOUND_DANGER = int
SOUND_BULLET_IMPACT = int
SOUND_CARCASS = int
SOUND_MEAT = int
SOUND_GARBAGE = int
SOUND_THUMPER = int
SOUND_BUGBAIT = int
SOUND_PHYSICS_DANGER = int
SOUND_DANGER_SNIPERONLY = int
SOUND_MOVE_AWAY = int
SOUND_PLAYER_VEHICLE = int
SOUND_READINESS_LOW = int
SOUND_READINESS_MEDIUM = int
SOUND_READINESS_HIGH = int
