# -*- coding: utf-8 -*-
"""
Created Jan-Feb 2012 most likely

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

@Author: Brendan Callahan, Zhaolun Su, Alexander A. 

"""

__author__="Alex Chubykin, Brendan Callahan"
__version__="version 7.3"
__date__="Wed Oct 12 12:48:14 2011"


#NOTE THAT THIS CLASS IS A NEAR-COMPLETE REWRITE OF THE ORIGINAL MANIPULATOR CONTROL
#PROGRAM.  IT'S NOW A MODULE AND THREAD MANAGEMENT SYSTEM THAT SERVES AS A MIDDLEMAN BETWEEN
#THE MAIN CLASS (OR WHATEVER OTHER CLASS) AND THE MANIPULATOR CONTROL BOXES (VIA THE
#MSSUNIT CLASS.)  NOT ALL INITIALIZED VARIABLES ARE USED.

from PyQt4.QtCore import *
from PyQt4.QtGui import *


import sys
import time
#from pygame.locals import *
#from PIL import ImageEnhance
import copy
import threading
import autopatcher as ap
#import MssUnitChr2 as ms
import MssUnit as ms
import SensapexUnit as sx
import TwoPhotonUnit as pp
import ScientificaUnit as sci

import UniversalLibrary as UL
import numpy as np
import __builtin__

import csv
import StringIO

import LogicParser as lp
import DigitalInput as di

# camera parameters
res = (1344,1024)
pixel_4x=[1.532,1.532] # one pixel in um at 4x, resolution 1344x1024
DelayInterval = 0.3 # delay interval between commands, s

mouse_seq=[] # mouse_seq is a list of tuples [(x1,y1),(x2,y2)]
scan_seq=[]
seq_coord=[] # seq_coord is a list of lists ([[x1,y1,z1],[x2,y2,z2]])
remembered_position_index=[] # stores the indeces of remembered positions
command_exec=0
Move_seq_marker=0

# L&N Manipulators part
MSSBAUD = 19200 # 19200 for the Rig, 9600 for arduino
SENSAPEXBAUD = 115200
SCIENTIFICABAUD = 9600
# Port the Arduino\lolshield is on:

coord_offset = [[0,0,0], [0,0,0], [0,0,0]]

"""
# Universal library acquisition
BoardNum = 0
Gain = UL.BIP5VOLTS
Chan = 0
tstart = time.time()
data = []
times = []
# digital input for the TTL signal - external synchronization (could also be done through the SYNC and TRIG inputs)
PortNum = UL.FIRSTPORTA
Direction = UL.DIGITALIN
BitNum = 0
#UL.cbDConfigPort(BoardNum, PortNum, Direction)
DataValue = 0
DataValue2 = 0
TTL_input = 0
TTL_switch=0
"""

