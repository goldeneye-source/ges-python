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
import GEPlayer, GEGlobal as Glb

# Common functions for use in scenarios

def choice( expr, if_true, if_false ):
	'''Choose between two values based on true/false evaluation'''
	return if_true if expr else if_false

def clamp( val, min_val, max_val ):
	'''Clamp a value between min_val and max_val'''
	if val > max_val:
		return max_val
	elif val < min_val:
		return min_val
	return val

def _( localizer, *args ):
	'''
	Advanced localization helper function. Combines the arguments provided
	with the localizer generating a proper advanced localization string.
	
	Ex:
	from .Utils import _
	_( "#GES_GP_CTK_DEFENDED", clr_hint, killer.GetCleanPlayerName(), token_name )
	
	>> #GES_GP_CTK_DEFENDED\r^b\rKiller Monkey\rKey
	
	@type localizer: str ("#LOCALIZE_TOKEN")
	@type *args: additional arguments
	'''
	args = [str( x ) for x in args]
	return localizer + "\r".join( args )

def lcat( localizer, *args ):
	'''If you don't like using _, use lcat!'''
	return _( localizer, args )

def plural( count, localizer, p="_P" ):
	'''Pluralize localized strings. Localizer must start with a '#'.'''
	'''Add advanced localization to the end with additions: '\r%i' % my_int'''
	return choice( count == 1, localizer, localizer + p )

def plural2( count, singular, plural ):
	'''Chooses singular or plural based on the count'''
	return choice( count == 1, singular, plural )

def GetPlayers():
	'''Return a list of players in the game'''
	plrs = []
	for i in range( 32 ):
		player = GEPlayer.GetMPPlayer( i )
		if player:
			plrs.append( player )
	return plrs

def OppositeTeam( team ):
	'''Get the opposite team'''
	if team == Glb.TEAM_NONE:
		return Glb.TEAM_NONE
	return Glb.TEAM_MI6 if ( team == Glb.TEAM_JANUS ) else Glb.TEAM_JANUS
