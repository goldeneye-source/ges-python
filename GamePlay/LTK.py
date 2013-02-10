from . import GEScenario
import GEEntity, GEPlayer, GEUtil, GEWeapon, GEMPGameRules, GEGlobal

USING_API = GEGlobal.API_VERSION_1_0_0

class LTK( GEScenario ):
	def GetTeamPlay( self ):
		return GEGlobal.TEAMPLAY_TOGGLE

	def GetPrintName( self ):
		return "#GES_GP_LTK_NAME"

	def GetScenarioHelp( self, help_obj ):
		help_obj.SetDescription( "#GES_GP_LTK_HELP" )

	def GetGameDescription( self ):
		if GEMPGameRules.IsTeamplay():
			return "Team LTK"
		else:
			return "LTK"

	def OnLoadGamePlay( self ):
		GEMPGameRules.SetAllowTeamSpawns( False )
		self.SetDamageMultiplier( 1000 )

	def OnUnloadGamePlay( self ):
		self.SetDamageMultiplier( 1 )

	def OnPlayerConnect( self, player ):
		player.SetDamageMultiplier( 1000 )

	def OnPlayerSpawn( self, player ):
		if player.IsInitialSpawn():
			GEUtil.PopupMessage( player, "#GES_GP_LTK_NAME", "#GES_GPH_LTK_GOAL" )

	def OnRoundBegin( self ):
		GEMPGameRules.ResetAllPlayersScores()
		GEMPGameRules.DisableArmorSpawns()

	def SetDamageMultiplier( self, amount ):
		for i in range( 32 ):
			if GEPlayer.IsValidPlayerIndex( i ):
				GEPlayer.GetMPPlayer( i ).SetDamageMultiplier( amount )
