from GamePlay import GEScenario
import GEEntity, GEPlayer, GEUtil, GEWeapon, GEMPGameRules, GEGlobal

USING_API = GEGlobal.API_VERSION_1_0_0

class DeathMatch( GEScenario ):
	def GetPrintName( self ):
		return "#GES_GP_DEATHMATCH_NAME"

	def GetScenarioHelp( self, help_obj ):
		help_obj.SetDescription( "#GES_GP_DEATHMATCH_HELP" )

	def GetGameDescription( self ):
		if GEMPGameRules.IsTeamplay():
			return "Team Deathmatch"
		else:
			return "Deathmatch"

	def GetTeamPlay( self ):
		return GEGlobal.TEAMPLAY_TOGGLE

	def OnLoadGamePlay( self ):
		GEMPGameRules.SetAllowTeamSpawns( False )
		self.CreateCVar( "dm_fraglimit", "0", "Enable frag limit for DeathMatch." )

	def OnThink( self ):
		fragLimit = int( GEUtil.GetCVarValue( "dm_fraglimit" ) )
		if fragLimit != 0:
			if GEMPGameRules.IsTeamplay():

				teamJ = GEMPGameRules.GetTeam( GEGlobal.TEAM_JANUS );
				teamM = GEMPGameRules.GetTeam( GEGlobal.TEAM_MI6 );

				jScore = teamJ.GetRoundScore() + teamJ.GetMatchScore()
				mScore = teamM.GetRoundScore() + teamM.GetMatchScore()

				if jScore >= fragLimit or mScore >= fragLimit:
					GEMPGameRules.EndMatch()
			else:
				for i in range( 32 ):

					if not GEPlayer.IsValidPlayerIndex( i ):
						continue

					player = GEPlayer.GetMPPlayer( i )

					if  ( player.GetMatchScore() + player.GetScore() ) >= fragLimit:
						GEMPGameRules.EndMatch()
