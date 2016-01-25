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

class MssUnit(Serial):
    device={}
    ASCII_Commands={'STX':0x02,'DLE':0x10,'NAK':0x15,'ETX':0x03,'ESC':0x1b,'ACK':0x06}
    Commands={'GetStatus':'#x?Z','GotoPosition':'#x!GF','GotoRelativePosition':'#x!DF','GetPosition':'#x?P'}
    data_read=[]
    all_data_read=[]
    resolution=(1344,1024) # default screen resolution
    pixel_4x=[1.532,1.532] # one pixel at 4x magnification, in um [x,y]
    full_step=4.9705 #full_step=5 # full_step=1.75 # one full step, in um
    
    remembered_coord_um=[]
    Mremembered_coord_um=[]
    remembered_positions=np.zeros((10,3)) # only the fixed number of spots for positions (keys 1-0)
    
    def __init__(self, port, baudrate, unitID, **kwargs):
        """ 
        Initialize the Serial superclass, and setup some default values
        """
        
        super(MssUnit,self).__init__(port=port,baudrate=baudrate,**kwargs)
        self.device={'IsPresent':1,'position':0,'pitch':0}
        
        self.unitID = unitID #This is the MSS Unit number that MSSInterface refers to this unit as, most likely 0 or 1
        self.unitType = "MSS"        
        
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
        ratio=[x/self.resolution[0], y/self.resolution[1]]        
        self.resolution=(x,y)
        self.pixel_4x[0]=self.pixel_4x[0]*ratio[0]
        self.pixel_4x[1]=self.pixel_4x[1]*ratio[1]
        return True      
    
    def setParent(self,parentin):
        self.parent = parentin
        
    def getChecksum(self,data_str):
        #return crc16.crc16xmodem(data_str)
        #return crc16my.crc16my(data_str)
        #return crc.crc16(data_str)
        return crc.crc16(data_str)
    
    
    def serial_read(self):
        self.data_read=[]
        a=self.read()
        if a!=0:
            self.data_read.append(a)
            while a!=0:
                a=self.read()
                self.data_read.append(a)
        return self.data_read
    
    def serial_read_all(self):
        return self.readline()           
    
    def serial_write(self,data,iteration = 0):
        try:
            return self.write(data)
        except:
            print "SERIAL WRITE EXCEPTION, RESENDING DATA"
            if iteration == 20:
                print "################MAX SERIAL WRITE EXCEPTIONS REACHED, RETURNING###################"
                return
            else:
                return self.serial_write(data,iteration+1)
    
    def serial_purge(self):
        self.flush()
        #self.flushInput()
        #self.flushOutput()
        pass
     
     #DON'T USE THIS.  IT RETURNS COORDINATES IN THE BOX COORDINATES, WHICH HAVE TO
     #BE PROCESSED W/ REGARD TO FULLSTEPS AND MICROSTEPS.  THE NUMBER AFTER THE DECIMAL IS
     #NOT THE ACTUAL DECIMAL VALUE, SEE DOCUMENTATION AND get_motors_coord_um
    def get_motors_coord(self,manip = None): #returns the motor coordinates in steps
        coord=[]     
        #no manipulator defined, all motors
        if manip == None:
            startmot = 1
            endmot = 7
        #first manipulator only
        if manip == 1:
            startmot = 1
            endmot = 4
        #second manipulator only
        if manip == 2:
            startmot = 4
            endmot = 7
        for i in range(startmot,endmot):
            a='#'+str(i)+'?P' 
            b=self.talk(a)
            if 'P' in b:
                coord.append(float(b[b.index('P')+1:-2]))
            else:
                b=self.talk(a)
                coord.append(float(b[b.index('P')+1:-2]))
        if manip == None:
            return [coord[:3],coord[3:]]
        else:
            return coord
        
    def get_motors_coord_um(self, manip=None): # returns the motor coordinates in um
        print "GETTING COORDS FOR UNIT ",self.unitID
        coord=[]        
        #no manipulator defined, all motors
        if manip == None:
            startmot = 1
            endmot = 7
        #first manipulator only
        if manip == 0:
            startmot = 1
            endmot = 4
        #second manipulator only
        if manip == 1:
            startmot = 4
            endmot = 7
        for i in range(startmot,endmot):
            a='#'+str(i)+'?Z' 
            
            b=self.talk(a)
            
            if i == 1:
                if "E+" in b:
                    #print "END POS UNIT:",self.unitID,"AXIS: X0+"
                    self.x0EndPosPlus = True
                else:
                    self.x0EndPosPlus = False
                if "E-" in b:
                    #print "END POS UNIT:",self.unitID,"AXIS: X0-"
                    self.x0EndPosMinus = True
                else:
                    self.x0EndPosMinus = False
            if i == 2:
                if "E+" in b:
                    #print "END POS UNIT:",self.unitID,"AXIS: Y0+"
                    self.y0EndPosPlus = True
                else:
                    self.y0EndPosPlus = False
                if "E-" in b:
                    #print "END POS UNIT:",self.unitID,"AXIS: Y0-"
                    self.y0EndPosMinus = True
                else:
                    self.y0EndPosMinus = False
            if i == 3:
                if "E+" in b:
                    #print "END POS UNIT:",self.unitID,"AXIS: Z0+"
                    self.z0EndPosPlus = True
                else:
                    self.z0EndPosPlus = False
                if "E-" in b:
                    #print "END POS UNIT:",self.unitID,"AXIS: Z0-"
                    self.z0EndPosMinus = True
                else:
                    self.z0EndPosMinus = False           
            if i == 4:
                if "E+" in b:
                    #print "END POS UNIT:",self.unitID,"AXIS: X1+"
                    self.x1EndPosPlus = True
                else:
                    self.x1EndPosPlus = False
                if "E-" in b:
                    #print "END POS UNIT:",self.unitID,"AXIS: X1-"
                    self.x1EndPosMinus = True
                else:
                    self.x1EndPosMinus = False
            if i == 5:
                if "E+" in b:
                    #print "END POS UNIT:",self.unitID,"AXIS: Y1+"
                    self.y1EndPosPlus = True
                else:
                    self.y1EndPosPlus = False
                if "E-" in b:
                    #print "END POS UNIT:",self.unitID,"AXIS: Y1-"
                    self.y1EndPosMinus = True
                else:
                    self.y1EndPosMinus = False
            if i == 6:
                if "E+" in b:
                    #print "END POS UNIT:",self.unitID,"AXIS: Z1+"
                    self.z1EndPosPlus = True
                else:
                    self.z1EndPosPlus = False
                if "E-" in b:
                    #print "END POS UNIT:",self.unitID,"AXIS: Z1-"
                    self.z1EndPosMinus = True
                else:
                    self.z1EndPosMinus = False            
            
            if self.unitID == 0:
                print b
            if b == None:
                self.parent.threadqueue[self.unitID].insert(0,mssi.askCoordsThread(self.parent,self.unitID))
                return
            if 'P' in b:
                #print "COORDS UNIT",self.unitID,"MANIP",i
                #print "B equals",b
                coordstring = b[b.index('P')+1:-4]
                #print "String equals",coordstring
                fullsteps = float(coordstring[:-2])
                microsteps = int(coordstring[-2:])
                #print "fullsteps",fullsteps
                #print "microsteps",microsteps
                sign = "+"                
                
                if fullsteps < 0:
                    fullsteps +=1
                    sign = "-"
                #print "fullsteps after increment",fullsteps
                
                actualcoords = fullsteps*self.full_step
                
                #print "actualcoords pre microsteps",actualcoords
                
                if sign == "+":
                    #print "MICROSTEP DISTANCE+:",((float(microsteps)*2.0)/100.0)*self.full_step
                    actualcoords += ((float(microsteps)*2.0)/100.0)*self.full_step
                else:
                    #print "MICROSTEP DISTANCE-:",(((50-float(microsteps))*2.0)/100.0)*self.full_step
                    actualcoords -= (((50-float(microsteps))*2.0)/100.0)*self.full_step
                #print "actualcoords post microsteps",actualcoords
                
                coord.append(round(float(actualcoords),5)) # recalculate in um, full_step is 1 step in mm
            else: # if didn't get through, repeat
                b=self.talk(a)
                coord.append(round(float(b[b.index('P')+1:-3])*self.full_step,4))
        if manip == None:
            self.parent.motorcoordinates[self.unitID][0]=copy.deepcopy(coord[:3])
            if self.parent.portdata[self.unitID][2] == 2:
                self.parent.motorcoordinates[self.unitID][1]=copy.deepcopy(coord[3:])
        if manip == 0:
            self.parent.motorcoordinates[self.unitID][0]=copy.deepcopy(coord[:3])
        if manip == 1:
            self.parent.motorcoordinates[self.unitID][1]=copy.deepcopy(coord[:3])
        
        
