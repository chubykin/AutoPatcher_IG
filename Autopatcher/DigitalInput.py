# -*- coding: utf-8 -*-
"""
Created on Mon Jul 16 16:12:33 2012

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

import autopatcher
import threading
import UniversalLibrary as UL
import LogicParser
import time

Gain = UL.BIP5VOLTS

#This is a class for communicating with the Measurement Computing board.  It queries the board
#as fast as it can for all provided channels, and stores currently up to 10000 data units for
#each channel.

#It also has an instance of logicparser, which isn't currently used as it's commented out.
#However LogicParser can be used with this to tell if certain conditions are met and to change how
#ListItemExec in MSSInterface executes.
class DigitalInput(threading.Thread):
    def __init__(self,interfacein,datacontrolin):
        #datacontrol = autopatcher.DataControl()
        threading.Thread.__init__(self)
        
        self.dataControl = datacontrolin
        self.boards = [0]
        self.channels = [0,1,2,3]
        self.data = []
        
        self.interface = interfacein
        
        #create a nested list with the boards and then the channels of the boards
        for boardnum in range (0,len(self.boards)):
            self.data.append([])
            for channelnum in range (0,len(self.channels)):
                self.data[boardnum].append([])
        self.framecount = 0
        self.outputcount = 0
                
                
        #self.currentEqns = ["A2 > 3000" , "(A1<2000)^(A2>3000)" , "(A1>2000)^((A2<2000)&((A3<2000)&(A4<2000)))"]
        
        self.logicParser = LogicParser.LogicParser(self)           
        
    def run(self):
        self.starttime = time.time()
        while(self.interface.digitalInputOn == True):
            for boardnum in range (0,len(self.boards)):
                for channelnum in range (0,len(self.channels)):
                    #print channelnum
                    self.data[boardnum][channelnum].append(self.dataControl.getData(boardnum,channelnum))#UL.cbAIn(boardnum, channelnum, Gain))
                    #print self.data[boardnum][channelnum][-1]
                    if len(self.data[boardnum][channelnum]) >= 10000:
                        self.data[boardnum][channelnum].pop(0)
            self.framecount += 1
            self.outputcount+=1
            
            if self.outputcount == 100:
                print "DIGITALINPUT FPS:",self.framecount/(time.time()-self.starttime)
                self.starttime = time.time()
                self.outputcount = 0
                self.framecount = 0
#            result = []                
#            for eqn in self.currentEqns:
#                result.append(self.logicParser.parseString(eqn))
            #print self.data[0][0][-1],self.data[0][1][-1],self.data[0][2][-1],self.data[0][3][-1]
            #print result
        
        print "####################DIGITALINPUT STOP##########################"
                        
    def getVal(self,boardnum,channelnum):
        if len(self.data[boardnum][channelnum]) != 0:
            return self.data[boardnum][channelnum][-1]
    

#di = DigitalInput()
#di.run()


#import UniversalLibrary as UL
#
#BoardNum = 0
#Gain = UL.BIP5VOLTS
#Chan = 1
#
#while 1:
#    DataValue = UL.cbAIn(BoardNum, Chan, Gain)
#    EngUnits = UL.cbToEngUnits(BoardNum, Gain, DataValue)
#
#    print DataValue, EngUnits