import GEUtil, GEGlobal
import os, traceback, pkgutil

# Handy helper function to remove old compiled files
# Pass in a path ending in * to do wildcard removal
def RemoveCompiled( path ):
	py_ext = ['.pyc', '.pyo']

	if path.endswith( '*' ):
		dir = os.path.split( path )[0]
		for file in os.listdir( dir ):
			( fn, ext ) = os.path.splitext( file )
			if file != '.' and file != '..' and py_ext.count( ext ):
				os.remove( dir + '\\' + file )
	else:
		for ext in py_ext:
			file = "%s%s" % ( path, ext )
			if os.path.exists( file ):
				os.remove( file )

def FindModule( package, name ):
	try:
		for m in GetModules( package ):
			if m.lower() == name.lower():
				return m
	except:
		pass

	return None

def CheckAPI( object, check_api, do_reload=False ):
	if do_reload:
		reload( object )

	if hasattr( object, "USING_API" ):
		api_lvl = getattr( object, "USING_API", "0.0.0" )
		if type( api_lvl ) is str:
			in_levels = api_lvl.split( "." )
			ck_levels = check_api.split( "." )
			# Bad level count or first two levels mismatch, bail
			if len( in_levels ) < 3:
				return False
			if in_levels[0] != ck_levels[0] or in_levels[1] != ck_levels[1]:
				return False
			# Warn if our third level mismatches (minor changes)
			if in_levels[2] != ck_levels[2]:
				Warning( "API Check: the most current api is %s, please update to prevent issues!\n" % check_api )

			return True
		else:
			return False
	else:
		return False

def PrintError( msg ):
	GEUtil.Warning( msg )
	GEUtil.Warning( '----------------------------------------------------\n' )
	traceback.print_exc()
	GEUtil.Warning( '----------------------------------------------------\n' )

def GetModules( package ):
	pkgpath = os.path.dirname( package.__file__ )
	return [name for _, name, _ in pkgutil.iter_modules( [pkgpath] )]
