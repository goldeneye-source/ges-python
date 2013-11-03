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
import GEEntity, GEPlayer, GEUtil
from GEGlobal import EventHooks

# This is a persistent tracker for players that can
# store arbitrary data for each player in a key:value
# dictionary
class GEPlayerTracker:
    def __init__( self, parent ):
        if not hasattr( parent, 'RegisterEventHook' ):
            raise AttributeError( "Parent must be a Gameplay Scenario type!" )

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
        if uid in self._players:
            return

        self._players[uid] = {}

    # Drops a player that is being tracked
    def _Drop( self, player ):
        if player == None:
            return

        uid = GEEntity.GetUID( player )
        if uid not in self._players:
            return

        del self._players[uid]

    def Clear( self, player=None ):
        '''Forcibly clear the player list, you will have to manually re-register players!'''
        if not player:
            self._players = {}
        else:
            uid = GEEntity.GetUID( player )
            if uid in self._players:
                self._players[uid] = {}

    def __len__( self ):
        return len( self._players )

    def __iter__( self ):
        return self._players.__iter__()

    def __getitem__( self, player_or_uid ):
        if not player_or_uid:
            return None

        try:
            uid = player_or_uid
            if type( uid ) is not int:
                uid = GEEntity.GetUID( uid )
            return self._players[ uid ]
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
        for uid in self._players.keys():
            self._players[uid][key] = value

    def CountValues( self, key, value ):
        '''Count the number of tracked players that have the supplied key/value pair'''
        count = 0
        for plr in self._players.values():
            try:
                if plr[key] == value:
                    count += 1
            except KeyError:
                pass
        return count

    def GetPlayers( self, key=None, value=None ):
        '''Returns a generator of players sliced by any supplied key and value combo'''
        for uid, item in self._players.items():
            # Convert to a valid player instance
            player = GEPlayer.ToMPPlayer( uid )
            if not player:
                continue

            # If we supplied a key check that this entry has it
            if key and key in item:
                # If we supplied a value, check that we have this value
                if not value or ( value and item[key] == value ):
                    yield player
            elif not key:
                yield player

    def Slice( self, key, filter_cb=None ):
        '''Returns a generator of tuples with the player and their value for the supplied key'''
        '''condition_cb can be set to a function that accepts the player's dict in order to filter returns'''
        if not key:
            raise AttributeError( "key cannot be None!" )

        for uid, item in self._players.items():
            # Convert to a valid player instance
            player = GEPlayer.ToMPPlayer( uid )
            if player:
                if not filter_cb or filter_cb( item ):
                    yield ( player, item.get( key, None ) )

    # Prints out a listing of data to the console
    def DumpData( self ):
        '''Dumps the data contained in the tracker to the console (for debugging)'''
        print "------- Player Tracker Dump ------"
        for uid in self._players.keys():
            player = GEPlayer.ToMPPlayer( uid )
            print "%s:" % player.GetCleanPlayerName()
            for key, value in self._players[uid].items():
                print "  %s => %s" % ( key, value )
        print "------- End Dump ------"
