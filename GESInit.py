import GEUtil
from GEGlobal import PY_BASE_DIR
import sys

# -----------------
# Setup PYTHONPATH
#
def SetPaths():
	# Clear the current path to make sure we don't have lingering bad directories
	sys.path = []

	# Append each directory that we want to look in for modules
	sys.path.append( PY_BASE_DIR )
	sys.path.append( PY_BASE_DIR + "/lib/pydev" )
	sys.path.append( PY_BASE_DIR + "/lib/python2.6" )

# -----------------
# I/O Redirection
#
class OutputCatcher:
	def __init__( self ):
		self.data = ''

	def write( self, stuff ):
		GEUtil.Msg( stuff )

class OutputErrCatcher:
	def __init__( self ):
		self.data = ''

	def write( self, stuff ):
		GEUtil.Warning( stuff )

if __name__ == "__main__":
	# Redirect the stdout and stderr to the game console
	oc = OutputCatcher()
	sys.stdout = oc
	sys.__stdout__ = oc

	oec = OutputErrCatcher()
	sys.stderr = oec
	sys.__stderr__ = oec

	# Call our path setter
	SetPaths()
