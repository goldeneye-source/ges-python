################ Copyright 2005-2016 Team GoldenEye: Source #################
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
class CGamePlayManager:
    pass

def GetScenario():
    '''Get the current active scenario, useful for specially coded NPC's'''
    return CBaseScenario

class CBaseScenario:
    def GetIdent( self ):
        return str

    def CreateCVar( self, name, default_value, help_string ):
        '''
        Create a console variable that can be set by config scripts
        or directly in the console by the server owner.
        
        name -- The name of the variable (string)
        default_value -- The default value of the variable (string)
        help_string -- A help string to show if you type in just the variable (string)
        '''
        return

    def ShowScenarioHelp( self, player, pane ):
        '''
        Show the specified help pane (must be pre-registered) to the player
        
        player -- GEPlayer.CGEMPPlayer
        pane -- The ID or the unique name of the pane you want to show
        '''
        return

class CScenarioHelp:
    def SetInfo( self, tagline, website ):
        '''
        Set the tagline and website for this scenario. Users can click the website
        to see advanced help.
        
        tagline -- Short statement describing this scenario [localizable]
        website -- Fully qualified URL (http://www.example.com/help)
        '''

    def SetDescription( self, description ):
        '''
        Set the overall description for this scenario, this is shown in the
        popup help box at the bottom of the screen.
        
        description -- Long description of the scenario [localizable]
        '''

    def SetDefaultPane( self, pane_id ):
        '''
        Sets the help pane that will be shown right after a player connects.
        
        pane_id -- Help pane ID
        '''

    def AddPane( self, name ):
        '''
        Creates a help pane that help is added to. The name must be a unique 
        string and is used to allow players to disable this help pane from 
        showing. It is useful to store the returned pane id later use in 
        showing the help and adding help items to the pane.

        Returns the ID of the created help pane.
        
        name -- Unique name of the pane
        '''
        return int

    def AddHelp( self, pane_id, image, description ):
        '''
        Adds a help block to the specified pane, you may pass localized variables
        to the description. Image is simply a filename entry with the actual image
        must be stored in "materials/vgui/hud/gameplayhelp/".
        
        pane_id -- ID of the help pane (returned from AddPane)
        image -- Filename of an image or empty string
        description -- Text to show in this block [localizable]
        '''
