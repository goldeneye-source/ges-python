from . import GEScenario
from Utils.GEWarmUp import GEWarmUp
import GEEntity, GEPlayer, GEUtil, GEWeapon, GEMPGameRules as GERules, GEGlobal

USING_API = GEGlobal.API_VERSION_1_0_0

class TournamentDM( GEScenario ):
	def __init__( self ):
		super( TournamentDM, self ).__init__()
		self.warmupTimer = GEWarmUp( self )
		self.notice_WaitingForPlayers = 0
		self.WaitingForPlayers = True

	def Cleanup( self ):
		GEScenario.Cleanup( self )
		self.warmupTimer = None

	def GetPrintName( self ):
		return "#GES_GP_TOURNAMENTDM_NAME"

	def GetScenarioHelp( self, help_obj ):
		help_obj.SetDescription( "#GES_GP_TOURNAMENTDM_HELP" )

	def GetGameDescription( self ):
		return "Tournament DM"

	def GetTeamPlay( self ):
		return GEGlobal.TEAMPLAY_ALWAYS

	def OnLoadGamePlay( self ):
		self.CreateCVar( "tdm_warmuptime", "30", "Warm up time in seconds." )
		self.CreateCVar( "tdm_fraglimit", "0", "Enable frag limit for DeathMatch." )

		# Make sure we don't start out in wait time if we changed gameplay mid-match
		if GERules.GetNumActiveTeamPlayers( GEGlobal.TEAM_MI6 ) >= 2 and GERules.GetNumActiveTeamPlayers( GEGlobal.TEAM_JANUS ) >= 2:
			self.WaitingForPlayers = False

	def OnRoundBegin( self ):
		GEScenario.OnRoundBegin( self )

		if not self.WaitingForPlayers and not self.warmupTimer.HadWarmup():
			self.warmupTimer.StartWarmup( int( GEUtil.GetCVarValue( "tdm_warmuptime" ) ) )

	def OnThink( self ):
		# Check for insufficient player count
		if GERules.GetNumActiveTeamPlayers( GEGlobal.TEAM_MI6 ) < 2 or GERules.GetNumActiveTeamPlayers( GEGlobal.TEAM_JANUS ) < 2:
			if not self.WaitingForPlayers:
				self.notice_WaitingForPlayers = 0
				GERules.EndRound()
			elif GEUtil.GetTime() > self.notice_WaitingForPlayers:
				GEUtil.HudMessage( None, "#GES_GP_WAITING", -1, -1, GEUtil.Color( 255, 255, 255, 255 ), 2.5, 1 )
				self.notice_WaitingForPlayers = GEUtil.GetTime() + 12.5

			self.warmupTimer.Reset()
			self.WaitingForPlayers = True
			return
		elif self.WaitingForPlayers:
			self.WaitingForPlayers = False
			if not self.warmupTimer.HadWarmup():
				self.warmupTimer.StartWarmup( int( GEUtil.GetCVarValue( "tdm_warmuptime" ) ), True )
			else:
				GERules.EndRound( False )

		fragLimit = int( GEUtil.GetCVarValue( "tdm_fraglimit" ) )
		if fragLimit != 0:
			teamJ = GERules.GetTeam( GEGlobal.TEAM_JANUS );
			teamM = GERules.GetTeam( GEGlobal.TEAM_MI6 );

			jScore = teamJ.GetRoundScore() + teamJ.GetMatchScore()
			mScore = teamM.GetRoundScore() + teamM.GetMatchScore()

			if jScore >= fragLimit or mScore >= fragLimit:
				GERules.EndMatch()
