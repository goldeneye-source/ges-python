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
from GEAiConst import Capability as Cap, State
from .Schedules import Sched, Cond
from .Tasks import Task
import GEAi, GEUtil

class AiSystems:
    MEMORY 	 = "memory"
    WEAPONS = "weapons"

class PYBaseNPC( GEAi.CBaseNPC ):

    def __init__( self, parent ):
        super( PYBaseNPC, self ).__init__( parent )
        # Private Variables
        self.__parent = parent
        self.__currTask = None

        self._cust_tasks = None
        self._cust_sched = None
        self._cust_cond = None

        self._token_target = None
        self._token_team = None

        self.ClearSystems()
        self.ClearEventHooks()

        # Default register Weapon and Memory systems
        self.RegisterSystem( AiSystems.WEAPONS, Weapons.WeaponManager( self ) )
        self.RegisterSystem( AiSystems.MEMORY, Memory.MemoryManager( self ) )

        # Default capabilities
        self.ClearCapabilities()
        self.AddCapabilities( Cap.MOVE_GROUND | Cap.MOVE_JUMP | Cap.MOVE_CLIMB | Cap.TURN_HEAD | Cap.AIM_GUN | Cap.USE | Cap.DUCK | Cap.USE_DOORS )

    def __del__( self ):
        # Uncomment this to confirm that your python npcs are being deleted properly!
        #GEUtil.Warning( "PYBaseNPC deleted!\n" )
        pass

    def Cleanup( self ):
        self.__currTask = None
        self.__parent = None
        self.ClearSystems()
        self.ClearEventHooks()

    # You shouldn't call these functions directly or override them
    def RegisterEventHook( self, hook, func ):
        if not self.__hooks.has_key( hook ):
            self.__hooks[hook] = []

        # Make sure we don't double register
        if self.__hooks[hook].count( func ) == 0:
            self.__hooks[hook].append( func )

    def CallEventHooks( self, hook, args=() ):
        if self.__hooks.has_key( hook ):
            for h in self.__hooks[hook]:
                h( *args )

    def ClearEventHooks( self ):
        self.__hooks = {}

    # Ai System functions
    def RegisterSystem( self, name, system ):
        if name in self.__systems:
            print "Warning: Ai System " + name + " has been overridden!"
        self.__systems[name] = system
        return system

    def GetSystem( self, name ):
        if name in self.__systems:
            return self.__systems[name]
        return None

    def ClearSystems( self ):
        self.__systems = {}

    def GetTokenTarget( self ):
        return self._token_target

    def GetTokenTeam( self ):
        return self._token_team

    def SetTokenTarget( self, classname, team=None ):
        if type( classname ) is str or not classname:
            self._token_target = classname
            self._token_team = team
        else:
            raise TypeError( "classname must be a string type" )

    def SetCustomSchedules( self, sched_class ):
        '''
        sched_class must inherit Ai.Schedules.Sched
        Example: self.SetCustomSchedules( MWGG_Sched )
        '''
        self._cust_sched = sched_class

    def SetCustomConditions( self, cond_class ):
        '''
        sched_class must inherit Ai.Schedules.Cond
        '''
        self._cust_cond = cond_class

    def SetCustomTasks( self, task_class ):
        '''
        sched_class must inherit Ai.Tasks.Task
        '''
        self._cust_sched = task_class
    # End restrictions



    def GetModel( self ):
        raise NameError

    def Classify( self ):
        raise NameError

    def OnSpawn( self ):
        pass

    def OnSetDifficulty( self, level ):
        pass

    def OnLooked( self, dist ):
        pass

    def OnListened( self ):
        pass

    def IsValidEnemy( self, enemy ):
        return True

    def GatherConditions( self ):
        # Do base check of conditions here common to all GE NPCs
        pass

    def SelectIdealState( self ):
        return State.NO_SELECTION

    def SelectSchedule( self ):
        return Sched.NO_SELECTION

    def TranslateSchedule( self, schedule ):
        return Sched.NO_SELECTION

    def ShouldInterruptSchedule( self, schedule ):
        return False

    def StartTask( self, taskID, taskData ):
        return False

    def RunTask( self, taskID, taskData ):
        return False

    def OnDebugCommand( self, command ):
        print "GE Ai: Command not recognized `%s`" % command

    # ----------------------------------- #
    # Private Functions - DO NOT OVERRIDE #
    # ----------------------------------- #
    def CheckStartTask( self, task_id, task_data ):
        # Pass the task to the Ai for custom handling
        ret = self.StartTask( task_id, task_data )

        if ret == False:
            # The Ai didn't want to handle it
            try:
                self.__currTask = Task.GetTask( task_id )
                self.__currTask.Start( self, task_data )
                return True
            except:
                self.__currTask = None

        # Pass back to C++
        return ret

    def CheckRunTask( self, taskID, taskData ):
        ret = self.RunTask( taskID, taskData )

        if ret == False and self.__currTask is not None:
            self.__currTask.Run( self, taskData )
            return True

        return ret

    # ---------------------------------------- #
    # Pass-Through Functions - DO NOT OVERRIDE #
    # ---------------------------------------- #
    # CBaseCombatCharacter
    def GetAbsOrigin( self ):
        return self.__parent.GetAbsOrigin()

    def GetHealth( self ):
        return self.__parent.GetHealth()

    def SetHealth( self, health ):
        self.__parent.SetHealth( health )

    def GetActiveWeapon( self ):
        return self.__parent.GetActiveWeapon()

    def WeaponSwitch( self, weapon ):
        return self.__parent.WeaponSwitch( weapon )

    # CNPC_GEBase
    def TaskComplete( self, ignoreFailedCond=False ):
        super( PYBaseNPC, self ).TaskComplete( ignoreFailedCond )
        self.__currTask = None

    def TaskFail( self, fail_code ):
        super( PYBaseNPC, self ).TaskFail( fail_code )
        self.__currTask = None

from Ai.Utils import Memory, Weapons
