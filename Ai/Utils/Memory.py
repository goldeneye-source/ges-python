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
from Ai import PYBaseNPC
import GEEntity, GEPlayer, GEWeapon, GEUtil, GEGlobal, GEMPGameRules as GERules
from GEGlobal import EventHooks

# Memory types, these are assigned by analyzing the classname
# mainly used for quick associative mapping
( TYPE_NONE, TYPE_WEAPON, TYPE_AMMO, TYPE_ARMOR, TYPE_TOKEN, TYPE_CAPAREA, TYPE_PLAYER, TYPE_NPC ) = range( 8 )

# One of these should be returned with the memory callback
# PRIORITY_NONE  -> Do not store this memory
# PRIORITY_LOW   -> Store, and give it low weight
# PRIORITY_HIGH  -> Store, and give it high weight
# PRIORITY_ULTRA -> Never forget that we remembered this and give highest weight
( PRIORITY_NONE, PRIORITY_LOW, PRIORITY_HIGH, PRIORITY_ULTRA ) = ( 0, 10, 50, 100 )

#===============================================================================
# Memory class that stores a single memory instance
#===============================================================================
class Memory:
    FL_NONE		 = 0
    FL_ARMED	 = 1
    FL_ONGROUND	 = 2
    FL_OBJECTIVE = 4

    def __init__( self ):
        # Properties of the memory
        self.type = TYPE_NONE
        self.classname = ""

        self.hEnt = GEEntity.EntityHandle( None )
        self.location = GEUtil.Vector()
        self.team = GEGlobal.TEAM_NONE
        self.flags = Memory.FL_NONE
        self.data = 0

        # Desirability Inputs
        self.priority = PRIORITY_NONE
        self.time_lastrecord = 0
        self.time_expires = 0

        # Dynamic variables
        self._confidence = 0
        self._distance = 0

    def __str__( self ):
        return "Memory of %s (%.2f)" % ( self.classname, self.GetConfidence() )

    def AddFlag( self, flag ):
        self.flags |= flag

    def RemoveFlag( self, flag ):
        self.flags &= ~flag

    def HasFlag( self, flag ):
        return ( self.flags & flag ) == flag

    # Refresh a memory time, autocalculates the timers for you
    def Refresh( self ):
        self.time_lastrecord = GEUtil.GetTime()

        if self.priority < PRIORITY_ULTRA:
            if self.priority == PRIORITY_HIGH:
                self.time_expires = self.time_lastrecord + 120.0
            else:
                self.time_expires = self.time_lastrecord + 30.0
        else:
            self.time_expires = -1.0

    def GetConfidence( self ):
        # Confidence is a measure of how long it was since we last saw it
        # TODO: Do we want to salt the measurement based on type?

        if self.time_expires > 0:
            # Confidence of 0 means forget me
            self._confidence = max( 0, ( self.time_expires - GEUtil.GetTime() ) / ( self.time_expires - self.time_lastrecord ) )
        else:
            # If we never expire... we always have some confidence in our memory
            expires = self.time_lastrecord + 120.0
            self._confidence = max( 0.25, ( expires - GEUtil.GetTime() ) / ( 120.0 ) )

        return self._confidence

    def GetDesirability( self ):
        return self.GetConfidence() * self.priority


