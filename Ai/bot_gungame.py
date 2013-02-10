from Ai.bot_deathmatch import bot_deathmatch
from Schedules import Cond
import GEGlobal as Glb

USING_API = Glb.API_VERSION_1_0_0

class bot_gungame( bot_deathmatch ):
	def GatherConditions( self ):
		bot_deathmatch.GatherConditions( self )
		self.ClearCondition( Cond.GES_CLOSE_TO_ARMOR )
		self.ClearCondition( Cond.GES_CAN_SEEK_ARMOR )
		self.ClearCondition( Cond.GES_CLOSE_TO_WEAPON )
		self.ClearCondition( Cond.BETTER_WEAPON_AVAILABLE )

	def SelectSchedule( self ):
		# Just to be sure
		self.ClearCondition( Cond.BETTER_WEAPON_AVAILABLE )
		self.ClearCondition( Cond.GES_CLOSE_TO_WEAPON )
		return bot_deathmatch.SelectSchedule( self )

