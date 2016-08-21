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
from . import BaseTask
import GEEntity, GEWeapon, GEUtil, GEAiTasks, GEGlobal as Glb, GEMPGameRules as GERules
from GEGamePlay import GetScenario
from GEGamePlay import CBaseScenario

class FindEnemy( BaseTask ):
    def Start( self, npc, data ):
        # Grab our contacts from the radar from our perspective and sort by range
        contacts = [c for c in GERules.GetRadar().ListContactsNear( npc.GetAbsOrigin() ) if c["type"] == Glb.RADAR_TYPE_PLAYER]
        contacts.sort( key=lambda x: x["range"] )

        # If we have at least 1 contact, mark him
        for contact in contacts:
            if not GERules.IsTeamplay() or contact["team"] != npc.GetTeamNumber():
                npc.SetTargetPos( contact["origin"] )
                self.Complete( npc )
                return

        # We didn't find anything
        self.Fail( npc, "No enemies in range" )

class FindAmmo( BaseTask ):
    def Start( self, npc, data ):
        from Ai import PYBaseNPC, AiSystems
        from Ai.Utils import Memory

        assert isinstance( npc, PYBaseNPC )

        if data <= 0:
            data = 512

        # combine that list of ammo with the item tracker's list
        ammocrates = GetScenario().itemTracker.ammocrates

        if len( ammocrates ) > 0:
            # we must start with a bestChoice, so choose the first one until we know better
            bestChoice = None

            # find closest ammocrate
            for ammocrate in ammocrates:
                if npc.GetSystem( AiSystems.WEAPONS ).WantsAmmoCrate( ammocrate, bestChoice ):
                    bestChoice = ammocrate

            if bestChoice != None:
                # target closest ammo
                npc.SetTarget( bestChoice )
                self.Complete( npc )
                return

        # We failed to find anything, fail the task
        npc.TaskFail( GEAiTasks.TaskFail.NO_TARGET )

class FindWeapon( BaseTask ):
   
    def Start( self, npc, data ):
        from Ai import PYBaseNPC, AiSystems

        assert isinstance( npc, PYBaseNPC )

        if data <= 0:
            data = 512

        # grab weapons nearby (this searches for dropped weapons which don't show up in itemTracker by default)
        weaponsNearby = GEEntity.GetEntitiesInBox( "weapon_*", npc.GetAbsOrigin(), GEUtil.Vector( -data, -data, -10 ), GEUtil.Vector( data, data, 120 ) )

        # combine that list of weapons with the item tracker's list
        weapons = list( set( GetScenario().itemTracker.weapons + weaponsNearby ) )
        
        if len( weapons ) > 0:
            bestChoice = None

            # find closest weapon
            for weapon in weapons:
                if npc.GetSystem( AiSystems.WEAPONS ).WantsWeapon( weapon, bestChoice ):
                    bestChoice = weapon
        
            if bestChoice != None:
                # target closest weapon
                npc.SetTarget( bestChoice )
                self.Complete( npc )
                return

        # We failed to find anything, fail the task
        npc.TaskFail( GEAiTasks.TaskFail.NO_TARGET )

class FindArmor( BaseTask ):
    def Start( self, npc, data ):
        from Ai import PYBaseNPC, AiSystems

        assert isinstance( npc, PYBaseNPC )

        armorvests = GetScenario().itemTracker.armorvests

        if len( armorvests ) > 0:
            # we must start with a bestChoice, so choose the first one until we know better
            bestChoice = armorvests[0]

            # find closest armor
            for armor in armorvests:
                if npc.GetAbsOrigin().DistTo( armor.GetAbsOrigin() ) < npc.GetAbsOrigin().DistTo( bestChoice.GetAbsOrigin() ):
                    bestChoice = armor
        
            # target closest armor
            npc.SetTarget( bestChoice )
            self.Complete( npc )
            return

        # We failed to find anything, fail the task
        npc.TaskFail( GEAiTasks.TaskFail.NO_TARGET )

class FindToken( BaseTask ):
    def Start( self, npc, data ):
        from Ai import PYBaseNPC
        assert isinstance( npc, PYBaseNPC )

        target = npc.GetTokenTarget()
        if not target:
            self.Fail( npc, "No token target specified by NPC" )
            return

        # Grab our contacts from the radar from our perspective and sort by range
        contacts = [c for c in GERules.GetRadar().ListContactsNear( npc.GetAbsOrigin() ) if self.ShouldSeek( npc, c )]
        contacts.sort( key=lambda x: x["range"] )

        # Reset the target
        npc.SetTokenTarget( None )

        # If we have at least 1 contact, mark it
        if len( contacts ) > 0:
            npc.SetTargetPos( contacts[0]["origin"] )
            self.Complete( npc )
            return

        # We didn't find anything
        self.Fail( npc, "No tokens in range" )

    def ShouldSeek( self, npc, contact ):
        if contact["classname"] != npc.GetTokenTarget():
            return False
        if npc.GetTokenTeam() and contact["team"] != npc.GetTokenTeam():
            return False
        return True

