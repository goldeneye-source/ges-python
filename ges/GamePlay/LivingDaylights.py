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
from . import GEScenario, GEScenarioHelp
from Utils import plural, clamp, choice, _
import GEEntity, GEPlayer, GEUtil, GEMPGameRules, GEGlobal

USING_API = GEGlobal.API_VERSION_1_1_1
EP_SHOUT_COLOR = GEUtil.CColor( 240, 200, 120, 170 )
FT_DEBUG = False

def ep_incrementscore( player, frags ):
    GEMPGameRules.GetTeam( player.GetTeamNumber() ).AddRoundScore( frags )
    player.AddRoundScore( frags )
    return player

def ep_naturalsubtraction( value, delta ):
    if value > delta:
        return value - delta
    return 0

def ep_player_by_id( uid ):
    return GEPlayer.ToMPPlayer( GEEntity.GetEntByUniqueId( uid ) )

def ep_shout( msg ):
    if FT_DEBUG :
        GEUtil.ClientPrint( None, GEGlobal.HUD_PRINTTALK, msg )
        GEUtil.HudMessage( None, msg, -1, -1, EP_SHOUT_COLOR, 2.0 )
    return msg

class LivingDaylightsFlag:
    LEVEL_LIMIT = 10
    ESCAPE_TIME = 80
    ESCAPE_AP_LIMIT = 40
    AGE_SCALE = 1.0
    BONUS_ITEM = [10, 15, 25, 35]
    BONUS_LIMIT = 4
    ADREN_MAX = 40

    def __init__( self ):
        self.zot()

    def age( self, ticks, handled ):
        if self.i_am_held():
            self.exp_to_next -= ticks * self.AGE_SCALE
            if handled and self.exp_to_next <= 0:
                if self.level < self.LEVEL_LIMIT:
                    self.level += 1
                self.earnings += 1
                self.exp_to_next += self.exp_this_level( self.level )
                return True
        return False

    def age_escape( self, ticks ):
        if self.exp_to_escape > -1 and self.i_am_held():
            self.adrenaline = ep_naturalsubtraction( self.adrenaline, ticks )
            self.exp_to_escape -= ticks
            if self.exp_to_escape <= 0:
                self.escapes += 1
                self.exp_to_escape = -1
                return True
        return False

    def age_item( self, itemindex, coeff ):
        if itemindex >= 0 and itemindex < self.BONUS_LIMIT:
            self.age( self.BONUS_ITEM[itemindex] * coeff, False )

    def escape( self, force, inflicted_damage ):
        if ( force or self.exp_to_escape >= 0 ) and self.i_am_held():
            self.exp_to_escape = self.ESCAPE_TIME
            if force:
                ep_shout( "Adrenaline trigger." )
                self.adrenaline = self.ADREN_MAX
                self.escape_ap = min( self.ESCAPE_AP_LIMIT, self.escape_ap + inflicted_damage )
            else:
                ep_shout( "No adrenaline." )

    def exp_this_level( self, req_level ):
        return ( clamp( req_level, 1, self.LEVEL_LIMIT ) + 2 ) * 10

    def i_am_held( self ):
        if self.token_id != 0 and self.player_id != 0:
            player = ep_player_by_id( self.player_id )
            return player != None and player.GetTeamNumber() != GEGlobal.TEAM_SPECTATOR and player.IsAlive()
        return False

    def level_by_playercount( self, pc ):
        self.level = clamp( self.LEVEL_LIMIT + 1 - pc , 0, self.LEVEL_LIMIT )

    def my_team( self ):
        if self.token_id != 0 and self.player_id != 0:
            player = ep_player_by_id( self.player_id )
            if player != None and player.IsAlive():
                return player.GetTeamNumber()
        return GEGlobal.TEAM_NONE

    def release( self ):
        self.player_previous = self.player_id
        self.earnings_total += self.earnings
        self.earnings_previous = self.earnings
        if GEMPGameRules.IsTeamplay():
            if self.player_id != 0:
                self.team_previous = ep_player_by_id( self.player_id ).GetTeamNumber()
        self.player_id = 0
        self.earnings = 0
        self.earnings_total = 0
        self.escapes = 0
        self.escape_ap = 0
        self.exp_to_next = 0
        self.exp_to_escape = -1
        self.armor_up = -1
        self.adrenaline = 0

    def zot( self ):
        # double zeroed because Python is lame.
        self.player_id = 0
        self.earnings = 0
        self.earnings_total = 0
        self.release()
        self.player_previous = self.player_id
        self.earnings_total += self.earnings
        self.earnings_previous = self.earnings
        self.team_previous = GEGlobal.TEAM_SPECTATOR
        self.level = 0
        self.token_id = 0

