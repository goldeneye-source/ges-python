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
	import CommonTasks as c

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