#    def set_camera_resolution(self,x,y):
#        ratio=[x/self.resolution[0], y/self.resolution[1]]        
#        self.resolution=(x,y)
#        self.pixel_4x[0]=self.pixel_4x[0]*ratio[0]
#        self.pixel_4x[1]=self.pixel_4x[1]*ratio[1]
#        return True        
#    
#    def screen2motor(self,(x_screen,y_screen), first_motor=1):
#        screen2motor_coord=[]
#        motor_coord=self.get_motors_coord(first_motor)
#        if first_motor==1:
#            screen2motor_coord[0]=x_screen*motor_coord[0]/(self.resolution[0]/2)
#            screen2motor_coord[1]=y_screen*motor_coord[1]/(self.resolution[1]/2)
#            return screen2motor_coord
#        else:
#            return np.NaN
           
           
           
    def move_to_um(self, manip, x=np.NaN,y=np.NaN,z=np.NaN): # coordinates are sent in um
        """
        move the three motors starting from the number defined by counter to the final position x,y,z
        """
        #self.waitUntilReady(manip)
        print ("MOVING ABS UNIT",self.unitID,"MANIPULATOR",manip,"TO UM, X:",x,"Y:",y,"Z:",z)
        messages=[]        
        coord=[x,y,z]     
        
        if manip == 0:
            startmot = 1
            endmot = 4
        if manip == 1:
            startmot = 4
            endmot = 7
            
        count = 0
        for i in range(startmot,endmot): # range from 0 to 3 (not including 3)            
            if not np.isnan(coord[count]): # if not NaN then move
                print "MOVING MOTOR "+str(i)
                
                #print "COORD[COUNT]",coord[count]                
                
                coord[count]=coord[count]/self.full_step
                
                #coord[count] -= .47
                #print "COORD[COUNT] IN FULLSTEPS",coord[count]
                microstepsval = abs(coord[count])-abs(float(int(coord[count])))
                #print "PROPORTIONAL MICROSTEPS:",microstepsval                
                
                if coord[count] > 0:
                    usteps = int(round(((microstepsval)/2.0)*100.0,0))
                    #print "POSITIVE USTEPS",usteps
                    sign = "+"
                    #coord[count] = int(coord[count])
                else:
                    usteps = int(round(50.0-((microstepsval)/2.0)*100.0,0))
                    sign = "-"
                    #print "NEGATIVE USTEPS",usteps
                    if usteps != 50:#usteps != 0 and usteps != 50:
                        #print "DECREMENTING coord[count]"
                        coord[count]-=1
                    #usteps = 50.0-((microstepsval)/2.0)*100.0
                    #coord[count] = int(coord[count])#+1
                
                if usteps == 50:
                    usteps = 0
                #print "ACTUAL MICROSTEPS:",usteps
                
                a='#'+str(i)+'!GS'+sign+'%05d' %abs(int(coord[count]))+"."+'%02d' %usteps # moves them fast
                print "MESSAGE IS:",a                
                b=self.talk(a)
                messages.append(b)
            count +=1
        return messages
        
    def move_relative_um(self, manip, x=np.NaN,y=np.NaN,z=np.NaN): # coordinates are in um
    
        print "MOVERELUNIT",self.unitID,manip,x,y,z
        """
        move the three motors relative to the current position,  x,y,z are screen coordinates. The first motor determines the starting motor as x
        """
        #self.waitUntilReady(manip)
        print ("MOVING RELATIVE UNIT",self.unitID,"MANIP",manip," X:",x,"Y:",y,"Z:",z)
        messages=[]        
        coord=[x,y,z]
        
        if manip == 0:
            startmot = 1
            endmot = 4
        if manip == 1:
            startmot = 4
            endmot = 7
        #self.current_coord=self.get_motors_coord_um()
        count = 0
        for i in range(startmot,endmot):
            if not np.isnan(coord[count]): # if not NaN then move
                #coord[i]=self.current_coord[i]+coord[i]
                print "MOVING MOTOR "+str(i)
                #print "COORD[COUNT] = ",coord[count]
                
                if coord[count] >= 0:
                    sign = "+"
                if coord[count] <= 0:
                    sign = "-"
                
                coord[count]=coord[count]/self.full_step
                #print "COORD[COUNT] IN FULLSTEPS",coord[count]
                microstepsval = abs(coord[count])-abs(float(int(coord[count])))
                #print "PROPORTIONAL MICROSTEPS:",microstepsval
                
                if coord[count] >= 0:
                    usteps = int(round(((microstepsval)/2.0)*100.0,0))
                    #coord[count] = int(coord[count])
                else:
                    usteps = int(round(((50-microstepsval)/2.0)*100.0,0))
                    #usteps = 50.0-((microstepsval)/2.0)*100.0
                    #coord[count] = int(coord[count])#+1
                    
                #print "ACTUAL MICROSTEPS:",usteps
                
                #usteps = (int(50-100*((coord[count]%self.full_step)/self.full_step)/2))%50
                
                a='#'+str(i)+'!DS'+sign+'%05d' %abs(int(coord[count]))+"."+'%02d' %usteps
                
                print "MESSAGE IS:",a
