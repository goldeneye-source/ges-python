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
from GEUtil import Warning

import ptvsd
from ptvsd.attach_server import AttachAlreadyEnabledError

PTVS_SECRET = "ges"

def ConnectDebugger( host_ovr=None, port_ovr=None ):
    '''
    This feature is currently deprecated
    '''
    Warning( "Eclipse debugging is no longer supported! Use ge_py_listendebugger instead.\n" )

def ListenDebugger( port_ovr=None ):
    '''
    Start a debug server for Python Tools for Visual Studio (ptvs)
    '''
    try:
        if port_ovr:
            ptvsd.enable_attach( secret=PTVS_SECRET, address=('0.0.0.0', port_ovr), redirect_output=False )
        else:
            ptvsd.enable_attach( secret=PTVS_SECRET, redirect_output=False )

        print( "Listening for Python Tools for Visual Studio debugger, version %s\n" % ptvsd.attach_server.PTVS_VER )
    
    except AttachAlreadyEnabledError:
        Warning( "Python debugger is already listening!\n" )
        
    print( "To connect using Visual Studio 2013 & PTVS:" )
    print( "  1) DEBUG -> Attach to process..." )
    print( "  2) Select Python Remote (ptvsd) from the Transport menu" )
    print( "  3) Enter tcp://%s@localhost:5678 in the Qualifier field and press Refresh" % PTVS_SECRET )
    print( "  4) Click Attach to start debugging" )
    print( "\nGood Luck and happy coding!\n" )
    
    