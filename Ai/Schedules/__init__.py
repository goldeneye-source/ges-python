# # NOTE: This must be first to prevent circular imports
class ISchedule( object ):
	def __init__( self, name=None, id_= -1 ):
		self.name = name or self.__name__
		self.id_ = int( id_ )
		self.tasks = []
		self.interrupts = []

	def __str__( self ):
		return "%s <%i>" % ( self.name, self.id_ )

	def AddTask( self, task, data=0 ):
		self.tasks.append( [int( task ), float( data )] )

	def AddInterrupt( self, interrupt ):
		self.interrupts.append( int( interrupt ) )

	def GetTasks( self ):
		return self.tasks

	def GetInterrupts( self ):
		return self.interrupts

# Import our definitions
import GEAiCond, GEAiSched

# Define the global conditions (interrupts)
class Cond( GEAiCond.Cond ):
	GES_CLOSE_TO_ARMOR	 = None
	GES_CLOSE_TO_WEAPON	 = None
	GES_CLOSE_TO_TOKEN	 = None
	GES_CAN_SEEK_ARMOR	 = None
	GES_HIGH_HEALTH		 = None
	GES_LOW_HEALTH 		 = None
	GES_ENEMY_UNARMED 	 = None
	GES_ENEMY_ARMED 	 = None
	GES_ENEMY_DANGEROUS	 = None
	GES_ENEMY_CLOSE 	 = None
	GES_ENEMY_FAR 		 = None
	GES_HIGH_ARMOR 		 = None
	GES_LOW_ARMOR 		 = None

# Define the global schedules
class Sched( GEAiSched.Sched ):
	_module		 	 	 = "Ai.Schedules.CommonSchedules"
	_order			 	 = [ "ESTABLISH_LINE_OF_FIRE", "COMBAT_FACE" ]

	# Override HL2 schedules that misbehave (these are loaded FIRST)
	ESTABLISH_LINE_OF_FIRE = "EstablishLOFFallback"
	COMBAT_FACE	 		 = "CombatFaceOverride"

	# Bot specific schedules
	BOT_PATROL 			 = "BotPatrol"
	BOT_SEEK_ENEMY 		 = "BotSeekEnemy"
	BOT_ENGAGE_ENEMY	 = "BotEngageEnemy"
	BOT_SEEK_WEAPON 	 = "BotSeekWeapon"
	BOT_SEEK_AMMO 		 = "BotSeekAmmo"
	BOT_SEEK_ARMOR 		 = "BotSeekArmor"
	BOT_SEEK_TOKEN		 = "BotSeekToken"