#                a='#'+str(i)+'!DS'+'%+011.4f' %coord[count]#+'%+06d'+str(usteps) # has to be formatted to #X!DFXXXXX.XXXX
                # a='#'+str(first_motor+i)+'!DF'+'{:+011.4f}'.format(coord[i])  # alternative, newere python syntaxis
                b=self.talk(a)
                messages.append(b)
            count +=1
        return messages        

    #DON'T USE, UNLESS YOU'RE GOING TO PROPERLY CALCULATE MICROSTEPS BEFOREHAND.
    def move_to(self,manip, x=np.NaN,y=np.NaN,z=np.NaN):
        """
        move the three motors starting from the number defined by counter to the final position x,y,z
        """
        print "MOVE_TO UNIT",self.unitID,"MANIP",manip," X:",x,"Y:",y,"Z:",z  
        
        if manip == 0:
            startmot = 1
            endmot = 4
        if manip == 1:
            startmot = 4
            endmot = 7

        messages=[]        
        coord=[x,y,z]
        #self.pixel_4x[2]=self.pixel_4x[0] # the 'z' pixel doesn't exist, setting it equal to x
        count=0        
        for i in range(startmot,endmot): # range from 0 to 3 (not including 3)
            if not np.isnan(coord[count]): # if not NaN then move
                #self.waitUntilReady()
                "MOVING MOTOR "+str(i)
                coord[count]=coord[count]*self.pixel_4x[count]/self.full_step
                a='#'+str(startmot+i)+'!GF'+coord[count] # moves them fast
                b=self.talk(a)
                messages.append(b)
            count +=1
        return messages
        


    #Don't use this, the get coordinates command now asks for all info
    def get_status_all(self,manip=None):
        if manip == 0 or manip == None:        
            for i in range(1,4):
                a='#'+str(i)+'?Z'
                motor_message=self.talk(a)
                time.sleep(0.1)
                
                if "#1:" in motor_message:
                    if "E+" in motor_message:
                        print "END POS UNIT:",self.unitID,"AXIS: X0+"
                        self.x0EndPosPlus = True
                    else:
                        self.x0EndPosPlus = False
                    if "E-" in motor_message:
                        print "END POS UNIT:",self.unitID,"AXIS: X0-"
                        self.x0EndPosMinus = True
                    else:
                        self.x0EndPosMinus = False
                if "#2:" in motor_message:
                    if "E+" in motor_message:
                        print "END POS UNIT:",self.unitID,"AXIS: Y0+"
                        self.y0EndPosPlus = True
                    else:
                        self.y0EndPosPlus = False
                    if "E-" in motor_message:
                        print "END POS UNIT:",self.unitID,"AXIS: Y0-"
                        self.y0EndPosMinus = True
                    else:
                        self.y0EndPosMinus = False
                if "#3:" in motor_message:
                    if "E+" in motor_message:
                        print "END POS UNIT:",self.unitID,"AXIS: Z0+"
                        self.z0EndPosPlus = True
                    else:
                        self.z0EndPosPlus = False
                    if "E-" in motor_message:
                        print "END POS UNIT:",self.unitID,"AXIS: Z0-"
                        self.z0EndPosMinus = True
                    else:
                        self.z0EndPosMinus = False
        if manip == 1 or manip == None:
            for i in range(4,7):
                a='#'+str(i)+'?Z'
                motor_message=self.talk(a)
                time.sleep(0.1)
                
                if "#4:" in motor_message:
                    if "E+" in motor_message:
                        print "END POS UNIT:",self.unitID,"AXIS: X1+"
                        self.x1EndPosPlus = True
                    else:
                        self.x1EndPosPlus = False
                    if "E-" in motor_message:
                        print "END POS UNIT:",self.unitID,"AXIS: X1-"
                        self.x1EndPosMinus = True
                    else:
                        self.x1EndPosMinus = False
                if "#5:" in motor_message:
                    if "E+" in motor_message:
                        print "END POS UNIT:",self.unitID,"AXIS: Y1+"
                        self.y1EndPosPlus = True
                    else:
                        self.y1EndPosPlus = False
                    if "E-" in motor_message:
                        print "END POS UNIT:",self.unitID,"AXIS: Y1-"
                        self.y1EndPosMinus = True
                    else:
                        self.y1EndPosMinus = False
                if "#6:" in motor_message:
                    if "E+" in motor_message:
                        print "END POS UNIT:",self.unitID,"AXIS: Z1+"
                        self.z1EndPosPlus = True
                    else:
                        self.z1EndPosPlus = False
                    if "E-" in motor_message:
                        print "END POS UNIT:",self.unitID,"AXIS: Z1-"
                        self.z1EndPosMinus = True
                    else:
                        self.z1EndPosMinus = False
        
    #Keep querying the unit until all motors respond as not moving; this keeps a queue item
    #from expiring before its action is completed.
    def waitUntilReady(self,manip):
        if manip == None:
            startmot = 1
            endmot = 7
        if manip == 0:
            startmot = 1
            endmot = 4
        if manip == 1:
            startmot = 4
            endmot = 7
            
        print("Waiting until ready UNIT",self.unitID,"MOTORS",startmot,"TO",endmot-1)
        isReady = False
        while isReady == False:
            isReady = True
            for i in range(startmot,endmot):
                a='#'+str(i)+'?Z'
                motor_message=self.talk(a)
                time.sleep(0.5)
                #REDO IN CASE OF ERROR
                breakoutcounter = 0
                while 'P' not in motor_message:
                    motor_message=self.talk(a)
                    breakoutcounter += 1
                    if breakoutcounter == 20:
                        print "WAITUNTILREADY TOO MANY FAILURES, BREAKING OUT"
                        break
                if 'M' in motor_message:
                    isReady = False
                    print("STILL MOVING")
        #Update motor coordinates after moving is complete
        #Actually don't do this, just queue the threads up, provides greater control over queueing
        #self.get_motors_coord_um()
        
    def talk(self,toSend):
            
        ptr=[]
        self.flush()
        checksum=self.getChecksum(toSend)
        #print 'checksum is:',checksum
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
        
        if self.silent == False:
            print ptr
        ptr_chr=[chr(e) for e in ptr]
        #ptr_chr.append('\r\n')
        ptr1=''.join(ptr_chr) # converting a list of chars into a string
        if self.silent == False:        
            print ptr1
            
        timeoutcounter = 0            
        while self.inWaiting()<1:
            if self.silent == False:
                print 'sending STX...'
            self.serial_write(chr(self.ASCII_Commands['STX']))
            
            timeoutcounter +=1
            if timeoutcounter == 20:
                print "#############TOO MANY TIMEOUT FAILURES MSSUNIT BREAKING OUT######################"
                return
            #self.flush() 
            time.sleep(0.01) # writes non stop receiving DLE's until the end!!! (25 bytes?)
        if self.silent == False:
            print 'received:',hex(ord(self.read(1)))
        else:
            hex(ord(self.read(1)))
        self.serial_write(ptr1) # gives NAK error (are there any other symbols in the string after creation?)
        #self.serial_write(ptr) # no NAK, only ACK, but no other information
        #self.flush()        
        time.sleep(0.0005)
        a=self.readall()
        self.all_data_read=[ord(e) for e in a]
        
        
            
        if self.silent == False:
            print ' rest:', [hex(ord(e)) for e in a]
        else:
            [hex(ord(e)) for e in a]
        if chr(0x15) in a:
            print 'error, NAK'
            #if error, resend.
            #return self.talk(toSend)
        if chr(0x10) in a:
            #print 'ACK'
            time.sleep(0.0005)
            a=self.readall()
            if self.silent == False:
                print 'ACK, rest:',a
        if chr(0x02) in a:
            #print 'received STX, sending DLE'
            self.write(chr(0x10))
            time.sleep(0.001)
            b=self.readall()
            if chr(0x03) in b:
                #print 'message received, ending with ETX, sending ACK'
                self.write(chr(10))
                if self.silent == False:
                    print 'sent ACK, received:', b
                return b
        #else:
            #print '___nothing'
            
        #self.write(ptr1)        
        #self.drainOutput()

        return a
        
    def talk_back(self):
        pass
    
    #NO LONGER USED, CALCUALTED ELSEWHERE
