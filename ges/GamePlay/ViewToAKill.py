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
from GamePlay import GEScenario
from .Utils import GetPlayers, _
from .Utils.GEPlayerTracker import GEPlayerTracker
import GEPlayer, GEUtil, GEMPGameRules as GERules, GEGlobal as Glb
import math

USING_API = Glb.API_VERSION_1_2_0


TR_CURINN = "curinn" #Length of current inning.  Also used to carry time between deaths.
TR_BESTINN = "bestinn" #Length of best inning.
TR_SPNTIME = "spntime" #Time the player spawned.  Will be set back when they steal time as this is what calculates their lifetime.
TR_OBJTAG = "objtag" #If the player is flagged as a high value target or not.

class ViewToAKill( GEScenario ):

    def __init__( self ):
        GEScenario.__init__( self )

        self.pltracker = GEPlayerTracker( self )

        self.longestinning = 1 # Keeps track of who has the current longest active inning time.
        self.nextchecktime = 0
    
    def GetPrintName( self ):
        return "#GES_GP_VTAK_NAME"

    def GetScenarioHelp( self, help_obj ):
        help_obj.SetDescription( "#GES_GP_VTAK_HELP" )

    def GetGameDescription( self ):
        return "A View to a Kill"

    def GetTeamPlay( self ):
        return Glb.TEAMPLAY_NONE

    def OnLoadGamePlay( self ):
        GERules.DisableSuperfluousAreas()
        GERules.EnableTimeBasedScoring() # Just enables a different scoreboard display.  Score is still just an int.

    def OnUnloadGamePlay(self):
        super( ViewToAKill, self ).OnUnloadGamePlay()
        self.pltracker = None
                
    def OnRoundBegin(self):
        GERules.ResetAllPlayersScores()

        for player in GetPlayers():
            self.pltracker[player][TR_CURINN] = 0
            self.pltracker[player][TR_BESTINN] = 0
            self.pltracker[player][TR_SPNTIME] = GEUtil.GetTime()
            self.pltracker[player][TR_OBJTAG] = False

    def OnPlayerConnect( self, player ):
        self.pltracker[player][TR_BESTINN] = 0
        self.pltracker[player][TR_CURINN] = 0

    def OnPlayerSpawn(self, player):
        self.pltracker[player][TR_SPNTIME] = GEUtil.GetTime() - self.pltracker[player][TR_CURINN] # Subtracting time from their spawn time gives them that time on spawn.
        self.pltracker[player][TR_OBJTAG] = False # If we managed to spawn with enough time to become an objective, the gamemode will know very soon.

    # We don't use standard scoring behavior here.  Kills don't add to score, but only current inning time.
    def OnPlayerKilled( self, victim, killer, weapon ):
        bonus = 0
        
        if victim == None:
            return
        if killer == None or victim == killer: # If we killed ourselves then our bonus becomes a deduction.
            bonus = int( self.pltracker[victim][TR_CURINN] / 2 ) * -1 # Still need to calculate bonus instead of dividing directly since we use it later.
            self.pltracker[victim][TR_CURINN] += bonus
        elif not killer.IsDead():
            bonus = int( self.pltracker[victim][TR_CURINN] / 2 )

            wepname = weapon.GetClassname().lower()
            #Bonus time for slapper kills, amounting to 75% of victim's time.
            if wepname == "weapon_slappers" or wepname == "player":
                bonus = round(bonus * 1.5)

            # We subtract from the killer's spawn time since inning time is calculated with: curtime - spawntime
            # and thus curtime - (spawntime - bonus) = curtime - spawntime + bonus = inningtime + bonus
            self.pltracker[killer][TR_SPNTIME] -= bonus
            # Also recalculate their current inning time here since they can die before the next server wide calculation.
            self.pltracker[killer][TR_CURINN] = int(GEUtil.GetTime() - self.pltracker[killer][TR_SPNTIME])

        if self.pltracker[victim][TR_CURINN] > self.pltracker[victim][TR_BESTINN]: # If we beat our best inning that life then we need to update it and our score.
            victim.SetRoundScore(int(self.pltracker[victim][TR_CURINN]))
            self.pltracker[victim][TR_BESTINN] = self.pltracker[victim][TR_CURINN]
        else:
            victim.SetRoundScore(int(self.pltracker[victim][TR_BESTINN])) #Needed in case of suicide.

        #Get rid of objective icon
        radar = GERules.GetRadar()
        radar.DropRadarContact( victim )
        victim.SetScoreBoardColor( Glb.SB_COLOR_NORMAL )

        # Killer, Victim, Time Stolen
        GEUtil.EmitGameplayEvent( "vtak_stealtime", str( killer.GetUserID() if killer else -1), str( victim.GetUserID() ), str( bonus ), "", True )


        # Convert our bonus time to a string, figure out the approperate color, and which player should receive the time notification.
        if bonus > 0:
            bonustag = "+" + self.vtak_SecondsToClockTime(bonus)
            bonuscolor = GEUtil.Color( 0, 255, 50, 255 )
            player = killer
        else:
            bonustag = "-" + self.vtak_SecondsToClockTime(bonus * -1)
            bonuscolor = GEUtil.Color( 255, 0, 50, 255 )
            player = victim

        # Print out how much time we gained/lost
        GEUtil.HudMessage( player, "                  " + bonustag, -1, 0.720, bonuscolor, 1.0, 3 )
        self.vtak_UpdateTimer( player, self.pltracker[player][TR_CURINN] )
        self.vtak_CheckCertainVictory()

        self.pltracker[victim][TR_CURINN] *= 0.25 #Victim will respawn with their current time multiplied by this value.

    # Update everyone's timers and see if their score should be adjusted.
    def OnThink(self):
        curtime = GEUtil.GetTime()

        if curtime < self.nextchecktime:
            return # We don't want to do all these calculations more than we need to.

        bestliveinning = 1 # We don't care about nonexistant innings.  Mainly because of the timeratio calculation that happens later which uses this as a divisor.
        
        for player in GetPlayers():
            if not player.IsDead():
                self.pltracker[player][TR_CURINN] = int(curtime - self.pltracker[player][TR_SPNTIME])
                plcurinn = int(self.pltracker[player][TR_CURINN]) # CURRINN doesn't need to be changed past this point so we can just store its value for easy reference.

                if plcurinn > self.pltracker[player][TR_BESTINN]: # If our current inning is better than our best inning, use that for the scoreboard.
                    player.SetRoundScore(plcurinn)
                    player.SetScoreBoardColor( Glb.SB_COLOR_WHITE )

                # Update our displays and check to see if we should be an objective.
                self.vtak_CheckObjStatus(player, plcurinn)
                self.vtak_UpdateTimer(player, plcurinn)

                if plcurinn > bestliveinning:
                    bestliveinning = plcurinn

        self.longestinning = bestliveinning
        self.nextchecktime = curtime + 1.0

    # Check to see if we should become an objective for other players
    def vtak_CheckObjStatus( self, player, seconds ):
        timeRatio = seconds/self.longestinning

        if timeRatio > 0.75 and seconds >= 60 and not self.pltracker[player][TR_OBJTAG]:
            radar = GERules.GetRadar()
            radar.SetupObjective( player, Glb.TEAM_NONE, "", "", GEUtil.Color( 180, 30, 30, 255 ), 256 ) # Minimum distance of 256 to make it harder to shoot targets through walls.
            radar.AddRadarContact( player, Glb.RADAR_TYPE_PLAYER, True, "", GEUtil.Color( 180, 30, 30, 255 ) )
            self.pltracker[player][TR_OBJTAG] = True
        return

    # Convert an integer value to a string that can be displayed on the HUD
    def vtak_SecondsToClockTime( self, seconds ):
        secondcount = seconds % 60
        secondstring = str(secondcount)
        
        if secondcount <= 9:
            secondstring = "0" + secondstring

        # Time to be displayed is minutes:seconds
        time = str(int(math.floor(seconds/60))) + ":" + secondstring
        return time

    # Update the HUD timer for the given player
    def vtak_UpdateTimer(self, player, seconds):
        timercolor = GEUtil.Color( 150, 150, 150, 255 )
        recordcolor = GEUtil.Color( 255, 255, 255, 255 )
        targetcolor = GEUtil.Color( 255, 0, 50, 255 )

        if self.pltracker[player][TR_OBJTAG]: # If we're an objective we need to know that before anything else.
            timercolor = targetcolor # So make our timer red.
        elif seconds >= self.pltracker[player][TR_BESTINN]: # Otherwise we could at least be beating our previous best inning.
            timercolor = recordcolor # Which deserves a brighter color.

        msg = _( "#GES_GP_VTAK_TIME", str(self.vtak_SecondsToClockTime(seconds)) )
        GEUtil.HudMessage( player, msg, -1, 0.745, timercolor, 1.5, 0 )

    # Certain victory is triggered when one player has so much time it's impossible to overtake them without using slappers.
    # Its threshold is calculated as: place2score + totalscore/2 + activeplayers*roundtimeleft/2
    # However, second place gets factored in to total score already so we have to subtract that out.
    # place2score + (totalscore - place2score)/2 + activeplayers*roundtimeleft/2
    # which simplifies to (second + totalscore + GERules.GetNumInRoundPlayers() * timeleft)/2

    # This is very difficult to get, it's mostly used as a measure to spare people from playing a round they have no chance of winning.
    def vtak_CheckCertainVictory(self):
        timeleft = int(GERules.GetRoundTimeLeft())
        
        if (timeleft < 20): #We have no round timer, or there's less than 20 seconds left on the clock, so let's ignore certain victory.
            return
        
        topplayer = None # Player currently winning
        first = 0 # Highscore of winning player
        second = 0 # Longest current inning time of player who is not the winning player.
        totalscore = 0 # Total of all the active innings.

        # Get the player currently in the lead, along with their best score.
        for player in GetPlayers():
            highscore = max(self.pltracker[player][TR_CURINN],self.pltracker[player][TR_BESTINN])
            
            if (highscore > first ):
                first = highscore
                topplayer = player

        # Now find the runner up, get their score, and also find the total inning time of everyone currently playing.
        for player in GetPlayers():
            score = self.pltracker[player][TR_CURINN]
            
            if ( score > second and player != topplayer):
                second = score

            totalscore += score
            
        # Shoot, someone actually got it.  Concede the round to them.
        if ( second + totalscore + GERules.GetNumInRoundPlayers() * timeleft < first * 2): # We move the /2 to the right hand side to make things nicer.
            msg = _( "#GES_GP_VTAK_VICTORY", topplayer.GetCleanPlayerName() )
            GEUtil.PostDeathMessage( msg )
            GEUtil.EmitGameplayEvent( "vtak_certainvictory" , str( topplayer.GetUserID()), str(first), "", "", True )
            GERules.EndRound()
            
