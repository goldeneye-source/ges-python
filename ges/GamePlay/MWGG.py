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
from GEUtil import Color
from .Utils import GetPlayers, _
import GEEntity, GEUtil, GEMPGameRules as GERules, GEGlobal as Glb

USING_API = Glb.API_VERSION_1_2_0

class MWGG( GEScenario ):
    gg_glow_color = Color( 232, 180, 2, 64 )
    gg_owner_color = Color( 232, 180, 2, 255 )
    gg_dropped_color = Color( 232, 180, 2, 100 )
    gg_held_color = Color( 232, 180, 2, 230 )

    def __init__( self ):
        super( MWGG, self ).__init__()

        self.gg_classname = "weapon_golden_gun"   # Classname of the weapon being used as the golden gun
        self.gg_owner = None                      # The ID of the player currently carrying the golden gun
        self.gg_armorcap = Glb.GE_MAX_ARMOR  # The max amount of armor the GG carrier can have their armor set to after a pickup.

    def GetPrintName( self ):
        return "#GES_GP_MWGG_NAME"

    def GetScenarioHelp( self, help_obj ):
        help_obj.SetDescription( "#GES_GP_MWGG_HELP" )

    def GetGameDescription( self ):
        return "MWGG"

    def GetTeamPlay( self ):
        return Glb.TEAMPLAY_NONE

    def OnLoadGamePlay( self ):
        super( MWGG, self ).OnLoadGamePlay()
        GERules.GetTokenMgr().SetupToken( self.gg_classname, limit=1, respawn_delay=20.0,
                            location=Glb.SPAWN_WEAPON | Glb.SPAWN_SPECIALONLY,
                            glow_color=self.gg_glow_color )

        GERules.GetTokenMgr().SetGlobalAmmo( self.gg_classname, 2 )
        GERules.GetRadar().SetForceRadar( True )

    def OnPlayerSpawn( self, player ):
        # Wipe any MWGG status effects, just in case.
        player.SetMaxArmor( int( Glb.GE_MAX_ARMOR ) )
        player.SetScoreBoardColor( Glb.SB_COLOR_NORMAL )

        if player.IsInitialSpawn():
            GEUtil.PopupMessage( player, "#GES_GPH_OBJECTIVE", "#GES_GPH_MWGG_GOAL", "mwgg_goal" )

    # Take off any damage the MWGG receives from his armor pickup cap.
    def CalculateCustomDamage( self, victim, info, health, armour ):
        if victim.GetUID() == self.gg_owner and self.gg_armorcap > 0 and armour > 0:
            self.gg_armorcap = max(self.gg_armorcap - armour, 0) #Subtract the armor damage from the max armor the carrier can pick up this life.
        
        return health, armour

    # Regulates how much armor the MWGG can pick up.  Does not affect his pickup cap since the damage event regulates that.
    def CanPlayerHaveItem( self, player, item ):
        if player.GetUID() == self.gg_owner:
            if item.GetClassname().startswith( "item_armorvest" ):
                amount = int( Glb.GE_MAX_ARMOR )
                armorcap = player.GetMaxArmor()
                
                if item.GetClassname().startswith( "item_armorvest_half" ):
                    amount /= 2
                
                if player.GetArmor() < 160 and player.GetArmor() < self.gg_armorcap:
                    player.SetArmor( int(amount * -1 + min(amount, self.gg_armorcap, armorcap))) #amount * -1 is there to negate the armor given by the pickup
                    return True
                
                return False
            
        return True

    def OnThink( self ):
        if self.gg_armorcap < Glb.GE_MAX_ARMOR or self.gg_armorcap == 0: #We have to check for this here since we can't immediately set max armor on the armorpickup event without denying the pickup.
            for player in GetPlayers():
                if player.GetUID() == self.gg_owner and player.GetArmor() >= self.gg_armorcap:
                    player.SetMaxArmor(0) # The GG carrier can't pick up any more armor, let them know by turning their armor gauge red.
                    self.gg_armorcap = 0
                    
    def OnTokenSpawned( self, token ):
        GERules.GetRadar().AddRadarContact( token, Glb.RADAR_TYPE_TOKEN, True, "ge_radar_gg" )
        GERules.GetRadar().SetupObjective( token, Glb.TEAM_NONE, "", "", self.gg_dropped_color )

    def OnTokenPicked( self, token, player ):
        radar = GERules.GetRadar()
        radar.DropRadarContact( token )
        radar.AddRadarContact( player, Glb.RADAR_TYPE_PLAYER, True, "", self.gg_owner_color )

        # Pickup event effects.
        GEUtil.PlaySoundTo( player, "GEGamePlay.Token_Grab" )
        msg = _( "#GES_GP_MWGG_PICKED", player.GetCleanPlayerName() )
        GEUtil.PostDeathMessage( msg )
        GEUtil.EmitGameplayEvent( "mwgg_ggpickup", str( player.GetUserID() ), "", "", "", True )
        GEUtil.HudMessage( player, "#GES_GP_MWGG_HAVEGG", -1, 0.75, self.gg_owner_color, 3.0 )

        # Modifications to the MWGG
        radar.SetPlayerRangeMod( player, 0.5 )
        player.SetScoreBoardColor( Glb.SB_COLOR_GOLD )
        self.gg_owner = player.GetUID()
        player.GiveNamedWeapon( "weapon_golden_gun", 7 ) #This is just to give extra ammo
        self.gg_armorcap = int( Glb.GE_MAX_ARMOR ) #Total armor for the rest of the life is capped at 160

    def OnTokenDropped( self, token, player ):
        radar = GERules.GetRadar()
        radar.DropRadarContact( player )
        radar.AddRadarContact( token, Glb.RADAR_TYPE_TOKEN, True, "ge_radar_gg" )
        radar.SetupObjective( token, Glb.TEAM_NONE, "", "", self.gg_dropped_color )

        msg = _( "#GES_GP_MWGG_DROPPED", player.GetCleanPlayerName() )
        GEUtil.PostDeathMessage( msg )
        player.SetScoreBoardColor( Glb.SB_COLOR_NORMAL )
        self.gg_owner = None

    def OnTokenRemoved( self, token ):
        # Prepare the golden gun for respawn by wiping all its associated data.
        GERules.GetRadar().DropRadarContact( token )
        GERules.GetRadar().DropRadarContact( token.GetOwner() )
        self.gg_owner = None
