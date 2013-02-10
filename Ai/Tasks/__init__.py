import GEUtil, GEAiTasks

class Task( GEAiTasks.Task ):
	_module			 	 = "Ai.Tasks.CommonTasks"

	GES_FIND_ENEMY 		 = "FindEnemy"
	GES_FIND_AMMO 		 = "FindAmmo"
	GES_FIND_WEAPON 	 = "FindWeapon"
	GES_FIND_ARMOR 		 = "FindArmor"
	GES_FIND_TOKEN	 	 = "FindToken"

class TaskFail( GEAiTasks.TaskFail ):
	# This does nothing, it's a placeholder
	pass

# This dict holds the registered tasks during startup in AiManager
# the NPC will try to find a custom task in here to start/run it when
# they have a schedule that asks for one
TASK_OBJS = {}

def ClearTasks():
	global TASK_OBJS
	TASK_OBJS = {}

class PYTask:
	def __init__( self ):
		self.name = self.__class__.__name__
		self.id = -1

	def __str__( self ):
		return self.GetName()

	def SetId( self, id_ ):
		if self.id == -1:
			self.id = id_
		else:
			GEUtil.Warning( "Task ID already set for %s!\n" % self.name )

	def GetId( self ):
		return self.id

	def GetName( self ):
		return self.name

	def Start( self, npc, data ):
		raise NameError

	def Run( self, npc, data ):
		self.Complete( npc )

	def Complete( self, npc ):
		npc.TaskComplete()

	def Fail( self, npc, reason ):
		npc.TaskFail( reason )
