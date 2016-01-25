# -*- coding: utf-8 -*-
"""
MssUnit.py
MssUnitChr2.py - 12/03/11 - change the move_to and move_relative to make the input parameters - coordinates in um (micrometers)
MockUnit.py - 01/28/12 - made to mimick MssUnit functionality without the hardware

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
__version__="version 0.1"
__date__="Mon Oct 31 22:36:50 2011"
__copyright__="Copyright (c) 2011 Alex Chubykin"
__license__="Python"

import numpy as np
#import crc16
#import crc16my
import crc16my2 as crc
from serial import Serial
import time

class MssUnit(Serial):
    device={}
    ASCII_Commands={'STX':0x02,'DLE':0x10,'NAK':0x15,'ETX':0x03,'ESC':0x1b,'ACK':0x06}
    Commands={'GetStatus':'#x?Z','GotoPosition':'#x!GF','GotoRelativePosition':'#x!DF','GetPosition':'#x?P'}
    data_read=[]
    all_data_read=[]
    resolution=(1344,1024) # default screen resolution
    pixel_4x=[1.532,1.532] # one pixel at 4x magnification, in um [x,y]
    full_step=1.75 # one full step, in um
    current_coord=[] # in MssUnitChr2.py  in um

    def __init__(self, port, baudrate, **kwargs):
        """ 
        Initialize the Serial superclass, and setup some default values
        """
        pass
    
    def getChecksum(self,data_str):
        #return crc16.crc16xmodem(data_str)
        #return crc16my.crc16my(data_str)
        #return crc.crc16(data_str)
        return crc.crc16(data_str)
    
    
    def serial_read(self):
        self.data_read=[]
        return self.data_read
    
    def serial_read_all(self):
        return []         
    
    def serial_write(self,data):
        return []  
    
    def serial_purge(self):
        pass
     
    def get_motors_coord(self,first_motor=1): #returns the motor coordinates in steps
        coord=[]        
        return coord
        
    def get_motors_coord_um(self, first_motor=1): # returns the motor coordinates in um
        coord=[]        
        return coord        
    
    
        
    def set_camera_resolution(self,x,y):
        ratio=[x/self.resolution[0], y/self.resolution[1]]        
        self.resolution=(x,y)
        self.pixel_4x[0]=self.pixel_4x[0]*ratio[0]
        self.pixel_4x[1]=self.pixel_4x[1]*ratio[1]
        return True        
    
    def screen2motor(self,(x_screen,y_screen), first_motor=1):
        screen2motor_coord=[]
        motor_coord=self.get_motors_coord(first_motor)
        if first_motor==1:
            screen2motor_coord[0]=x_screen*motor_coord[0]/(self.resolution[0]/2)
            screen2motor_coord[1]=y_screen*motor_coord[1]/(self.resolution[1]/2)
            return screen2motor_coord
        else:
            return np.NaN
           
           
           
    def move_to_um(self, x=np.NaN,y=np.NaN,z=np.NaN, first_motor=1): # coordinates are sent in um
        """
        move the three motors starting from the number defined by counter to the final position x,y,z
        """
        messages=[]        
        return messages
    
    def move_relative_um(self, x=np.NaN,y=np.NaN,z=np.NaN, first_motor=1): # coordinates are in um
        """
        move the three motors relative to the current position,  x,y,z are screen coordinates. The first motor determines the starting motor as x
        """
        messages=[]        
        return messages
        
        

    def move_to(self, x=np.NaN,y=np.NaN,z=np.NaN, first_motor=1):
        """
        move the three motors starting from the number defined by counter to the final position x,y,z
        """
        messages=[]        
        return messages
    
    def move_relative(self, x=np.NaN,y=np.NaN,z=np.NaN, first_motor=1): # coordinates are in screen pixels
        """
        move the three motors relative to the current position,  x,y,z are screen coordinates. The first motor determines the starting motor as x
        """
        messages=[]        
        return messages
        
    
        
        
    def talk(self,toSend):
        ptr=[]
        self.flush()
        checksum=self.getChecksum(toSend)
        print 'checksum is:',checksum
        ptr=[ord(e) for e in toSend]
        
        #ptr.insert(0,self.ASCII_Commands['STX'])
        
        # this part is confirmed        
        loNibble=np.uint8(checksum)
        hiNibble=np.uint8(np.right_shift(checksum,8))
        ptr.append(hiNibble)
        ptr.append(loNibble)
        
        
        ptr.append(self.ASCII_Commands['DLE'])
        ptr.append(self.ASCII_Commands['ETX'])
        #ptr.append(0)
        
        print ptr
        ptr_chr=[chr(e) for e in ptr]
        #ptr_chr.append('\r\n')
        ptr1=''.join(ptr_chr) # converting a list of chars into a string
        print ptr1

        return []
        
    def talk_back(self):
        pass
        
        
    
def main():

    # Baud must match that of Arduino\lolshield sketch:
    # 300, 1200, 2400, 4800, 9600, 14400, 19200 or 28800: Values greater than
    # this seem to fail.
    BAUD = 19200 # 19200 for the Rig, 9600 for arduino
    # Port the Arduino\lolshield is on:
    PORT = 'COM1' # 'COM4'- Gateway # COM6 - Tanya's PC # COM1 - Rig PC
    MyUnit = MssUnit(port=PORT, baudrate=BAUD,timeout=1)
    

    time.sleep(1.5)

    for i in range(0,3): # important! - running this cycle results in a positive response code 0x10 for the 7th device - don't know why
        a='#'+str(i)+'?Z' # only #7?Z works, not #7?P
        MyUnit.talk(a)
        time.sleep(0.1)

    
    
    
if __name__ == "__main__":
    main()
                        
                
        
        
        
        
        
        