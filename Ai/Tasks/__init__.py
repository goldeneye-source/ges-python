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
import GEUtil, GEAiTasks
from GEAi import ITask

class BaseTask( ITask ):
    def __str__( self ):
        return "%s <%i>" % ( self.name, self.id_ )

    def Register( self, name ):
        ITask.Register( self, name )
        Task.RegisterTask( self )

    def Start( self, npc, data ):
        raise NameError( "You must define a Start function!" )

    def Run( self, npc, data ):
        # Default behavior is to end the task on the run phase
        self.Complete( npc )

    def Complete( self, npc ):
        npc.TaskComplete()

    def Fail( self, npc, reason ):
        npc.TaskFail( reason )

class Task( GEAiTasks.Task ):
    import common as c

    GES_FIND_ENEMY = c.FindEnemy()
    GES_FIND_AMMO = c.FindAmmo()
    GES_FIND_WEAPON = c.FindWeapon()
    GES_FIND_ARMOR = c.FindArmor()
    GES_FIND_TOKEN = c.FindToken()

    registered_tasks = {}

    @classmethod
    def RegisterTask( cls, task ):
        if hasattr( task, "id_" ):
            cls.registered_tasks[ task.id_ ] = task

    @classmethod
    def GetTask( cls, id_ ):
        if id_ in cls.registered_tasks:
            return cls.registered_tasks[ id_ ]
        return None

class TaskFail( GEAiTasks.TaskFail ):
    # This does nothing, it's a placeholder
    pass