#===============================================================================
# MemoryManager class that controls our memories
#===============================================================================
class MemoryManager:
    TAG = "MemoryManager"
    DISCOVERY_EFFICIENCY = 0.5

    def __init__( self, parent, callback=None ):
        assert isinstance( parent, PYBaseNPC )
        if not isinstance( parent, PYBaseNPC ):
            raise TypeError( "Memory initialized on a non-NPC, aborting" )

        self._memories = {}
        self._npc = parent
        self._callback = callback
        self.debug = False
        self.next_discovery = 0

        # Register callback to do discovery automatically
        parent.RegisterEventHook( EventHooks.AI_ONLOOKED, self.PerformDiscovery )
        parent.RegisterEventHook( EventHooks.AI_GATHERCONDITIONS, self.AgeMemories )

    #===========================================================================
    # This uses the parent's current location to scan for
    # memories to add to our bucket
    #===========================================================================
    def PerformDiscovery( self, dist ):
        # Check for new items on our efficiency cycle
        if GEUtil.GetTime() >= self.next_discovery:
            seen = self._npc.GetSeenEntities()
            for ent in seen:
                assert isinstance( ent, GEEntity.CBaseEntity )

                ent_type = self._GetType( ent )
                mem = self._HasMemory( ent, ent_type )

                if not mem:
                    # First time we saw this entity, store a new memory
                    if self._callback:
                        priority, data = self._callback( ent )
                        if priority != PRIORITY_NONE:
                            self.AddMemory( ent, ent_type, priority, data )
                    elif not ent.GetPlayerOwner() and not ent.IsPlayer() and not ent.IsNPC():
                        self.AddMemory( ent, ent_type, PRIORITY_LOW )
                else:
                    # Refresh our existing memory
                    self.RefreshMemory( mem, ent )

            self.next_discovery = GEUtil.GetTime() + self.DISCOVERY_EFFICIENCY

    #===========================================================================
    # Ages memories by removing old ones
    #===========================================================================
    def AgeMemories( self ):
        now = GEUtil.GetTime()
        for mlist in self._memories.values():
            mlist[:] = [x for x in mlist if x.time_expires < 0 or now < x.time_expires]

    #===========================================================================
    # Remember various things (attributes) about the given entity
    # To make an infinite memory, use priority = PRIORITY_ULTRA
    #===========================================================================
    def AddMemory( self, ent, ent_type, priority, data=None ):
        assert isinstance( ent, GEEntity.CBaseEntity )

        mem = Memory()

        # Set the priority
        mem.priority = priority
        mem.data = data
        # Figure out our type classification
        mem.type = ent_type
        mem.classname = ent.GetClassname()

        # Refresh our crucial data
        self.RefreshMemory( mem, ent )

        # Finally, store this memory
        if ent_type not in self._memories:
            self._memories[ent_type] = []
        self._memories[ent_type].append( mem )

        self._spew( "Created new memory of %s (%d)" % ( self._transType( ent_type ), ent.GetUID() ) )

    def RefreshMemory( self, mem, ent ):
        assert isinstance( mem, Memory )
        assert isinstance( ent, GEEntity.CBaseEntity )

        mem.Refresh()

        mem.hEnt = GEEntity.EntityHandle( ent )
        mem.location = ent.GetAbsOrigin()
        mem.team = ent.GetTeamNumber()

        # Set player specific flags
        player = GEPlayer.ToCombatCharacter( ent )
        if player:
            weapon = GEWeapon.ToGEWeapon( player.GetActiveWeapon() )
            if weapon and weapon.GetWeaponId() != GEGlobal.WEAPON_SLAPPERS:
                mem.AddFlag( Memory.FL_ARMED )
            else:
                mem.RemoveFlag( Memory.FL_ARMED )

        # Set objective flag based on radar
        if GERules.GetRadar().IsObjective( ent ):
            mem.AddFlag( Memory.FL_OBJECTIVE )
        else:
            mem.RemoveFlag( Memory.FL_OBJECTIVE )

    def FindMemoriesByType( self, mem_type, min_confidence=0.2 ):
        # Troll through our memories and find ones of the given type and confidence
        memories = []

        if mem_type not in self._memories:
            return memories

        for item in self._memories[mem_type]:
            if item.GetConfidence() >= min_confidence:
                memories.append( item )

        # Sort memories by desirability (High to Low)
        f = lambda x, y: cmp( y.GetDesirability(), x.GetDesirability() )
        memories.sort( f )

        return memories

    def FindMemoriesNear( self, loc, mem_type, max_dist=512.0, min_confidence=0.2 ):
        # Troll through our memories and find ones of the given type, distance, and confidence
        memories = []

        if mem_type not in self._memories:
            return memories

        for item in self._memories[mem_type]:
            if item.GetConfidence() >= min_confidence:
                dist = loc.DistTo( item.location )
                if dist <= max_dist:
                    item._distance = dist
                    memories.append( item )

        # Sort memories by distance (Low to High)
        f = lambda x, y: cmp( x._distance, y._distance )
        memories.sort( f )

        return memories

    def DumpMemories( self ):
        print "----- NPC MEMORY DUMP -----"
        for m_type in self._memories.keys():
            print "%s:" % self._transType( m_type )

            for m in self._memories[m_type]:
                assert isinstance( m, Memory )
                print "   %d: %s, Desire: %f, %s, (%.1f, %.1f, %.1f)" % \
                ( m.hEnt.GetUID(), m.classname, m.GetDesirability(), self._transPriority( m.priority ),
                  m.location[0], m.location[1], m.location[2] )
        print "----- END DUMP -----"

    def _HasMemory( self, ent, ent_type ):
        # If we never saw this type we don't have it
        if ent_type not in self._memories:
            return None

        # Check all memories of this type to see if we may have seen this entity
        for m in self._memories[ent_type]:
            if self._IsSameMemory( m, ent ):
                return m

        return None

    def _IsSameMemory( self, memory, ent ):
        assert isinstance( memory, Memory )
        assert isinstance( ent, GEEntity.CBaseEntity )

        # UID's match, simple
        if memory.hEnt.GetUID() == ent.GetUID():
            return True

        # Classnames are different!
        if memory.classname != ent.GetClassname():
            return False

        ml = memory.location
        el = ent.GetAbsOrigin()

        # Check location similarities
        if  abs( ml[0] - el[0] ) < 10. and abs( ml[1] - el[1] ) < 10. and abs( ml[2] - el[2] ) < 10.:
            return True

        return False

    def _GetType( self, entity ):
        # TODO: Check for objective?
        classname = entity.GetClassname()
        if classname.startswith( "weapon_" ):
            # Make sure we are not really a token!
            if GERules.GetTokenMgr().IsValidToken( classname ):
                return TYPE_TOKEN
            else:
                return TYPE_WEAPON
        elif classname.startswith( "token_" ):
            return TYPE_TOKEN
        elif classname.startswith( "ge_ammocrate" ):
            return TYPE_AMMO
        elif classname.startswith( "item_armorvest" ):
            return TYPE_ARMOR
        elif classname.startswith( "ge_capturearea" ):
            return TYPE_CAPAREA
        elif entity.IsPlayer():
            return TYPE_PLAYER
        elif entity.IsNPC():
            return TYPE_NPC
        else:
            return TYPE_NONE

    def _transType( self, t ):
        if t == TYPE_AMMO:
            return "Ammo"
        elif t == TYPE_ARMOR:
            return "Armor"
        elif t == TYPE_NPC:
            return "NPCs"
        elif t == TYPE_PLAYER:
            return "Players"
        elif t == TYPE_WEAPON:
            return "Weapons"
        elif t == TYPE_TOKEN:
            return "Tokens"
        elif t == TYPE_CAPAREA:
            return "Capture Areas"
        else:
            return "Other / Misc"

    def _transPriority( self, p ):
        if p == PRIORITY_LOW:
            return "low priority"
        elif p == PRIORITY_HIGH:
            return "high priority"
        elif p == PRIORITY_ULTRA:
            return "ultra priority"
        else:
            return "no priority"

    def _spew( self, string ):
        if self.debug:
            print "[" + self.TAG + "] " + string