class LivingDaylights( GEScenario ):
    BAR_CARRY = 100
    BAR_ESCAPE = 100
    BAR_TEAMBALANCE = 50
    BAR_CAP_X = 0.3

    COLOR_COLD = GEUtil.CColor( 30, 150, 180, 170 )
    COLOR_HOLD = GEUtil.CColor( 255, 180, 225, 170 )
    COLOR_H_MI = GEUtil.CColor( 180, 225, 255, 170 )
    COLOR_H_JS = GEUtil.CColor( 255, 225, 180, 170 )
    COLOR_P_JS = GEUtil.CColor( 255, 180, 180, 170 )
    COLOR_WARM = GEUtil.CColor( 180, 150, 30, 170 )
    COLOR_CASH = GEUtil.CColor( 240, 225, 45, 170 )
    COLOR_MI6 = GEUtil.CColor( 94, 171, 231, 255 )
    COLOR_JS = GEUtil.CColor( 206, 43, 43, 255 )

    PERK_ADREN = 0.3
    PERK_SPEED = 0.025

    THEFT_DELTA = 1

    # Flag information management
    FLAGLIST_LIMIT = 16
    FLAGLIST_MAXID = FLAGLIST_LIMIT - 1
    flaglist = [LivingDaylightsFlag() for j in range( FLAGLIST_LIMIT )]

    def ft_ageflag( self, flagindex, ticks ):
        if self.flaglist[flagindex].age( ticks, True ) :
                self.ft_creditcarrier( self.flaglist[flagindex] )

    # Flag Tag functions
    def ft_ageflags( self ):
        for j in range( self.FLAGLIST_LIMIT ):
            flag = self.flaglist[j]
            if flag.exp_to_escape > -1:
                self.ft_perk_speed( j )
            if flag.age_escape( 1 ) :
                self.ft_creditescape( flag )
            if flag.age( 1, True ) :
                self.ft_creditcarrier( flag, 1 )
                self.ft_perk_speed( j )
            if flag.armor_up > -1:
                self.ft_escapee_armorapply( flag )

    def ft_announceearning( self, flag, frags ):
        player = ep_player_by_id( flag.player_id )
        GEUtil.PlaySoundTo( player, "GEGamePlay.Token_Chime" )
        self.ft_progressbar( flag, ep_player_by_id( flag.player_id ) )

    def ft_announceescaping( self, flag ):
        player = ep_player_by_id( flag.player_id )
        GEUtil.HudMessage( player, _( plural( flag.escapes, "#GES_GP_LD_ESCAPED" ), flag.escapes ), -1, -1, EP_SHOUT_COLOR, 2.0 )
        GEUtil.PlaySoundTo( player, "Buttons.beep_ok" )
        ep_shout( "Escaped successfully." )

    def ft_associate( self, token, player ):
        flagindex = self.ft_flagindexbytoken( token )
        if( flagindex >= 0 ) :
            self.flaglist[flagindex].player_id = GEEntity.GetUID( player )
        else :
            ep_shout( "[ft_associate] Token %d does not have associated information." % ( GEEntity.GetUID( token ) ) )
        return flagindex

    def ft_coldflaglevel( self, index ):
        if( index >= 0 ):
            self.flaglist[index].level_by_playercount( GEMPGameRules.GetNumActivePlayers() )

    def ft_creditcarrier( self, flag, frags ):
        player = ep_player_by_id( flag.player_id )
        ep_incrementscore( player, frags )
        self.ft_announceearning( flag, frags )
        GEUtil.EmitGameplayEvent( "ld_flagpoint", str( player.GetUserID() ), "-1", "timer", str( frags ) )

    def ft_creditescape( self, flag ):
        player = ep_player_by_id( flag.player_id )
        ep_incrementscore( player, flag.escapes )
        self.ft_escapee_armorup( flag, player )
        self.ft_announceescaping( flag )
        self.ft_escapebar_remove( flag )
        GEUtil.EmitGameplayEvent( "ld_flagpoint", str( player.GetUserID() ), "-1", "escape", str( flag.escapes ) )

    def ft_disassociate( self, token, respawned ):
        flagindex = self.ft_flagindexbytoken( token )
        if( flagindex >= 0 ) :
            flag = self.flaglist[flagindex]
            self.ft_progressbar_remove( flag )
            self.ft_escapebar_remove( flag )
            if respawned:
                flag.zot()
            else:
                flag.release()
        else:
            ep_shout( "[Disassociate] Token %d was unregistered when dropped." )
        return flagindex

    def ft_escapebar( self, flag, player ):
        GEUtil.InitHudProgressBar( player, 1, "%d " % ( flag.escapes + 1 ), GEGlobal.HUDPB_SHOWBAR, flag.ESCAPE_TIME, -1, .72, self.BAR_ESCAPE, 10, self.COLOR_WARM )

    def ft_escapebar_remove( self, flag ):
        GEUtil.RemoveHudProgressBar( ep_player_by_id( flag.player_id ), 1 )

    def ft_escapee_armorapply( self, flag ):
        ep_player_by_id( flag.player_id ).SetArmor( flag.armor_up )
        flag.armor_up = -1

    def ft_escapee_armorup( self, flag, player ):
        flag.armor_up = clamp( int( player.GetArmor() + flag.escape_ap ), 0, GEGlobal.GE_MAX_ARMOR )
        flag.escape_ap = 0;

    def ft_flagdebt( self ):
        return self.ft_flagsdesired() - self.ft_flagsregistered()

    def ft_flagindexbytoken( self, token ):
        uid = GEEntity.GetUID( token )
        rtn_j = -1
        for j in range( self.FLAGLIST_LIMIT ) :
            if( self.flaglist[j].token_id == uid ) :
                rtn_j = j
                break
        return rtn_j

    def ft_flagindexbyplayer( self, player ):
        uid = GEEntity.GetUID( player )
        rtn_j = -1
        for j in range( self.FLAGLIST_LIMIT ) :
            if( self.flaglist[j].player_id == uid ) :
                rtn_j = j
                break
        return rtn_j

    def ft_flagindexbyplayerprevious( self, player ):
        uid = GEEntity.GetUID( player )
        rtn_j = -1
        for j in range( self.FLAGLIST_LIMIT ) :
            if( self.flaglist[j].player_previous == uid ) :
                rtn_j = j
                break
        return rtn_j

    def ft_flaglist_openslot( self ):
        rtn_index = -1
        for j in range( self.FLAGLIST_LIMIT ):
            if self.flaglist[j].token_id == 0:
                rtn_index = j
                break
        return rtn_index

    def ft_flagsdesired( self ):
        if GEMPGameRules.IsTeamplay():
            fd = min( min( GEMPGameRules.GetTeam( GEGlobal.TEAM_MI6 ).GetNumPlayers(), GEMPGameRules.GetTeam( GEGlobal.TEAM_JANUS ).GetNumPlayers() ), self.FLAGLIST_LIMIT )
            fd = clamp( fd, 1, fd - max( 0, int( GEUtil.GetCVarValue( "ld_teamguardians" ) ) ) )
        else:
            playersperflag = max( 1, int( GEUtil.GetCVarValue( "ld_playersperflag" ) ) )
            fd = min( int( ( GEMPGameRules.GetNumActivePlayers() + playersperflag - 1 ) / playersperflag ), self.FLAGLIST_LIMIT )
        return fd

    def ft_flagsregistered( self ):
        flagsregistered = 0
        for j in range( self.FLAGLIST_LIMIT ) :
            if self.flaglist[j].token_id != 0 :
                flagsregistered += 1
        return flagsregistered

    def ft_gameislive( self ):
        return GEMPGameRules.GetNumActivePlayers() > 1 or FT_DEBUG

    def ft_omnomnomnom( self, player, itemname ):
        flagindex = self.ft_flagindexbyplayer( player )
        if flagindex >= 0:
            quality = -1
            if itemname.startswith( "item_armorvest_half" ):
                quality = 2
            elif itemname.startswith( "item_armorvest" ):
                quality = 3
            elif itemname.startswith( "weapon_" ):
                quality = 1
            elif itemname.startswith( "ge_ammo" ):
                quality = 0
            if quality >= 0:
                if self.ft_gameislive():
                    self.flaglist[flagindex].age_item( quality, 1.0 )
