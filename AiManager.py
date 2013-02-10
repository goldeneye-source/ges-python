from GESFuncs  import *
from GEGlobal import PY_BASE_DIR
import sys, reimport
import GEAi
import Ai, Ai.Schedules, Ai.Tasks, Ai.Utils

class PYAiManager( GEAi.CAiManager ):
	def __init__( self ):
		super( PYAiManager, self ).__init__()
		self.ClearSchedules()
		reimport.reimport( Ai )

	def __del__( self ):
		self.ClearSchedules()

	def CreateNPC( self, ident, parent ):
		tmp = FindModule( Ai, ident )
		if not tmp:
			GEUtil.Warning( "Failed to find npc %s!\n" % ident )
			return None
		else:
			ident = tmp
			module = "Ai.%s" % ident
			npc = None

			try:
				# Try to load immediately, fallback to import if new class
				npc = getattr( sys.modules[module], ident )( parent )
				print "Loading NPC %s from cache" % ident
			except KeyError:
				try:
					RemoveCompiled( "%s\\Ai\\%s" % ( PY_BASE_DIR, ident ) )

					__import__( module, globals(), locals() )

					npc = getattr( sys.modules[module], ident )( parent )

					print "Loading NPC %s from disk" % ident

				except ImportError:
					PrintError( "Failed to load NPC %s\n" % ident )

			if npc:
				# Make sure we are using the proper API!
				if not CheckAPI( sys.modules[module], GEGlobal.API_AI_VERSION ):
					GEUtil.Warning( "Ai load FAILED due to API mismatch. Did you define USING_API?\n" )
					return None

				# Load any custom schedules defined by the npc
				self.LoadSchedules( npc )

			return npc

	def ClearSchedules( self ):
		Ai.Tasks.ClearTasks()

		RemoveCompiled( "%s\\Ai\\Schedules\\*" % ( PY_BASE_DIR ) )
		RemoveCompiled( "%s\\Ai\\Tasks\\*" % ( PY_BASE_DIR ) )
		RemoveCompiled( "%s\\Ai\\Utils\\*" % ( PY_BASE_DIR ) )

	def LoadSchedules( self, npc=None ):
		if not npc:
			print "Loading Python Ai Tasks and Schedules..."

		# Resolve all our classes and modules up-front for simplicity
		if npc:
			task_class = npc._cust_tasks
			sched_class = npc._cust_sched
			cond_class = npc._cust_cond

			if task_class and "_module" in task_class.__dict__:
				task_module = task_class.__dict__["_module"]
			else:
				task_module = npc.__module__

			if sched_class and "_module" in sched_class.__dict__:
				sched_module = sched_class.__dict__["_module"]
			else:
				sched_module = npc.__module__
		else:
			task_class = Ai.Tasks.Task
			sched_class = Ai.Schedules.Sched
			cond_class = Ai.Schedules.Cond

			task_module = task_class.__dict__["_module"]
			sched_module = sched_class.__dict__["_module"]

		if task_module not in sys.modules:
			__import__( task_module, globals(), locals() )

		if sched_module not in sys.modules:
			__import__( sched_module, globals(), locals() )

		# Load tasks registered in Ai.Tasks.Task or the passed NPC
		items = task_class.__dict__.items() if task_class else []
		for task, value in items:
			if type( value ) is str and not task.startswith( "_" ):
				try:
					obj = getattr( sys.modules[task_module], value )
					if issubclass( obj, Ai.Tasks.PYTask ):
						t = obj()
						id_ = self.RegisterTask( "TASK_" + task )
						if id_ != -1:
							# Store the ID internally with the task
							t.SetId( id_ )
							# Link the ID with the Task class
							setattr( task_class, task, id_ )
							# Store the task object for retrieval by the NPC
							Ai.Tasks.TASK_OBJS[id_] = obj
					else:
						setattr( task_class, task, Ai.Tasks.Task.INVALID )
						GEUtil.Warning( "Failed to create task `%s` because %s.%s must inherit Ai.Tasks.PYTask!\n" % ( task, task_module, value ) )
				except AttributeError:
					setattr( task_class, task, Ai.Tasks.Task.INVALID )
					PrintError( "Failed to create task `%s` because %s.%s is not defined!\n" % ( task, task_module, value ) )

		# Load in conditions defined in Ai.Schedules.Cond or the passed NPC
		items = cond_class.__dict__.items() if cond_class else []
		for cond, value in items:
			if value is None and not cond.startswith( "_" ):
				id_ = self.RegisterCondition( "COND_" + cond )
				if id_ != -1:
					# Link the ID with the Cond class
					setattr( cond_class, cond, id_ )
				else:
					setattr( cond_class, cond, Ai.Schedules.Cond.NONE )
					GEUtil.Warning( "Failed to create condition %s\n" % cond )

		# Load in schedules defined in Ai.Schedules.Sched or the passed NPC
		items = []
		if sched_class:
			load_order = getattr( sched_class, "_order", None )
			if load_order and type( load_order ) is list:
				for x in load_order:
					if hasattr( sched_class, x ):
						items.append( ( x, getattr( sched_class, x ) ) )
			items.extend( sched_class.__dict__.items() )

		for sched, value in items:
			if type( value ) is str and not sched.startswith( "_" ):
				print "Trying to convert schedule %s..." % value
				try:
					obj = getattr( sys.modules[sched_module], value )
					if issubclass( obj, Ai.Schedules.PYSchedule ):
						s = obj()
						s.name = "SCHED_" + sched
						id_ = self.RegisterSchedule( s )
						if id_ != -1:
							# Link the ID with the Sched class
							setattr( sched_class, sched, id_ )
					else:
						setattr( sched_class, sched, Ai.Schedules.Sched.NO_SELECTION )
						GEUtil.Warning( "Failed to create schedule `%s` because %s.%s must inherit Ai.Schedules.PySchedule!\n" % ( sched, sched_module, value ) )
				except AttributeError:
					setattr( sched_class, sched, Ai.Schedules.Sched.NO_SELECTION )
					PrintError( "Failed to create schedule `%s` because %s.%s is not defined!\n" % ( sched, sched_module, value ) )

pyAiMangObj = None

def GetAiManager():
	global pyAiMangObj

	if not pyAiMangObj:
		pyAiMangObj = PYAiManager()

	return pyAiMangObj

def PurgeAiManager():
	global pyAiMangObj
	pyAiMangObj = None

# If imported directly, attempt to create the AiManager
if __name__ == '__main__':
	GetAiManager()
