# -*- coding: utf-8 -*-
"""
Created on Wed Jul 23 16:10:13 2014

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


#from serial import Serial
from serial import Win32Serial
import io
#from PyQt4.QtCore import *
#from PyQt4.QtGui import *
import sys
import time
import copy

import crc16my2 as crc

class ScientificaUnit(Win32Serial):
    
    ASCII_Commands={'STX':0x02,'DLE':0x10,'NAK':0x15,'ETX':0x03,'ESC':0x1b,'ACK':0x06, 'CR':0x0D}
    #ERRORS = {0:"UMANIPULATORCTL_NO_ERROR", -1: "UMANIPULATORCTL_OS_ERROR", -2:"UMANIPULATORCTL_NOT_OPEN",-3:"UMANIPULATORCTL_TIMEOUT",-4:"UMANIPULATORCTL_INVALID_ARG",-5:"UMANIPULATORCTL_INVALID_DEV",-6:"UMANIPULATORCTL_INVALID_RESP",-7:"UMANIPULATORCTL_INVALID_CRC"}
    #STATUS = {-1:"UMANIPULATORCTL_STATUS_READ_ERROR",0x01:"UMANIPULATORCTL_STATUS_X_MOVING",0x02:"UMANIPULATORCTL_STATUS_Y_MOVING",0x04:"UMANIPULATORCTL_STATUS_Z_MOVING",0x10:"UMANIPULATORCTL_STATUS_X_BUSY",0x20:"UMANIPULATORCTL_STATUS_Y_BUSY",0x40:"UMANIPULATORCTL_STATUS_Z_BUSY",0x80:"UMANIPULATORCTL_STATUS_JAMMED"}
    #MODE = {-1:"UMANIPULATORCTL_MODE_READ_ERROR",0:"UMANIPULATORCTL_MODE_UNKNOWN",1:"UMANIPULATORCTL_MODE_1",2:"UMANIPULATORCTL_MODE_2",3:"UMANIPULATORCTL_MODE_3",4:"UMANIPULATORCTL_MODE_4",5:"UMANIPULATORCTL_MODE_5",6:"UMANIPULATORCTL_MODE_PEN",7:"UMANIPULATORCTL_MODE_SNAIL"}
    #MAX_MANIPULATORS = 15
    #DEF_REFRESH_TIME = 2500
    #MAX_POSITION = 20400
    
    full_step=4.9705
    umPerSciManipulatorUnit = .1 #One step for the manipulator equals .1 um
    
    #These can be between 1000 and 50000, based on the (see protocol pdf).  These are arbitrary units
    #and can be changed for how fast the manipulator will go when being controlled by the keyboard.
    fastManualSpeed = 10000
    slowManualSpeed = 1000

    def __init__(self, port, baudrate, unitID, **kwargs):
        """ 
        Initialize the Serial superclass, and setup some default values
        """

        super(ScientificaUnit,self).__init__(port=port,baudrate=baudrate,**kwargs)
        #self.device={'IsPresent':1,'position':0,'pitch':0}
                
        self.silent = False
        
        self.parent = None
        
        self.numdevices = 1
        self.device = 1
        #self.stepLengthUM = None
        
        self.unitID = unitID
        self.unitType = "SCI"
        
        self._reconfigurePort()
        #self.getStepLength()
        
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
        
        #This stuff is important because it specifies the protocol for serial communication with the
        #device, without it it won't be able to communicate
        self.setRTS(False)
        self.setDTR(False)
        self.setParity('N')
        self.setStopbits(1)
        
        
 #   def getStepLength(self):
 #       message = ''.join(self.talk("141f0000")[5:9])
 #       print message
 #       #Step length is returned as a multiple of 10 nanometers.  So if 6 is returned
 #       #by the device, that means that the step length is 60 nanometers, or .06 um
 #       stepnm = int(message,16)/100.0
 #       self.stepLengthUM = stepnm

        
    def setParent(self,parentin):
        self.parent = parentin
    #Not that this function is ever going to be used aside from testing,
    #but it should only be given integers as parameters, as the position values
    #for the device are integers.
    def move_to(self, manip, x=None, y=None, z=None):
        
        #for i in range (0,3):
        message = []
        message.append("ABS ")
            #message.append("3") #move to
            #if i == 0:
            #    message.append("16")
            #    hexval = (hex(x))
            #elif i == 1:
            #    message.append("17")
            #    hexval = (hex(y))
            #elif i == 2:
            #    message.append("18")
            #    hexval = (hex(z))
            #
            #hexval = hexval[2:]
            #if len(hexval) < 4:
            #    for i in range (len(hexval),4):
            #        hexval = "0"+hexval
            #message.append(hexval)
        message.append(str(x))
        message.append(" ")
        message.append(str(y))
        message.append(" ")
        message.append(str(z))
        self.talk(''.join(message))
            
        #self.talk("1000000f")
    
    def move_to_um(self, manip, x=None, y=None, z=None):
        
        #print "########ORIGINAL X",x
        x = int(round(x/self.umPerSciManipulatorUnit))
        #print "MOVING TO X = ",x
        y = int(round(y/self.umPerSciManipulatorUnit))
        z = int(round(z/self.umPerSciManipulatorUnit))
        
        self.move_to(manip,x,y,z)
        
    def move_relative_um(self,device,x,y,z):
        
        #print "relval",x
        #x = x/self.umPerSciManipulatorUnit
        #y = y/self.umPerSciManipulatorUnit
        #z = z/self.umPerSciManipulatorUnit
        
        self.get_motors_coord_um()
        self.move_to_um(1,int(self.parent.motorcoordinates[self.unitID][0][0]+x),int(self.parent.motorcoordinates[self.unitID][0][1]+y),int(self.parent.motorcoordinates[self.unitID][0][2]+z))
        
    def waitUntilReady(self,manip = None):
        pass
    
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
        self.flushInput()
        self.flushOutput()
        pass
        
    def talk(self,toSend):
        self.serial_purge()
        #no checksum here, the characters can simply be sent as ASCII strings with spaces
        #between commands and parameters etc (you don't need to use tabs).  A carriage return character
        #must go at the end of each command.  No other special characters are used.
        toSend = toSend+chr(self.ASCII_Commands['CR'])
          
        ordchars = []
        
        for character in toSend:
            ordchars.append(character)
            
        print ordchars
        print hex(ord(ordchars[0]))
        charchars=''.join(ordchars)
         
        print charchars
        
        #for ordchar in ordchars:
        self.serial_write(charchars) 
        #print self.serial_write('\r')  
        
        
        receivedchars = []
        
        lastChar = ''
        counter = 0
        while counter < 100:
            lastChar = self.read()
            if lastChar == '\r':
                break
            counter += 1
            receivedchars.append(lastChar)
            
        print "RECEIVED: ",receivedchars
        wholemessage = ''.join(receivedchars)

                
        return wholemessage
        
        #if received[2] == 3:
    
    def get_motors_coord_um(self, manip=None):
                
        message = self.talk("P")
        print "MESSAGE: ",message
        message = message.split('\t')
        message = map(int,message)
        message = [x*self.umPerSciManipulatorUnit for x in message]        
        
        print "SPLITINTMESSAGE: ",message        
        
        if self.parent != None:
            print "##################MESSAGE#########################"
            self.parent.motorcoordinates[self.unitID][0]=copy.deepcopy(message)
            print self.parent.motorcoordinates
            

    
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
        
#class MainDisplay(QMainWindow):
#    def __init__(self, spexunit):
#        #this has to go at the beginning of every qt widget initialization
#        QMainWindow.__init__(self)
#        
#        self.spexUnit = spexunit        
#        
#        self.mainWidget = QWidget()
#        self.mainLayout = QVBoxLayout()
#        self.button1 = QPushButton("1")
#        self.button1line = QLineEdit("#1!")
#        self.button1.connect(self.button1, SIGNAL("clicked()"), self.pressed1)
#        self.button2 = QPushButton("2")
#        self.button2line = QLineEdit("#1!")
#        self.button2.connect(self.button2, SIGNAL("clicked()"), self.pressed2)
#        self.button3 = QPushButton("3")
#        self.button3line = QLineEdit("#1!")
#        self.button3.connect(self.button3, SIGNAL("clicked()"), self.pressed3)
#        self.button4 = QPushButton("4")
#        self.button4line = QLineEdit("#1!")
#        self.button4.connect(self.button4, SIGNAL("clicked()"), self.pressed4)
#        self.mainLayout.addWidget(self.button1)
#        self.mainLayout.addWidget(self.button1line)
#        self.mainLayout.addWidget(self.button2)
#        self.mainLayout.addWidget(self.button2line)
#        self.mainLayout.addWidget(self.button3)
#        self.mainLayout.addWidget(self.button3line)
#        self.mainLayout.addWidget(self.button4)
#        self.mainLayout.addWidget(self.button4line)
#        self.mainWidget.setLayout(self.mainLayout)
#        self.setCentralWidget(self.mainWidget)
#    def pressed1(self):
#        print self.spexUnit.talk(str(self.button1line.text()))
#    def pressed2(self):
#        print self.spexUnit.MyUnit[0].talk(str(self.button2line.text()))
#    def pressed3(self):
#        print self.spexUnit.MyUnit[0].talk(str(self.button3line.text()))
#    def pressed4(self):
#        print self.spexUnit.MyUnit[0].talk(str(self.button4line.text()))

    

    
    
    #for debugging independently of main prog
#    app = QApplication(sys.argv)
#    mainwindow = MainDisplay(spexu)
#    mainwindow.show()  
#    app.exec_()


#    # Baud must match that of Arduino\lolshield sketch:
#    # 300, 1200, 2400, 4800, 9600, 14400, 19200 or 28800: Values greater than
#    # this seem to fail.
#    BAUD = 19200 # 19200 for the Rig, 9600 for arduino
#    # Port the Arduino\lolshield is on:
#    PORT = 'COM4' # 'COM4'- Gateway # COM6 - Tanya's PC # COM1 - Rig PC
#    MyUnit = MssUnit(port=PORT, baudrate=BAUD,timeout=0.1)
#    print MyUnit.isOpen()
#
#    time.sleep(1.5)
#
#    for i in range(0,3): # important! - running this cycle results in a positive response code 0x10 for the 7th device - don't know why
#        a='#'+str(i)+'?Z' # only #7?Z works, not #7?P
#        MyUnit.talk(a)
#        time.sleep(0.1)
#
#    #MyUnit.talk('#3!H+')
#    #MyUnit.write('2222222')
#    time.sleep(0.5)
#    #for i in range(0,1):
#    #    MyUnit.talk('#3!F+1000')
#    print 'serial_read_all: ',MyUnit.serial_read_all()
#    print MyUnit.all_data_read
#    MyUnit.talk('#0?P')
#    time.sleep(0.5)
#    a=MyUnit.readline()
#    if a:
#        print "something in the port..."
#        a_chr=[ord(e) for e in a]
#        print a_chr
#        print a
#    else:
#        print "nothing in the port..."
#        
#    print MyUnit.serial_read_all()
#    print MyUnit.all_data_read
#    
#    #MyUnit.write('55555')
#    time.sleep(0.5)
#    MyUnit.move_relative(100,100)
#    time.sleep(0.5)
#    for i in range(0,3): # important! - running this cycle results in a positive response code 0x10 for the 7th device - don't know why
#        a='#'+str(i)+'?Z' # only #7?Z works, not #7?P
#        MyUnit.talk(a)
#        time.sleep(0.1)
    
    
if __name__ == "__main__":
    main()
                        
                
        
        
        
        
        
        
