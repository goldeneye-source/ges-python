import GEAiCond, GEAiSched
from GEAi import ISchedule

class BaseSchedule( ISchedule ):
	def __init__( self, name=None, id_= -1 ):
		# Always have a name
		if name is None:
			name = self.__name__

		ISchedule.__init__( self, name, int( id_ ) )

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

import CommonSchedules

# Define the global schedules
class Sched( GEAiSched.Sched ):
	# Override HL2 schedules that misbehave (these are loaded FIRST)
	ESTABLISH_LINE_OF_FIRE = CommonSchedules.EstablishLOFFallback()
	COMBAT_FACE	 		 = CommonSchedules.CombatFaceOverride()

	# Bot specific schedules
	BOT_PATROL 			 = CommonSchedules.BotPatrol()
	BOT_SEEK_ENEMY 		 = CommonSchedules.BotSeekEnemy()
	BOT_ENGAGE_ENEMY	 = CommonSchedules.BotEngageEnemy()
	BOT_SEEK_WEAPON 	 = CommonSchedules.BotSeekWeapon()
	BOT_SEEK_AMMO 		 = CommonSchedules.BotSeekAmmo()
	BOT_SEEK_ARMOR 		 = CommonSchedules.BotSeekArmor()
	BOT_SEEK_TOKEN		 = CommonSchedules.BotSeekToken()
