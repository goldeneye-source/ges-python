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
from GESFuncs  import *
from GEGlobal import PY_BASE_DIR
import sys
import GEAi, GEUtil
import Ai

class PYAiManager( GEAi.CAiManager ):
	def __init__( self ):
		super( PYAiManager, self ).__init__()
		self.ClearSchedules()

		import reimport
		reimport.reimport( Ai )

	def CreateNPC( self, ident, parent ):
		tmp = FindModule( Ai, ident )
		if not tmp:
			GEUtil.DevWarning( "Failed to find npc %s!\n" % ident )
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
					GEUtil.Warning( "Ai load FAILED due to API mismatch.\n" )
					return None

				# Load any custom schedules defined by the npc
				self.LoadSchedules( npc )

			return npc

	def ClearSchedules( self ):
		RemoveCompiled( "%s\\Ai\\Schedules\\*" % ( PY_BASE_DIR ) )
		RemoveCompiled( "%s\\Ai\\Tasks\\*" % ( PY_BASE_DIR ) )
		RemoveCompiled( "%s\\Ai\\Utils\\*" % ( PY_BASE_DIR ) )

	def LoadSchedules( self, npc=None ):
		import traceback
		import Ai.Tasks, Ai.Schedules

		if not npc:
			print "Loading Python Ai Tasks and Schedules..."

		# Resolve all our classes and modules up-front for simplicity
		if npc:
			task_class = npc._cust_tasks
			sched_class = npc._cust_sched
			cond_class = npc._cust_cond
		else:
			task_class = Ai.Tasks.Task
			sched_class = Ai.Schedules.Sched
			cond_class = Ai.Schedules.Cond

		# Load tasks registered in Ai.Tasks.Task or the passed NPC
		items = task_class.__dict__.items() if task_class else []
		for name, task in items:
			try:
				if issubclass( task.__class__, Ai.Tasks.BaseTask ):
					GEUtil.DevMsg( "Registering Task: %s\n" % name )
					task.Register( name )
			except:
				GEUtil.Warning( "Failed to register task: %s\n" % name )
				print traceback.print_exc( file=sys.stderr )

		# Load in conditions defined in Ai.Schedules.Cond or the passed NPC
		items = cond_class.__dict__.items() if cond_class else []
		for name, cond in items:
			try:
				if issubclass( cond.__class__, Ai.Schedules.BaseCondition ):
					GEUtil.DevMsg( "Registering Condition: %s\n" % name )
					cond.Register( name )
			except:
				GEUtil.Warning( "Failed to register condition: %s\n" % name )
				print traceback.print_exc( file=sys.stderr )

		# Load in schedules defined in Ai.Schedules.Sched or the passed NPC
		items = []
		if sched_class:
			load_order = getattr( sched_class, "_order", None )
			if load_order and type( load_order ) is list:
				for x in load_order:
					if hasattr( sched_class, x ):
						items.append( ( x, getattr( sched_class, x ) ) )
			items.extend( sched_class.__dict__.items() )

		for name, sched in items:
			try:
				if issubclass( sched.__class__, Ai.Schedules.BaseSchedule ):
					GEUtil.DevMsg( "Registering schedule: %s\n" % name )
					sched.Register( name )
			except:
				GEUtil.Warning( "Failed to register schedule: %s\n" % name )
				print traceback.print_exc( file=sys.stderr )

pyAiMangObj = None

def GetManager():
	global pyAiMangObj

	if not pyAiMangObj:
		pyAiMangObj = PYAiManager()

	return pyAiMangObj

def PurgeManager():
	global pyAiMangObj
	pyAiMangObj = None
