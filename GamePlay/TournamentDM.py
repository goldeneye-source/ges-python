################ Copyright 2005-2013 Team GoldenEye: Source #################
#
# This file is part of GoldenEye: Source's Python Library.
#
# GoldenEye: Source's Python Library is free software: you can redistribute
# it and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the License,
# or(at your option) any later version.
#
# GoldenEye: Source's Python Library is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GoldenEye: Source's Python Library.
# If not, see <http://www.gnu.org/licenses/>.
#############################################################################
from . import GEScenario
from Utils import clamp, plural, _
from Utils.GEWarmUp import GEWarmUp
import GEUtil, GEMPGameRules as GERules, GEGlobal

# Tournament Deathmatch
# Coded by Troy and Killer Monkey
# /////////////////////////// Scenario Data ///////////////////////////

USING_API = GEGlobal.API_VERSION_1_1_1

class TournamentDM( GEScenario ):
    def __init__( self ):
        super( TournamentDM, self ).__init__()

        self.WaitingForPlayers = True
        self.FirstBlood = False
        self.LateAttendance = False
        self.notice_WaitingForPlayers = 0

        self.warmupTimer = GEWarmUp( self )

        # CVar Holders
        self.FragLimit = 50
        self.FragMessages = True

    def GetPrintName( self ):
        return "#GES_GP_TOURNAMENTDM_NAME"

    def GetScenarioHelp( self, help_obj ):
        help_obj.SetDescription( "#GES_GP_TOURNAMENTDM_HELP" )

    def GetGameDescription( self ):
        return "Tournament DM"

    def GetTeamPlay( self ):
        return GEGlobal.TEAMPLAY_ALWAYS

    def OnLoadGamePlay( self ):
        GEUtil.PrecacheSound( "GEGamePlay.Token_Drop_Friend" )
        GEUtil.PrecacheSound( "GEGamePlay.Token_Grab" )

        self.CreateCVar( "tdm_fraglimit", "50", "Sets the frag limit which is total score needed to win the match. (Use 0 to disable, Max is 100)" )
        self.CreateCVar( "tdm_fragmessages", "1", "Enable frag messages to be displayed in the chat. (Use 0 to disable)" )
        self.CreateCVar( "tdm_warmuptime", "30", "Sets the warmup time in seconds. (Use 0 to disable)" )

        # Make sure we don't start out in wait time if we changed gameplay mid-match
        if GERules.IsTeamplay():
            if GERules.GetNumActiveTeamPlayers( GEGlobal.TEAM_MI6 ) >= 2 and GERules.GetNumActiveTeamPlayers( GEGlobal.TEAM_JANUS ) >= 2:
                self.WaitingForPlayers = False
        else:
            if GERules.GetNumActivePlayers() >= 4:
                self.WaitingForPlayers = False

    def OnUnloadGamePlay( self ):
        GEScenario.OnUnloadGamePlay( self )
        self.warmupTimer = None

    def OnCVarChanged( self, name, oldvalue, newvalue ):
        if name == "tdm_fraglimit":
            # Clamp the fraglimit
            val = clamp( int( newvalue ), 0, 100 )
            if val != self.FragLimit:
                self.FragLimit = val
        elif name == "tdm_fragmessages":
            val = int( newvalue )
            if val == 0 and self.FragMessages:
                self.FragMessages = False
            elif val != 0 and not self.FragMessages:
                self.FragMessages = True
        elif name == "tdm_warmuptime":
            if self.warmupTimer.IsInWarmup():
                val = int( newvalue )
                self.warmupTimer.StartWarmup( val )
                if val <= 0:
                    GERules.EndRound( False )

    def OnRoundBegin( self ):
        GEScenario.OnRoundBegin( self )

    def OnPlayerSpawn( self, player ):
        if player.IsInitialSpawn():
            if self.FragLimit >= 2:
                GEUtil.PopupMessage( player, "Tournament DM", _( "#GES_GP_TDM_GOAL_MANY", self.FragLimit ) )
            elif self.FragLimit == 1:
                GEUtil.PopupMessage( player, "Tournament DM", "#GES_GP_TDM_GOAL_ONE" )
            else:
                GEUtil.PopupMessage( player, "Tournament DM", "#GES_GPH_DM_GOAL" )

    def OnPlayerKilled( self, victim, killer, weapon ):
        if self.WaitingForPlayers or self.warmupTimer.IsInWarmup() or not victim:
            return

        if not killer or victim == killer:
            # World kill or suicide
            victim.AddRoundScore( -1 )
        elif GERules.IsTeamplay() and killer.GetTeamNumber() == victim.GetTeamNumber():
            # Same-team kill
            killer.AddRoundScore( -1 )
        else:
            # Normal kill
            GERules.GetTeam( killer.GetTeamNumber() ).AddRoundScore( 1 )
            killer.AddRoundScore( 1 )

            if self.FragLimit > 0 and self.FragMessages:
                if killer.GetTeamNumber() == GEGlobal.TEAM_MI6:
                    team = GERules.GetTeam( GEGlobal.TEAM_MI6 )
                    teamName = '^i' + team.GetName()
                    teamScore = team.GetRoundScore() + team.GetMatchScore()
                    self.PrintFragMessages( killer, teamName, teamScore )
                elif killer.GetTeamNumber() == GEGlobal.TEAM_JANUS:
                    team = GERules.GetTeam( GEGlobal.TEAM_JANUS )
                    teamName = '^r' + team.GetName()
                    teamScore = team.GetRoundScore() + team.GetMatchScore()
                    self.PrintFragMessages( killer, teamName, teamScore )

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
                if self.warmupTimer.IsInWarmup():
                    GEUtil.EmitGameplayEvent( "tdm_startwarmup" )
            else:
                GERules.EndRound( False )

        if self.FragLimit > 0:
            teamJ = GERules.GetTeam( GEGlobal.TEAM_JANUS )
            teamM = GERules.GetTeam( GEGlobal.TEAM_MI6 )

            jScore = teamJ.GetRoundScore() + teamJ.GetMatchScore()
            mScore = teamM.GetRoundScore() + teamM.GetMatchScore()

            if jScore >= self.FragLimit or mScore >= self.FragLimit:
                self.LateAttendance = True
                GERules.EndMatch()

