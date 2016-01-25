# -*- coding: utf-8 -*-
"""
MssUnit.py
MssUnitChr2.py - 12/03/11 - change the move_to and move_relative to make the input parameters - coordinates in um (micrometers)
MssUnit.py - 12/10/11 - less talkative version of the working MssUnitChr2.py

License: GPL version 3.0
January 25, 2016
Copyright:

This file is part of AutoPatcher_IG.

    AutoPatcher_IG is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    AutoPatcher_IG is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with AutoPatcher_IG.  If not, see <http://www.gnu.org/licenses/>.

@Author: Brendan Callahan, Alexander A. Chubykin, Zhaolun Su

"""
__author__="Alex Chubykin"
__version__="version 2.0"
__date__="Mon Oct 31 22:36:50 2011"
__copyright__="Copyright (c) 2011 Alex Chubykin"
__license__="Python"

import numpy as np
import crc16my2 as crc
#import crc16my
#import crc16my2 as crc
from serial import Serial
import time
import copy
import MSSInterface as mssi

import sys
sys.path.append('../2-Photon/')
import opencv_LoadImage4_1

class TwoPhotonUnit():
    device={}
    ASCII_Commands={'STX':0x02,'DLE':0x10,'NAK':0x15,'ETX':0x03,'ESC':0x1b,'ACK':0x06}
    Commands={'GetStatus':'#x?Z','GotoPosition':'#x!GF','GotoRelativePosition':'#x!DF','GetPosition':'#x?P'}
    data_read=[]
    all_data_read=[]
    resolution=(1344,1024) # default screen resolution
    pixel_4x=[1.532,1.532] # one pixel at 4x magnification, in um [x,y]
    full_step=4.9705 #full_step=5 # full_step=1.75 # one full step, in um
    
    
    def __init__(self, unitID=0):
        """ 
        Initialize the Serial superclass, and setup some default values
        """
        
        self.unitID = unitID #This is the MSS Unit number that MSSInterface refers to this unit as, most likely 0 or 1
        self.unitType = "2P"        
        
        self.silent = True
        
        self.parent = None
        
        self.x0EndPosPlus = False
        self.x0EndPosMinus = False
        self.y0EndPosPlus = False
        self.y0EndPosMinus = False
        self.z0EndPosPlus = False
        self.z0EndPosMinus = False
        
        self.x1EndPosPlus = False
        self.x1EndPosMinus = False
        self.y1EndPosPlus = False
        self.y1EndPosMinus = False
        self.z1EndPosPlus = False
        self.z1EndPosMinus = False
    
    def set_camera_resolution(self,x,y):
        pass
    
    def setParent(self,parentin):
        self.parent = parentin
        
    def getChecksum(self,data_str):
        pass
    
    def serial_read(self):
        pass
    
    def serial_read_all(self):
        pass     
    
    def serial_write(self,data,iteration = 0):
        pass
    
    def serial_purge(self):
        pass
     
    def get_motors_coord(self,manip = None): #returns the motor coordinates in steps
        pass
        
    def get_motors_coord_um(self, manip=None): # returns the motor coordinates in um
        newcoords = opencv_LoadImage4_1.return_xyz_coordinates()
        newcoords[0] = float(newcoords[0])
        newcoords[1] = float(newcoords[1])
        newcoords[2] = float(newcoords[2])
        self.parent.motorcoordinates[self.unitID][0] = copy.deepcopy(newcoords)
        return newcoords
           
    def move_to_um(self, manip, x=np.NaN,y=np.NaN,z=np.NaN): # coordinates are sent in um
        pass
        
    def move_relative_um(self, manip, x=np.NaN,y=np.NaN,z=np.NaN): # coordinates are in um
        pass
    
    def move_to(self,manip, x=np.NaN,y=np.NaN,z=np.NaN):
        pass
        
    def get_status_all(self,manip=None):
        pass
        
    #Keep querying the unit until all motors respond as not moving; this keeps a queue item
    #from expiring before its action is completed.
    def waitUntilReady(self,manip):
        pass
        
    def talk(self,toSend):
            
        pass
        
    def talk_back(self):
        pass
    

    
if __name__ == "__main__":
    main()