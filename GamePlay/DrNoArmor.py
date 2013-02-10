from .DeathMatch import DeathMatch
import GEEntity, GEPlayer, GEUtil, GEWeapon, GEMPGameRules, GEGlobal

USING_API = GEGlobal.API_VERSION_1_0_0

class DrNoArmor( DeathMatch ):
	def GetPrintName( self ):
		return "Dr. No Armor"

	def GetScenarioHelp( self, help_obj ):
		help_obj.SetDescription( "#GES_GP_DEATHMATCH_HELP" )

	def GetGameDescription( self ):
		if GEMPGameRules.IsTeamplay():
			return "Team Dr. No Armor"
		else:
			return "Dr. No Armor"

	def OnRoundBegin( self ):
		super( DrNoArmor, self ).OnRoundBegin()
		GEMPGameRules.DisableArmorSpawns()

