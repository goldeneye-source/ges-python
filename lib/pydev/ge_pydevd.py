import pydevd, reimport
import GEUtil

def ConnectDebugger( host_ovr=None, port_ovr=None ):
	if pydevd.connected:
		GEUtil.Warning( "In order to run another debug session you MUST restart the game.\n" )
		return

	if port_ovr:
		pydevd.settrace( host=host_ovr, port=port_ovr, suspend=False )
	else:
		pydevd.settrace( host=host_ovr, suspend=False )

