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
import GEUtil

class GEOvertime:
    def __init__( self ):
        self.end_time = 0
        self.trip_time = 0
        self.is_tripped = False

    def StartOvertime( self, failsafe, trip=30 ):
        if failsafe == -1:
            self.end_time = -1
        else:
            self.end_time = GEUtil.GetTime() + failsafe
            self.trip_time = self.end_time - trip
            self.is_tripped = False

    def CheckOvertime( self ):
        if self.end_time == -1:
            return True

        if GEUtil.GetTime() >= self.end_time:
            return False
        elif not self.is_tripped and GEUtil.GetTime() >= self.trip_time:
            time = self.end_time - self.trip_time
            GEUtil.PopupMessage( None, "#GES_GPH_OVERTIME_TRIP_TITLE", "#GES_GPH_OVERTIME_TRIP\r%i" % int( time ) )
            self.is_tripped = True

        return True