#    def move_relative(self, x=np.NaN,y=np.NaN,z=np.NaN, first_motor=1): # coordinates are in screen pixels
#        """
#        move the three motors relative to the current position,  x,y,z are screen coordinates. The first motor determines the starting motor as x
#        """
#        messages=[]        
#        coord=[x,y,z]
#        self.current_coord=self.get_motors_coord()
#        x=int(x-self.resolution[0]/2) # from the center of the screen,x
#        y=int(y-self.resolution[1]/2)
#        if self.silent == False:
#            print x,y
#        
#        #self.pixel_4x[2]=self.pixel_4x[0] # the 'z' pixel doesn't exist, setting it equal to x
#        for i in range(0,2):
#            if not np.isnan(coord[i]): # if not NaN then move
#                self.waitUntilReady()
#                "MOVING MOTOR "+str(i)
#                coord[i]=int(coord[i]*self.pixel_4x[i]/self.full_step)
#                coord[i]=self.current_coord[i]+coord[i]
#                a='#'+str(first_motor+i)+'!DF'+str(coord[i]) # absolute move as relative move doesn't work
#                #a='#'+str(first_motor+i)+'!EF'+str(coord[i]) # moves them fast
#                b=self.talk(a)
#                messages.append(b)
#        return messages
        
        
    
