import GEAiCond, GEAiSched
from GEAi import ISchedule

class BaseSchedule( ISchedule ):
	def __init__( self, name=None ):
		# Always have a name
		if name is None:
			name = self.__class__.__name__

		# Pass id of -1 since we receive an id when registered!
		ISchedule.__init__( self, name, -1 )

		self.tasks = []
		self.interrupts = []

	def __str__( self ):
		return "%s <%i>" % ( self.name, self.id_ )

	def __eq__( self, other ):
		if isinstance( other, int ):
			return self.id_ == other
		return NotImplemented

	def __ne__( self, other ):
		ret = self.__eq__( other )
		if ret is NotImplemented:
			return ret
		return not ret

	def Build( self ):
		raise NotImplementedError( "You must define a Build function!" )

	def Register( self ):
		self.Build()

		for task in self.tasks:
			if issubclass( task[1].__class__, ISchedule ):
				task[1] = task[1].id_
			else:
				try:
					task[1] = float( task[1] )
				except:
					pass

		ISchedule.Register( self )

	def AddTask( self, task, data=0 ):
		self.tasks.append( [ task, data ] )

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


# Define the global schedules
class Sched( GEAiSched.Sched ):
	import common as c

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
