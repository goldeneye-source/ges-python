from Ai import AiSystems
from GEAiConst import State
from Ai.bot_deathmatch import bot_deathmatch
from Ai.Utils import Weapons
from Schedules import Sched, Cond
from Tasks import Task
import GEEntity, GEUtil, GEWeapon, GEMPGameRules as GERules, GEGlobal as Glb
import random

USING_API = Glb.API_VERSION_1_0_0

class bot_mwgg( bot_deathmatch ):
	def __init__( self, parent ):
		bot_deathmatch.__init__( self, parent )
		self.SetCustomConditions( MWGG_Cond )

	def bot_WeaponParamCallback( self ):
		params = bot_deathmatch.bot_WeaponParamCallback( self )
		params["melee_bonus"] = -1
		return params

	def GatherConditions( self ):
		bot_deathmatch.GatherConditions( self )

		if self.HasWeapon( Glb.WEAPON_GOLDENGUN ):
			self.SetCondition( MWGG_Cond.MWGG_HAS_GG )
			self.SetTokenTarget( None )
		else:
			self.ClearCondition( MWGG_Cond.MWGG_HAS_GG )
			self.SetTokenTarget( "weapon_golden_gun" )

	def SelectSchedule( self ):
		sched = bot_deathmatch.SelectSchedule( self )

		if self.GetState() != State.COMBAT:
			if random.random() < 0.6 and not self.HasCondition( MWGG_Cond.MWGG_HAS_GG ):
				return Sched.BOT_SEEK_TOKEN

		return sched

# Schedule and condition declarations
class MWGG_Cond( Cond ):
	MWGG_HAS_GG = None