class MSSInterface():
    def __init__(self,is2Photon=False):
        
        self.is2Photon = is2Photon
        self.portdata = self.getPortData()
        print self.portdata
        
        self.Speed = 'S' #Speed for whatever speed-intensive actions are performed, universal for all mssunits for now
        
        self.myarrows = None #This is passed by QTTest, so that MSSInterface can update
                             #the graphical coordinates whenever these are queried from a MssUnit.
        self.myarrowsalternate = None
                             
        #Each of the two MssUnit objects (MyUnit1 and MyUnit2) have to be initialized with 
        #their own set of threads and queues etc.
        self.initialized = False
        
        #This array contains the references to the MssUnit instances, so they can be
        #accessed via the corresponding array indices.
        self.MyUnit = []
        self.dataControl = ap.DataControl()
        self.threadqueuemanager = []
        self.threadqueue=[]
        self.currentthread = [] #The thread/command that is currently being executed for the corresponding MssUnit
        self.motorcoordinates = []       
        self.endpos = []
        
        self.arrowMoving = False #whether the user is currently using the keyboard to move something
        
        self.purgeQueue = [] #make this true for the respective unit to purge the queue, it will be reset to false after
        
        self.digitalInput = di.DigitalInput(self,self.dataControl)
        self.logicParser = lp.LogicParser(self.digitalInput)
        
        self.digitalInputOn = False
        
        #Create a MssUnit instance for each port specified by the user.  They will be accessible
        #through self.MyUnit[num], in the order that they are created.  It is assumed that unit[0],
        #motors 1-3 are the stage.
        
        if (is2Photon):
            print 'is 2 phonton is tru \n\n'        
            self.MyUnit.append(pp.TwoPhotonUnit())
            if self.portdata[1][1] == "MSS":
                self.MyUnit.append(ms.MssUnit(port=self.portdata[1][0], baudrate=MSSBAUD,unitID=1,timeout=0.1))
            elif self.portdata[1][1] == "SX":
                self.MyUnit.append(sx.SensapexUnit(port=self.portdata[1][0], baudrate=SENSAPEXBAUD,unitID=1,timeout=0.1))
            elif self.portdata[1][1] == "SCI":
                self.MyUnit.append(sci.ScientificaUnit(port=self.portdata[1][0], baudrate=SCIENTIFICABAUD,unitID=1,timeout=0.1))
            #self.portdata[0][1] = "2P"            
            
            for counter in range (0,2):
                self.portdata[counter][2] = 1
                self.MyUnit[counter].setParent(self)
                self.threadqueue.append([])
                self.currentthread.append(None)
                self.purgeQueue.append(False)
                
                #Motor coordinates for each unit are stored with a separate list for each motor set.  So to access
                #the coordinates for Unit 0, Manipulator 1, you would get motorcoordinates[0][1].
                self.motorcoordinates.append([])
                for i in range(0,self.portdata[counter][2]):
                    self.motorcoordinates[-1].append([None,None,None])
                
                self.endpos.append([[False,False,False,False,False,False],[False,False,False,False,False,False]])
                
                #Query the motor status for each unit.
                self.initUnit(counter)
                
            
        else:                        
            for counter in range (0,len(self.portdata)):
                if self.portdata[counter][1] == "MSS":
                    self.MyUnit.append(ms.MssUnit(port=self.portdata[counter][0], baudrate=MSSBAUD,unitID=counter,timeout=0.1))
                elif self.portdata[counter][1] == "SX":
                    self.MyUnit.append(sx.SensapexUnit(port=self.portdata[counter][0], baudrate=SENSAPEXBAUD,unitID=counter,timeout=0.1))
                elif self.portdata[counter][1] == "SCI":
                    print 'SCI is true \n\n'
                    self.MyUnit.append(sci.ScientificaUnit(port=self.portdata[counter][0], baudrate=SCIENTIFICABAUD,unitID=counter,timeout=0.1))
                #Pass this object reference to both MssUnits, so that they can update
                #coordinates etc while they're waiting for commands to complete.
                self.MyUnit[counter].setParent(self)
                
                #This list of queues check whether currentthread[counter] has completed every .1s, and
                #starts the next function in threadqueue if so.  The threads for multiple 
                #control boxes are handled and executed independently.
                self.threadqueue.append([])
                self.currentthread.append(None)
                self.purgeQueue.append(False)
                
                #Motor coordinates for each unit are stored with a separate list for each motor set.  So to access
                #the coordinates for Unit 0, Manipulator 1, you would get motorcoordinates[0][1].
                self.motorcoordinates.append([])
                for i in range(0,self.portdata[counter][2]):
                    self.motorcoordinates[-1].append([None,None,None])
                
                self.endpos.append([[False,False,False,False,False,False],[False,False,False,False,False,False]])
                
                #Query the motor status for each unit.
                self.initUnit(counter)
                counter += 1
            
            #get the motor status (e.g. are any of the motors at an end position) for this unit.
            #You can also call getStatus(Mssunit, manipulator #) for only 3 of the motors you want to check
            
        #set up dummy thread stuff 
        if (len(self.threadqueue) == 1):
            self.threadqueue.append([])
            self.currentthread.append(None)
            self.purgeQueue.append(False)
        #Start the thread queue oversight class (see the class itself below for more info on how it works)
        self.threadqueuemanager = ThreadQueue(self)
        self.threadqueuemanager.start()
         
        #DOESN'T WORK.  MOTHBALLED UNITL WE CAN FIGURE OUT HOW TO CHANGE RAMP TIME.
        #self.setRamp(0,"12345")
        #self.setRamp(1,"12345")
        
        self.currentlistitemqueue = []        
        
        for i in range(0,len(self.MyUnit)):
            self.getStatus(i)
            self.askCoords(i)
            self.currentlistitemqueue.append([[[],[],[]],[[],[],[]]])

        
        self.initialized = True
    
    def getPortData(self):
        portdata = []
        portsReader = csv.reader(open('.\configuration\ports.csv'),quoting=csv.QUOTE_NONNUMERIC)
        print 'Ports Configuration Loaded'
        for i in range (0,100): #hopefully someone doesn't hook up more than 100 devices
            portdata.append([])     
            for j in range (0,3):
                try:
                    if j == 2:
                        portdata[i].append(int(portsReader.next()[0]))
                    else:
                        portdata[i].append(portsReader.next()[0])
                    
                except:
                    portdata.pop(len(portdata)-1) #get rid of the extra list
                    return portdata
    
    def areThreadsActive(self,unit=None):
        if unit == None:
            if len(self.threadqueue[0]) == 0 and len(self.threadqueue[1]) == 0 and self.currentthread[0].isAlive() == False and self.currentthread[1].isAlive() == False:         
                return False
            else:
                return True
        elif len(self.threadqueue[unit]) == 0 and self.currentthread[unit].isAlive() == False:
            return False
        else:
            return True
    
    #Makes sure everything is working, plugged in, and returning values.
    def initUnit(self,unitnum):
        
        if self.is2Photon and unitnum == 0:
            self.askCoords(0)
        #Print out the initial status messages for the specified unit.
        elif self.MyUnit[unitnum].unitType == "MSS":
            print self.portdata[unitnum][0],"is open:",self.MyUnit[unitnum].isOpen()
            time.sleep(1.5)
            #time.sleep(0.1)
            self.MyUnit[unitnum].set_camera_resolution(res[0],res[1]) # also updates the scale
            
            # assaying the status and position of the motors
            print 'What is the status of the motors of Unit',str(unitnum)+'?'
            for i in range(1,7):
                a='#'+str(i)+'?Z'
                motor_message=self.MyUnit[unitnum].talk(a)
                time.sleep(0.1)
                print motor_message
    

    #"Arrows" corresponds to the manipulator control panel.  This is passed from the main program
    #very soon after the program is started.            
    def setArrows(self,arrowsin):
        self.myarrows = arrowsin
        #Note that self.askCoords will ask all motors on all units
        #for their current coordinates
        
        
    def setArrowsAlternate(self,arrowsalternatein):
        self.myarrowsalternate = arrowsalternatein
    #The following few thread modules are used for keyboard control of the manipulators.
    #For instance, this one will move the manipulator/microscope in the +X direction until
    #the key is released, as long as nothing else is currently in the queue.
    
    #The arrowMoving variable is used to prevent multiple movement commands from the keyboard from
    #being executed at once. (also, no threads must be in the queue)
    def moveXPlus(self,unitnum,manip):
        #thread = moveXPlusThread(self,unitnum,manip,self.Speed)
        #self.threadqueue[unitnum].append(thread)
        print "X+ unitnum "+str(unitnum)
        if self.currentthread[unitnum] == 0 or self.currentthread[unitnum].isAlive() == False:
            if len(self.threadqueue[unitnum]) == 0:
                if self.arrowMoving == False:
                    self.arrowMoving = True
                    if self.MyUnit[unitnum].unitType == 'SCI':
                        if (self.Speed == 'F'):
                            unitSpeed = self.MyUnit[unitnum].fastManualSpeed
                        if (self.Speed == 'S'):
                            unitSpeed = self.MyUnit[unitnum].slowManualSpeed
                        a = "VJ "+str(unitSpeed)+" 0 0"
                    else:
                        print"STARTING X MOVE**************************"
                        if manip == 0:
                            a='#1!'+self.Speed+'+'
                        if manip == 1:
                            a='#4!'+self.Speed+'+'
                    self.MyUnit[unitnum].talk(a)
                    
                
    def moveXMinus(self,unitnum,manip):
        if self.currentthread[unitnum] == 0 or self.currentthread[unitnum].isAlive() == False:
            if len(self.threadqueue[unitnum]) == 0:
                if self.arrowMoving == False:
                    self.arrowMoving = True
                    print"STARTING X MOVE**************************"
                    if self.MyUnit[unitnum].unitType == 'SCI':
                        if (self.Speed == 'F'):
                            unitSpeed = -1*self.MyUnit[unitnum].fastManualSpeed
                        if (self.Speed == 'S'):
                            unitSpeed = -1*self.MyUnit[unitnum].slowManualSpeed
                        a = "VJ "+str(unitSpeed)+" 0 0"
                    else:
                        if manip == 0:
                            a='#1!'+self.Speed+'-'
                        if manip == 1:
                            a='#4!'+self.Speed+'-'
                    self.MyUnit[unitnum].talk(a)
                    
        #thread = moveXMinusThread(self,unitnum,manip,self.Speed)
        #self.threadqueue[unitnum].append(thread)
    def stopX(self,unitnum,manip):
        if self.arrowMoving:
            if self.MyUnit[unitnum].unitType == 'SCI':
                print "Stopping X SCI"
                self.MyUnit[unitnum].talk('VJ 0 0 0')
            else:
                if manip == 0:
                    self.MyUnit[unitnum].talk('#1!A')
                if manip == 1:
                    self.MyUnit[unitnum].talk('#4!A')
            self.arrowMoving = False
            self.askCoords(unitnum,manip)
        #thread = stopXThread(self,unitnum,manip)
        #self.threadqueue[unitnum].append(thread)
        #self.askCoords(unitnum,manip)
    
        
    def moveYPlus(self,unitnum,manip):
        if self.currentthread[unitnum] == 0 or self.currentthread[unitnum].isAlive() == False:
            if self.arrowMoving == False:
                self.arrowMoving = True
                if self.MyUnit[unitnum].unitType == 'SCI':
                    if (self.Speed == 'F'):
                        unitSpeed = self.MyUnit[unitnum].fastManualSpeed
                    if (self.Speed == 'S'):
                        unitSpeed = self.MyUnit[unitnum].slowManualSpeed
                    a = "VJ 0 "+str(unitSpeed)+" 0"
                else:
                    if manip == 0:
                        a='#2!'+self.Speed+'+'
                    if manip == 1:
                        a='#5!'+self.Speed+'+'
                self.MyUnit[unitnum].talk(a)
                
#        thread = moveYPlusThread(self,unitnum,manip,self.Speed)
#        self.threadqueue[unitnum].append(thread)
    def moveYMinus(self,unitnum,manip):
        if self.currentthread[unitnum] == 0 or self.currentthread[unitnum].isAlive() == False:
            if self.arrowMoving == False:
                self.arrowMoving = True
                if self.MyUnit[unitnum].unitType == 'SCI':
                    if (self.Speed == 'F'):
                        unitSpeed = -1*self.MyUnit[unitnum].fastManualSpeed
                    if (self.Speed == 'S'):
                        unitSpeed = -1*self.MyUnit[unitnum].slowManualSpeed
                    a = "VJ 0 "+str(unitSpeed)+" 0"
                else:
                    if manip == 0:
                        a='#2!'+self.Speed+'-'
                    if manip == 1:
                        a='#5!'+self.Speed+'-'
                self.MyUnit[unitnum].talk(a)
                
#        thread = moveYMinusThread(self,unitnum,manip,self.Speed)
#        self.threadqueue[unitnum].append(thread)
    def stopY(self,unitnum,manip):
        if self.arrowMoving:
            if self.MyUnit[unitnum].unitType == 'SCI':
                print "Stopping X SCI"
                self.MyUnit[unitnum].talk('VJ 0 0 0')
            else:
                if manip == 0:
                    self.MyUnit[unitnum].talk('#2!A')
                if manip == 1:
                    self.MyUnit[unitnum].talk('#5!A')
            self.arrowMoving = False
            self.askCoords(unitnum,manip)