# 					ep_shout("Consumed %s for %d EXP." % (itemname, self.flaglist[flagindex].BONUS_ITEM[quality]))
        return True

    def ft_perk_speed( self, flagindex ):
        if flagindex >= 0 and self.flaglist[flagindex].i_am_held():
            flag = self.flaglist[flagindex]
            player = ep_player_by_id( flag.player_id )
            perk = ( 1.0 + ( float( GEMPGameRules.GetNumActivePlayers() ) + ( float( flag.adrenaline ) * self.PERK_ADREN ) ) * self.PERK_SPEED ) ** 0.5
            ep_shout( "[Perk Speed] %f" % perk )
            player.SetSpeedMultiplier( min( perk, choice( GEMPGameRules.IsTeamplay(), 1.20, 1.35 ) ) )

    def ft_playercarries( self, player ):
        return self.ft_flagindexbyplayer( player ) != -1

    def ft_progressbar( self, flag, player ):
        GEUtil.InitHudProgressBar( player, 0, "%d " % flag.earnings, GEGlobal.HUDPB_SHOWBAR, flag.exp_this_level( flag.level ), -1, .76, self.BAR_CARRY, 10, self.COLOR_H_MI )

    def ft_progressbar_remove( self, flag ):
        GEUtil.RemoveHudProgressBar( ep_player_by_id( flag.player_id ), 0 )

    def ft_progressbars( self ):
        for j in range( self.FLAGLIST_LIMIT ) :
            flag = self.flaglist[j]
            if flag.player_id != 0 :
                GEUtil.UpdateHudProgressBar( ep_player_by_id( flag.player_id ), 0, flag.exp_to_next )
            if flag.exp_to_escape > -1:
                GEUtil.UpdateHudProgressBar( ep_player_by_id( flag.player_id ), 1, flag.exp_to_escape )

    def ft_progressbars_legacy( self ):
        for j in range( self.FLAGLIST_LIMIT ) :
            flag = self.flaglist[j]
            if flag.player_id != 0 :
                step = 4.0
                text_lifespan = 0.2
                scale = 1.0 / step
                width = scale * flag.exp_this_level( flag.level )
                fill = scale * flag.exp_to_next
                exp_bar = ""
                for jj in range( 1, int( width ), 1 ):
                    if jj < fill:
                        exp_bar = "-%s" % exp_bar
                    else:
                        exp_bar = "!%s" % exp_bar
                exp_bar = "[%s] %d" % ( exp_bar, flag.earnings )
                GEUtil.HudMessage( ep_player_by_id( flag.player_id ), exp_bar, -1, .75, EP_SHOUT_COLOR, text_lifespan )

    def ft_registerflag( self, newflag_id ):
        newflag_index = self.ft_flaglist_openslot()
        if( newflag_index > -1 ):
            self.flaglist[newflag_index].zot()
            self.flaglist[newflag_index].token_id = newflag_id
        else:
            ep_shout( "[Register Flag] Failed to find an information slot. (CRITICAL)" )
        return newflag_index

    def ft_shepherd( self ):
        if self.ft_flagdebt() > 0 :
            GEMPGameRules.GetTokenMgr().SetupToken( self.TokenClass, limit=self.ft_flagsdesired() )

    def ft_showteamflags( self, player=None ):
        if GEMPGameRules.IsTeamplay():
            if player is None:
                if self.ShowMI6Flags:
                    GEUtil.HudMessage( GEGlobal.TEAM_MI6, _( "#GES_GP_LD_TEAMHOLDS", self.MI6Flags, self.FlagCount ), -1, 0.65, self.COLOR_MI6, 5.0, 1 )
                if self.ShowJanusFlags:
                    GEUtil.HudMessage( GEGlobal.TEAM_JANUS, _( "#GES_GP_LD_TEAMHOLDS", self.JanusFlags, self.FlagCount ), -1, 0.65, self.COLOR_JS, 5.0, 1 )

                self.ShowMI6Flags = self.ShowJanusFlags = False
            else:
                if player.GetTeamNumber() == GEGlobal.TEAM_MI6:
                    GEUtil.HudMessage( player, _( "#GES_GP_LD_TEAMHOLDS", self.MI6Flags, self.FlagCount ), -1, 0.65, self.COLOR_MI6, 5.0, 1 )
                else:
                    GEUtil.HudMessage( player, _( "#GES_GP_LD_TEAMHOLDS", self.JanusFlags, self.FlagCount ), -1, 0.65, self.COLOR_JS, 5.0, 1 )


    def ft_teambalancebars( self ):
        if GEMPGameRules.IsTeamplay():
            mi_flags = 0
            js_flags = 0
            barwidth = 0
            for j in range( self.FLAGLIST_LIMIT ) :
                if self.flaglist[j].token_id != 0:
                    barwidth += 1
                    thisflagteam = self.flaglist[j].my_team()
                    if thisflagteam == GEGlobal.TEAM_MI6:
                        mi_flags += 1
                    if thisflagteam == GEGlobal.TEAM_JANUS:
                        js_flags += 1

            # Store out values before adding micro t
            if self.MI6Flags != mi_flags or barwidth != self.FlagCount:
                self.ShowMI6Flags = True
            if self.JanusFlags != js_flags or barwidth != self.FlagCount:
                self.ShowJanusFlags = True

            self.MI6Flags = mi_flags
            self.JanusFlags = js_flags
            self.FlagCount = barwidth

            microt = barwidth * 0.05
            barwidth += microt
            mi_flags += microt
            js_flags += microt

            GEUtil.InitHudProgressBar( None, 2, "", GEGlobal.HUDPB_SHOWBAR, barwidth, .1875, .920, self.BAR_TEAMBALANCE, 10, self.COLOR_H_MI )
            GEUtil.InitHudProgressBar( None, 3, "", GEGlobal.HUDPB_SHOWBAR, barwidth, .1875, .905, self.BAR_TEAMBALANCE, 10, self.COLOR_P_JS )
            GEUtil.UpdateHudProgressBar( None, 2, mi_flags )
            GEUtil.UpdateHudProgressBar( None, 3, js_flags )
        else:
            GEUtil.RemoveHudProgressBar( None, 2 )
            GEUtil.RemoveHudProgressBar( None, 3 )

    def ft_zot( self ):
        GEMPGameRules.GetTokenMgr().SetupToken( self.TokenClass, limit=0 )
        for j in range( self.FLAGLIST_LIMIT ) :
            self.flaglist[j].zot()

    def ft_zot_token( self, token ):
        j = self.ft_flagindexbytoken( token )
        if j >= 0 :
            self.flaglist[j].zot()
        else:
            ep_shout( "[Zot Token] Attempted to remove unregistered token %d" % GEEntity.GetUID( token ) )

    # Engine callbacks
    def __init__( self ):
        super( LivingDaylights, self ).__init__()
        self.TokenClass = 'token_deathmatch'
        self.TokenGlow = GEUtil.CColor( 244, 192, 11, 64 )

        self.MI6Flags = 0
        self.JanusFlags = 0
        self.FlagCount = 0
        self.ShowMI6Flags = True
        self.ShowJanusFlags = True

    def GetGameDescription( self ):
        if GEMPGameRules.IsTeamplay():
            return "Team Living Daylights"
        return "Living Daylights"

    def GetPrintName( self ):
        return "#GES_GP_LD_NAME"

    def GetScenarioHelp( self, help_obj ):
        assert isinstance( help_obj, GEScenarioHelp )

        help_obj.SetInfo( "#GES_GPH_LD_TAGLINE", "http://wiki.geshl2.com/index.php/Living_Daylights" )
        help_obj.SetDescription( "#GES_GP_LD_HELP" )

        pane = help_obj.AddPane( "ld" )
        help_obj.AddHelp( pane, "ld_earnpoints1", "" )
        help_obj.AddHelp( pane, "ld_earnpoints2", "#GES_GPH_LD_FLAG_POINTS" )

    def GetTeamPlay( self ):
        return GEGlobal.TEAMPLAY_TOGGLE

    def OnThink( self ):
        if self.ft_gameislive():
            self.ft_ageflags()
            self.ft_progressbars()

    def OnPlayerKilled( self, victim, killer, weapon ):
        if victim == None:
            return
        # Disconnecting player_previous to prevent multiple penalties.
        flagindex = self.ft_flagindexbyplayer( victim )
        if flagindex >= 0:
            self.flaglist[flagindex].player_previous = 0
            GEUtil.EmitGameplayEvent( "ld_flagdropped", str( victim.GetUserID() ), str( killer.GetUserID() ) )

        vid = GEEntity.GetUID( victim )
        kid = GEEntity.GetUID( killer )
        ep_shout( "[OPK] Victim %d, Killer %d, VFlag Index %d" % ( vid, kid, flagindex ) )
        bounty = min( self.flaglist[flagindex].earnings, self.flaglist[flagindex].LEVEL_LIMIT )

        # Suicide
        if killer == None or killer.GetIndex() == 0 or vid == kid or GEMPGameRules.IsTeamplay() and victim.GetTeamNumber() == killer.GetTeamNumber():
            suicide_bounty = -choice( flagindex >= 0, bounty + bounty, 1 )
            ep_incrementscore( victim, suicide_bounty )
            if flagindex >= 0:
                GEUtil.EmitGameplayEvent( "ld_flagpoint", str( victim.GetUserID() ), "-1", "suicide", str( suicide_bounty ) )
            return

        # slap and snatch TODO: Verify
        if weapon != None and weapon.GetClassname() == "weapon_slappers" and flagindex >= 0:
            delta = choice( flagindex >= 0, bounty, 0 )
            if delta > 0:
                ep_incrementscore( victim, -delta )
                GEUtil.HudMessage( victim, _( plural( delta, "#GES_GP_LD_LOSEPOINTS" ), delta ), -1, -1, EP_SHOUT_COLOR, 2.0 )
                ep_incrementscore( killer, delta )
                GEUtil.HudMessage( killer, _( plural( delta, "#GES_GP_LD_STOLEPOINTS" ), delta ), -1, -1, EP_SHOUT_COLOR, 2.0 )
                GEUtil.EmitGameplayEvent( "ld_flagpoint", str( victim.GetUserID() ), str( killer.GetUserID() ), "slapperkill", str( -delta ) )

        # credit if token will be removed from play. TODO: Verify
        if self.ft_flagdebt() < 0:
            if flagindex >= 0:
                ep_incrementscore( killer, self.flaglist[flagindex].level )
            else:
                ep_shout( "[OPK] No flag index associated with slain carrier whose flag is removed." )

    def OnPlayerSay( self, player, text ):
        return False

    def OnLoadGamePlay( self ):
        self.CreateCVar( "ld_playersperflag", "4", "Number of players per flag spawned." )
        self.CreateCVar( "ld_teamguardians", "0", "Flags are withheld to ensure this many players must guard on the shortest team. One flag will always be available." )

        tokenmgr = GEMPGameRules.GetTokenMgr()
        tokenmgr.SetupToken( self.TokenClass, limit=1, location=GEGlobal.SPAWN_TOKEN, allow_switch=False,
                            glow_color=self.TokenGlow, respawn_delay=30.0, print_name="#GES_GP_LD_OBJ",
                            view_model="models/weapons/tokens/v_flagtoken.mdl",
                            world_model="models/weapons/tokens/w_flagtoken.mdl" )

        GEMPGameRules.GetRadar().SetForceRadar( True )

        GEUtil.PrecacheSound( "GEGamePlay.Token_Chime" )
        GEUtil.PrecacheSound( "GEGamePlay.Token_Knock" )
        GEUtil.PrecacheSound( "GEGamePlay.Token_Grab" )
        GEUtil.PrecacheSound( "Buttons.beep_ok" )
        GEUtil.PrecacheSound( "Buttons.beep_denied" )

    def OnRoundBegin( self ):
        self.ft_zot()
        GEMPGameRules.ResetAllPlayersScores()

    def OnRoundEnd( self ):
        GEMPGameRules.GetRadar().DropAllContacts()

    def OnPlayerSpawn( self, player ):
        assert isinstance( player, GEPlayer.CGEMPPlayer )

        player.SetSpeedMultiplier( 1.0 )
        player.SetScoreBoardColor( GEGlobal.SB_COLOR_NORMAL )
        player.SetMaxArmor( int( GEGlobal.GE_MAX_ARMOR ) )
        player.GiveNamedWeapon( "weapon_slappers", 0 )
        self.ft_shepherd()
        self.ft_teambalancebars()
        self.ft_showteamflags( player )

    def CanPlayerChangeTeam( self, player, oldteam, newteam ):
        # If we switched from DM to Team (or vice versa) or Spectating, reset help
        if oldteam == GEGlobal.TEAM_SPECTATOR \
          or oldteam == GEGlobal.TEAM_NONE and newteam >= GEGlobal.TEAM_MI6 \
          or oldteam >= GEGlobal.TEAM_MI6 and newteam == GEGlobal.TEAM_NONE:
            # Reset this players help archive so they don't recall old help
            player.SetInitialSpawn( True )

        return True

    def CanPlayerHaveItem( self, player, item ):
