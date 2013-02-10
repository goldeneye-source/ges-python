from Ai import PYBaseNPC, AiSystems
from Ai.Utils import Memory, Weapons
from GEAiConst import Class, State, Capability as Cap, Disposition as D
from Schedules import Sched, Cond
import GEEntity, GEPlayer, GEUtil, GEWeapon, GEMPGameRules as GERules, GEGlobal as Glb
import random

import GEGamePlay

USING_API = Glb.API_VERSION_1_0_0

class bot_deathmatch( PYBaseNPC ):
	def __init__( self, parent ):
		PYBaseNPC.__init__( self, parent )
		self._min_weap_weight = Weapons.Weight.WORST
		self._max_weap_weight = Weapons.Weight.BEST

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
		for id in loadout:
			weap_info = GEWeapon.WeaponInfo( id )
			if "weight" in weap_info:
				if weap_info["weight"] < min_weight:
					min_weight = weap_info["weight"]
				elif weap_info["weight"] > max_weight:
					max_weight = weap_info["weight"]

		self._min_weap_weight = min_weight
		self._max_weap_weight = max_weight

	def IsValidEnemy( self, enemy ):
		myteam = self.GetTeamNumber()
		if myteam != Glb.TEAM_NONE and enemy.GetTeamNumber() == self.GetTeamNumber():
			return False

		return True

	def GatherConditions( self ):
		self.ClearCondition( Cond.NO_PRIMARY_AMMO )
		self.ClearCondition( Cond.LOW_PRIMARY_AMMO )
		self.ClearCondition( Cond.GES_ENEMY_FAR )
		self.ClearCondition( Cond.GES_ENEMY_CLOSE )
		self.ClearCondition( Cond.GES_CAN_SEEK_ARMOR )

		memory = self.GetSystem( AiSystems.MEMORY )

		if self.GetEnemy() is not None:
			# Set condition of enemy distance
			dist_to_enemy = self.GetEnemy().GetAbsOrigin().DistTo( self.GetAbsOrigin() )
			if dist_to_enemy > 800:
				self.SetCondition( Cond.GES_ENEMY_FAR )
			elif dist_to_enemy < 150:
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

		# Ammo Checks
		currWeap = self.GetActiveWeapon()
		assert isinstance( currWeap, GEWeapon.CGEWeapon )
		if currWeap and not currWeap.IsMeleeWeapon() and currWeap.GetWeaponId() != Glb.WEAPON_MOONRAKER:
			if currWeap.GetAmmoCount() <= currWeap.GetMaxAmmoCount() / 100:
				# We have very little ammo left for this weapon
				self.SetCondition( Cond.NO_PRIMARY_AMMO )
			elif currWeap.GetClip() < ( currWeap.GetMaxClip() / 8.0 ):
				# We are running out of our clip
				self.SetCondition( Cond.LOW_PRIMARY_AMMO )

		# Armor checks
		armor_mem = memory.FindMemoriesByType( Memory.TYPE_ARMOR )
		if len( armor_mem ) > 0:
			self.SetCondition( Cond.GES_CAN_SEEK_ARMOR )
			for m in armor_mem:
				if self.GetAbsOrigin().DistTo( m.location ) < 1024:
					self.SetCondition( Cond.GES_CLOSE_TO_ARMOR )
					break

	def SelectSchedule( self ):
		# Run away from explosions!
		if self.HasCondition( Cond.HEAR_DANGER ):
			return Sched.TAKE_COVER_FROM_BEST_SOUND

		# Basic advanced action probability (40% chance)
		action_prob = 0.4
		dice_roll = random.random()

		if self.GetState() == State.COMBAT:
			if self.HasCondition( Cond.GES_ENEMY_FAR ):
				action_prob = 0.6

			# Low health condition, attempt to find armor or run away
			if self.GetHealth() <= ( self.GetMaxHealth() / 2.0 ) and self.GetArmor() < ( self.GetMaxArmor() / 2.0 ):
				if self.GetHealth() <= 20 or self.HasCondition( Cond.GES_CLOSE_TO_ARMOR ):
					action_prob = 0.8

				if self.HasCondition( Cond.GES_CAN_SEEK_ARMOR ) and dice_roll < action_prob:
					return Sched.BOT_SEEK_ARMOR
				elif self.GetHealth() <= 20 and self.HasCondition( Cond.GES_ENEMY_DANGEROUS ):
					return Sched.RUN_FROM_ENEMY

			if not self.HasCondition( Cond.GES_ENEMY_CLOSE ) and dice_roll < action_prob:
				return Sched.BOT_ENGAGE_ENEMY
			elif ( self.HasCondition( Cond.GES_ENEMY_FAR ) or self.HasCondition( Cond.TOO_FAR_TO_ATTACK ) ) \
					and not self.HasCondition( Cond.GES_ENEMY_DANGEROUS ) and dice_roll < action_prob:
				return Sched.CHASE_ENEMY

			# Let the base AI handle combat situations
			return Sched.NO_SELECTION
		else:
			# Always seek ammo if we are almost out
			if self.HasCondition( Cond.NO_PRIMARY_AMMO ):
				return Sched.BOT_SEEK_AMMO

			# Need Armor?
			if self.GetArmor() < ( self.GetMaxArmor() * 0.8 ) and self.HasCondition( Cond.GES_CAN_SEEK_ARMOR ):
				if self.GetHealth() <= 20 or self.HasCondition( Cond.GES_CLOSE_TO_ARMOR ):
					action_prob = 0.85
				if dice_roll < action_prob:
					return Sched.BOT_SEEK_ARMOR

			# See a better weapon?
			if self.HasCondition( Cond.BETTER_WEAPON_AVAILABLE ):
				if self.HasCondition( Cond.GES_CLOSE_TO_WEAPON ):
					action_prob = 0.75
				if dice_roll < action_prob:
					return Sched.BOT_SEEK_WEAPON

			# Our default is to find an enemy which falls back to patrolling
			return Sched.BOT_SEEK_ENEMY

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
				print GEWeapon.WeaponInfo( weap.GetWeaponId(), self.GetNPC() )
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
