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
	# sys.__stdout__ = oc

	oec = OutputErrCatcher()
	sys.stderr = oec
	# sys.__stderr__ = oec
