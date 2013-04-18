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
from .DeathMatch import DeathMatch
import GEEntity, GEPlayer, GEUtil, GEWeapon, GEMPGameRules, GEGlobal

USING_API = GEGlobal.API_VERSION_1_1_0

class DrNoArmor( DeathMatch ):
	def GetPrintName( self ):
		return "Dr. No Armor"

	def GetScenarioHelp( self, help_obj ):
		help_obj.SetDescription( "#GES_GP_DEATHMATCH_HELP" )

	def GetGameDescription( self ):
		if GEMPGameRules.IsTeamplay():
			return "Team Dr. No Armor"
		else:
			return "Dr. No Armor"

	def OnRoundBegin( self ):
		super( DrNoArmor, self ).OnRoundBegin()
		GEMPGameRules.DisableArmorSpawns()