#        thread = stopYThread(self,unitnum,manip)
#        self.threadqueue[unitnum].append(thread)
#        self.askCoords(unitnum,manip)
    
    # For some reason z direction is inverted too
    def moveZPlus(self,unitnum,manip):
        if self.currentthread[unitnum] == 0 or self.currentthread[unitnum].isAlive() == False:
            if self.arrowMoving == False:
                self.arrowMoving = True
                if self.MyUnit[unitnum].unitType == 'SCI':
                    if (self.Speed == 'F'):
                        unitSpeed = self.MyUnit[unitnum].fastManualSpeed
                    if (self.Speed == 'S'):
                        unitSpeed = self.MyUnit[unitnum].slowManualSpeed
                    a = "VJ 0 0 "+str(unitSpeed)
                else:
                    if manip == 0:
                        a='#3!'+self.Speed+'+'
                    if manip == 1:
                        a='#6!'+self.Speed+'+'
                self.MyUnit[unitnum].talk(a)
                
#        thread = moveZPlusThread(self,unitnum,manip,self.Speed)
#        self.threadqueue[unitnum].append(thread)
    def moveZMinus(self,unitnum,manip):
        if self.currentthread[unitnum] == 0 or self.currentthread[unitnum].isAlive() == False:
            if self.arrowMoving == False:
                self.arrowMoving = True
                if self.MyUnit[unitnum].unitType == 'SCI':
                    if (self.Speed == 'F'):
                        unitSpeed = -1*self.MyUnit[unitnum].fastManualSpeed
                    if (self.Speed == 'S'):
                        unitSpeed = -1*self.MyUnit[unitnum].slowManualSpeed
                    a = "VJ 0 0 "+str(unitSpeed)
                else:
                    if manip == 0:
                        a='#3!'+self.Speed+'-'
                    if manip == 1:
                        a='#6!'+self.Speed+'-'
                self.MyUnit[unitnum].talk(a)
                
#        thread = moveZMinusThread(self,unitnum,manip,self.Speed)
#        self.threadqueue[unitnum].append(thread)
    def stopZ(self,unitnum,manip):
        if self.arrowMoving:
            if self.MyUnit[unitnum].unitType == 'SCI':
                print "Stopping X SCI"
                self.MyUnit[unitnum].talk('VJ 0 0 0')
            else:
                if manip == 0:
                    self.MyUnit[unitnum].talk('#3!A')
                if manip == 1:
                    self.MyUnit[unitnum].talk('#6!A')
            self.arrowMoving = False
            self.askCoords(unitnum,manip)
#        thread = stopZThread(self,unitnum,manip)
#        self.threadqueue[unitnum].append(thread)
#        self.askCoords(unitnum,manip)

    #Changes the speed variable, and also asks the coordinates of
    #all motors on all units at the next opportunity
    def speedFast(self):
        self.Speed = 'F'
        self.askCoords()
        self.getStatus()
    def speedSlow(self):
        self.Speed = 'S'  
        self.askCoords()
        
    #Queues up a request to stop all movement.  DOES NOT INTERRUPT, SHOULD PROBABLY BE
    #FIXED TO CLEAR THE THREAD QUEUE AND STOP ALL MOVEMENT JUST IN CASE.
    def allStop(self,unitnum=None):
        if unitnum != None:
            thread = allStopThread(self,self.MyUnit[unitnum])
            self.threadqueue[unitnum].append(thread)
        #if no unit is specified, send request to all units
        else:
            counter = 0
            for unitqueue in self.threadqueue:
                thread = allStopThread(self,self.MyUnit[counter],manip) 
                unitqueue.append(thread)
            counter +=1
        self.askCoords()
        
    #this sets all coordinage values to zero on the box.  Without accounting for the difference 
    #in position elsewhere, the program will have to be restarted because you're most likely going 
    #to lose track of the location of the grid etc.
    def setZero(self,unit,manip):
        if unit == None:
            for unit in range (0,len(self.MyUnit)):
                thread = setZeroThread(self,unit)
                self.threadqueue[unit].append(thread)
                self.askCoords()
        else:
            if manip == None:
                thread = setZeroThread(self,unit)
                self.threadqueue[unit].append(thread)
                self.askCoords(unit)
            else:
                thread = setZeroThread(self,unit,manip)
                self.threadqueue[unit].append(thread)
                self.askCoords(unit,manip)
        
        
#  MOTHBALLED FOR NOW, NEEDS TO BE PORTED TO THE NEW UNIT/MANIP SYSTEM
#    def rememberCoord(self):
#        self.askCoords()
#        self.MyUnit.remembered_coord_um=self.motorcoordinates
#        print self.MyUnit.remembered_coord_um
#    def MrememberCoord(self):
#        self.MaskCoords()
#        self.Mremembered_coord_um=self.Mmotorcoordinates
#        print "Remembering ",self.Mremembered_coord_um
        
    #Calling convention is absolutely necessary. 
    #moveTo()
    #waitForReady()
    #askCoords()
    
    #Move to a specific location
    def moveTo(self,unitnum,manip,x,y,z=None):
        if z==None and unitnum==0 and manip==0:
            z=self.motorcoordinates[unitnum][manip][2]
        elif z==None:
            print "###########NO Z ENTERED FOR MANIPULATOR MOVE##########"
        thread = moveToThread(self,unitnum,manip,x,y,z)
        self.threadqueue[unitnum].append(thread)
        self.waitForReady(unitnum, manip)
        self.askCoords(unitnum, manip)
        new_coords = [x,y,z]
        current_coords = self.getCoords(unitnum, manip)
        waitingcount = 0
        while not( abs(new_coords[0] - current_coords[0]) <= 1.5 and abs(new_coords[1] - current_coords[1])<=1.5 and abs(new_coords[2] - current_coords[2])<=1.5 ):
            time.sleep(0.1)
            current_coords = self.getCoords(unitnum, manip)
            sys.stdout.write('.')
            waitingcount = waitingcount + 1
            if waitingcount > 100:
                break
            #print "Current Coords: ", current_coords
            #print "new coords", new_coords

    
    #Move to a relative location
    def moveToRel(self,unitnum,manip,x,y,z=None):
        original_coords = self.getCoords(unitnum, manip)
        new_coords = [original_coords[0]+x, original_coords[1]+y, original_coords[2]+z ]
        if z==None and unitnum==0 and manip==0:
            z=self.motorcoordinates[unitnum][manip][2]
        elif z==None:
            print "###########NO Z ENTERED FOR MANIPULATOR MOVE##########"
        thread = moveRelThread(self,unitnum,manip,x,y,z)
        self.threadqueue[unitnum].append(thread)
        self.waitForReady(unitnum, manip)
        self.askCoords(unitnum, manip)
        current_coords = self.getCoords(unitnum, manip)
        waitingcount = 0
        while not( abs(new_coords[0] - current_coords[0]) <= 1.5 and abs(new_coords[1] - current_coords[1])<=1.5 and abs(new_coords[2] - current_coords[2])<=1.5 ):
            time.sleep(0.1)
            current_coords = self.getCoords(unitnum, manip)
            sys.stdout.write('.')
            waitingcount = waitingcount + 1
            if waitingcount > 100:
                break
            #print "Current Coords: ", current_coords
            #print "new coords", new_coords
    
    def moveToRelWithoutWaiting(self,unitnum,manip,x,y,z=None):
        #self.waitForReady(unitnum, manip)
        if z==None and unitnum==0 and manip==0:
            z=self.motorcoordinates[unitnum][manip][2]
        elif z==None:
            print "###########NO Z ENTERED FOR MANIPULATOR MOVE##########"
        thread = moveRelThread(self,unitnum,manip,x,y,z)
        self.threadqueue[unitnum].append(thread)
        #self.waitForReady(unitnum, manip)
        #self.askCoords(unitnum, manip)
        

    def moveToWithoutWaiting(self,unitnum,manip,x,y,z=None):
        self.waitForReady(unitnum, manip)
        current_coords = self.getCoords(unitnum, manip)
        print "xyz", x,y,z
        if z==None and unitnum==0 and manip==0:
            z=self.motorcoordinates[unitnum][manip][2]
        elif z==None:
            print "###########NO Z ENTERED FOR MANIPULATOR MOVE USING CURRENT Z COORDINATE##########"
            z = current_coords[2]
        thread = moveToThread(self,unitnum,manip,x,y,z)
        self.threadqueue[unitnum].append(thread)
        
        # new_coords = [x,y,z]
        # current_coords = self.getCoords(unitnum, manip)
        # while not( abs(new_coords[0] - current_coords[0]) <= 1.5 and abs(new_coords[1] - current_coords[1])<=1.5 and abs(new_coords[2] - current_coords[2])<=1.5 ):
        #     time.sleep(0.1)
        #     current_coords = self.getCoords(unitnum, manip)
        #     sys.stdout.write('.')
        #     #print "Current Coords: ", current_coords
        #     #print "new coords", new_coords

    #don't think this is used anymore
    def getEndPositions(self):
        pass        
        #return [self.MyUnit.xEndPosPlus,self.MyUnit.yEndPosPlus,self.MyUnit.zEndPosPlus,self.MyUnit.xEndPosMinus,self.MyUnit.yEndPosMinus,self.MyUnit.zEndPosMinus,self.MyUnit.MxEndPosPlus,self.MyUnit.MyEndPosPlus,self.MyUnit.MzEndPosPlus,self.MyUnit.MxEndPosMinus,self.MyUnit.MyEndPosMinus,self.MyUnit.MzEndPosMinus]
        
        
