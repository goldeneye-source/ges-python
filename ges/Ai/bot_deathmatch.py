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
import random

from GEAiConst import Class, State, Capability as Cap, Disposition as D
import GEUtil, GEEntity, GEPlayer, GEWeapon, GEMPGameRules as GERules, GEGlobal as Glb

from . import PYBaseNPC, AiSystems
from .Utils import Memory, Weapons
from .Schedules import Sched, Cond

USING_API = Glb.API_VERSION_1_1_0

class bot_deathmatch( PYBaseNPC ):
    def __init__( self, parent ):
        PYBaseNPC.__init__( self, parent )
        self._min_weap_weight = Weapons.Weight.WORST
        self._max_weap_weight = Weapons.Weight.BEST
        self._medium_weap_weight = Weapons.Weight.MEDIUM

        self.justSpawned = False
        self.time_ignore_no_target_until = GEUtil.GetTime()
        self.time_ignore_new_target_until = GEUtil.GetTime()

        # Register our custom memory callback
        self.GetSystem( AiSystems.MEMORY )._callback = self.bot_MemoryCallback
        self.GetSystem( AiSystems.WEAPONS ).param_callback = self.bot_WeaponParamCallback

        # Add bot specific capabilities
        self.AddCapabilities( Cap.USE_WEAPONS | Cap.USE_SHOT_REGULATOR )
        self.AddCapabilities( Cap.WEAPON_MELEE_ATTACK | Cap.WEAPON_RANGE_ATTACK | Cap.MOVE_SHOOT )

        # Add bot specific relationships
        self.AddClassRelationship( Class.GES_BOT, D.HATE, 5 )
        self.AddClassRelationship( Class.PLAYER, D.HATE, 5 )

        random.seed( GEUtil.GetTime() )

    def GetModel( self ):
        return "models/players/bond/bond.mdl"

    def Classify( self ):
        return Class.GES_BOT

    def OnSpawn( self ):
        PYBaseNPC.OnSpawn( self )

        min_weight = Weapons.Weight.BEST
        max_weight = Weapons.Weight.WORST
        loadout = GERules.GetWeaponLoadout()
        for id_ in loadout:
            weap_info = GEWeapon.WeaponInfo( id_ )
            if "weight" in weap_info:
                if weap_info["weight"] < min_weight:
                    min_weight = weap_info["weight"]
                elif weap_info["weight"] > max_weight:
                    max_weight = weap_info["weight"]

        self._min_weap_weight = min_weight
        self._max_weap_weight = max_weight
        self._medium_weap_weight = (min_weight + max_weight) / 2.0

        self.ClearSchedule();
        self.justSpawned = False

    def IsValidEnemy( self, enemy ):
        myteam = self.GetTeamNumber()
        if myteam != Glb.TEAM_NONE and enemy.GetTeamNumber() == self.GetTeamNumber():
            return False

        return True

    def GatherConditions( self ):
        self.ClearCondition( Cond.NO_PRIMARY_AMMO )
        self.ClearCondition( Cond.LOW_PRIMARY_AMMO )
        self.ClearCondition( Cond.GES_LOW_AMMO )
        self.ClearCondition( Cond.GES_ENEMY_FAR )
        self.ClearCondition( Cond.GES_ENEMY_CLOSE )
        self.ClearCondition( Cond.GES_CAN_SEEK_ARMOR )
        self.ClearCondition( Cond.GES_CAN_NOT_SEEK_ARMOR )
        self.ClearCondition( Cond.GES_CLOSE_TO_ARMOR )
        self.ClearCondition( Cond.GES_NO_TARGET )

        if self.HasCondition( Cond.TOO_CLOSE_TO_ATTACK ):
            self.SetCondition( Cond.CAN_RANGE_ATTACK1 )
            self.ClearCondition( Cond.TOO_CLOSE_TO_ATTACK ) #TODO: DONT CLEAR IF CURRENT WEAPON IS EXPLOSIVE

        memory = self.GetSystem( AiSystems.MEMORY )

        if self.GetTarget() is None:
            if self.time_ignore_no_target_until <= GEUtil.GetTime():
                self.SetCondition( Cond.GES_NO_TARGET )

        if self.GetEnemy() is not None:
            # Set condition of enemy distance
            dist_to_enemy = self.GetEnemy().GetAbsOrigin().DistTo( self.GetAbsOrigin() )
            if dist_to_enemy > 800:
                self.SetCondition( Cond.GES_ENEMY_FAR )
            elif dist_to_enemy < 200:
                self.SetCondition( Cond.GES_ENEMY_CLOSE )

            # Set condition of enemy "strength"
            try:
                enemy_weapon = self.GetEnemy().GetActiveWeapon()
                if enemy_weapon and enemy_weapon.GetWeight() > max( Weapons.Weight.MEDIUM, self._max_weap_weight - 1 ):
                    self.SetCondition( Cond.GES_ENEMY_DANGEROUS )
                elif enemy_weapon and enemy_weapon.IsMeleeWeapon():
                    self.SetCondition( Cond.GES_ENEMY_UNARMED )
            except:
                pass

            # Should we switch enemies?
            if self.time_ignore_new_target_until < GEUtil.GetTime():
                self.ClearCondition( Cond.NEW_ENEMY )
                self.time_ignore_new_target_until = GEUtil.GetTime() + 1

                seen = self.GetSeenEntities()

                if self.GetEnemy() != None and not self.GetEnemy().IsAlive():
                    self.SetEnemy(None)

                closestEnemy = None
                for ent in seen:
                    player = GEPlayer.ToMPPlayer( ent )
                    if player != None and player.IsAlive():
                        if not GERules.IsTeamplay() or player.GetTeamNumber() != self.GetTeamNumber():
                            if closestEnemy == None:
                                closestEnemy = player
                            elif self.GetAbsOrigin().DistTo( player.GetAbsOrigin() ) < self.GetAbsOrigin().DistTo( closestEnemy.GetAbsOrigin() ):
                                closestEnemy = player

                closestContact = None
                contacts = [c for c in GERules.GetRadar().ListContactsNear( self.GetAbsOrigin() ) if c["type"] == Glb.RADAR_TYPE_PLAYER]
                for contact in contacts:
                    player = GEPlayer.ToMPPlayer( GEEntity.GetEntByUniqueId( contact["ent_handle"].GetUID() ) )
                    if player != None and player.IsAlive():
                        if not GERules.IsTeamplay() or player.GetTeamNumber() != self.GetTeamNumber():
                            if closestContact == None:
                                closestContact = player
                            elif self.GetAbsOrigin().DistTo( player.GetAbsOrigin() ) < self.GetAbsOrigin().DistTo( closestContact.GetAbsOrigin() ):
                                closestContact = player

                if closestContact != None:
                    if closestEnemy == None:
                        closestEnemy = closestContact
                    elif self.GetAbsOrigin().DistTo( closestContact.GetAbsOrigin() ) < self.GetAbsOrigin().DistTo( closestEnemy.GetAbsOrigin() ) * 0.6:
                        closestEnemy = closestContact

                newEnemy = False
                if closestEnemy != None:
                    if self.GetEnemy() == None \
                        or self.GetAbsOrigin().DistTo( closestEnemy.GetAbsOrigin() ) < self.GetAbsOrigin().DistTo( self.GetEnemy().GetAbsOrigin() ) * 0.8:
                        self.SetEnemy( closestEnemy )
                        self.time_ignore_new_target_until = GEUtil.GetTime() + 5
                        newEnemy = True
                
                self.ClearCondition( Cond.SEE_ENEMY )
                if self.GetEnemy() != None and self.GetEnemy() in seen:
                    self.SetCondition( Cond.SEE_ENEMY )
                    if newEnemy:
                        self.SetCondition( Cond.NEW_ENEMY )

        # Ammo Checks
        currWeap = self.GetActiveWeapon()
        assert isinstance( currWeap, GEWeapon.CGEWeapon )
        if currWeap and not currWeap.IsMeleeWeapon() and currWeap.GetWeaponId() != Glb.WEAPON_MOONRAKER:

            if ( currWeap.GetMaxClip() > 0 and currWeap.GetAmmoCount() < ( currWeap.GetMaxClip() * 2 ) ) \
                or currWeap.GetAmmoCount() <= currWeap.GetMaxAmmoCount() / 4.0:
                self.SetCondition( Cond.GES_LOW_AMMO )

            if currWeap.GetAmmoCount() <= currWeap.GetMaxAmmoCount() / 100:
                # We have very little ammo left for this weapon
                self.SetCondition( Cond.NO_PRIMARY_AMMO )
            elif currWeap.GetMaxClip() > 0 and currWeap.GetClip() < ( currWeap.GetMaxClip() / 8.0 ):
                # We are running out of our clip
                self.SetCondition( Cond.LOW_PRIMARY_AMMO )

        if currWeap and currWeap.GetWeight() < self._medium_weap_weight:
            self.SetCondition( Cond.LOW_WEAPON_WEIGHT )

        # Armor checks
        from GEGamePlay import GetScenario
        from GEGamePlay import CBaseScenario
        armorvests = GetScenario().itemTracker.armorvests
        if len(armorvests) > 0:
            if self.GetArmor() < self.GetMaxArmor():
                self.SetCondition( Cond.GES_CAN_SEEK_ARMOR )
            else:
                self.SetCondition( Cond.GES_CAN_NOT_SEEK_ARMOR )

            # find close armor
            for armor in armorvests:
                if self.GetAbsOrigin().DistTo( armor.GetAbsOrigin() ) < 512:
                    self.SetCondition( Cond.GES_CLOSE_TO_ARMOR )
                    break
        else:
            self.SetCondition( Cond.GES_CAN_NOT_SEEK_ARMOR )

    def TranslateSchedule( self, schedule ):
        if schedule == Sched.COMBAT_FACE:
            return Sched.BOT_COMBAT_FACE
        elif schedule == Sched.RANGE_ATTACK1:
            return Sched.BOT_RANGE_ATTACK1
        else:
            return Sched.NO_SELECTION

    def SelectSchedule( self ):

        # Run away from explosions!
        if self.HasCondition( Cond.HEAR_DANGER ):
            return Sched.TAKE_COVER_FROM_BEST_SOUND

        # Run away from enemies / keep them at a distance
        if self.HasCondition( Cond.SEE_ENEMY ) \
            and not self.HasCondition( Cond.CAN_MELEE_ATTACK1 ) \
            and (self.HasCondition( Cond.TOO_CLOSE_TO_ATTACK ) or self.HasCondition( Cond.GES_ENEMY_CLOSE )):
            return Sched.RUN_FROM_ENEMY_FALLBACK

        # Take cover from enemies when we're hurt or they're dangerous
        if self.HasCondition( Cond.SEE_ENEMY ) \
            and not self.HasCondition( Cond.CAN_MELEE_ATTACK1 ) \
            and random.random() < 0.2:

            if self.HasCondition( Cond.HEAVY_DAMAGE ) \
                or self.HasCondition( Cond.LIGHT_DAMAGE ) \
                or self.HasCondition( Cond.HEAR_BULLET_IMPACT ):
                return Sched.BOT_TAKE_COVER_FROM_ENEMY

            if self.HasCondition( Cond.GES_ENEMY_CLOSE ) \
                or self.HasCondition( Cond.GES_ENEMY_DANGEROUS ):
                return Sched.BOT_TAKE_COVER_FROM_ENEMY

        # we need to clear this because we haven't set a target yet
        # and NO TARGET interrupts
        self.time_ignore_no_target_until = GEUtil.GetTime() + 0.5
        self.ClearCondition( Cond.GES_NO_TARGET )
        self.SetTarget( None )

        # If we have a melee weapon out, seek out a better weapon immediately and don't get distracted
        if self.HasCondition( Cond.CAN_MELEE_ATTACK1 ) \
            and self.HasCondition( Cond.BETTER_WEAPON_AVAILABLE ):
            return Sched.BOT_SEEK_WEAPON_DETERMINED

        # If we have a very weak weapon, go grab a better one as soon as you can (and don't get distracted)
        if self.HasCondition( Cond.GES_CLOSE_TO_WEAPON ) \
            and self.HasCondition( Cond.BETTER_WEAPON_AVAILABLE ) \
            and self.HasCondition( Cond.LOW_WEAPON_WEIGHT ):
            return Sched.BOT_SEEK_WEAPON_DETERMINED

        # If we're near armor and have the chance to grab it, do so (and don't get distracted)
        if self.HasCondition( Cond.GES_CLOSE_TO_ARMOR ) \
            and self.HasCondition( Cond.GES_CAN_SEEK_ARMOR ) \
            and not self.HasCondition( Cond.GES_CAN_NOT_SEEK_ARMOR ) \
            and (not self.HasCondition( Cond.SEE_ENEMY ) or self.GetHealth() + self.GetArmor() < ( self.GetMaxHealth() + self.GetMaxArmor() ) / 3.0 ):
            return Sched.BOT_SEEK_ARMOR_DETERMINED

        # If we have a very weak weapon, grab a better one (but you can be distracted because you're not close)
        if not self.HasCondition( Cond.SEE_ENEMY ) \
            and self.HasCondition( Cond.LOW_WEAPON_WEIGHT ) \
            and self.HasCondition( Cond.BETTER_WEAPON_AVAILABLE ) \
            and not self.HasCondition( Cond.HEAR_DANGER) \
            and not self.HasCondition( Cond.HEAVY_DAMAGE ):
            return Sched.BOT_SEEK_WEAPON

        # BROKEN FOR NOW I want to set state...
        #if self.HasCondition( Cond.GES_ENEMY_FAR ) \
            #and not self.HasCondition( Cond.SEE_ENEMY ) \
            #and self.GetState() == State.COMBAT:
            #self.SetState( State.ALERT )

        if self.GetState() == State.COMBAT:

            # Low health condition, attempt to find armor or run away
            if self.GetHealth() <= ( self.GetMaxHealth() / 2.0 ) and self.GetArmor() < ( self.GetMaxArmor() / 2.0 ):
                # grab armor if the armor is close and the enemy is far
                if self.GetArmor() < self.GetMaxArmor() \
                    and self.HasCondition( Cond.GES_CAN_SEEK_ARMOR ) \
                    and not self.HasCondition( Cond.GES_CAN_NOT_SEEK_ARMOR ) \
                    and (self.HasCondition( Cond.GES_ENEMY_FAR ) or self.HasCondition( Cond.GES_CLOSE_TO_ARMOR )):
                    return Sched.BOT_SEEK_ARMOR

                # run away if we see a dangerous enemy
                elif self.HasCondition( Cond.GES_ENEMY_DANGEROUS ) \
                    and self.HasCondition( Cond.SEE_ENEMY ) \
                    and self.HasCondition( Cond.GES_ENEMY_CLOSE ):
                    return Sched.RUN_FROM_ENEMY_FALLBACK

            # See a better weapon? grab it
            if not self.HasCondition( Cond.SEE_ENEMY ) \
                and self.HasCondition( Cond.GES_CLOSE_TO_WEAPON ) \
                and self.HasCondition( Cond.BETTER_WEAPON_AVAILABLE ) \
                and not self.HasCondition( Cond.HEAR_DANGER) \
                and not self.HasCondition( Cond.HEAVY_DAMAGE ):
                return Sched.BOT_SEEK_WEAPON

            # Seek ammo if we are almost out
            if self.HasCondition( Cond.GES_LOW_AMMO ) \
                and self.HasCondition( Cond.GES_AMMO_AVAILABLE ):
                return Sched.BOT_SEEK_AMMO_DETERMINED

            # Let the base AI handle combat situations
            return Sched.NO_SELECTION
        else:

            # Seek ammo if we are almost out
            if self.HasCondition( Cond.GES_LOW_AMMO ) \
                and self.HasCondition( Cond.GES_AMMO_AVAILABLE ):
                return Sched.BOT_SEEK_AMMO_DETERMINED

            # Seek armor if we need it
            if self.GetArmor() < self.GetMaxArmor() \
                and self.HasCondition( Cond.GES_CAN_SEEK_ARMOR ) \
                and not self.HasCondition( Cond.GES_CAN_NOT_SEEK_ARMOR ) \
                and ( self.GetHealth() <= 50 or self.HasCondition( Cond.GES_CLOSE_TO_ARMOR ) ):
                return Sched.BOT_SEEK_ARMOR

            # Grab a better weapon if we don't see an enemy
            if not self.HasCondition( Cond.SEE_ENEMY ) \
                and self.HasCondition( Cond.BETTER_WEAPON_AVAILABLE ) \
                and not self.HasCondition( Cond.HEAR_DANGER) \
                and not self.HasCondition( Cond.HEAVY_DAMAGE ):
                return Sched.BOT_SEEK_WEAPON

        hasEnemyOnRadar = len( [c for c in GERules.GetRadar().ListContactsNear( self.GetAbsOrigin() ) if c["type"] == Glb.RADAR_TYPE_PLAYER] ) > 0
        if hasEnemyOnRadar:
            if self.HasCondition( Cond.SEE_ENEMY ):
                return Sched.BOT_ENGAGE_ENEMY
            elif self.HasCondition( Cond.GES_CLOSE_TO_WEAPON ):
                 # BOT_SEEK_ENEMY is interrupted when we're close to a weapon, so we would rather grab it
                return Sched.BOT_SEEK_WEAPON
            else:
                return Sched.BOT_SEEK_ENEMY
        else:
            # We don't see any enemies, walk around at random
            return Sched.BOT_PATROL

    def ShouldInterruptSchedule( self, schedule ):
        # This is for future expansion pack! ;-)
        return False

    def OnDebugCommand( self, cmd ):
        memory = self.GetSystem( AiSystems.MEMORY )
        weapons = self.GetSystem( AiSystems.WEAPONS )

        if cmd == "dump_memory" and memory:
            memory.DumpMemories()
        elif cmd == "dump_weapon":
            weap = self.GetActiveWeapon()
            assert isinstance( weap, GEWeapon.CGEWeapon )
            if weap is not None:
                print( GEWeapon.WeaponInfo( weap.GetWeaponId(), self.GetNPC() ) )
        elif cmd == "debug_memory" and memory:
            memory.debug = ~( memory.debug )
        elif cmd == "debug_weapons" and weapons:
            weapons.debug = ~( weapons.debug )
        else:
            super( bot_deathmatch, self ).OnDebugCommand( cmd )

    def bot_MemoryCallback( self, ent ):
        weap = GEWeapon.ToGEWeapon( ent )
        if weap is not None and not weap.GetClassname().startswith( "token_" ):
            assert isinstance( weap, GEWeapon.CGEWeapon )

            weap_info = GEWeapon.WeaponInfo( weap.GetWeaponId() )
            if weap.GetPlayerOwner():
                # Don't remember player owned weapons
                return ( Memory.PRIORITY_NONE, 0 )
            elif weap.GetOwner():
                # These are weapons owned by a spawner
                if weap.GetWeight() >= Weapons.Weight.HIGH:
                    return ( Memory.PRIORITY_ULTRA, weap_info )
                elif weap.GetWeight() >= Weapons.Weight.MEDIUM:
                    return ( Memory.PRIORITY_HIGH, weap_info )

            # Dropped weapons and low weight weapons get this
            weap_info = GEWeapon.WeaponInfo( weap.GetWeaponId() )
            return ( Memory.PRIORITY_LOW, weap_info )

        elif ent.GetClassname() == "ge_ammocrate":
            return ( Memory.PRIORITY_HIGH, None )

        elif ent.GetClassname().startswith( "item_armorvest" ):
            return ( Memory.PRIORITY_ULTRA, None )

        else:
            return ( Memory.PRIORITY_LOW, None )

    def bot_WeaponParamCallback( self ):
        curr_weap = self.GetActiveWeapon()
        if curr_weap and curr_weap.IsExplosiveWeapon() and self.HasCondition( Cond.TOO_CLOSE_TO_ATTACK ):
            return { "explosive_bonus" :-5, }
        else:
            return { }