# 		itemname = entity.GetClassname()
        return self.ft_omnomnomnom( player, item.GetClassname() )
# 		return not (itemname.startswith("item_armorvest") and self.ft_flagindexbyplayer(player) >= 0)

    def ShouldForcePickup( self, player, item ):
        if self.ft_playercarries( player ):
            GEUtil.PlaySoundTo( player, "HL2Player.PickupWeapon" )
            return True
        return False

    def CalculateCustomDamage( self, victim, info, health, armour ):
        assert isinstance( victim, GEPlayer.CGEMPPlayer )
        if victim == None:
            return health, armour
        killer = GEPlayer.ToMPPlayer( info.GetAttacker() )
        v_flagindex = self.ft_flagindexbyplayer( victim )
        k_flagindex = self.ft_flagindexbyplayer( killer )
        # ep_shout("[SDCD] %d %d" % (v_flagindex, k_flagindex) )
        if v_flagindex >= 0:
            # Suicide or friendly fire exacerbates but does not trigger escape.
            total_damage = health + armour
            if killer == None or GEEntity.GetUID( victim ) == GEEntity.GetUID( killer ) or GEMPGameRules.IsTeamplay() and victim.GetTeamNumber() == killer.GetTeamNumber():
                self.flaglist[v_flagindex].escape( False, total_damage )
            else:
                self.flaglist[v_flagindex].escape( True, total_damage )
                self.ft_escapebar( self.flaglist[v_flagindex], victim )
        if k_flagindex >= 0:
            # Flag carrier steals a point on successful attack.
            if victim.GetRoundScore() > 0:
                ep_incrementscore( victim, -self.THEFT_DELTA )
                ep_incrementscore( killer, self.THEFT_DELTA )
                GEUtil.PlaySoundTo( killer, "Buttons.beep_ok" )
                GEUtil.PlaySoundTo( victim, "Buttons.Token_Knock" )
                ep_shout( "Point stolen from %s via slap." % victim.GetPlayerName() )
                GEUtil.EmitGameplayEvent( "ld_flagpoint", str( killer.GetUserID() ), str( victim.GetUserID() ), "flaghit", "1" )
        return health, armour

    def CalcFinalScores( self ):
        pass

    def OnTokenSpawned( self, token ):
        self.ft_registerflag( GEEntity.GetUID( token ) )
        GEMPGameRules.GetRadar().AddRadarContact( token, GEGlobal.RADAR_TYPE_TOKEN, True, "", self.COLOR_COLD )
        GEMPGameRules.GetRadar().SetupObjective( token, GEGlobal.TEAM_NONE, "!%s" % self.TokenClass, "#GES_GP_LD_OBJ_TAKE", GEUtil.CColor( 220, 220, 220, 200 ) )
        token.SetSkin( 0 )
        self.ft_teambalancebars()
        self.ft_showteamflags()

    def OnTokenPicked( self, token, player ):
        player.SetScoreBoardColor( GEGlobal.SB_COLOR_WHITE )
        GEMPGameRules.GetRadar().DropRadarContact( token )
        GEMPGameRules.GetRadar().AddRadarContact( player, GEGlobal.RADAR_TYPE_PLAYER, True, "sprites/hud/radar/run", choice( GEMPGameRules.IsTeamplay(), choice( player.GetTeamNumber() == GEGlobal.TEAM_MI6, self.COLOR_H_MI, self.COLOR_H_JS ), self.COLOR_HOLD ) )
        GEUtil.PlaySoundTo( player, "GEGamePlay.Token_Grab" )
        GEUtil.EmitGameplayEvent( "ld_flagpickup", str( player.GetUserID() ) )
        flagindex = self.ft_flagindexbytoken( token )
        if GEMPGameRules.IsTeamplay() and flagindex >= 0 and self.flaglist[flagindex].team_previous == player.GetTeamNumber() :
            self.ft_associate( token, player )
        else:
            self.ft_coldflaglevel( self.ft_associate( token, player ) )

        # Support team colors!
        if GEMPGameRules.IsTeamplay():
            if player.GetTeamNumber() == GEGlobal.TEAM_MI6:
                skin = 1
                color = self.COLOR_MI6
            else:
                skin = 2
                color = self.COLOR_JS

            token.SetSkin( skin )
            GEMPGameRules.GetRadar().SetupObjective( player, GEGlobal.TEAM_NONE, "!%s" % self.TokenClass, "", color )
        else:
            GEMPGameRules.GetRadar().SetupObjective( player, GEGlobal.TEAM_NONE, "!%s" % self.TokenClass, "", self.COLOR_HOLD )

        health_coefficient = 2.0 * float( player.GetHealth() + player.GetArmor() ) / float( player.GetMaxHealth() + player.GetMaxArmor() )
        player.SetHealth( int( GEGlobal.GE_MAX_HEALTH ) )
        player.SetArmor( int( GEGlobal.GE_MAX_ARMOR ) )
        # Suppress Armor pickup
        player.SetMaxArmor( 0 )
        self.flaglist[self.ft_flagindexbytoken( token )].age_item( 3, health_coefficient )
        self.ft_teambalancebars()
        self.ft_showteamflags()

    def OnTokenDropped( self, token, player ):
        player.SetScoreBoardColor( GEGlobal.SB_COLOR_NORMAL )
        if self.ft_flagdebt() >= 0:
            GEMPGameRules.GetRadar().AddRadarContact( token, GEGlobal.RADAR_TYPE_TOKEN, True, "", self.COLOR_WARM )
            GEMPGameRules.GetRadar().SetupObjective( token, GEGlobal.TEAM_NONE, "!%s" % self.TokenClass, "#GES_GP_LD_OBJ_TAKE", GEUtil.CColor( 220, 220, 220, 200 ) )
            GEMPGameRules.GetRadar().DropRadarContact( player )
            self.ft_disassociate( token, False )
        else:
            GEMPGameRules.GetTokenMgr().RemoveTokenEnt( token )

        self.ft_teambalancebars()
        self.ft_showteamflags()
        token.SetSkin( 0 )

    def OnTokenRemoved( self, token ):
        self.ft_disassociate( token, True )
        GEMPGameRules.GetRadar().DropRadarContact( token )
        GEMPGameRules.GetRadar().DropRadarContact( token.GetOwner() )
        self.ft_teambalancebars()
        self.ft_showteamflags()