#    def moveToRememberedCoord(self):
#        if len(MyUnit.remembered_coord_um)>0:
#            x,y,z=self.MyUnit.remembered_coord_um
#            print self.MyUnit.remembered_coord_um
#            self.moveTo(x,y,z)
#        else:
#            print("**********NO OR BAD REMEMBERED COORDINATES")

 ####################################################################################################################           

    #Query the requested device for its coordinates.  This is not done immediately - it takes some
    #time for the request to process, which means that you can't call this function and immediately
    #get the coordinates.  If you need the coordinates immediately after this function is called, 
    #queue up this function, and then a loop that waits until the box is ready (i.e. nothing is in 
    #the queue) before then retrieving the stored coordinate value; this way it is guaranteed
    #that this function is completed by the time you retrieve the stored coordinates.
    
    #You can request a specific device (e.g. unit 1 device 0), a specific unit, or nothing at all:
    #this way it will only update coordinates to the level of specificity requested, although this
    #provides only a marginal performance increase.
    def askCoords(self,unitnum=None,manip=None):
        if unitnum == None and manip == None:
            for i in range(0,len(self.threadqueue)):
                thread = askCoordsThread(self,i)
                self.threadqueue[i].append(thread)
        elif manip == None:
            thread = askCoordsThread(self,unitnum)
            self.threadqueue[unitnum].append(thread)
        else:
            thread = askCoordsThread(self,unitnum,manip)
            self.threadqueue[unitnum].append(thread)
        
    #This returns the requested set of coordinates, but DOES NOT update them from the boxes:
    #it's just an easy way to request the full coordinate data, or a specific part of it.
    def getCoords(self,unit=None,manip=None):
        if unit == None and manip == None:
            returncoords = copy.deepcopy(self.motorcoordinates)
            # returncoords[0][0] = returncoords[0][0] - coord_offset[0][0]
            # returncoords[0][1] = returncoords[0][1] - coord_offset[0][1]
            # returncoords[0][2] = returncoords[0][2] - coord_offset[0][2]
            # returncoords[1][0] = returncoords[1][0] - coord_offset[1][0]
            # returncoords[1][1] = returncoords[1][1] - coord_offset[1][1]
            # returncoords[1][2] = returncoords[1][2] - coord_offset[1][2]
            # returncoords[2][0] = returncoords[2][0] - coord_offset[2][0]
            # returncoords[2][1] = returncoords[2][1] - coord_offset[2][1]
            # returncoords[2][2] = returncoords[2][2] - coord_offset[2][2]
            return returncoords
        elif manip == None:
            return copy.deepcopy(self.motorcoordinates[unit])
        else:
            return copy.deepcopy(self.motorcoordinates[unit][manip])
    
    #This checks the "status" of the motors, as in, whether they are moving or not.
    #It also checks whether the motors are at their end position, and updates the stored values
    #in MSSUnit for this accordingly, so that the graphics can be updated.    
    
    #REDUNDANT, GETCOORDS NOW GETS STATUS AS WELL
    def getStatus(self,unit=None,manip=None):
        pass
#        if unit == None and manip == None:  
#            for i in range(0,len(self.threadqueue)):
#                thread = getStatusThread(self,i,manip)
#                self.threadqueue[i].append(thread)
#        else:
#            thread = getStatusThread(self,unit,manip)
#            self.threadqueue[unit].append(thread)
        
    #This can (and should) be placed in between thread commands that involve movement.
    #Movement-related commands usually continue to execute even while the box is ready for
    #a new command, and thus can be interrupted by new commands.  This module continually asks
    #the box whether it is still moving, and does not resolve (and move on to the next item in
    #the thread queue) until all motors are stopped.
    def waitForReady(self,unit=None,manip=None):
        if unit == None:
            print("NO UNIT WAIT FOR READY")
            counter = 0
            for unitqueue in self.threadqueue:
                thread = waitForReadyThread(self,counter,manip)
                self.unitqueue.append(thread)
                counter +=1
        else:
            thread = waitForReadyThread(self,unit,manip)
            self.threadqueue[unit].append(thread)
    
    #Remember that the stage is assumed to be unit 0 manipulator 0
    #This moves through a series of points sequentially, probably corresponding to the grid center points.
    def traversePoints(self,pointsin):
        self.thread = TraversePointsThread(self,0,pointsin)
        self.threadqueue[0].append(self.thread)
        

########################AUTOPATCHER COMMAND THREADS##################################
    def sendBinary(self,params):
        self.thread = sendBinaryThread(params,self.dataControl)
        self.threadqueue[params[0][0]].append(self.thread)
        
    def startDigitalInput(self):
        self.digitalInput = di.DigitalInput(self,self.dataControl)
        self.thread = startDigitalInputThread(self,self.digitalInput)
        self.threadqueue[0].append(self.thread)
    
    def stopDigitalInput(self):
        self.thread = stopDigitalInputThread(self,self.digitalInput)
        self.threadqueue[0].append(self.thread)
        
    def runListItems(self,unit,manip,listin,lifttype,liftin):
        while len(self.currentlistitemqueue[unit][manip]) > 0:
            self.currentlistitemqueue[unit][manip].pop(0)
        for i in range (0,5):
            self.currentlistitemqueue[unit][manip].append([])
        self.currentlistitemqueue[unit][manip][0] = listin
        print "listin is "
        print listin
        print self.currentlistitemqueue
        #self.currentlistitemqueue[unit][manip].append([])
        for item in self.currentlistitemqueue[unit][manip][0]:
            self.currentlistitemqueue[unit][manip][1].append(item.times+1)
            self.currentlistitemqueue[unit][manip][2] = 0
            self.currentlistitemqueue[unit][manip][3] = liftin
            self.currentlistitemqueue[unit][manip][4] = lifttype
        print self.currentlistitemqueue    
        self.thread = listItemExec(self,unit,manip)
        self.threadqueue[unit].append(self.thread)
    
    #ramp length for start/stop motion can be between 0 and 65535 ms
    #DOESN'T WORK.  ACCD TO DOCUMENTATION IT SHOULD.
    def setRamp(self,unit,ramplengthms):
        self.thread = setRampThread(self,unit,ramplengthms)
        self.threadqueue[unit].append(self.thread)
            
