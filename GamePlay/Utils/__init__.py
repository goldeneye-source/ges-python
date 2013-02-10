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

def plural( count, localizer, additions="", p="_P" ):
	'''Pluralize localized strings. Localizer must start with a '#'.'''
	'''Add advanced localization to the end with additions: '\r%i' % my_int'''
	return choice( count == 1, localizer + additions, localizer + p + additions )

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