def main():

    # Baud must match that of Arduino\lolshield sketch:
    # 300, 1200, 2400, 4800, 9600, 14400, 19200 or 28800: Values greater than
    # this seem to fail.
    BAUD = 19200 # 19200 for the Rig, 9600 for arduino
    # Port the Arduino\lolshield is on:
    PORT = 'COM4' # 'COM4'- Gateway # COM6 - Tanya's PC # COM1 - Rig PC
    MyUnit = MssUnit(port=PORT, baudrate=BAUD,timeout=0.1)
    print MyUnit.isOpen()

    time.sleep(1.5)

    for i in range(0,3): # important! - running this cycle results in a positive response code 0x10 for the 7th device - don't know why
        a='#'+str(i)+'?Z' # only #7?Z works, not #7?P
        MyUnit.talk(a)
        time.sleep(0.1)

    #MyUnit.talk('#3!H+')
    #MyUnit.write('2222222')
    time.sleep(0.5)
    #for i in range(0,1):
    #    MyUnit.talk('#3!F+1000')
    print 'serial_read_all: ',MyUnit.serial_read_all()
    print MyUnit.all_data_read
    MyUnit.talk('#0?P')
    time.sleep(0.5)
    a=MyUnit.readline()
    if a:
        print "something in the port..."
        a_chr=[ord(e) for e in a]
        print a_chr
        print a
    else:
        print "nothing in the port..."
        
    print MyUnit.serial_read_all()
    print MyUnit.all_data_read
    
    #MyUnit.write('55555')
    time.sleep(0.5)
    MyUnit.move_relative(100,100)
    time.sleep(0.5)
    for i in range(0,3): # important! - running this cycle results in a positive response code 0x10 for the 7th device - don't know why
        a='#'+str(i)+'?Z' # only #7?Z works, not #7?P
        MyUnit.talk(a)
        time.sleep(0.1)
    
    
if __name__ == "__main__":
    main()
                        
                
        
        
        
        
        
        