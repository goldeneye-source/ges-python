from GamePlay import GEScenario
import GEEntity, GEPlayer, GEUtil, GEWeapon, GEMPGameRules, GEGlobal, GEGamePlay
from Utils.GEWarmUp import GEWarmUp
from GEWeapon import CGEWeapon

USING_API = GEGlobal.API_VERSION_1_0_0


					#	#	#	#	#	#	#	#
					#		 -  UPLINK  -		#
		#	#	#	#	#	#	#	#	#	#	#
		#  Created by  WNxEuphonic  #
		#	#	#	#	#	#	#	#    #    #    #
			#            Special Thanks <3         #
			#    #    #    #    #    #    #    #   #
			#  KillerMonkey and E-S for answering  #
			#  and putting up with all my annoying #
			#  questions. WNx for being the best   #
			#  clan in the world, the dev team for #
			#  making such an amazing game (I did  #
			#  get inspiration from the official   #
			#  gameplays).            			   #
			#	#	#	#	#	#	#    #    #    #	#	#	#	#	#
								#	If you make edits to this gameplay,	#
								#	you must remain primary credit to	#
								#	WNxEuphonic. If you use code from	#
								#	this gameplay you must give some	#
								#	form of credit to WNxEuphonic.		#
								#	#    #    #    #	#	#	#	#	#


class UplinkPoint( object ):
		"""Handles information about each point"""
		
		def __init__( self, location, name, UID ):
			self.location = location
			self.name = name
			self.UID = UID
			
			self.owner = GEGlobal.TEAM_NONE
			
			self.numJanus = 0
			self.numMI6 = 0
			self.isContested = False
			self.inProgress = False
			
			self.timerJanus = 0
			self.timerMI6 = 0
			
			self.pointTimer = 0
			
			self.playerList = []
		
		def updatePointTimer(self, timerMax):
			if self.owner != GEGlobal.TEAM_NONE:
				self.pointTimer += 1
				
				if self.pointTimer >= timerMax:
					self.pointTimer = 0
					GEMPGameRules.GetTeam( self.owner ).AddRoundScore( 1 )
			
		def updateUplinkTimer(self, timerMax):
			if self.owner != GEGlobal.TEAM_MI6 and self.numMI6:
				if not self.numJanus:
					self.timerMI6 += 1 + self.numMI6
					if self.timerMI6 >= timerMax:
						self.timerMI6 = 0; self.timerJanus = 0
						self.pointTimer = 0
						return GEGlobal.TEAM_MI6
					elif self.timerJanus:
						self.timerJanus -= 5
						if self.timerJanus < 0:
							self.timerJanus = 0
						
			elif self.owner != GEGlobal.TEAM_JANUS and self.numJanus:
				if not self.numMI6:
					self.timerJanus += 1 + self.numJanus
					if self.timerJanus >= timerMax:
						self.timerMI6 = 0; self.timerJanus = 0
						self.pointTimer = 0
						return GEGlobal.TEAM_JANUS
					elif self.timerMI6:
						self.timerMI6 -= 5
						if self.timerMI6 < 0:
							self.timerMI6 = 0
			
			else:
				if self.timerMI6:
					self.timerMI6 -= 4
					if self.timerMI6 < 0:
						self.timerMI6 = 0
				if self.timerJanus:
					self.timerJanus -= 4
					if self.timerJanus < 0:
						self.timerJanus = 0
			
			return False
					
				
		def addPlayerList(self, player):
			self.playerList += [player]
			if player.GetTeamNumber() == GEGlobal.TEAM_JANUS:
				self.numJanus += 1
			elif player.GetTeamNumber() == GEGlobal.TEAM_MI6:
				self.numMI6 += 1
			
		def removePlayerList(self, player):
			if player in self.playerList:
				self.playerList.remove(player)
				playerTeam = player.GetTeamNumber()			
					
				if playerTeam == GEGlobal.TEAM_JANUS:
					self.numJanus -= 1
					if self.numJanus < 0:
						self.numJanus = 0
				elif playerTeam == GEGlobal.TEAM_MI6:
					self.numMI6 -= 1
					if self.numMI6 < 0:
						self.numMI6 = 0
		
		def checkContestedChange(self):
			if self.numMI6 and self.numJanus and not self.isContested:
				self.isContested = True
				return True
			elif self.isContested and (not self.numMI6 or not self.numJanus):
				self.isContested = False
				return True
			else:
				return False
		
		def checkProgressChange(self):
			if not self.inProgress:
				if self.owner != GEGlobal.TEAM_JANUS and self.numJanus:
					self.inProgress = True
					return True
				
				elif self.owner != GEGlobal.TEAM_MI6 and self.numMI6:
					self.inProgress = True
					return True
			
			else:
				if self.owner == GEGlobal.TEAM_JANUS and not self.numMI6:
					self.inProgress = False
					return True
				elif self.owner == GEGlobal.TEAM_MI6 and not self.numJanus:
					self.inProgress = False
					return True
				elif self.owner == GEGlobal.TEAM_NONE and not self.numJanus and not self.numMI6:
					self.inProgress = False
					return True
				else:
					return False