#This class queues up commands to be sent to the control boxes.  A queue is instantiated for each
#box, and this checks every .1 seconds whether the current module is resolved, and if so, starts
#the next one in the queue.  Modules are just functions that interact with the MssUnit class, which
#are instantiated as paused thread objects (which are then resumed to start them).  This approach prevents
#near-simultaneous commands from interfering with one another, due to the amount of time it takes to
#execute commands, especially movement-related ones.
class ThreadQueue(QObject, threading.Thread ):
    
    def __init__(self,interfacein):
        super(ThreadQueue, self).__init__(None)
        threading.Thread.__init__(self)
        self.interface = interfacein
        self.counter = 0
       
    updateUnit = pyqtSignal()
    updateUnitAlternate = pyqtSignal()  

    
    def run(self):
        
        self.slotsConnected = False
        self.altSlotsConnected = False
        
        self.lastthreadqueuelengths = []
        self.lastthreadqueueactive = []        
    
        for unit in range (0,len(self.interface.MyUnit)):
            self.lastthreadqueuelengths.append(0)
            self.lastthreadqueueactive.append(False)
        
        while (True): #keep going forever

            if self.interface.myarrows != None:
                if self.slotsConnected == False:
                    self.updateUnit.connect(self.interface.myarrows.updateUnit)
                    
                    self.slotsConnected = True
            if self.interface.myarrowsalternate != None:
                if self.altSlotsConnected == False:
                    self.updateUnitAlternate.connect(self.interface.myarrowsalternate.updateUnitAlternate)
                    
                    self.altSlotsConnected = True
        
            #time.sleep(0.05)
            time.sleep(1)
            unitnum = 0 #which unit index is currently being accessed
            
            for unit in range(0,len(self.interface.purgeQueue)):
                if self.interface.purgeQueue[unit] == True:
                    while len(self.interface.threadqueue[unit]) != 0:
                        self.interface.threadqueue[unit].pop()
                    self.interface.purgeQueue[unit] = False     
                    self.interface.stopDigitalInput()
            
            
            #This segment is for managing the graphical queue counter.  It compares thread active and
            #previous thread length values, and if they've changed, it updates the graphics to reflect this.

            #If there are any inequalities in the previous vs current values                                
            for unit in range(0,len(self.interface.MyUnit)):
                if len(self.interface.threadqueue[unit]) != self.lastthreadqueuelengths[unit] \
                    or self.interface.currentthread[unit].isAlive() != self.lastthreadqueueactive[unit]:
                    
                    if self.interface.myarrows != None: #if the Arrows object has been passed
                        self.updateUnit.emit()
                        break
                    
            for unitqueue in self.interface.threadqueue:
                
            
            #for the dummy interface if applicable
                if self.interface.myarrowsalternate != None: #if the Arrows object has been passed
                    self.updateUnitAlternate.emit()
            #for each queue for each unit
            for unitqueue in self.interface.threadqueue:
                #if the user isn't moving anything around with the keyboard
                if self.interface.arrowMoving == False:
                    #Query for the status every so many iterations
                    if self.counter == 10000:
                        if self.interface.currentthread[unitnum] == None or self.interface.currentthread[unitnum].isAlive() == False:
                            if self.interface.initialized == True and self.interface.arrowMoving == False:
                                print"1000GETTINGSTATUS",unitnum
                                self.interface.waitForReady(unitnum)
                                self.interface.getStatus(unitnum)
                    #Query for the coordinates every so many iterations
                    if self.counter == 20000:
                        self.counter = 0 #reset the counter used for this
                        if self.interface.currentthread[unitnum] == None or self.interface.currentthread[unitnum].isAlive() == False:
                            if self.interface.initialized == True and self.interface.arrowMoving == False:   
                                print"2000ASKINGCOORDS",unitnum
                                self.interface.waitForReady(unitnum)
                                self.interface.askCoords(unitnum)
                                self.counter = 0
                    #If no thread is currently running or the current thread has resolved
                    if self.interface.currentthread[unitnum] == None or self.interface.currentthread[unitnum].isAlive() == False:
                        #If there's anything queued up, pop it to the active thread and start it                        
                        if len(self.interface.threadqueue[unitnum]) != 0:
                            self.interface.currentthread[unitnum] = self.interface.threadqueue[unitnum].pop(0)
                            self.interface.currentthread[unitnum].start()
                            print"STARTING THREAD"
                    unitnum +=1 #move on to the thread queue for the next unit
                self.counter +=1
                
                for unit in range(0, len(self.interface.MyUnit)):
                    self.lastthreadqueuelengths[unit] = len(self.interface.threadqueue[unit])
                    if self.interface.currentthread[unit] != None:
                        self.lastthreadqueueactive[unit] = self.interface.currentthread[unit].isAlive()
                    else:
                        self.lastthreadqueueactive[unit] = False

#THIS DOES NOT WORK.  ACCORDING TO THE DOCUMENTATION IT'S SUPPOSED TO.  MAYBE
#FOR A LATER MSSUNIT VERSION OR SOMETHING, WHO KNOWS.  WOULD BE NICE IF IT DID WORK.
class setRampThread( threading.Thread ):
    def __init__(self,interface,unit,ramplengthms):
        threading.Thread.__init__(self)
        self.unit = unit
        self.ramplengthms = ramplengthms
        self.interface = interface
    def run ( self ):
        self.interface.MyUnit[self.unit].talk("#0!RU"+str(self.ramplengthms))
        time.sleep(.1)
        self.interface.MyUnit[self.unit].talk("#2!RU"+str(self.ramplengthms))
        time.sleep(.1)
        self.interface.MyUnit[self.unit].talk("#3!RU"+str(self.ramplengthms))
        time.sleep(.1)
        self.interface.MyUnit[self.unit].talk("#4!RU"+str(self.ramplengthms))
        time.sleep(.1)
        self.interface.MyUnit[self.unit].talk("#5!RU"+str(self.ramplengthms))
        time.sleep(.1)
        self.interface.MyUnit[self.unit].talk("#6!RU"+str(self.ramplengthms))

