from . import PYTask
from Ai import PYBaseNPC, AiSystems
from Ai.Utils import Memory
import GEEntity, GEWeapon, GEUtil, GEAiTasks, GEGlobal as Glb, GEMPGameRules as GERules

class FindEnemy( PYTask ):
	def Start( self, npc, data ):
		range_sort = lambda x, y: x["range"] > y["range"]

		# Grab our contacts from the radar from our perspective and sort by range
		contacts = [c for c in GERules.GetRadar().ListContactsNear( npc.GetAbsOrigin() ) if c["type"] == Glb.RADAR_TYPE_PLAYER]
		contacts.sort( range_sort )

		# If we have at least 1 contact, mark him
		for contact in contacts:
			if not GERules.IsTeamplay() or contact["team"] != npc.GetTeamNumber():
				npc.SetTargetPos( contact["origin"] )
				self.Complete( npc )
				return

		# We didn't find anything
		self.Fail( npc, "No enemies in range" )

class FindAmmo( PYTask ):
	def Start( self, npc, data ):
		assert isinstance( npc, PYBaseNPC )

		if data <= 0:
			data = 512

		currWeap = npc.GetActiveWeapon().GetClassname()
		memory = npc.GetSystem( AiSystems.MEMORY )

		# If we have a memory, try to find ammo for our current weapon
		if memory is not None:
			weap_memories = memory.FindMemoriesByType( Memory.TYPE_WEAPON )
			for w in weap_memories:
				assert isinstance( w, Memory.Memory )
				if w.classname == currWeap:
					ammo_memories = memory.FindMemoriesNear( w.location, Memory.TYPE_AMMO, data )
					if len( ammo_memories ) > 0:
						npc.SetTargetPos( ammo_memories[0].location )
						self.Complete( npc )
						return

		# If we get here we either don't have a memory or didn't remember an ammo box
		my_pos = npc.GetAbsOrigin()
		ammo = GEEntity.GetEntitiesInBox( "ge_ammocrate", my_pos, GEUtil.Vector( -data, -data, 0 ), GEUtil.Vector( data, data, 120 ) )

		# Sort by closest ammo
		dist_cmp = lambda x, y: cmp( my_pos.DistTo( x.GetAbsOrigin() ), my_pos.DistTo( y.GetAbsOrigin() ) )
		ammo.sort( dist_cmp )

		if len( ammo ) > 0:
			npc.SetTarget( ammo[0] )
			self.Complete( npc )
			return

		# We failed to find anything, fail the task
		npc.TaskFail( GEAiTasks.TaskFail.NO_TARGET )

class FindWeapon( PYTask ):
	def WantsWeapon( self, npc, weapon=None, memory=None ):
		assert isinstance( weapon, GEWeapon.CGEWeapon )
		assert isinstance( memory, Memory.Memory )

		weapon = GEWeapon.ToGEWeapon( weapon )
		my_pos = npc.GetAbsOrigin()
		curr_weap = npc.GetActiveWeapon()

		if not curr_weap:
			return True
		elif weapon:
			return not weapon.GetPlayerOwner() and \
				weapon.GetWeight() >= curr_weap.GetWeight() and \
				weapon.GetAbsOrigin().DistTo( my_pos ) < 2048. and \
				npc.GetAmmoCount( weapon.GetAmmoType() ) < weapon.GetMaxAmmoCount()
		elif memory and type( memory.data ) is dict:
			try:
				dist = memory.location.DistTo( my_pos )
				# If we are close, see if there is actually a weapon there!
				if dist < 500.:
					weaps = GEEntity.GetEntitiesInBox( "weapon_*", memory.location, GEUtil.Vector( -64, -64, -10 ), GEUtil.Vector( 64, 64, 32 ) )
					if len( weaps ) == 0:
						return False
				# Otherwise do a heuristic check
				return memory.data["weight"] >= curr_weap.GetWeight() and \
					dist < 2048. and \
					npc.GetAmmoCount( memory.data["ammo_type"] ) < npc.GetMaxAmmoCount( memory.data["ammo_type"] )
			except:
				return False
		else:
			return False

	def Start( self, npc, data ):
		assert isinstance( npc, PYBaseNPC )

		if data <= 0:
			data = 512

		memory = npc.GetSystem( AiSystems.MEMORY )
		my_pos = npc.GetAbsOrigin()

		# If we have a memory, try to find the best weapon we remember
		if memory is not None:
			weap_memories = memory.FindMemoriesByType( Memory.TYPE_WEAPON )
			for m in weap_memories:
				assert isinstance( m, Memory.Memory )
				if self.WantsWeapon( npc, memory=m ):
				#	print "Going for weapon %s from memory!" % m.classname
					npc.SetTargetPos( m.location )
					self.Complete( npc )
					return

		# If we get here we either don't have a memory or didn't remember any valid weapons
		weaps = GEEntity.GetEntitiesInBox( "weapon_*", my_pos, GEUtil.Vector( -data, -data, -10 ), GEUtil.Vector( data, data, 120 ) )

		# Sort by closest ammo
		weight_cmp = lambda x, y: cmp( GEWeapon.ToGEWeapon( x ).GetWeight(), GEWeapon.ToGEWeapon( y ).GetWeight() )
		weaps.sort( weight_cmp )

		for weap in weaps:
			if self.WantsWeapon( npc, weapon=weap ):
			#	print "Going for weapon %s that I found!" % weap.GetClassname()
				npc.SetTarget( weap )
				self.Complete( npc )
				return

		# We failed to find anything, fail the task
		npc.TaskFail( GEAiTasks.TaskFail.NO_TARGET )

class FindArmor( PYTask ):
	def Start( self, npc, data ):
		assert isinstance( npc, PYBaseNPC )

		if data <= 0:
			data = 720

		memory = npc.GetSystem( AiSystems.MEMORY )

		# If we have a memory, try to find the closest armor we remember
		if memory is not None:
			armor_memories = memory.FindMemoriesByType( Memory.TYPE_ARMOR )
			if len( armor_memories ) > 0:
				npc.SetTargetPos( armor_memories[0].location )
				self.Complete( npc )
				return

		# If we get here we either don't have a memory or didn't remember an ammo box
		my_pos = npc.GetAbsOrigin()
		armor = GEEntity.GetEntitiesInBox( "item_armorvest*", my_pos, GEUtil.Vector( -data, -data, -10 ), GEUtil.Vector( data, data, 120 ) )

		# Sort by closest armor
		dist_cmp = lambda x, y: cmp( my_pos.DistTo( x.GetAbsOrigin() ), my_pos.DistTo( y.GetAbsOrigin() ) )
		armor.sort( dist_cmp )

		if len( armor ) > 0:
			npc.SetTarget( armor[0] )
			self.Complete( npc )
			return

		# We failed to find anything, fail the task
		npc.TaskFail( GEAiTasks.TaskFail.NO_TARGET )

class FindToken( PYTask ):
	def Start( self, npc, data ):
		assert isinstance( npc, PYBaseNPC )

		target = npc.GetTokenTarget()
		if not target:
			self.Fail( npc, "No token target specified by NPC" )
			return

		range_sort = lambda x, y: x["range"] > y["range"]

		# Grab our contacts from the radar from our perspective and sort by range
		contacts = [c for c in GERules.GetRadar().ListContactsNear( npc.GetAbsOrigin() ) if self.ShouldSeek( npc, c )]
		contacts.sort( range_sort )

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

