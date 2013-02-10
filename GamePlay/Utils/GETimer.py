import GEUtil, GEMPGameRules
from GEGlobal import EventHooks

def EndMatchCallback( timer, type_ ):
	if type_ == Timer.UPDATE_FINISH:
		GEMPGameRules.EndMatch()

def EndRoundCallback( timer, type_ ):
	if type_ == Timer.UPDATE_FINISH:
		GEMPGameRules.EndRound()

class TimerTracker:
	def __init__( self, parent ):
		self.timers = []
		self.firstrun = True
		self.lastagetime = 0
		self._oneshots = 0

		# Register finishCallback to age timers automatically
		parent.RegisterEventHook( EventHooks.GP_THINK, self.AgeTimers )

	def __del__( self ):
		self.timers = None

	def CreateTimer( self, name ):
		t = Timer( name )
		self.timers.append( t )
		return t

	def RemoveTimer( self, name=None ):
		if not name:
			self.timers = []
		else:
			for t in self.timers:
				if t.GetName() == name:
					self.timers.remove( t )
					return

	def OneShotTimer( self, time, callback, update_inter=0.5 ):
		t = Timer( "_oneshot_timer_%d" % self._oneshots )
		t.SetUpdateCallback( callback, update_inter )
		t.Start( time, False )
		self.timers.append( t )
		self._oneshots += 1

	def ResetTimer( self, name=None ):
		for t in self.timers:
			if not name or t.name == name:
				t.Stop()

	def AgeTimers( self ):
		now = GEUtil.GetTime()

		if self.firstrun:
			self.lastagetime = now
			self.firstrun = False

		delta = now - self.lastagetime
		for t in self.timers:
			t.AgeTimer( now, delta )
			if t.debug:
				GEUtil.Msg( "[GETimer] Timer %s is %0.1f / %0.1f\n" % ( t.GetName(), t.GetTime(), t.GetLimit() ) )

		self.lastagetime = now

# Simple timer that can be registered to a timer updater
# which decrements all timers it is currently tracking
class Timer:
	( UPDATE_START, UPDATE_RUN, UPDATE_PAUSE, UPDATE_STOP, UPDATE_FINISH ) = range( 5 )
	( STATE_RUN, STATE_PAUSE, STATE_STOP ) = range( 3 )

	def __init__( self, name ):
		self.name = name
		self.currTime = 0
		self.maxTime = 0
		self.startAgeTime = 0
		self.ageDelay = 0
		self.ageRate = 0
		self.state = Timer.STATE_STOP
		self.repeat = False
		self.updateCallback = None
		self.updateRate = 0.25
		self.updateNext = 0
		self.updateDirty = False
		self.debug = False

	def SetUpdateCallback( self, cb, interval=0.25 ):
		self.updateCallback = cb
		self.updateRate = interval
		self.updateNext = 0

	def SetAgeRate( self, rate, delay=0 ):
		self.ageRate = rate
		self.ageDelay = delay

	def Start( self, maxTime=0, repeat=False ):
		if self.state is Timer.STATE_STOP:
			self.currTime = 0
			self.updateNext = 0
			self.maxTime = maxTime
			self.repeat = repeat

		self.state = Timer.STATE_RUN
		self._CallUpdate( Timer.UPDATE_START )

	def Restart( self ):
		self._CallUpdate( Timer.UPDATE_FINISH )
		self.currTime = 0
		self.updateNext = 0
		self.state = Timer.STATE_RUN
		self._CallUpdate( Timer.UPDATE_START )

	def Pause( self ):
		if self.state is Timer.STATE_RUN:
			self.startAgeTime = GEUtil.GetTime() + self.ageDelay
			self.state = Timer.STATE_PAUSE
			self._CallUpdate( Timer.UPDATE_PAUSE )

	def Stop( self ):
		self.repeat = False
		self.state = Timer.STATE_STOP
		self._CallUpdate( Timer.UPDATE_STOP )

	def Finish( self ):
		self._CallUpdate( Timer.UPDATE_FINISH )
		self.Stop()

	def GetName( self ):
		return self.name

	def GetCurrentTime( self ):
		return self.currTime

	def GetMaxTime( self ):
		return self.maxTime

	def AgeTimer( self, now, delta ):
		if self.state == Timer.STATE_RUN:
			self.currTime += delta

			# Check if we are done
			if self.maxTime > 0 and self.currTime >= self.maxTime:
				# Repeat if desired, otherwise stop
				if self.repeat:
					self.Restart()
				else:
					self.Finish()
			else:
				self.updateDirty = True

		elif self.state == Timer.STATE_PAUSE and self.currTime > 0:
			# Age the timer if we have it defined
			if now >= self.startAgeTime and self.ageRate > 0:
				self.currTime -= delta * self.ageRate;

				if self.currTime <= 0:
					self.currTime = 0
					self.Stop()
				else:
					self.updateDirty = True

		# Attempt an update call
		self._CallUpdate( Timer.UPDATE_RUN )

	def _CallUpdate( self, type_ ):
		now = GEUtil.GetTime()
		# We only attempt this if we have a callback, are a special update or are dirty and its time
		if self.updateCallback and ( type_ != Timer.UPDATE_RUN or ( self.updateDirty and now >= self.updateNext ) ):
			self.updateNext = now + self.updateRate
			self.updateDirty = False
			# Call into our callback
			self.updateCallback( self, type_ )
