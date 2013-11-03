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
import GEEntity, GEPlayer, GEUtil, GEWeapon, GEAiConst, GEAiSched

def HintFlags( token_string ):
    '''Convert a hint flag name to it's ID'''
    return int

def ActivityId( activity ):
    '''Convert an activity name to it's ID'''
    return int

def ScheduleID( name ):
    '''Convert a schedule name to it's ID'''
    return int

def TaskID( name ):
    '''Convert a task name to it's ID'''
    return int

def ConditionID( name ):
    '''Convert a condition name to it's ID'''
    return int

class CNPC_GEBase( GEPlayer.CBaseCombatCharacter ):
    '''Placeholder, not used'''

class CBaseNPC:
    def __init__( self, parent ):
        '''Initialize this NPC with a CNPC_GEBase parent'''

    def GetNPC( self ):
        '''
        Returns the actual NPC instance this was initialized with.
        '''
        return CNPC_GEBase

    def GetPlayer( self ):
        '''
        If this NPC is a bot, it will be associated with a player
        instance. This returns that player instance so that you can
        check things like score, model, etc.
        '''
        return GEPlayer.CGEBotPlayer

    def GetSeenEntities( self ):
        return [GEEntity.CBaseEntity]

    def GetHeardSounds( self ):
        return [GEUtil.CSound]

    def GetHeldWeapons( self ):
        return [GEWeapon.CGEWeapon]

    def GetHeldWeaponIds( self ):
        return [int]

    def Say( self, msg ):
        '''Say something to the chat'''

    def SayTeam( self, msg ):
        '''Say something to my team'''

    # Pass-Through functions (to CNPC_GEBase)
    def HasWeapon( self, weapon ):
        '''
        Check if the NPC has the weapon in question.
        You can pass in a valid weapon id, weapon classname, 
        or weapon entity
        
        weapon -- Weapon ID, Name, or Instance (GEWeapon.CGEWeapon)
        '''
        return bool

    def GiveWeapon( self, classname ):
        return GEWeapon.CGEWeapon

    def GiveAmmo( self, amount, ammo_name ):
        '''Give ammo to this NPC of the given amount and type.'''

    def GetAmmoCount( self, ammo_name ):
        '''Get the ammo count for the given type.'''
        return int

    def GetMaxAmmoCount( self, ammo_name ):
        '''Get the maximum ammo count for the given type.'''
        return int

    def GetMaxHealth( self ):
        return int

    def GetArmor( self ):
        return int

    def GetMaxArmor( self ):
        return int

    def SetArmor( self, armor_value ):
        '''Set the armor value to the given amount'''

    def GetEnemy( self ):
        return GEEntity.CBaseEntity

    def SetTarget( self, target_ent ):
        '''
        Set the current target entity for this NPC.

        target_ent -- Target Entity (GEEntity.CBaseEntity)
        '''

    def SetTargetPos( self, target_pos ):
        '''
        Set the current target position for this NPC.

        target_pos -- Target Position (GEUtil.Vector)
        '''

    def GetTarget( self ):
        '''Get the current target entity for this NPC.'''
        return GEEntity.CBaseEntity

    def FindWeapon( self, range_vector ):
        '''
        Find the closest weapon within the given range from this NPC.
        The range vector forms a box centered on this NPC:
            rect( this.GetAbsOrigin() - range_vector, this.GetAbsOrigin() + range_vector )

        range_vector -- Radial distance from this NPC to search (GEUtil.Vector)
        '''
        return GEWeapon.CGEWeapon

    def AddCapabilities( self, capability ):
        ''' Add the given capability to this NPC.'''

    def HasCapability( self, capability ):
        '''Check if the NPC has the given capability.'''
        return bool

    def RemoveCapabilities( self, capability ):
        '''Remove the given capability from this NPC.'''

    def ClearCapabilities( self ):
        '''Clear all capabilities from this NPC.'''

    def AddRelationship( self, entity, disposition, priority ):
        '''
        Add a relationship to the given entity.

        Arguments:
        entity -- The entity to set a relationship with (GEEntity.CBaseEntity)
        disposition -- The type of relationship (GEAiConst.Disposition)
        priority -- A numerical priority ranking for this relationship (int)
        '''

    def GetRelationship( self, entity ):
        '''Get the current relationship with the given entity.'''
        return GEAiConst.Disposition

    def RemoveRelationship( self, entity ):
        '''Remove all relationships with the given entity.'''

    def AddClassRelationship( self, entity_class, disposition, priority ):
        '''
        Add a relationship with a class of entities.

        Arguments:
        entity_class -- The entity class to have a relationship with (GEAiConst.Class)
        disposition -- The type of relationship (GEAiConst.Disposition)
        priority -- A numerical priority ranking for this relationship (int)
        '''

    def SetCondition( self, condition ):
        '''Set a defined condition on this NPC'''

    def HasCondition( self, condition ):
        '''Check if this NPC has the defined condition'''
        return bool

    def ClearCondition( self, condition ):
        '''Clear the defined condition from this NPC'''

    def SetSchedule( self, schedule ):
        '''
        Force the NPC to use the given schedule. This will instantly override
        any schedule previously chosen for this NPC.

        Returns true if the schedule was set.
        '''
        return bool

    def ClearSchedule( self ):
        '''Clear the current schedule from this NPC; forces a new selection.'''

    def GetState( self ):
        '''Get the current state of this NPC.'''
        return GEAiConst.State

    def Remember( self, memory ):
        '''Store a memory defined in GEAiCont.Memory'''

    def Forget( self, memory ):
        '''Forget a memory defined in GEAiCont.Memory'''

    def HasMemory( self, memory ):
        '''Check if this NPC has a memory from GEAiConst.Memory'''
        return bool

    def TaskComplete( self, ignore_task_failed_condition ):
        '''
        Set the current task as "complete" which moves this NPC to it's next task.

        ignore_task_failed_condition -- Ignore a failed condition; force completion (bool)
        '''

    def TaskFail( self, fail_code ):
        '''
        Fail the current task with the provided failure code.

        fail_code -- GEAiTasks.TaskFail or string
        '''

    def GetTeamNumber( self ):
        '''Get this NPC's team number.'''
        return int

    def IsSelected( self ):
        '''Useful for debugging ONLY, tells you if this NPC is selected using `npc_select`'''
        return bool

class ISchedule:
    name = str
    id_ = int
    
    def __init__( self ):
        pass

    def Register( self, sched_name ):
        '''Registers this schedule with the Ai System.'''
        
class ITask:
    name = str
    id_ = int
    
    def __init__( self ):
        pass

    def Register( self, task_name ):
        '''Registers this task with the Ai System.'''

class ICondition:
    name = str
    id_ = int
    
    def __init__( self ):
        pass

    def Register( self, cond_name ):
        '''Registers this condition (interrupt) with the Ai System.'''

class CAiManager:
    def __init__( self ):
        pass

