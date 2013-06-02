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
from DeathMatch import DeathMatch
import GEPlayer, GEUtil, GEGlobal as Glb, GEMPGameRules as GERules
from GEUtil import TempEnt as TE, Color, TraceOpt
from .Utils import GetPlayers, _

USING_API = Glb.API_VERSION_1_1_0

class KMTest( DeathMatch ):
	def __init__( self ):
		super( DeathMatch, self ).__init__()
		self.obj_blink = True

	def GetPrintName( self ):
		return "KM's Test Scenario"

	def GetGameDescription( self ):
		return "KM Test"

	def GetTeamPlay( self ):
		return Glb.TEAMPLAY_TOGGLE

	def OnLoadGamePlay( self ):
		super( KMTest, self ).OnLoadGamePlay()
		GEUtil.PrecacheSound( "GEGamePlay.Baron_Flawless" )
		GEUtil.PrecacheSound( "@custom/nano-blade-loop.wav" )

	def OnPlayerSpawn( self, player ):
		GERules.GetRadar().SetupObjective( player, 0, "", player.GetCleanPlayerName(), Color( 120, 120, 0, 255 ), 0, True )

	def OnPlayerSay( self, player, cmd ):
		assert isinstance( player, GEPlayer.CGEMPPlayer )

		cmd = cmd.lower()
		origin = player.GetAbsOrigin()
		origin[2] += 20.0

		if cmd == "ring":
			GEUtil.CreateTempEnt( TE.RING, origin=origin )
		elif cmd == "beam":
			origin = player.GetEyePosition()
			end = GEUtil.VectorMA( origin, player.GetAimDirection(), 300.0 )
			GEUtil.CreateTempEnt( TE.BEAM, origin=origin, end=end )
		elif cmd == "follow":
			GEUtil.CreateTempEnt( TE.BEAM_FOLLOW, origin=origin, entity=player, duration=3.0 )
		elif cmd == "dust":
			GEUtil.CreateTempEnt( TE.DUST, origin=origin, size=50.0, speed=0.2 )
		elif cmd == "smoke":
			GEUtil.CreateTempEnt( TE.SMOKE, origin=origin, size=50.0, framerate=2 )
		elif cmd == "spark":
			origin = GEUtil.VectorMA( origin, player.GetAimDirection(), 150.0 )
			GEUtil.CreateTempEnt( TE.SPARK, origin=origin )
		elif cmd == "trace":
			origin = player.GetEyePosition()
			end = GEUtil.VectorMA( origin, player.GetAimDirection(), 300.0 )
			hit = GEUtil.Trace( origin, end, TraceOpt.PLAYER, player )

			if hit == None:
				GEUtil.HudMessage( None, "No hit!", -1, -1 )
			else:
				player = GEPlayer.ToMPPlayer( hit )
				GEUtil.HudMessage( None, "Hit: " + hit.GetClassname(), -1, -1, hold_time=10.0, color=Color( 255, 255, 0, 255 ) )
				GEUtil.HudMessage( None, "Player: " + player.GetPlayerName(), y=0.6, x=-1 )
		elif cmd == "obj":
			self.obj_blink = not self.obj_blink
			for pl in GetPlayers():
				GERules.GetRadar().SetupObjective( pl, 0, "", pl.GetCleanPlayerName(), Color( 120, 120, 0, 255 ), 0, self.obj_blink )
		elif cmd == "box":
			GEUtil.PopupMessage( None, "Default Title",
				"This is a really long message that should not be "
				"displayed for more than four lines I don't want to "
				"keep typing but I will god damnit! I really don't "
				"like typing so I am eventually going to stop doing "
				"it but not anytime soon baby cakes!" )
		elif cmd == "sound":
			GEUtil.PlaySoundFrom( player.GetAbsOrigin(), "@custom/nano-blade-loop.wav", 0.27 )
		elif cmd == Glb.SAY_COMMAND1:
			if not hasattr( self, "blah" ):
				self.blah = 1
			else:
				self.blah += 1

			GEUtil.HudMessage( None, "Test: " + str( self.blah ), -1, -1, GEUtil.Color( 100, 184, 234 ), 3.0 )
		else:
			return False

		return True