class listItemExec( threading.Thread ):
    def __init__(self,interfacein,unit,manip):
        threading.Thread.__init__(self)
        self.interface = interfacein
        self.unit = unit
        self.manip = manip
    def run ( self ):
        print "RUNNING LISTITEM"
        firstpoint = True        
        
        if self.interface.currentlistitemqueue[self.unit][self.manip][2] < len(self.interface.currentlistitemqueue[self.unit][self.manip][0]):
            currentlistitem = self.interface.currentlistitemqueue[self.unit][self.manip][0][self.interface.currentlistitemqueue[self.unit][self.manip][2]]
            print "EXECUTING ITEM",currentlistitem.index
            if self.interface.getCoords(self.unit,self.manip) != [currentlistitem.x,currentlistitem.y,currentlistitem.z]:
                z_offset = 0
                self.interface.waitForReady(self.unit,self.manip)      
                if self.unit == 0 and self.manip == 0:
                    self.interface.moveToWithoutWaiting(self.unit,self.manip,currentlistitem.x,currentlistitem.y,self.interface.getCoords(0,0)[2])
                else:
                    if self.interface.currentlistitemqueue[self.unit][self.manip][3] != 0:
                        if self.interface.currentlistitemqueue[self.unit][self.manip][4] == "zlift":
                            self.interface.moveToRelWithoutWaiting(self.unit,self.manip,0.0,0.0,-self.interface.currentlistitemqueue[self.unit][self.manip][3])
                            self.interface.waitForReady(self.unit,self.manip)
                            z_offset = self.interface.currentlistitemqueue[self.unit][self.manip][3]
                        elif self.interface.currentlistitemqueue[self.unit][self.manip][4] == "axial":
                            
                            if not firstpoint:
                                Mstartpoint = copy.deepcopy(self.interface.motorcoordinates[self.unit][self.manip])
                                MstartpointStage = self.interface.myarrows.deviceReadout[self.unit][self.manip].getStagefromMCoord(Mstartpoint[0],Mstartpoint[1],Mstartpoint[2])
                                firstoffsetpoint = [MstartpointStage[0] + self.interface.myarrows.deviceReadout[self.unit][self.manip].axialUnitVector[0]*self.interface.currentlistitemqueue[self.unit][self.manip][3], MstartpointStage[1] + self.interface.myarrows.deviceReadout[self.unit][self.manip].axialUnitVector[1]*self.interface.currentlistitemqueue[self.unit][self.manip][3],MstartpointStage[2] + self.interface.myarrows.deviceReadout[self.unit][self.manip].axialUnitVector[2]*self.interface.currentlistitemqueue[self.unit][self.manip][3]]
                                #print "FIRSTOFFSETPOINT",firstoffsetpoint
                                firstoffsetpointM= self.interface.myarrows.deviceReadout[self.unit][self.manip].getMfromStageCoord(firstoffsetpoint[0],firstoffsetpoint[1],firstoffsetpoint[2])
                                #print "FIRSTOFFSETPOINTM",firstoffsetpointM                            
                                self.interface.moveToWithoutWaiting(self.unit,self.manip,firstoffsetpointM[0],firstoffsetpointM[1],firstoffsetpointM[2])
                                self.interface.waitForReady(self.unit,self.manip)
                                self.interface.askCoords(self.unit,self.manip)
                            else:
                                firstpoint = False
                            secondoffsetpointstage = self.interface.myarrows.deviceReadout[self.unit][self.manip].getStagefromMCoord(currentlistitem.x,currentlistitem.y,currentlistitem.z)
                            secondoffsetpoint = [secondoffsetpointstage[0]+self.interface.myarrows.deviceReadout[self.unit][self.manip].axialUnitVector[0]*self.interface.currentlistitemqueue[self.unit][self.manip][3],secondoffsetpointstage[1]+self.interface.myarrows.deviceReadout[self.unit][self.manip].axialUnitVector[1]*self.interface.currentlistitemqueue[self.unit][self.manip][3],secondoffsetpointstage[2]+self.interface.myarrows.deviceReadout[self.unit][self.manip].axialUnitVector[2]*self.interface.currentlistitemqueue[self.unit][self.manip][3]]
                            #print "SECONDOFFSETPOINT",secondoffsetpoint                               
                            secondoffsetpointM = self.interface.myarrows.deviceReadout[self.unit][self.manip].getMfromStageCoord(secondoffsetpoint[0],secondoffsetpoint[1],secondoffsetpoint[2])
                            #print "SECONDOFFSETPOINTM",secondoffsetpointM                                  
                            self.interface.moveToWithoutWaiting(self.unit,self.manip,secondoffsetpointM[0],secondoffsetpointM[1],secondoffsetpointM[2]-z_offset)
                            self.interface.waitForReady(self.unit,self.manip)
                            self.interface.askCoords(self.unit,self.manip)
                        
                    self.interface.moveToWithoutWaiting(self.unit,self.manip,currentlistitem.x,currentlistitem.y,currentlistitem.z)
                self.interface.waitForReady(self.unit,self.manip)
                self.interface.askCoords(self.unit,self.manip)            
            
            commandarray = []
            for commandItem in currentlistitem.commandLayout.containedItems:
                commandarray.append([self.unit,self.manip,commandItem.t,commandItem.binvals])
            self.interface.sendBinary(commandarray)
            
            logicactivated = False
            print "ddenabled",currentlistitem.dropdownEnabled
            print "logic",currentlistitem.logic
            print "parsestring",self.interface.logicParser.parseString(currentlistitem.logic)
            print "times",self.interface.currentlistitemqueue[self.unit][self.manip][1]
            
            if currentlistitem.dropdownEnabled:
                if currentlistitem.logic != "" and currentlistitem.logic != None:
                    print "CHECKING TIMES"
                    if self.interface.currentlistitemqueue[self.unit][self.manip][1][currentlistitem.index] > 0:
                        print "CHECKING LOGIC"                        
                        if self.interface.logicParser.parseString(currentlistitem.logic):
                            print "LOGIC VERIFIED SETTING NEXT ITEM TO",currentlistitem.goto
                            self.interface.currentlistitemqueue[self.unit][self.manip][2] = currentlistitem.goto
                            self.interface.currentlistitemqueue[self.unit][self.manip][1][currentlistitem.index] -= 1
                            logicactivated = True
                        
            if logicactivated == False:
                self.interface.currentlistitemqueue[self.unit][self.manip][2] += 1
               
            self.newthread = listItemExec(self.interface,self.unit,self.manip)
            self.interface.threadqueue[self.unit].append(self.newthread)
        else:
            self.interface.stopDigitalInput()
            print "####################DONE EXECUTING LIST ITEMS#########################"
            

class startDigitalInputThread( threading.Thread ):
    def __init__(self,interfacein,digitalinputin):
        threading.Thread.__init__(self)
        self.interface = interfacein
        self.digitalinput = digitalinputin
    def run ( self ):
        self.interface.digitalinput = self.digitalinput
        self.interface.logicParser = self.digitalinput.logicParser
        self.interface.digitalInputOn = True
        self.digitalinput.start()

class stopDigitalInputThread( threading.Thread ):
    def __init__(self,interfacein,digitalinputin):
        threading.Thread.__init__(self)
        self.interface = interfacein
        self.digitalinput = digitalinputin
    def run ( self ):
        self.interface.digitalInputOn = False
        
class sendBinaryThread( threading.Thread ):
    def __init__(self,params,dataControl):
        threading.Thread.__init__(self)
        self.params = params
        self.dataControl = dataControl
    def run ( self ):
        
        pattern = ""        
        
        for command in self.params:
            pattern = ""
            for tfval in command[3]:

                if tfval == True:
                    pattern = pattern + '1'
                else:
                    pattern = pattern + '0'
            
            pattern = int(pattern,2)
            command.append(pattern)
                
        for command in self.params:
            print __builtin__.bin(command[4])
            
            self.dataControl.DOut(UL.FIRSTPORTA, command[4])
            
            #Is delay before or after?
            time.sleep(command[2]*.001)
            
        print "Sending binary complete."
            

class waitForReadyThread ( threading.Thread ):
    def __init__(self,Interfacein,unit,manip=None):
        threading.Thread.__init__(self)
        self.interface = Interfacein
        self.unit = unit
        self.manip = manip
    def run ( self ):
        self.interface.MyUnit[self.unit].waitUntilReady(self.manip)

class getStatusThread ( QObject, threading.Thread ):
    
    updateArrows = pyqtSignal()
    updateArrowsAlternate = pyqtSignal()

    def __init__(self,Interfacein,unit,manip=None):
        super(getStatusThread, self).__init__(None)
        threading.Thread.__init__(self)
        self.interface = Interfacein
        self.unit = unit
        self.manip = manip
        
    def run ( self ):
        if (self.interface.myarrows != None):
            self.updateArrows.connect(self.interface.myarrows.updateTextSlot)    
        if (self.interface.myarrowsalternate != None):
            self.updateArrowsAlternate.connect(self.interface.myarrowsalternate.updateTextSlot)        
        
        self.interface.MyUnit[self.unit].get_status_all(self.manip)
        if (self.interface.myarrows != None):
            self.updateArrows.emit()
        if (self.interface.myarrowsalternate != None):
            self.updateArrowsAlternate.emit()


class askCoordsThread (QObject, threading.Thread ):
    updateArrows = pyqtSignal()
    updateArrowsAlternate = pyqtSignal()
    
    def __init__(self,Interfacein,unit,manip=None):
        super(askCoordsThread, self).__init__(None)
        threading.Thread.__init__(self)
        self.interface = Interfacein
        self.unit = unit
        self.manip = manip
    def run ( self ):
        if (self.interface.myarrows != None):
            self.updateArrows.connect(self.interface.myarrows.updateTextSlot)    
        if (self.interface.myarrowsalternate != None):
            self.updateArrowsAlternate.connect(self.interface.myarrowsalternate.updateTextSlot)               
        
        print("ASKING COORDS....")
        time.sleep(.1)
        self.interface.MyUnit[self.unit].get_motors_coord_um(self.manip)
        print "Unit",self.unit,"at",self.interface.motorcoordinates[self.unit]
        if (self.interface.myarrows != None and self.interface.initialized == True):
            self.updateArrows.emit()
        if (self.interface.myarrowsalternate != None and self.interface.initialized == True):
           self.updateArrowsAlternate.emit()
        