class Uplink( GEScenario ):
	
	def __init__( self ):
		super( Uplink, self ).__init__()
		
		self.warmupTimer = GEWarmUp( self )
		self.notice_WaitingForPlayers = 0
		self.WaitingForPlayers = True
		
		self.RoundActive = False
		self.prevCount = 0
		
#		>> Uplink Point data >>
		self.areaDictionary = {}		# Holds each Uplink Point's data (as a class object)
		
#		>> Uplink Point variables >>
		self.pointRadius = 220.0		# Sets radius of each Uplink Point
		self.uplinkTimerMax = 100		# Sets amount of time to make uplink
		self.pointTimerMax = 120		# Sets amount of time between each point being awarded
		self.areaTotal = 3				# Sets the number of Uplink Points to spawn
		self.skinNeutral = 0
		self.skinJanus = 2
		self.skinMI6 = 1
		self.uplinkReward = 2
		self.pointsJanus = 0
		self.pointsMI6 = 0
		
#		>> Ping effect variables >>
		self.pingTimerMax = 20						# Sets how long between each "ping" effect on Uplink Points
		self.pingTimer = self.pingTimerMax + 1		# Keeps track of how long since last "ping" effect on Uplink Points
		
#		>> Color variables >>
		self.ColorNeutral = GEUtil.CColor(255,255,255,255)
		self.ColorNeutralPing = GEUtil.CColor(255,255,255,100)
		self.ColorMI6 = GEUtil.CColor(0,150,255,255)
		self.ColorMI6Ping = GEUtil.CColor(0,150,255,100)
		self.ColorJanus = GEUtil.CColor(255,0,0,255)
		self.ColorJanusPing = GEUtil.CColor(255,0,0,100)
		
#		>> Scoreboard color variables >>
		self.ScoreboardDefault = GEGlobal.SB_COLOR_NORMAL
		self.ScoreboardOnPoint = GEGlobal.SB_COLOR_WHITE

#		>> Message & Progress Bar colors >>
		self.ColorMsg = GEUtil.CColor(220,220,220,240)
		self.ColorBarStandard = GEUtil.CColor(220,220,220,240)	# Color of progress bar when player is capturing an Uplink Point
		self.ColorBarContested = GEUtil.CColor(220,220,220,100)	# Color of progress bar when player is capturing an Uplink Point but blocked by enemy player
		
#		>> Killticker Message colors >>
		self.ColorKilltickerJanus = "^r"
		self.ColorKilltickerMI6 = "^i"
		self.ColorKilltickerDefault = "^1"
		
