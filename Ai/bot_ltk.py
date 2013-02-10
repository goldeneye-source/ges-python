from Ai import AiSystems
from Ai.bot_deathmatch import bot_deathmatch
from Ai.Utils import Weapons
from Schedules import Sched, Cond
import GEEntity, GEUtil, GEWeapon, GEMPGameRules as GERules, GEGlobal as Glb

USING_API = Glb.API_VERSION_1_0_0

class bot_ltk( bot_deathmatch ):
	def GatherConditions( self ):
		bot_deathmatch.GatherConditions( self )
		self.ClearCondition( Cond.GES_CLOSE_TO_ARMOR )
		self.ClearCondition( Cond.GES_CAN_SEEK_ARMOR )

	def bot_WeaponParamCallback( self ):
		params = bot_deathmatch.bot_WeaponParamCallback( self )
		params["melee_bonus"] = -5
		return params
