import GEUtil

class GEOvertime:
	def __init__( self ):
		self.end_time = 0
		self.trip_time = 0
		self.is_tripped = False

	def StartOvertime( self, failsafe, trip=30 ):
		if failsafe == -1:
			self.end_time = -1
		else:
			self.end_time = GEUtil.GetTime() + failsafe
			self.trip_time = self.end_time - trip
			self.is_tripped = False

	def CheckOvertime( self ):
		if self.end_time == -1:
			return True

		if GEUtil.GetTime() >= self.end_time:
			return False
		elif not self.is_tripped and GEUtil.GetTime() >= self.trip_time:
			time = self.end_time - self.trip_time
			GEUtil.PopupMessage( None, "#GES_GPH_OVERTIME_TRIP_TITLE", "#GES_GPH_OVERTIME_TRIP\r%i" % int( time ) )
			self.is_tripped = True

		return True
