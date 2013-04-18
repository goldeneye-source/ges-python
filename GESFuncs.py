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
import GEGlobal
from GEUtil import Warning
import os, traceback, pkgutil

# Handy helper function to remove old compiled files
# Pass in a path ending in * to do wildcard removal
def RemoveCompiled( path ):
	py_ext = ['.pyc', '.pyo']

	if path.endswith( '*' ):
		dir_ = os.path.split( path )[0]
		for file_ in os.listdir( dir_ ):
			( fn, ext ) = os.path.splitext( file_ )
			if file_ != '.' and file_ != '..' and py_ext.count( ext ):
				os.remove( dir_ + '\\' + file_ )
	else:
		for ext in py_ext:
			file_ = "%s%s" % ( path, ext )
			if os.path.exists( file_ ):
				os.remove( file_ )

def FindModule( package, name ):
	try:
		for m in GetModules( package ):
			if m.lower() == name.lower():
				return m
	except:
		pass

	return None

def CheckAPI( obj, check_api, do_reload=False ):
	if do_reload:
		reload( obj )

	obj_name = obj.__name__

	if hasattr( obj, "USING_API" ):
		api_lvl = str( getattr( obj, "USING_API", "0.0" ) )

		in_levels = api_lvl.split( "." )
		ck_levels = check_api.split( "." )

		# Bad level count or first two levels mismatch, bail
		if len( in_levels ) < 3:
			Warning( "---------------------------------------------------\n" )
			Warning( "!!! PYTHON LOAD ERROR !!!\n\n" )
			Warning( "API Check: malformed 'USING_API' in %s, must be 'X.X.X' string!\n" % obj_name )
			Warning( "---------------------------------------------------\n" )
			return False

		if in_levels[0] != ck_levels[0]:
			Warning( "---------------------------------------------------\n" )
			Warning( "!!! PYTHON LOAD ERROR !!!\n\n" )
			Warning( "The API had a MAJOR update.\nYou must update %s before it will load!\n" % obj_name )
			Warning( "---------------------------------------------------\n" )
			# First level failure means no load
			return False
		elif in_levels[1] != ck_levels[1]:
			# Second level failure induces a large error message
			Warning( "---------------------------------------------------\n" )
			Warning( "!!! PYTHON LOAD WARNING !!!\n\n" )
			Warning( "The API had a large update.\nPlease check %s for errors!\n" % obj_name )
			Warning( "---------------------------------------------------\n" )
		elif in_levels[2] != ck_levels[2]:
			# Warn if our third level mismatches (minor changes)
			Warning( "Python API: the most current API is %s, please update to prevent issues!\n" % check_api )

		return True
	else:
		Warning( "---------------------------------------------------\n" )
		Warning( "!!! PYTHON LOAD ERROR !!!\n\n" )
		Warning( "Failed to find attribute 'USING_API' in %s!\n" % obj_name )
		Warning( "---------------------------------------------------\n" )
		return False

def PrintError( msg ):
	Warning( msg )
	Warning( "----------------------------------------------------\n" )
	traceback.print_exc()
	Warning( "----------------------------------------------------\n" )

def GetModules( package ):
	pkgpath = os.path.dirname( package.__file__ )
	return [name for _, name, _ in pkgutil.iter_modules( [pkgpath] )]
