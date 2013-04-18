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
from GEGlobal import PY_BASE_DIR
import sys, datetime

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

def LoadManager( name ):
	import reimport

	try:
		if name in sys.modules:
			reimport.reimport( name )
		else:
			__import__( name, globals(), locals() )

		mgr = sys.modules[name]
		return mgr.GetManager()
	except KeyError, e:
		GEUtil.Warning( "Failed to find manager named: %s!\n" % name )
		raise e
	except NameError:
		GEUtil.Warning( "%s must define a 'GetManager' function!\n" % name )

def UnloadManager( name ):
	try:
		mgr = sys.modules[name]
		mgr.PurgeManager()

		import gc
		gc.collect()
	except KeyError:
		GEUtil.Warning( "Failed to find manager named: %s!\n" % name )
	except NameError:
		GEUtil.Warning( "%s must define a 'PurgeManager' function!\n" % name )

# -----------------
# Error Logger
#
class ErrorLog( object ):
	def __init__( self ):
		log_file = PY_BASE_DIR + '/python.log'
		log_header = ''

		# Make sure our log doesn't get too large (512 KB limit)
		try:
			import os
			if os.path.getsize( log_file ) > 512000:
				os.remove( log_file )
			log_header = '\n\n'
		except:
			pass

		try:
			# Open log to append new errors
			self.log = open( log_file, 'a+' )
			self.log.write( "%s------------------------------------------\n" % log_header )
			self.log.write( "Log started on %s\n" % datetime.datetime.now() )
			self.log.write( "------------------------------------------\n\n" )
			self.log.flush()
		except:
			GEUtil.Warning( "Failed to open Python log file for write!\n" )
			if self.log:
				self.log.close()
			self.log = None

	def __del__( self ):
		try:
			# Close the log out
			self.log.write( "\n------------------------------------------\n" )
			self.log.write( "Log ended on %s\n" % datetime.datetime.now() )
			self.log.write( "\n------------------------------------------\n\n" )
			self.log.close()
		except ( IOError, TypeError ):
			pass

	def write( self, lines ):
		try:
			# Print error to the log
			self.log.writelines( lines )
			self.log.flush()
		except ( IOError, TypeError ):
			pass

# -----------------
# I/O Redirection
#
class OutputCatcher( object ):
	def __init__( self ):
		self.data = ''

	def write( self, stuff ):
		GEUtil.Msg( stuff )

class OutputErrCatcher( object ):
	def __init__( self ):
		self.data = ''
		self.log = ErrorLog()

	def write( self, stuff ):
		GEUtil.Warning( stuff )
		self.log.write( stuff )

if __name__ == "__main__":
	# Call our path setter
	SetPaths()

	# Redirect the stdout and stderr to the game console
	oc = OutputCatcher()
	sys.stdout = oc

	oec = OutputErrCatcher()
	sys.stderr = oec
