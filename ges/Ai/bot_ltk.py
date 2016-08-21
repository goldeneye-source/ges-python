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
from .bot_deathmatch import bot_deathmatch
from .Schedules import Cond
import GEGlobal as Glb

USING_API = Glb.API_VERSION_1_1_0

class bot_ltk( bot_deathmatch ):
    def GatherConditions( self ):
        bot_deathmatch.GatherConditions( self )
        self.ClearCondition( Cond.GES_CLOSE_TO_ARMOR )
        self.ClearCondition( Cond.GES_CAN_SEEK_ARMOR )
        self.SetCondition( Cond.GES_CAN_NOT_SEEK_ARMOR )

    def bot_WeaponParamCallback( self ):
        params = bot_deathmatch.bot_WeaponParamCallback( self )
        params["melee_bonus"] = -5
        return params