# /////////////////////////// Utility Functions ///////////////////////////

    def PrintFragMessages( self, killer, teamName, teamScore ):
        if not self.FirstBlood and self.FragLimit > 1:
            GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "#GES_GP_TDM_FIRSTBLOOD", teamName )
            self.PlayTeamSounds( killer.GetTeamNumber() )
            self.FirstBlood = True

        if not self.LateAttendance:
            scoreToWin = self.FragLimit - teamScore

            if scoreToWin == 0:
                GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, "#GES_GP_TDM_WON", teamName )
            elif scoreToWin <= 3:
                GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, plural( scoreToWin, "#GES_GP_TDM_FRAGS_LEFT" ), teamName, str( scoreToWin ) )
                self.PlayTeamSounds( killer.GetTeamNumber() )

    def PlayTeamSounds( self, team ):
        if team == GEGlobal.TEAM_MI6:
            GEUtil.PlaySoundTo( GEGlobal.TEAM_MI6, "GEGamePlay.Token_Grab" )
            GEUtil.PlaySoundTo( GEGlobal.TEAM_JANUS, "GEGamePlay.Token_Drop_Friend" )
        elif team == GEGlobal.TEAM_JANUS:
            GEUtil.PlaySoundTo( GEGlobal.TEAM_MI6, "GEGamePlay.Token_Drop_Friend" )
            GEUtil.PlaySoundTo( GEGlobal.TEAM_JANUS, "GEGamePlay.Token_Grab" )