class moveRelThread ( threading.Thread ):
    def __init__(self,Interfacein,unit,manip,x,y,z):
        threading.Thread.__init__(self)
        
        self.interface = Interfacein
        self.unit = unit
        self.manip = manip
        self.x = x
        self.y = y
        self.z = z
        print "MOVEREL",self.unit,self.manip,self.x,self.y,self.z
    
    def run ( self ):
        self.interface.MyUnit[self.unit].move_relative_um(self.manip,self.x,self.y,self.z)
        
class moveToThread ( threading.Thread ):
    def __init__(self,Interfacein,unit,manip,x,y,z):
        threading.Thread.__init__(self)
        self.interface = Interfacein
        self.unit = unit
        self.manip = manip
        self.x = x
        self.y = y
        self.z = z
    
    def run ( self ):
        if self.interface.getCoords(self.unit,self.manip) != [self.x,self.y,self.z]:
            self.interface.MyUnit[self.unit].move_to_um(self.manip,self.x,self.y,self.z)
        else:
            print "Already in position, skipping move command"
        
        
class TraversePointsThread ( threading.Thread ):
    def __init__(self,Interfacein,unit,pointsarrayin):
        threading.Thread.__init__(self)
        self.interface = Interfacein
        self.unit = unit
        self.pointsarray = pointsarrayin
    
    def run ( self ):
        counter = 0
        self.z = self.interface.motorcoordinates[0][0][2]
        for x in self.pointsarray:
            print counter,": Moving to point ",x[0],",",x[1]
            self.interface.MyUnit[self.unit].waitUntilReady(0)
            self.interface.MyUnit[self.unit].move_to_um(0,x[0],x[1],self.z)
            self.interface.MyUnit[self.unit].get_motors_coord_um()
            self.interface.MyUnit[self.unit].waitUntilReady(0)
        
class moveXPlusThread ( threading.Thread ):
    def __init__(self,Interfacein,unit,manip,speedin):
        threading.Thread.__init__(self)
        self.interface = Interfacein
        self.unit = unit
        self.manip = manip
        self.speed = speedin
        #self.daemon = True
    
    def run ( self ):
        print"STARTING X MOVE**************************"
        if self.manip == 0:
            a='#1!'+self.speed+'+'
        if self.manip == 1:
            a='#4!'+self.speed+'+'
        self.interface.MyUnit[self.unit].talk(a)
        self.interface.arrowMoving = True
        
class moveXMinusThread ( threading.Thread ):
    def __init__(self,Interfacein,unit,manip,speedin):
        threading.Thread.__init__(self)
        self.interface = Interfacein
        self.unit = unit
        self.manip = manip
        self.speed = speedin
        #self.daemon = True
    def run ( self ):
        if self.manip == 0:
            a='#1!'+self.speed+'-'
        if self.manip == 1:
            a='#4!'+self.speed+'-'
        self.interface.MyUnit[self.unit].talk(a) 
        self.interface.arrowMoving = True
        
class moveYPlusThread ( threading.Thread ):
    def __init__(self,Interfacein,unit,manip,speedin):
        threading.Thread.__init__(self)
        self.interface = Interfacein
        self.unit = unit
        self.manip = manip
        self.speed = speedin
    
    def run ( self ):
        self.interface.isTalking = True
        if self.manip == 0:
            a='#2!'+self.speed+'+'
        if self.manip == 1:
            a='#5!'+self.speed+'+'
        self.interface.MyUnit[self.unit].talk(a)
        self.interface.arrowMoving = True

class moveYMinusThread ( threading.Thread ):
    def __init__(self,Interfacein,unit,manip,speedin):
        threading.Thread.__init__(self)
        self.interface = Interfacein
        self.unit = unit
        self.manip = manip
        self.speed = speedin
    def run ( self ):
        self.interface.isTalking = True
        if self.manip == 0:
            a='#2!'+self.speed+'-'
        if self.manip == 1:
            a='#5!'+self.speed+'-'
        self.interface.MyUnit[self.unit].talk(a)
        self.interface.arrowMoving = True
        
class moveZPlusThread ( threading.Thread ):
    def __init__(self,Interfacein,unit,manip,speedin):
        threading.Thread.__init__(self)
        self.interface = Interfacein
        self.unit = unit
        self.manip = manip
        self.speed = speedin
    def run ( self ):
        if self.manip == 0:
            a='#3!'+self.speed+'+'
        if self.manip == 1:
            a='#6!'+self.speed+'+'
        self.interface.MyUnit[self.unit].talk(a)
        self.interface.arrowMoving = True
        
class moveZMinusThread ( threading.Thread ):
    def __init__(self,Interfacein,unit,manip,speedin):
        threading.Thread.__init__(self)
        self.interface = Interfacein
        self.unit = unit
        self.manip = manip
        self.speed = speedin
    def run ( self ):
        if self.manip == 0:
            a='#3!'+self.speed+'-'
        if self.manip == 1:
            a='#6!'+self.speed+'-'
        self.interface.MyUnit[self.unit].talk(a)
        self.interface.arrowMoving = True
        
       
class stopXThread ( threading.Thread ):
    def __init__(self,Interfacein,unit,manip):
        threading.Thread.__init__(self)
        self.interface = Interfacein
        self.unit = unit
        self.manip = manip
    def run ( self ):
        if self.manip == 0:
            self.interface.MyUnit[self.unit].talk('#1!A')
        if self.manip == 1:
            self.interface.MyUnit[self.unit].talk('#4!A')
        self.interface.arrowMoving = False

class stopYThread ( threading.Thread ):
    def __init__(self,Interfacein,unit,manip):
        threading.Thread.__init__(self)
        self.interface = Interfacein
        self.unit = unit
        self.manip = manip
    def run ( self ):
        if self.manip == 0:
            self.interface.MyUnit[self.unit].talk('#2!A')
        if self.manip == 1:
            self.interface.MyUnit[self.unit].talk('#5!A')
        self.interface.arrowMoving = False

class stopZThread ( threading.Thread ):
    def __init__(self,Interfacein,unit,manip):
        threading.Thread.__init__(self)
        self.interface = Interfacein
        self.unit = unit
        self.manip = manip
    def run ( self ):
        if self.manip == 0:
            self.interface.MyUnit[self.unit].talk('#3!A')
        if self.manip == 1:
            self.interface.MyUnit[self.unit].talk('#6!A')
        self.interface.arrowMoving = False
        
class allStopThread ( threading.Thread ):
    def __init__(self,Interfacein,unit):
        threading.Thread.__init__(self)
        self.interface = Interfacein
        self.unit = unit
    def run ( self ):
        self.interface.unit.talk('#1!A')
        self.interface.unit.talk('#2!A')
        self.interface.unit.talk('#3!A') 
        self.interface.unit.talk('#4!A')
        self.interface.unit.talk('#5!A')
        self.interface.unit.talk('#6!A') 
        self.interface.arrowMoving = False
        
class setZeroThread( threading.Thread ):
    def __init__(self,Interfacein,unit,manip=None):
        threading.Thread.__init__(self)
        self.interface = Interfacein
        self.unit = unit
        self.manip = manip
        #self.manip = manip
    def run ( self ):
        if self.interface.portdata[self.unit][1] == "MSS":
            if self.manip == None:
                self.interface.MyUnit[self.unit].talk('#1!@S')
                self.interface.MyUnit[self.unit].talk('#2!@S')
                self.interface.MyUnit[self.unit].talk('#3!@S')
                self.interface.MyUnit[self.unit].talk('#4!@S')
                self.interface.MyUnit[self.unit].talk('#5!@S')
                self.interface.MyUnit[self.unit].talk('#6!@S')
            if self.manip == 0:
                self.interface.MyUnit[self.unit].talk('#1!@S')
                self.interface.MyUnit[self.unit].talk('#2!@S')
                self.interface.MyUnit[self.unit].talk('#3!@S')
            if self.manip == 1:
                self.interface.MyUnit[self.unit].talk('#4!@S')
                self.interface.MyUnit[self.unit].talk('#5!@S')
                self.interface.MyUnit[self.unit].talk('#6!@S')
            
