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
import GEUtil, GEMPGameRules
from GEGlobal import EventHooks

class GEWarmUp:
	CHAN_TIMER = 4
	COLOR_TIMER = GEUtil.CColor( 255, 255, 255, 255 )
	COLOR_GETREADY = GEUtil.CColor( 255, 255, 255 )

	def __init__( self, parent ):
		self.Reset()

		self.preRoundEndDelay = 3.5
		self.noticeInterval = 1.0

		parent.RegisterEventHook( EventHooks.GP_THINK, self.Think )

	def Reset( self ):
		self.hadWarmUp = False
		self.inWarmUp = False
		self.endRoundTime = 0
		self.endWarmUpTime = 0
		self.nextNoticeTime = 0

	def IsInWarmup( self ):
		if self.endRoundTime:
			return True
		return self.inWarmUp

	def HadWarmup( self ):
		return self.hadWarmUp

	def StartWarmup( self, duration=30.0, endround_if_no_warmup=False ):
		now = GEUtil.GetTime()
		if duration > 0:
			self.endWarmUpTime = now + duration
			self.nextNoticeTime = now
			self.inWarmUp = True
			GEUtil.EmitGameplayEvent( "ges_startwarmup" )
			return True
		elif endround_if_no_warmup:
			self.EndWarmup()
			return True
		else:
			# Just pass through...
			self.hadWarmUp = True
			self.inWarmUp = False
			return False

	def EndWarmup( self ):
		self.Reset()
		self.endRoundTime = GEUtil.GetTime() + self.preRoundEndDelay
		# Clear the timer's message
		GEUtil.HudMessage( None, "", -1, -1, self.COLOR_TIMER, 0.5, self.CHAN_TIMER )
		# Tell us to get ready
		GEUtil.HudMessage( None, "#GES_GP_GETREADY", -1, -1, self.COLOR_GETREADY, self.preRoundEndDelay + 3.0 )

	def Think( self ):
		# Don't worry about this if we are done
		if self.hadWarmUp:
			return

		now = GEUtil.GetTime()

		if self.inWarmUp and now < self.endWarmUpTime:
			if now >= self.nextNoticeTime:
				# Let everyone know how much time is left
				remains = self.endWarmUpTime - now
				GEUtil.HudMessage( None, "#GES_GP_WARMUP\r%0.0f sec" % remains, -1, 0.62, self.COLOR_TIMER, 2.0, self.CHAN_TIMER )
				self.nextNoticeTime = now + self.noticeInterval

		elif self.inWarmUp and now >= self.endWarmUpTime:
			# Notify players that warmup is now over
			self.EndWarmup()

		elif self.endRoundTime and now >= self.endRoundTime:
			# This completes our warmup
			self.endRoundTime = 0
			self.hadWarmUp = True
			GEMPGameRules.EndRound( False )
			GEUtil.EmitGameplayEvent( "ges_endwarmup" )



