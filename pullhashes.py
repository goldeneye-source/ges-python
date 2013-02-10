import os
from hashlib import md5

dir = "./GamePlay/"
ignore = [ '__init__.py', 'TokenSpawnTest.py' ]

f = open( "gphashes.txt", "w" )
f.write( "\"Hashes\"\n{\n" )

for fn in os.listdir( dir ):
	if fn.endswith( '.py' ) and fn not in ignore:
		m = md5( open( dir + fn, "rb" ).read() )
		f.write( "\t\"hash\"\t\"%s\"\t//%s\n" % ( m.hexdigest(), fn ) )

f.write( "}" )
f.close()