#ORIGINAL CODE, PROBABLY PRETTY BUTCHERED AT THIS POINT
#    # starting the clock for the pygame loop
#    my_clock = pygame.time.Clock()
#    
#    # main loop, pygame
#    while 1:
#        # Maintain our framerate:
#        my_clock.tick(FRAMERATE)
#        # pyUniversal library - acquiring data from external DAQ board
#        """
#        pyUniversal library block:
#        """
#        """
#        DataValue = UL.cbAIn(BoardNum, Chan, Gain)
#        data.append( DataValue )
#        times.append( time.time()-tstart )
#        if times[-1] > 10.0:
#            tstart = time.time()
#            data=[]
#            times=[]
#        #print DataValue
#        # get TTL input from Clampex    
#        TTL_input = UL.cbDBitIn(BoardNum, PortNum, BitNum, DataValue2)
#        if TTL_input == 1:  # move only if a TTL signal received
#            if TTL_switch==0: # Incoming TTL signal only switches the switch once (could be long TTL signal, assayed twice)
#                Move_seq_marker=1 # good to move
#                print "TTL signal received"
#                TTL_switch=1
#        else:
#            TTL_switch=0 # as soon as the TTL signal is gone, the TTL_switch is switched off
#        
#        # end of pyUniversal library block
#        """
#        """
#        Move Sequence block
#        """
#        # version CCD_LN7_2.py uses absolute coordinates of the microscope stage in um as a reference in seq_coord
#        if Move_seq_marker==1 and command_exec==1:  # move only when the TTL signal marks command marker, and the 'm' key was pressed to mark the Move_seq_marker
#            if len(seq_coord)>0:
#                print 'Moving sequence initiated...'
#                # seq_coord already has the sequence of the absolute coordinates to move to (in the microscope stage coordinate system)
#                x,y,z=seq_coord.pop(0)            
#                MyUnit.move_to_um(x,y,z) 
#                mouse_seq.pop(0)
#            Move_seq_marker=0
#            
#        for event in pygame.event.get():
#            
#            if event.type == QUIT:
#                pygame.quit()
#                sys.exit()
#                    
#            keyinput = pygame.key.get_pressed() # returns the status of every key pressed - tuple
#            if keyinput[K_b]: brightness -= .1
#            if keyinput[K_n]: brightness += .1
#            if keyinput[K_c]: contrast -= .1
#            if keyinput[K_v]: contrast += .1
#            if keyinput[K_q]: cam.displayCapturePinProperties()
#            if keyinput[K_e]: cam.displayCaptureFilterProperties()
#            if keyinput[K_t]:
#                filename = str(time.time()) + ".jpg"
#                cam.saveSnapshot(filename, quality=80, timestamp=0)
#                shots += 1
#            
#            
#            
#    
#            
#            if event.type == KEYDOWN:
#                # memorizing/recalling positions            
#                for i in range(0,10):
#                    if event.key == ord(str(i)):
#                        if pygame.key.get_mods() & KMOD_CTRL: # CTRL+X remmebers position
#                            print 'CTRL+',str(i),' pressed, microscope positioned remembered'
#                            MyUnit.remembered_positions[i,:]=MyUnit.get_motors_coord_um()
#                            remembered_position_index.append(i)
#                            remembered_position_index.sort()
#                        elif pygame.key.get_mods() & KMOD_SHIFT: # SHIFT+X deletes position
#                            MyUnit.remembered_positions[i,:]=[0,0,0]
#                            del remembered_position_index[remembered_position_index.index(i)]
#                            print 'SHIFT+',str(i),' pressed, positioned deleted'
#                        else:
#                            if np.all(MyUnit.remembered_positions[i,:]==0): # if the coordinates are zeros, no moving
#                                pass
#                            else:
#                                print str(i),' pressed, microscope position recalled'
#                                x,y,z=MyUnit.remembered_positions[i,:]
#                                MyUnit.move_to_um(x,y,z)        
#                
#                # controlling the manipulator with arrows
#                if event.key == K_LEFT or event.key == ord('a'):
#                    moveRight = False
#                    moveLeft = True
#                if event.key == K_RIGHT or event.key == ord('d'):
#                    moveLeft = False
#                    moveRight = True
#                if event.key == K_UP or event.key == ord('w'):
#                    moveDown = False
#                    moveUp = True
#                if event.key == K_DOWN or event.key == ord('s'):
#                    moveUp = False
#                    moveDown = True
#                # Z axis movement
#                if event.key == ord('r'):
#                    moveZDown = False
#                    moveZUp = True
#                if event.key == ord('f'):
#                    moveZUp = False
#                    moveZDown = True

#                    
#                # initiating the sequence of stage movements                
#                if event.key == ord('m'): # every 'm'-keypress switches the status of the move marker
#                    if command_exec==0:
#                        command_exec=1
#                    else:
#                        command_exec=0
#                    

#                    
#                    
#            if event.type == KEYUP:
#                if event.key == K_ESCAPE:
#                    pygame.quit()
#                    sys.exit()
#                if event.key == K_p: # stops the movement along all axes
#                    MyUnit.talk('#1!A')
#                    MyUnit.talk('#2!A')
#                    MyUnit.talk('#3!A') 
#                
#            # mouseclick processing
#            if event.type == pygame.MOUSEBUTTONDOWN and event.button == M_LEFT: # left mouse clicked (M_LEFT=1)
#                posn_of_click = event.dict['pos']    # get the coordinates
#                print(posn_of_click)
#                #pygame.draw.circle(screen, Color('red'), posn_of_click, 64)
#                #scan_seq.append(stage_message)
#                mouse_seq.append(posn_of_click)
#                temp_coord=MyUnit.get_motors_coord_um()
#                x_a=-1*round((posn_of_click[0]-res[0]/2)/pixel_4x[0],4) # correct polarity
#                temp_coord[0]=temp_coord[0]+x_a
#                x_b=-1*round((posn_of_click[1]-res[1]/2)/pixel_4x[1],4) # correct polarity
#                temp_coord[1]=temp_coord[1]+x_b
#                seq_coord.append(temp_coord) # sequence of absolute coordinates in um (microscope coordinates) to go to
#                
#            if event.type == pygame.MOUSEBUTTONDOWN and event.button == M_RIGHT: # left mouse clicked (M_RIGHT=3)          
#                if len(mouse_seq)>0:
#                    mouse_seq.pop()
#                    seq_coord.pop() # seq_coord is a list of lists ([[x1,y1,z1],[x2,y2,z2]])
#                


#  This code updates coordinates from the motor status messages; it isn't advised to 
#  use this for program variables since the status message transmits more information 
#  and thus clips 2 decimals off the end of the coordinates.
#            if 'P' in motor_message:
#                print motor_message
#                index_P=motor_message.index('P')
#                if motor_message[index_P+1]=='+':
#                    motor_coord[i]=float(motor_message[index_P+2:-3])
#                else:
#                    motor_coord[i]=float(motor_message[index_P+1:-3])
#            else: # the message didn't get in the first time, repeating
#                motor_message=self.MyUnit2.talk(a)
#                print motor_message
#                index_P=motor_message.index('P')
#                if motor_message[index_P+1]=='+':
#                    motor_coord[i]=float(motor_message[index_P+2:-3])
#                else:
#                    motor_coord[i]=float(motor_message[index_P+1:-3])

#Don't think this is currently used
#    def get_screen_coord(Device_number=0):
#        """
#        get the current coordinates of the microscope stage-Device_number=0 (always 
#        center of the screen) or the manipulators (Device_number>0)
#        """
#        if Device_number==0:
#            return res/2 # global variable!!! - correct
#        else:
#            return NaN  # to determine the coordinates of the manipulators (more precisely tip of the pipette - need to use object recognition in opencv)
        
#    def send_TTL(channel=0, time=1): # time in ms
#        pass
