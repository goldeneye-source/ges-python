################ Copyright 2005-2016 Team GoldenEye: Source #################
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
from .Utils import GetPlayers, _
from .Utils.GEPlayerTracker import GEPlayerTracker
from GEUtil import Color
import GEUtil, GEMPGameRules as GERules, GEGlobal as Glb, GEWeapon

USING_API = Glb.API_VERSION_1_2_0

TR_ELIMINATED = "eliminated" # If we're eliminated and can not join the round.  Starts true but is set to false upon successful spawn.  Used to track who can spawn.
TR_WASINPLAY = "wasinplay" # If we played in this round.  Starts false but is set to true for all players in the round when it inits.  Used for progress bars.

CLR_MI6_BAR = Color( 100, 184, 234, 220 )
CLR_JANUS_BAR = Color( 206, 43, 43, 255 )
CLR_DM_BAR = Color( 170, 170, 170, 220 )
CLR_SHOWDOWN_BAR = Color( 180, 225, 255, 170 )

# For some odd reason, you only live twice...
class YOLT( GEScenario ):
    def __init__( self ):
        GEScenario.__init__( self )

        self.pltracker = GEPlayerTracker( self )

        self.game_foes_orig = 0
        self.game_MI6_foes_orig = 0
        self.game_Janus_foes_orig = 0
        self.game_foes = None

    def GetTeamPlay( self ):
        return Glb.TEAMPLAY_TOGGLE

    def GetPrintName( self ):
        return "#GES_GP_YOLT_NAME"

    def GetScenarioHelp( self, help_obj ):
        help_obj.SetDescription( "#GES_GP_YOLT_HELP" )

    def GetGameDescription( self ):
        if GERules.IsTeamplay():
            return "Team YOLT"
        else:
            return "YOLT"

    def OnLoadGamePlay( self ):
        GERules.DisableSuperfluousAreas()
        self.CreateCVar( "yolt_timeperplayer", "30", "How many seconds are added to the clock for each player in the round." )        
        self.CreateCVar( "yolt_basetime", "0", "How many seconds are added to the clock regardless of the playercount." )        

    def OnUnloadGamePlay( self ):
        super( YOLT, self ).OnUnloadGamePlay()
        self.pltracker = None

    def OnPlayerConnect( self, player ):
        self.pltracker[player][TR_ELIMINATED] = True
        self.pltracker[player][TR_WASINPLAY] = False

    def OnPlayerDisconnect( self, player ):
        if GERules.IsRoundLocked() and self.yolt_IsInPlay( player ):
            self.yolt_DecreaseFoes( player )

    def CanPlayerChangeTeam( self, player, oldTeam, newTeam, wasforced ):
        if wasforced: # Make sure we can't eliminate people with autobalance.  Seriously, without this check you can eliminate an entire team.
            return True
        
        if GERules.IsRoundLocked():
            if oldTeam == Glb.TEAM_SPECTATOR: # Switching from spectator.  But we're only allowed to join the round if it isn't locked.
                GEUtil.PopupMessage( player, "#GES_GPH_CANTJOIN_TITLE", "#GES_GPH_CANTJOIN" )
                self.pltracker[player][TR_ELIMINATED] = True  
            elif not self.pltracker[player][TR_ELIMINATED]: # We switched during a locked round, eliminate us.
                # Tell everyone who was eliminated
                msg = _( "#GES_GP_YOLT_ELIMINATED", player.GetPlayerName() )
                GEUtil.PostDeathMessage( msg )
                # Tell plugins who was eliminated
                GEUtil.EmitGameplayEvent( "yolt_eliminated", str( player.GetUserID() ), str(-1), str(-1) )
                # Tell the victim they are eliminated
                GEUtil.PopupMessage( player, "#GES_GPH_ELIMINATED_TITLE", "#GES_GPH_ELIMINATED" )
                # Decrease the foes, which will call initfoes if we're the first one out.
                self.yolt_DecreaseFoes( player )
        else:
            player.ChangeTeam( newTeam, True ) # Force team change instead, so we don't suicide and start the round.
            return False # Since we force changed team we don't want to finish the normal team swap.

        return True

    def OnPlayerSpawn( self, player ):
        # Update our tracker variables
        self.pltracker[player][TR_ELIMINATED] = False

        if not GERules.IsRoundLocked():
            self.yolt_InitOpenroundBars()

        if player.IsInitialSpawn():
            # Simple help message
            GEUtil.PopupMessage( player, "#GES_GP_YOLT_NAME", "#GES_GPH_YOLT_GOAL" )

    def OnPlayerObserver( self, player ):
        # Init the tracking bars
        self.yolt_InitObserverBars( player )

    def OnRoundBegin( self ):
        super( YOLT, self ).OnRoundBegin()

        # Remove latent bars and let everyone know it's an open round
        self.yolt_InitOpenroundBars()

        GERules.UnlockRound()
        GERules.GetRadar().SetForceRadar( False )
        
        self.pltracker.SetValueAll( TR_WASINPLAY, False )

        self.game_foes_orig = 0
        self.game_MI6_foes_orig = 0
        self.game_Janus_foes_orig = 0
        self.game_foes = None

        GERules.EnableArmorSpawns()

        # Start dynamic timer
        self.yolt_UpdateTimer(0)
    
        GERules.SetSpawnInvulnTime( 5, True )

    def OnPlayerKilled( self, victim, killer, weapon ):
        # Execute default DM scoring behavior
        GEScenario.OnPlayerKilled( self, victim, killer, weapon )

        if not victim or GERules.GetNumInRoundPlayers() < 2: # We don't do YOLT logic if there aren't enough players for it.
            return

        # Lock the round (if not done already)
        GERules.LockRound()
        if self.game_foes_orig == 0: # If we don't have any foes we'll need to init them.
            self.yolt_InitFoes()

        if victim.GetDeaths() >= 2 and not self.pltracker[victim][TR_ELIMINATED]: # Make sure we're not already eliminated since switching teams can do that.
            # Tell everyone who was eliminated
            msg = _("#GES_GP_YOLT_ELIMINATED", victim.GetPlayerName())
            GEUtil.PostDeathMessage( msg )
            # Tell plugins who was eliminated
            GEUtil.EmitGameplayEvent( "yolt_eliminated", str( victim.GetUserID() ), str( killer.GetUserID() if killer else -1 ), str(weapon.GetClassname().lower() if weapon else -1), "", True )
            # Tell the victim they are eliminated
            GEUtil.PopupMessage( victim, "#GES_GPH_ELIMINATED_TITLE", "#GES_GPH_ELIMINATED" )
            # Decrease the foes, eliminate the victim
            self.yolt_DecreaseFoes( victim )

    def CanPlayerRespawn( self, player ):
        if GERules.IsRoundLocked() and self.pltracker[player][TR_ELIMINATED]:
            player.SetScoreBoardColor( Glb.SB_COLOR_ELIMINATED )
            return False

        player.SetScoreBoardColor( Glb.SB_COLOR_NORMAL )
        return True

    def CanMatchEnd( self ):
        if GERules.IsIntermission() or GERules.GetNumInRoundPlayers() < 2: #We just finished a round or it's not possible to get kills.
            return True
        else:
            return False

    def yolt_UpdateTimer( self, playercount, onlydecrease = False ):
        playertime = int( GEUtil.GetCVarValue( "yolt_timeperplayer" ) )
        basetime = int( GEUtil.GetCVarValue( "yolt_basetime" ) )

        #Dynamic timer disabled.
        if playertime == 0 and basetime == 0:
            return

        #Setting unlimited time, which we have to do here instead of directly so we don't mess with static roundtimes.
        if playercount == 0:
            GERules.SetRoundTimeLeft(0)
            GERules.AllowRoundTimer( False ) # We do both of these so it hides the match timer and flashes green when the time is started.
            return

        GERules.AllowRoundTimer( True ) # Reenable it now that the timer is started again.
        newtime = basetime + playercount * playertime

        #Make sure we're decreasing and not increasing the roundtime if we want to avoid doing that.
        if onlydecrease:
            timeleft = int(GERules.GetRoundTimeLeft())

            if (timeleft > newtime):
                GERules.SetRoundTimeLeft(newtime)
        else:
            GERules.SetRoundTimeLeft(newtime)

    def yolt_InitFoes( self ):
        if self.game_foes_orig != 0:
            # We are already init'd
            return
        
        if GERules.IsTeamplay():
            mi6_count = GERules.GetNumInRoundTeamPlayers( Glb.TEAM_MI6 )
            janus_count = GERules.GetNumInRoundTeamPlayers( Glb.TEAM_JANUS )
            self.game_foes_orig = mi6_count + janus_count
            self.game_MI6_foes_orig = mi6_count
            self.game_Janus_foes_orig = janus_count
            self.game_foes = [mi6_count, janus_count]
            playercount = min(mi6_count, janus_count) * 2
            # Display the foes progress bars (note color and values are swapped since these are "foes")
            GEUtil.InitHudProgressBar( Glb.TEAM_MI6_NO_OBS, 0, "#GES_GP_FOES", Glb.HUDPB_SHOWVALUE, janus_count, -1, 0.02, 0, 10, CLR_JANUS_BAR, janus_count )
            GEUtil.InitHudProgressBar( Glb.TEAM_JANUS_NO_OBS, 0, "#GES_GP_FOES", Glb.HUDPB_SHOWVALUE, mi6_count, -1, 0.02, 0, 10, CLR_MI6_BAR, mi6_count )
        else:
            # DM foes is just a number
            self.game_foes_orig = GERules.GetNumInRoundPlayers()
            playercount = self.game_foes_orig
            # Subtract one because we don't count the local player as a "foe"
            GEUtil.InitHudProgressBar( Glb.TEAM_NO_OBS, 0, "#GES_GP_FOES", Glb.HUDPB_SHOWVALUE, self.game_foes_orig - 1, -1, 0.02, 0, 10, CLR_DM_BAR, self.game_foes_orig - 1 )
            # Copy our origin into the tracker
            self.game_foes = self.game_foes_orig

        for player in GetPlayers():
            if not self.pltracker[player][TR_ELIMINATED]:
                self.pltracker[player][TR_WASINPLAY] = True

        self.yolt_UpdateTimer( playercount )
        
        # Initialize observer bars
        self.yolt_InitObserverBars( Glb.TEAM_OBS )
        
    def yolt_DecreaseFoes( self, victim ):
        # Init the foes if needed
        if self.game_foes_orig == 0:
            self.yolt_InitFoes()

        # Mark the victim as eliminated
        self.pltracker[victim][TR_ELIMINATED] = True
        victim.SetScoreBoardColor( Glb.SB_COLOR_ELIMINATED ) # Make sure they get the color change if they're the last to die.

        playercount = 1

        if GERules.IsTeamplay():
            # Team foes is ( mi6, janus )
            if victim.GetTeamNumber() == Glb.TEAM_MI6:
                self.game_foes[0] -= 1
            else:
                self.game_foes[1] -= 1

            # Update non-observers (note the reversal of scores)
            GEUtil.UpdateHudProgressBar( Glb.TEAM_MI6_NO_OBS, 0, self.game_foes[1] )
            GEUtil.UpdateHudProgressBar( Glb.TEAM_JANUS_NO_OBS, 0, self.game_foes[0] )

            # Update observers
            GEUtil.UpdateHudProgressBar( Glb.TEAM_OBS, 0, self.game_foes[0] )
            GEUtil.UpdateHudProgressBar( Glb.TEAM_OBS, 1, self.game_foes[1] )

            # Update timer max
            playercount = min(self.game_foes[0], self.game_foes[1]) * 2
        else:
            # DM foes is just a number
            self.game_foes -= 1
            # We subtract 1 here to account for the local player (prevents "1 / X" at win)
            GEUtil.UpdateHudProgressBar( Glb.TEAM_NO_OBS, 0, self.game_foes - 1 )
            # Update observers, we don't subtract 1 anymore
            GEUtil.UpdateHudProgressBar( Glb.TEAM_OBS, 0, self.game_foes )

            # Update timer max
            playercount = self.game_foes

            #We do this here so the victim doesn't see themselves taken off the foe meter.
            self.yolt_InitObserverBars( victim )

        # Check if we have a winner
        self.yolt_CheckWin()

        self.yolt_UpdateTimer(playercount, True)                                       

    def yolt_CheckWin( self ):
        if not self.game_foes:
            return

        if GERules.IsTeamplay():
            # Default no winner
            winner = None
            winnercount = 1
            if self.game_foes[0] <= 0:
                # MI6 has no foes, Janus won
                winner = GERules.GetTeam( Glb.TEAM_JANUS )
                winnercount = self.game_foes[1]
                losercount = self.game_MI6_foes_orig
            elif self.game_foes[1] <= 0:
                # Janus has no foes, MI6 won
                winner = GERules.GetTeam( Glb.TEAM_MI6 )
                winnercount = self.game_foes[0]
                losercount = self.game_Janus_foes_orig
            elif self.yolt_IsShowdown():
                # When we are down to 1 player on each team, force show the radar
                GERules.GetRadar().SetForceRadar( True )
                self.yolt_InitShowdownBars()
                GERules.StagnateArmorSpawns()

            if winner:
                # Split up the spoils among the surviving players on the winning team.
                for player in GetPlayers():
                    if self.yolt_IsInPlay( player ):
                        player.AddRoundScore( int(round(losercount/winnercount)) )
                
                winner.AddRoundScore( losercount ) # The team gets all of it, though.
                GERules.EndRound()
        else:
            # DM uses a number
            if self.game_foes <= 1:
                # There is only 1 player left, find who that is
                for player in GetPlayers():
                    if self.yolt_IsInPlay( player ):
                        player.AddRoundScore( self.game_foes_orig ) #They still might not win, but if they don't manage to win with this many points they don't deserve it.
                        GEUtil.EmitGameplayEvent( "yolt_lastmanstanding", str( player.GetUserID() ), str(self.game_foes_orig), "", "", True )
                        break
                # Round is over
                GERules.EndRound()
            elif self.yolt_IsShowdown():
                GERules.GetRadar().SetForceRadar( True )
                self.yolt_InitShowdownBars()
                GERules.StagnateArmorSpawns() #If it's a showdown, stop the armor spawns to prevent dinking around.

    def yolt_InitObserverBars( self, player ):
        if not GERules.IsRoundLocked():
            self.yolt_InitOpenroundBars()
            return
        
        # We don't init if there are no foes
        if not self.game_foes:
            return

        if self.yolt_IsShowdown():
            self.yolt_InitShowdownBars()
            return

        # Remove latent bars
        GEUtil.RemoveHudProgressBar( player, 0 )
        GEUtil.RemoveHudProgressBar( player, 1 )

        # Initialize and update
        if GERules.IsTeamplay():
            GEUtil.InitHudProgressBar( player, 0, "##TEAM_MI6: ", Glb.HUDPB_SHOWVALUE, self.game_MI6_foes_orig, 0.35, 0.14, 0, 10, CLR_MI6_BAR, self.game_foes[0] )
            GEUtil.InitHudProgressBar( player, 1, "##TEAM_JANUS: ", Glb.HUDPB_SHOWVALUE, self.game_Janus_foes_orig, 0.5, 0.14, 0, 10, CLR_JANUS_BAR, self.game_foes[1] )
        else:
            foes_orig = self.game_foes_orig
            if self.pltracker.GetValue( player, TR_WASINPLAY, False ):
                # Previously in-game players see a different original foes count
                foes_orig -= 1
                
            
            GEUtil.InitHudProgressBar( player, 0, "#GES_GP_FOES", Glb.HUDPB_SHOWVALUE, foes_orig, -1, 0.14, 0, 10, CLR_DM_BAR, self.game_foes )

    def yolt_InitShowdownBars( self ):
        # Remove latent bars
        GEUtil.RemoveHudProgressBar( None, 0 )
        GEUtil.RemoveHudProgressBar( None, 1 )

        # Prop up nice showdown bars for everyone
        GEUtil.InitHudProgressBar( Glb.TEAM_NO_OBS, 0, "#GES_GP_SHOWDOWN", Glb.HUDPB_TITLEONLY, y=0.02, color=CLR_SHOWDOWN_BAR )
        GEUtil.InitHudProgressBar( Glb.TEAM_OBS, 0, "#GES_GP_SHOWDOWN", Glb.HUDPB_TITLEONLY, y=0.14, color=CLR_SHOWDOWN_BAR )

    def yolt_InitOpenroundBars( self ):
        # Remove latent bars
        GEUtil.RemoveHudProgressBar( None, 0 )
        GEUtil.RemoveHudProgressBar( None, 1 )

        # Prop up nice showdown bars for everyone
        GEUtil.InitHudProgressBar( Glb.TEAM_NO_OBS, 0, "#GES_GP_OPENROUND", Glb.HUDPB_TITLEONLY, y=0.02, color=CLR_SHOWDOWN_BAR )
        GEUtil.InitHudProgressBar( Glb.TEAM_OBS, 0, "#GES_GP_OPENROUND", Glb.HUDPB_TITLEONLY, y=0.14, color=CLR_SHOWDOWN_BAR )

    def yolt_IsShowdown( self ):
        return (self.game_foes[0] == 1 and self.game_foes[1] == 1) if GERules.IsTeamplay() else self.game_foes == 2

    def yolt_IsInPlay( self, player ):
        try:
            return player.GetTeamNumber() != Glb.TEAM_SPECTATOR 	\
                    and not self.pltracker[player][TR_ELIMINATED]
        except KeyError:
            pass
