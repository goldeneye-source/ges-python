import GEEntity, GEPlayer, GEUtil
from GEGlobal import EventHooks

# This is a persistent tracker for players that can
# store arbitrary data for each player in a key:value
# dictionary
class GEPlayerTracker:
	def __init__( self, parent ):
		self.Clear()
		parent.RegisterEventHook( EventHooks.GP_PLAYERCONNECT, self._Track )
		parent.RegisterEventHook( EventHooks.GP_PLAYERDISCONNECT, self._Drop )

	# Starts tracking a player's key/value pairs
	# tracking is done on the player's unique id
	# so that there is no chance of duplicates or
	# overwrites
	def _Track( self, player ):
		if player == None:
			return

		uid = GEEntity.GetUID( player )
		if uid in self.PlayerDict:
			return

		self.PlayerDict[uid] = {}

	# Drops a player that is being tracked
	def _Drop( self, player ):
		if player == None:
			return

		uid = GEEntity.GetUID( player )
		if uid not in self.PlayerDict:
			return

		del self.PlayerDict[uid]

	def Clear( self, player=None ):
		'''Forcibly clear the player list, you will have to manually re-register players!'''
		if not player:
			self.PlayerDict = {}
		else:
			uid = GEEntity.GetUID( player )
			if uid in self.PlayerDict:
				self.PlayerDict[uid] = {}

	def __len__( self ):
		return len( self.PlayerDict )

	def __iter__( self ):
		return self.PlayerDict.__iter__()

	def __getitem__( self, player_or_uid ):
		if not player_or_uid:
			return None

		try:
			if type( player_or_uid ) is int:
					return self.PlayerDict.get( player_or_uid )
			else:
				uid = GEEntity.GetUID( player_or_uid )
				return self.PlayerDict.get( uid )
		except:
			raise KeyError( "Invalid player passed to GEPlayerTracker!" )

	def __setitem__( self, key, value ):
		raise NameError( "Cannot set the value of a player entry directly!" )

	# Returns the value of the player's tracked key
	def GetValue( self, player, key, default=None ):
		'''Get a value for the supplied player and key'''
		try:
			return self[player][key]
		except ( KeyError, TypeError ):
			return default

	# Set's a key/value pair for a player
	# if the player is not already tracked this
	# will also start tracking them
	def SetValue( self, player, key, value ):
		'''Set a value for the supplied player and key'''
		try:
			self[player][key] = value
		except KeyError:
			self._Track( player )
			self[player][key] = value

	# Sets the specified key value on all tracked players
	def SetValueAll( self, key, value ):
		'''Sets the supplied key/value pair on all tracked players'''
		for uid in self.PlayerDict.keys():
			self.PlayerDict[uid][key] = value

	def CountValues( self, key, value ):
		'''Count the number of tracked players that have the supplied key/value pair'''
		count = 0
		for plr in self.PlayerDict.values():
			try:
				if plr[key] == value:
					count += 1
			except KeyError:
				pass
		return count

	def GetPlayers( self, key=None, value=None ):
		'''Returns a list of tracked players sliced by any supplied key and value combo'''
		players = []
		for player, item in self.PlayerDict.items():
			# Convert to a valid player instance
			player = GEPlayer.ToMPPlayer( player )
			if not player:
				continue

			# If we supplied a key check that this entry has it
			if key and key in item:
				# If we supplied a value, check that we have this value
				if value and item[key] == value:
					players.append( player )
				elif not value:
					players.append( player )
			elif not key:
				players.append( player )

		return players

	# Prints out a listing of data to the console
	def DumpData( self ):
		'''Dumps the data contained in the tracker to the console (for debugging)'''
		print "------- Player Tracker Dump ------"
		for uid in self.PlayerDict.keys():
			player = GEPlayer.ToMPPlayer( uid )
			print "%s:" % player.GetCleanPlayerName()
			for key, value in self.PlayerDict[uid].items():
				print "  %s => %s" % ( key, value )
		print "------- End Dump ------"
