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
import pydevd_constants
pydevd_constants.DEBUG_TRACE_LEVEL = -1
pydevd_constants.DEBUG_TRACE_BREAKPOINTS = -1
pydevd_constants.USE_PSYCO_OPTIMIZATION = False

# ----NOTES----
# pydevd_comm: a timeout was added to the StartClient function
# pydevd_comm: A better debug output was put into place around line 270 in ReaderThread.OnRun

import pydevd, GEUtil

def ConnectDebugger( host_ovr=None, port_ovr=None ):
	if pydevd.connected:
		GEUtil.Warning( "In order to run another debug session you MUST restart the game.\n" )
		return

	if port_ovr:
		pydevd.settrace( host=host_ovr, port=port_ovr, suspend=False )
	else:
		pydevd.settrace( host=host_ovr, suspend=False )

	GEUtil.Msg( "Python debugger successfully connected!\n" )