#		>> Message & Progress Bar information >>
		self.barIndex = 0
		self.msgIndex = 1
		self.barTitle = "Uplink"								# Displays as the title of the progress bar when a player is capturing an Uplink Point
		self.completeMsg = "Uplink Complete!"					# Displays when a player is finished capturing an Uplink Point
		self.ownedMsg = "Your team owns this Uplink Point"		# Displays when a player steps on an Uplink Point their team already owns
		self.reenterMsg = ""									# Displays when a player spawns at the start of a new round onto an Uplink Point (Currently disabled)
		self.capturedPrintMsg = "^1 made an ^uUplink"			# Displays in killticker when team make an Uplink
		self.capturedPrintMsgAnd = " ^1and "					# Displays before final player who helped complete an Uplink
		self.printMI6 = "MI6"
		self.printJanus = "Janus"
		self.helpMsg = "MI6 and Janus are fighting for control over key military satellites. Several Uplink Points are in your area, stand close to one to begin an Uplink. Once the Uplink is complete, the satellite will be under your team's control, continuously generating points for your team. The more satellites your team owns, the more points generated.\n\nControl and protect Uplink Points while preventing your opponents from doing the same!\n\nTeamplay: Always\n\nCreated by WNxEuphonic"

#		>> Uplink Point Distribution display >>
		self.distColorJanus = GEUtil.CColor(255,0,0,255)
		self.distColorMI6 = GEUtil.CColor(0,0,255,255)
		self.distColorNeutral = GEUtil.CColor(255,255,255,255)
	
	def GetPrintName( self ):
		return "Uplink"

	def GetScenarioHelp( self, help_obj ):
		help_obj.SetDescription( self.helpMsg )
		help_obj.SetInfo("Capture and Defend Uplink Points", "http://people.ucsc.edu/~tsumner/Uplink.html" )
		
		pane = help_obj.AddPane( "uplink1" )
		help_obj.AddHelp( pane, "up_goal", "Uplink Points are marked by flags and glowing rings")
		help_obj.AddHelp( pane, "", "Stand on an Uplink Point to start an Uplink")
		help_obj.AddHelp( pane, "", "Once the Uplink is complete, your team owns that Uplink Point")
		help_obj.AddHelp( pane, "", "The more Uplink Points your team owns, the more points earned")
		
		help_obj.SetDefaultPane( pane )

	def GetGameDescription( self ):
			return "Uplink"

	def GetTeamPlay( self ):
		return GEGlobal.TEAMPLAY_ALWAYS

	def OnLoadGamePlay( self ):
		GEUtil.PrecacheModel( "models/weapons/tokens/w_flagtoken.mdl" )
		GEUtil.PrecacheSound( "GEGamePlay.Token_Grab" )
		GEUtil.PrecacheSound( "GEGamePlay.Token_Drop_Enemy" )
		GEUtil.PrecacheSound( "GEGamePlay.Token_Chime" )
		
		GEMPGameRules.GetRadar().SetForceRadar( True )
		GEMPGameRules.SetAllowTeamSpawns( False )
				
		if GEMPGameRules.GetNumActivePlayers() >= 2:
			self.WaitingForPlayers = False
		
		self.CreateCVar( "up_warmup", "20", "The warm up time in seconds (Use 0 to disable warmup)" )
		self.CreateCVar( "up_points_override", "0", "Sets number of Uplink Points to spawn. Set to 0 to use default amount. Takes effect on round end" )
		self.CreateCVar( "up_ping", "1", "When set to 0, disables the 'ping' effect on Uplink Points" )
	
	def OnRoundBegin(self):
		GEMPGameRules.ResetAllPlayersScores()
		self.pointsJanus = 0; self.pointsMI6 = 0
		self.areaDictionary = {}
		self.RoundActive = True
		self.UpdateAreaTotal()
		if not self.WaitingForPlayers:
			self.CreateAreas(0)
	
	def OnRoundEnd(self):
		self.RoundActive = False
		self.pointsMI6 = 0; self.pointsJanus = 0
		
		self.RemoveAreas()
		
		self.HideOwnershipDist(None)
		self.UpdateAreaTotal()
	
	def CanPlayerChangeTeam( self, player, oldTeam, newTeam ):
		if oldTeam != newTeam:
			for item in self.areaDictionary:
				if player in self.areaDictionary[ item ].playerList:
					self.areaDictionary[ item ].removePlayerList( player )
				else:
					continue
		
		return True
	
	def OnPlayerDisconnect( self, player ):
		for item in self.areaDictionary:
			if player in self.areaDictionary[ item ].playerList:
				self.areaDictionary[ item ].removePlayerList( player )
			else:
				continue
	
	def OnCaptureAreaSpawned( self, area ):
		name = GEMPGameRules.CGECaptureArea.GetGroupName(area)
		# # # 		NOT REQUIRED AFTER FUTURE PATCH 	# # #
		for item in self.areaDictionary:
			if area.GetAbsOrigin() == self.areaDictionary[item].location:
				GEMPGameRules.GetTokenMgr().RemoveCaptureArea( name )
				self.CreateCaptureZone(name, self.skinNeutral)
				GEUtil.Warning( "Gameplay: Prevented overlapping Uplink Point\n" )
				return
			else:
				continue
		# # #					 END	 				# # #
		
		self.areaDictionary[ name ] = UplinkPoint(area.GetAbsOrigin(), name, area)
		self.ShowOwnershipDist( None )
		
		GEMPGameRules.GetRadar().AddRadarContact( area, GEGlobal.RADAR_TYPE_OBJECTIVE, True, "sprites/hud/radar/capture_point", self.ColorNeutral )
		self.CreateObjective( area, name, False )
	
	def OnCaptureAreaRemoved( self, area ):
		GEMPGameRules.GetRadar().DropRadarContact( area )
		self.ShowOwnershipDist( None )
		
		areaName = GEMPGameRules.CGECaptureArea.GetGroupName(area)
		if areaName in self.areaDictionary:
			if self.areaDictionary[ areaName ].owner == self.pointsJanus:
				self.pointsJanus -= 1
			elif self.areaDictionary[ areaName ].owner == self.pointsMI6:
				self.pointsMI6 -= 1
			del self.areaDictionary[ areaName ]
	
	def OnCaptureAreaEntered( self, area, player, token ):
		if not self.WaitingForPlayers and not self.warmupTimer.IsInWarmup() and self.RoundActive:
			areaName = GEMPGameRules.CGECaptureArea.GetGroupName(area)
			if areaName in self.areaDictionary:
				self.areaDictionary[ areaName ].addPlayerList(player)
				player.SetScoreBoardColor( self.ScoreboardOnPoint )
				
				changedContest = self.areaDictionary[ areaName ].checkContestedChange()
				
				if self.areaDictionary[ areaName ].owner == player.GetTeamNumber():
					self.ShowMsg( player, self.ownedMsg)
				
				elif self.areaDictionary[ areaName ].isContested:
					self.ShowBar( player, self.ColorBarContested )
				
				else:
					self.ShowBar( player, self.ColorBarStandard)
		
				if changedContest:
					self.ChangeContested( areaName, area, self.areaDictionary[ areaName ].isContested )
				
				if self.areaDictionary[ areaName ].checkProgressChange():
					self.CreateObjective( self.areaDictionary[ areaName ].UID, self.areaDictionary[ areaName ].name, self.areaDictionary[ areaName ].inProgress)
			else:
				self.ShowMsg( player, self.reenterMsg)
	
	def OnCaptureAreaExited( self, area, player ):
		if not self.WaitingForPlayers and not self.warmupTimer.IsInWarmup():
			self.ClearBars(player)
			self.ClearMsg(player)
			player.SetScoreBoardColor( self.ScoreboardDefault )
			
			if self.RoundActive:
				areaName = GEMPGameRules.CGECaptureArea.GetGroupName(area)
				if areaName in self.areaDictionary:
					self.areaDictionary[ areaName ].removePlayerList(player)
					
					if self.areaDictionary[ areaName ].checkContestedChange():
						self.ChangeContested( areaName, area, self.areaDictionary[ areaName ].isContested)
					
					if self.areaDictionary[ areaName ].checkProgressChange():
						self.CreateObjective( self.areaDictionary[ areaName ].UID, self.areaDictionary[ areaName ].name, self.areaDictionary[ areaName ].inProgress)
	
	def OnPlayerSpawn( self, player ):
		
		if not self.WaitingForPlayers and not self.warmupTimer.IsInWarmup():
			self.ShowOwnershipDist( player )
		
			if GEMPGameRules.GetNumActivePlayers() > 4 + self.prevCount:
				oldTotal = self.areaTotal
				self.UpdateAreaTotal()
				self.CreateAreas( oldTotal )
	
	def OnPlayerKilled( self, victim, killer, weapon ):
		# No points if in warmup
		if self.warmupTimer.IsInWarmup() or not victim:
			return

		# Death by world
		if not killer:
			victim.AddRoundScore( -1 )
			return
		
		victimTeam = victim.GetTeamNumber()
		killerTeam = killer.GetTeamNumber()

		if victim == killer or victimTeam == killerTeam:
			# Suicide or team kill
			killer.AddRoundScore( -1 )
		else:
			killer.AddRoundScore( 1 )
	
	def OnThink(self):
		self.UpdateRings()
		
		if GEMPGameRules.GetNumActivePlayers() < 2:
			if not self.WaitingForPlayers:
				self.notice_WaitingForPlayers = 0
				self.RemoveAreas()
				GEMPGameRules.EndRound()
			elif GEUtil.GetTime() > self.notice_WaitingForPlayers:
				GEUtil.HudMessage( None, "#GES_GP_WAITING", -1, -1, GEUtil.Color( 255, 255, 255, 255 ), 2.5, 1 )
				self.notice_WaitingForPlayers = GEUtil.GetTime() + 12.5

			self.warmupTimer.Reset()
			self.WaitingForPlayers = True
			return

		elif self.WaitingForPlayers:
			self.WaitingForPlayers = False
			if not self.warmupTimer.HadWarmup():
				self.warmupTimer.StartWarmup( int( GEUtil.GetCVarValue( "up_warmup" ) ), True )
				if self.warmupTimer.inWarmUp:
					GEUtil.EmitGameplayEvent( "up_startwarmup" )
			else:
				GEMPGameRules.EndRound( False )
		
		if not self.warmupTimer.IsInWarmup() and not self.WaitingForPlayers:
			for uplinkPoint in self.areaDictionary:
				updated = self.areaDictionary[uplinkPoint].updateUplinkTimer( self.uplinkTimerMax )
				self.UpdateBar( self.areaDictionary[uplinkPoint].playerList, self.areaDictionary[uplinkPoint].name )
				if updated:
					self.ChangeOwner( self.areaDictionary[uplinkPoint].name, self.areaDictionary[uplinkPoint].UID, updated )
				self.areaDictionary[uplinkPoint].updatePointTimer( self.pointTimerMax )
			

			####################					# # # # # # # # # # # # # # # # # #					   ####################
			#########################################         Custom Functions        #########################################
			####################					# # # # # # # # # # # # # # # # # #					   ####################


	def UpdateRings( self ):
		if self.pingTimer > self.pingTimerMax:
			ping = True; self.pingTimer = 0
		else:
			ping = False; self.pingTimer += 1
		
		for item in self.areaDictionary:
			area = self.areaDictionary[item].location
			RingColor = self.GetColor( self.areaDictionary[item].owner )
			GEUtil.CreateTempEnt( "ring", origin = area, framerate = 15, duration = 0.6, speed = 0, width=3.0, amplitude=0.00, radius_start=self.pointRadius, radius_end=self.pointRadius + 0.1, color=RingColor )
			
			if ping and int( GEUtil.GetCVarValue( "up_ping" ) ):
				PingColor = self.GetColorPing(self.areaDictionary[item].owner)
				GEUtil.CreateTempEnt( "ring", origin = area, framerate = 15, duration = 2, speed = 10, width=0.33, amplitude=0.0, radius_start=0, radius_end=self.pointRadius,  color=PingColor )

	def CreateAreas( self, shift ):
		for curNum in range( self.areaTotal - shift ):
			curName = "Uplink Zone #" + str(curNum + 1 + shift)
			self.CreateCaptureZone( curName, self.skinNeutral )
	
	def RemoveAreas( self ):
		keyList = self.areaDictionary.keys()
		for uplinkPoint in keyList:
			GEMPGameRules.GetTokenMgr().RemoveCaptureArea( uplinkPoint )
		return
	
	def UpdateAreaTotal( self ):
		self.prevCount = GEMPGameRules.GetNumActivePlayers()
		
		override = int( GEUtil.GetCVarValue( "up_points_override" ) )
		if override > 0:
			self.areaTotal = override
		
		elif self.prevCount < 4:
			self.areaTotal = 1
		elif self.prevCount < 6:
			self.areaTotal = 2
		elif self.prevCount < 10:
			self.areaTotal = 3
		elif self.prevCount < 13:
			self.areaTotal = 4
		elif self.prevCount < 17:
			self.areaTotal = 5
		else:
			self.areaTotal = 6
		return
	
	def GetColor( self, owner ):
		if owner == GEGlobal.TEAM_JANUS:
			return self.ColorJanus
		elif owner == GEGlobal.TEAM_MI6:
			return self.ColorMI6
		else:
			return self.ColorNeutral
			
	def GetColorPing(self, owner):
		if owner == GEGlobal.TEAM_JANUS:
			return self.ColorJanusPing
		elif owner == GEGlobal.TEAM_MI6:
			return self.ColorMI6Ping
		else:
			return self.ColorNeutralPing
	
	def CreateCaptureZone(self, name, skinType):
		GEMPGameRules.GetTokenMgr().SetupCaptureArea( name , model= "models/weapons/tokens/w_flagtoken.mdl", skin=skinType, limit=1, location=GEGlobal.SPAWN_TOKEN, radius=0.5*self.pointRadius, rqd_team = GEGlobal.TEAM_NONE, rqd_token= None, spread=0)

	def CreateObjective(self, area, name, capturing):
		if capturing:
			title = "!"
		else:
			title = ""
			
		color = self.GetColor( self.areaDictionary[ name ].owner )
		GEMPGameRules.GetRadar().SetupObjective( area, GEGlobal.TEAM_NONE, "", title, color, int( 0.45 * self.pointRadius ), capturing )
	
	def PrintCapture(self, playerList, team):
		if team == GEGlobal.TEAM_MI6:
			color = self.ColorKilltickerMI6
			name = self.printMI6
		else:
			color = self.ColorKilltickerJanus
			name = self.printJanus
		
		if len( playerList ) == 1:
			msg = color + playerList[0] + self.capturedPrintMsg
		elif len( playerList ) == 2:
			msg = color + playerList[1] + self.capturedPrintMsgAnd + color + playerList[0] + self.capturedPrintMsg
		else:
			msg = color + name + self.capturedPrintMsg
			
		GEUtil.PostDeathMessage( msg )
	
	def ShowMsg(self, player, msg):
		GEUtil.InitHudProgressBar(player, self.barIndex, msg, GEGlobal.HUDPB_TITLEONLY, 0, -1, .75, 0, 0, self.ColorMsg)
	
	def ShowBar(self, player, color):
		GEUtil.InitHudProgressBar(player, self.barIndex, self.barTitle, 1, float(self.uplinkTimerMax), -1, .75, 110, 12, color)
	
	def ConfigBar(self, player, color):
		GEUtil.ConfigHudProgressBar( player, self.barIndex, self.barTitle, color )
	
	def UpdateBar(self, playerList, areaName):
		for player in playerList:
			if player.GetTeamNumber() == GEGlobal.TEAM_MI6:
				num = self.areaDictionary[ areaName ].timerMI6
			else:
				num = self.areaDictionary[ areaName ].timerJanus
			GEUtil.UpdateHudProgressBar( player, self.barIndex, num )

	def ClearBars(self, player):
		GEUtil.RemoveHudProgressBar(player, self.barIndex)
	
	def ClearMsg(self, player):
		GEUtil.RemoveHudProgressBar(player, self.msgIndex)
	
	def ChangeContested(self, areaName, areaID, newState):
		if newState:
			colorBar = self.ColorBarContested
		else:
			colorBar = self.ColorBarStandard
		for player in self.areaDictionary[ areaName ].playerList:
			if player.GetTeamNumber() != self.areaDictionary[ areaName ].owner:
				self.ConfigBar(player, colorBar)
	
	def ChangeOwner(self, areaName, areaID, newOwner):
		oldOwner = self.areaDictionary[ areaName ].owner
		self.areaDictionary[ areaName ].owner = newOwner
		
		self.areaDictionary[ areaName ].inProgress = False
		
		GEMPGameRules.GetRadar().AddRadarContact( areaID, GEGlobal.RADAR_TYPE_OBJECTIVE, True, "sprites/hud/radar/capture_point", self.GetColor(newOwner) )
		self.CreateObjective(areaID, areaName, False)
		
		if newOwner == GEGlobal.TEAM_JANUS:
			self.pointsJanus += 1
			GEUtil.PlaySoundToTeam( newOwner, "GEGamePlay.Token_Grab", True )
			GEUtil.PlaySoundToTeam( GEGlobal.TEAM_MI6, "GEGamePlay.Token_Drop_Enemy", True )
			self.CreateCaptureZone( areaName, self.skinJanus )
			GEUtil.EmitGameplayEvent( "up_capture_team", "%i" % GEGlobal.TEAM_JANUS )
		elif newOwner == GEGlobal.TEAM_MI6:
			self.pointsMI6 += 1
			GEUtil.PlaySoundToTeam( newOwner, "GEGamePlay.Token_Grab", True )
			GEUtil.PlaySoundToTeam( GEGlobal.TEAM_JANUS, "GEGamePlay.Token_Drop_Enemy", True )
			self.CreateCaptureZone( areaName, self.skinMI6 )
			GEUtil.EmitGameplayEvent( "up_capture_team", "%i" % GEGlobal.TEAM_MI6 )
		if oldOwner == GEGlobal.TEAM_JANUS:
			self.pointsJanus -= 1
		elif oldOwner == GEGlobal.TEAM_MI6:
			self.pointsMI6 -= 1
		
		GEMPGameRules.GetTeam( newOwner ).AddRoundScore( 1 )
		
		nameList = []
		
		self.ShowOwnershipDist( None )
		
		for player in self.areaDictionary[ areaName ].playerList:
			self.ClearBars( player )
			self.ShowMsg( player, self.completeMsg )
			player.AddRoundScore( self.uplinkReward )
			GEUtil.PlaySoundToPlayer( player, "GEGamePlay.Token_Chime", False )
			nameList += [player.GetCleanPlayerName()]
			if oldOwner == GEGlobal.TEAM_NONE:
				GEUtil.EmitGameplayEvent( "up_capture_neutral", "%i" % player.GetUserID() )
			else:
				GEUtil.EmitGameplayEvent( "up_capture_steal", "%i" % player.GetUserID() )
		self.PrintCapture(nameList, newOwner)

	def ShowOwnershipDist(self, target):
		numNeutral = self.areaTotal - self.pointsJanus - self.pointsMI6
		if not numNeutral > 0:
			numNeutral = "-"
		
		GEUtil.HudMessage( target, str(self.pointsJanus), 0.475, 0.0, self.distColorJanus, float('inf'), 1 )
		GEUtil.HudMessage( target, str(numNeutral), 0.50, 0.0, self.distColorNeutral, float('inf'), 2 )
		GEUtil.HudMessage( target, str(self.pointsMI6), 0.525, 0.00, self.distColorMI6, float('inf'), 3 )
	
	def HideOwnershipDist(self, target):
		GEUtil.HudMessage( target, "", 0.0, 0.0, self.distColorNeutral, 0, 1 )
		GEUtil.HudMessage( target, "", 0.0, 0.0, self.distColorNeutral, 0, 2 )
		GEUtil.HudMessage( target, "", 0.0, 0.0, self.distColorNeutral, 0, 3 )