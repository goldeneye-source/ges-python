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
import GEAiCond, GEAiSched
from GEUtil import Warning
from GEAi import ISchedule, ICondition, ITask

class BaseCondition( ICondition ):
    pass

class BaseSchedule( ISchedule ):
    def __init__( self ):
        # Pass id of -1 since we receive an id when registered!
        ISchedule.__init__( self )

        self.tasks = []
        self.interrupts = []

    def __str__( self ):
        return "%s <%i>" % ( self.name, self.id_ )

    def Build( self ):
        raise NameError( "You must define a Build function!" )

    def Register( self, name ):
        # Reset ourselves
        self.tasks = []
        self.interrupts = []

        # Build the schedule tasks & interrupts
        self.Build()

        # Convert task data items as needed
        for task in self.tasks:
            if issubclass( task[1].__class__, ISchedule ):
                task[1] = task[1].id_
            else:
                try:
                    task[1] = float( task[1] )
                except:
                    pass

        # Call into C++ to register this schedule and receive an id
        ISchedule.Register( self, name )

    def AddTask( self, task, data=0 ):
        if isinstance( task, ITask ):
            self.tasks.append( [ task, data ] )
        else:
            Warning( "GEAi: Invalid task added to schedule %s!\n" % self.__class__.__name__ )

    def AddInterrupt( self, interrupt ):
        if isinstance( interrupt, ICondition ):
            self.interrupts.append( interrupt )
        else:
            Warning( "GEAi: Invalid interrupt added to schedule %s!\n" % self.__class__.__name__ )

    def GetTasks( self ):
        return self.tasks

    def GetInterrupts( self ):
        return self.interrupts


# Define the global conditions (interrupts)
class Cond( GEAiCond.Cond ):
    GES_CLOSE_TO_ARMOR	 = BaseCondition()
    GES_CLOSE_TO_WEAPON	 = BaseCondition()
    GES_CLOSE_TO_TOKEN	 = BaseCondition()
    GES_CAN_SEEK_ARMOR	 = BaseCondition()
    GES_HIGH_HEALTH		 = BaseCondition()
    GES_LOW_HEALTH 		 = BaseCondition()
    GES_ENEMY_UNARMED 	 = BaseCondition()
    GES_ENEMY_ARMED 	 = BaseCondition()
    GES_ENEMY_DANGEROUS	 = BaseCondition()
    GES_ENEMY_CLOSE 	 = BaseCondition()
    GES_ENEMY_FAR 		 = BaseCondition()
    GES_HIGH_ARMOR 		 = BaseCondition()
    GES_LOW_ARMOR 		 = BaseCondition()


# Define the global schedules
class Sched( GEAiSched.Sched ):
    import common as c

    _order = ["ESTABLISH_LINE_OF_FIRE", "COMBAT_FACE"]

    # Override HL2 schedules that misbehave (these are loaded FIRST)
    ESTABLISH_LINE_OF_FIRE = c.EstablishLOFFallback()
    COMBAT_FACE = c.CombatFaceOverride()

    # Bot specific schedules
    BOT_PATROL = c.BotPatrol()
    BOT_SEEK_ENEMY = c.BotSeekEnemy()
    BOT_ENGAGE_ENEMY = c.BotEngageEnemy()
    BOT_SEEK_WEAPON = c.BotSeekWeapon()
    BOT_SEEK_AMMO = c.BotSeekAmmo()
    BOT_SEEK_ARMOR = c.BotSeekArmor()
    BOT_SEEK_TOKEN = c.BotSeekToken()
