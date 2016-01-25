# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 14:01:28 2011

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

@Author: Brendan Callahan, Alexander A. Chubykin

"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
#import argl as argl
import sys
import cv
import CameraWidget as cw
import autopatcher
import Grid
#import MousePoints  no longer used, StoredCoordinates is used instead
import math
import MSSInterface
import time
import copy
import csv
import numpy
import ManipPatcherControl
import StoredCoordinates
import gc
app = QApplication(sys.argv)


width = 0 #width & height of video
height = 0
cameraDevice = cw.CameraDevice()
grid = Grid.Grid()
#MousePoints = MousePoints.MousePoints()  not used anymore
MSSInterface = MSSInterface.MSSInterface()

myCrosshairCursor = QCursor(QBitmap("mycrosshair.bmp"),QBitmap("mycrosshairmask.bmp"),10,10)

class MainDisplay(QMainWindow):
    def __init__(self, parent=None):
        #this has to go at the beginning of every qt widget initialization
        QMainWindow.__init__(self)
        
        self.garbagecollection = GarbageCollector(self)
        
        self.mousegridmode = True #True = grid mode, False = Mouse Mode    
        
        
        
        #menubar does nothing for now
        
        self.menubar = QMenuBar()
        
        self.fileMenu = QMenu("&File")
        self.menubar.addMenu("&File")
        self.fileMenu.triggered.connect(app.quit)
        self.fileMenu.addSeparator()
        self.quitAction = self.fileMenu.addAction(self.tr("&QUIT"))
        
        self.setMenuBar(self.menubar)
        self.setWindowTitle("Video Display")
        
        (width,height) = cameraDevice.frameSize
        
        #size of main window
        self.setGeometry(3,20,1345,1045)
        
        #this is a QGraphicsView that contains the video output
        #and the grid overlay.
        self.display = VideoDisplay(self)
        self.display.setMaximumSize(width,height)
        self.display.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.display.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.setCentralWidget(self.display)
        
        #Instantiate the control window.  This is passed to at least MSSInterface,
        #so that the coordinate values can be \d when they're requested. 
        self.myarrows = Arrows(self)
        self.myarrows.show()
        
        #The window for the grid that has the row/col parameter inputs and the center point coordinates
        self.gridcontrol = GridControl()
        self.gridcontrol.show()
        grid.setGridControlBox(self.gridcontrol)
        
        #The window that allows you to communicate binary commands to the patcher chip(?)
        self.manippatcher = ManipPatcherControl.ManipPatcherControl(self)
        self.manippatcher.setInterface(MSSInterface,grid)
        self.manippatcher.show()
        
        #These keep track of whether a key is depressed, so that it can be checked when the key is released.
        self.moveUp = False
        self.moveDown = False
        self.moveLeft = False
        self.moveRight = False
        self.moveZUp = False
        self.moveZDown = False
        
        self.MmoveUp = False
        self.MmoveDown = False
        self.MmoveLeft = False
        self.MmoveRight = False
        self.MmoveZUp = False
        self.MmoveZDown = False
       
        #keeps track of what unit and manipulator the keyboard is currently set to control.
        self.currentkeyboardunit = 0
        self.currentkeyboardmanip = 1
        
        #give the manipulator control box to MSSInterface so it can update values in it
        MSSInterface.setArrows(self.myarrows)
        
        #Set the grid's start point to the current coordinates of the microscope.
        #Wait for a start point to be retrieved in order to do this.
        grid.startPoint = copy.deepcopy(MSSInterface.getCoords()[0][0])
        while grid.startPoint[0] == None:
            grid.startPoint = copy.deepcopy(MSSInterface.getCoords()[0][0])
            
        self.storedCoordinates = StoredCoordinates.StoredCoordinates(MSSInterface,self)
        self.storedCoordinates.show()
        
        #Give the stored coordinates dialog/data structure to the patcher command queuing dialog
        #even though the data should be separate from the graphics
        self.manippatcher.setStoredCoordinates(self.storedCoordinates)        
        
        
        self.clicktomove = [] #click to move around, disables grid and mouse points
        for unit in MSSInterface.MyUnit:
            self.clicktomove.append([])
            for device in range (MSSInterface.portdata[unit.unitID][2]):
                self.clicktomove[-1].append(None)
            
        self.calibrationstatus = []
        for unit in MSSInterface.MyUnit:
            self.calibrationstatus.append([])
            for device in range(0,MSSInterface.portdata[unit.unitID][2]):
                self.calibrationstatus[-1].append(0)
                
        self.axialcalibrationstatus = []
        for unit in MSSInterface.MyUnit:
            self.axialcalibrationstatus.append([])
            for device in range(0,MSSInterface.portdata[unit.unitID][2]):
                self.axialcalibrationstatus[-1].append(None)
            
        self.debugwindow = DebugWindow(self)

    def ctmPressed(self,unit,manip):
        
        if self.clicktomove[unit][manip] == True:
            for u in range (0,len(MSSInterface.MyUnit)):
                for m in range (0,MSSInterface.portdata[u][2]):
                    self.clicktomove[u][m] = False
        else:
            for u in range (0,len(MSSInterface.MyUnit)):
                for m in range (0,MSSInterface.portdata[u][2]):
                    self.clicktomove[u][m] = False
            self.clicktomove[unit][manip] = True
    
        for u in range (0,len(MSSInterface.MyUnit)):
            for m in range (0,MSSInterface.portdata[u][2]):
                if self.clicktomove[u][m] == False:
                    if u == 0 and m == 0:
                        self.myarrows.deviceReadout[u][m].clicktomovebutton.setStyleSheet("QWidget { background-color: rgb(220,20,60) }")
                        self.myarrows.deviceReadout[u][m].clicktomovebutton.setText("CTM Off")
                    else:
                        self.myarrows.deviceReadout[u][m].clicktomovebutton.setStyleSheet("QWidget {}")
                        self.myarrows.deviceReadout[u][m].clicktomovebutton.setText("CTM Off")
                else:
                    self.myarrows.deviceReadout[u][m].clicktomovebutton.setStyleSheet("QWidget {background-color: rgb(0,255,127)}")
                    self.myarrows.deviceReadout[u][m].clicktomovebutton.setText("CTM On")
             
        #        if self.parent.parent.clicktomove == True:
#            self.clicktomovebutton.setStyleSheet("QWidget { background-color: rgb(220,20,60) }")
#            self.clicktomovebutton.setText("CTM Off")
#            self.parent.parent.clicktomove = False
#        else:
#            self.clicktomovebutton.setText("CTM On")
#            self.clicktomovebutton.setStyleSheet("QWidget {background-color: rgb(0,255,127)}")
#            self.parent.parent.clicktomove = True
            
    
    #is supposed to close the app.  still doesn't
    def closeEvent(self, event):
        app.exit()
        self.myarrows.destroy()
        self.gridcontrol.destroy()
        self.display.destroy()
        self.destroy()
        
    #Used to watch for keyboard input.  Usually just a simple key press, but for moving around
    #you have to hold keys down, which is kept track of.  Calls the appropriate command or queue 
    #item in MSSInterface
    def keyPressEvent(self, event):
        if type(event) == QKeyEvent:
            if event.isAutoRepeat() == False:
                
                #Allow the user to switch which manipulator is being controlled
                #by the keyboard YHJKLO keys by using the number keys
                if event.key() == Qt.Key_1:
                    #only allow this to happen if the thread queue is empty and the user is not currently
                    #using the arrow keys to move, so that they don't change the selected device such that
                    #the stop signal gets sent to the wrong device
                    if MSSInterface.arrowMoving == False: #if we aren't currently moving
                        print("SELECTING UNIT 0 MANIP 1")
                        #change the graphical content so the proper manipulator is highlighted
                        self.myarrows.deviceReadout[0][1].deviceLabel.setStyleSheet("QWidget {background-color: rgb(0,255,127); font-weight:bold;}")
                        self.myarrows.deviceReadout[1][0].deviceLabel.setStyleSheet("QWidget {font-weight:bold;}")
                        self.myarrows.deviceReadout[1][1].deviceLabel.setStyleSheet("QWidget {font-weight:bold;}")
                        self.currentkeyboardunit = 0
                        self.currentkeyboardmanip = 1
                if event.key() == Qt.Key_2:
                    if MSSInterface.arrowMoving == False:
                        print("SELECTING UNIT 1 MANIP 0")
                        self.myarrows.deviceReadout[0][1].deviceLabel.setStyleSheet("QWidget {font-weight:bold;}")
                        self.myarrows.deviceReadout[1][0].deviceLabel.setStyleSheet("QWidget {background-color: rgb(0,255,127); font-weight:bold;}")
                        self.myarrows.deviceReadout[1][1].deviceLabel.setStyleSheet("QWidget {font-weight:bold;}")
                        self.currentkeyboardunit = 1
                        self.currentkeyboardmanip = 0
                if event.key() == Qt.Key_3:
                    if MSSInterface.arrowMoving == False:
                        print("SELECTING UNIT 1 MANIP 1")
                        self.myarrows.deviceReadout[0][1].deviceLabel.setStyleSheet("QWidget {font-weight:bold;}")
                        self.myarrows.deviceReadout[1][0].deviceLabel.setStyleSheet("QWidget {font-weight:bold;}")
                        self.myarrows.deviceReadout[1][1].deviceLabel.setStyleSheet("QWidget {background-color: rgb(0,255,127); font-weight:bold;}")
                        self.currentkeyboardunit = 1
                        self.currentkeyboardmanip = 1
                
                #for setting the current location as zero
                if event.key() == Qt.Key_Home:
                    MSSInterface.setZero(0,0)
                
                #for setting the current manipulator as zero
                if event.key() == Qt.Key_End:
                    MSSInterface.setZero(self.currentkeyboardunit,self.currentkeyboardmanip)
                
                #for movement control keys
                if event.key() == Qt.Key_W or event.key() == Qt.Key_Up:
                    print ("****************UP PRESSED")
                    self.moveUp = True
                    self.moveDown = False
                    MSSInterface.moveYPlus(0,0)
                if event.key() == Qt.Key_A or event.key() == Qt.Key_Left:
                    print ("****************LEFT PRESSED")
                    self.moveLeft = True
                    self.moveRight = False
                    MSSInterface.moveXPlus(0,0)
                if event.key() == Qt.Key_S or event.key() == Qt.Key_Down:
                    print ("****************DOWN PRESSED")
                    self.moveDown = True
                    self.moveUp = False 
                    MSSInterface.moveYMinus(0,0)
                if event.key() == Qt.Key_D or event.key() == Qt.Key_Right:
                    print ("****************RIGHT PRESSED")
                    self.moveRight = True
                    self.moveLeft = False
                    MSSInterface.moveXMinus(0,0)
                if event.key() == Qt.Key_R:
                    print ("****************ZUP PRESSED")
                    self.moveZUp = True
                    self.moveZDown = False
                    MSSInterface.moveZPlus(0,0)
                if event.key() == Qt.Key_F:
                    print ("****************ZDOWN PRESSED")
                    self.moveZDown = True
                    self.moveZUp = False
                    MSSInterface.moveZMinus(0,0)
                if event.key() == Qt.Key_X:
                    print("****************SPEED FAST")
                    MSSInterface.speedFast()
                if event.key() == Qt.Key_Z:
                    print("****************SPEED SLOW")
                    MSSInterface.speedSlow()
                if event.key() == Qt.Key_P:
                    print("****************ALL STOP")
                    MSSInterface.allStop()
#                if event.key() == Qt.Key_3:
#                    MSSInterface.rememberCoord()
#                if event.key() == Qt.Key_4:
#                    MSSInterface.moveToRememberedCoord()
#                if event.key() == Qt.Key_5:
#                    MSSInterface.MrememberCoord()
#                if event.key() == Qt.Key_6:
#                    MSSInterface.MmoveToRememberedCoord()
                    
                if event.key() == Qt.Key_U:
                    print ("****************MYUP PRESSED")
                    self.MmoveUp = True
                    self.MmoveDown = False
                    MSSInterface.moveYPlus(self.currentkeyboardunit,self.currentkeyboardmanip)
                if event.key() == Qt.Key_J:
                    print ("****************MYDOWN PRESSED")
                    self.MmoveDown = True
                    self.MmoveUp = False
                    MSSInterface.moveYMinus(self.currentkeyboardunit,self.currentkeyboardmanip)
                if event.key() == Qt.Key_H:
                    print ("****************MBACK PRESSED")
                    self.MmoveFwd = False
                    self.MmoveBack = True
                    MSSInterface.moveXPlus(self.currentkeyboardunit,self.currentkeyboardmanip)
                if event.key() == Qt.Key_K:
                    print ("****************MFWD PRESSED")
                    self.MmoveFwd = True
                    self.MmoveBack = False
                    MSSInterface.moveXMinus(self.currentkeyboardunit,self.currentkeyboardmanip)
                if event.key() == Qt.Key_L:
                    print ("****************MZUP PRESSED")
                    self.MmoveZUp = True
                    self.MmoveZDown = False
                    MSSInterface.moveZPlus(self.currentkeyboardunit,self.currentkeyboardmanip)
                if event.key() == Qt.Key_O:
                    print ("****************MZDOWN PRESSED")
                    self.MmoveZDown = True
                    self.MmoveZUp = False
                    MSSInterface.moveZMinus(self.currentkeyboardunit,self.currentkeyboardmanip)
#        if self.moveUp:
#            MSSInterface.moveUp()
#        if self.moveLeft:
#            MSSInterface.moveLeft()
#        if self.moveDown:
#            MSSInterface.moveDown()
#        if self.moveRight:
#            MSSInterface.moveRight()
#        if self.moveZUp:
#            MSSInterface.moveZUp()
#        if self.moveZDown:
#            MSSInterface.moveZDown()
    
    #If a key is released then stop the motor in that dimension and have it update the coordinates
    def keyReleaseEvent(self,event):
        if type(event) == QKeyEvent:
            if event.isAutoRepeat() == False:
                if event.key() == Qt.Key_W or event.key() == Qt.Key_Up:
                    print ("****************UP RELEASED")
                    self.moveUp = False
                    MSSInterface.stopY(0,0)
                    self.waitForMotorsAndUpdate()
                if event.key() == Qt.Key_A or event.key() == Qt.Key_Left:
                    print ("****************LEFT RELEASED")
                    self.moveLeft = False
                    MSSInterface.stopX(0,0)
                    self.waitForMotorsAndUpdate()
                if event.key() == Qt.Key_S or event.key() == Qt.Key_Down:
                    print ("****************DOWN RELEASED")
                    self.moveDown = False
                    MSSInterface.stopY(0,0)
                    self.waitForMotorsAndUpdate()
                if event.key() == Qt.Key_D or event.key() == Qt.Key_Right:
                    print ("****************RIGHT RELEASED")
                    self.moveRight = False
                    MSSInterface.stopX(0,0)
                    self.waitForMotorsAndUpdate()
                if event.key() == Qt.Key_R:
                    print ("****************ZUP RELEASED")
                    self.moveZUp = False
                    MSSInterface.stopZ(0,0)
                    self.waitForMotorsAndUpdate()
                if event.key() == Qt.Key_F:
                    print ("****************ZDOWN RELEASED")
                    self.moveZDown = False
                    MSSInterface.stopZ(0,0)
                    self.waitForMotorsAndUpdate()
                    
                if event.key() == Qt.Key_U:
                    print ("****************MYUP RELEASED")
                    self.MmoveUp = False
                    MSSInterface.stopY(self.currentkeyboardunit,self.currentkeyboardmanip)
                    self.waitForMotorsAndUpdate()
                if event.key() == Qt.Key_J:
                    print ("****************MYDOWN RELEASED")
                    self.MmoveLeft = False
                    MSSInterface.stopY(self.currentkeyboardunit,self.currentkeyboardmanip)
                    self.waitForMotorsAndUpdate()
                if event.key() == Qt.Key_H:
                    print ("****************MBACK RELEASED")
                    self.MmoveBack = False
                    MSSInterface.stopX(self.currentkeyboardunit,self.currentkeyboardmanip)
                    self.waitForMotorsAndUpdate()
                if event.key() == Qt.Key_K:
                    print ("****************MFWD RELEASED")
                    self.MmoveFwd = False
                    MSSInterface.stopX(self.currentkeyboardunit,self.currentkeyboardmanip)
                    self.waitForMotorsAndUpdate()
                if event.key() == Qt.Key_L:
                    print ("****************MZUP RELEASED")
                    self.MmoveZUp = False
                    MSSInterface.stopZ(self.currentkeyboardunit,self.currentkeyboardmanip)
                    self.waitForMotorsAndUpdate()
                if event.key() == Qt.Key_O:
                    print ("****************MZDOWN RELEASED")
                    self.MmoveZDown = False
                    MSSInterface.stopZ(self.currentkeyboardunit,self.currentkeyboardmanip)
                    self.waitForMotorsAndUpdate()
                if event.key() == Qt.Key_F12:
                    self.debugwindow.show()

                
    def waitForMotorsAndUpdate(self):
        pass #MSSInterface.askCoords()
        


class DebugWindow(QDialog):
    def __init__(self, parent=None):
        super(DebugWindow, self).__init__(parent)
        self.parent = parent
        
        self.mainLayout = QVBoxLayout()
        self.button1 = QPushButton("1")
        self.button1line = QLineEdit("#1!")
        self.button1.connect(self.button1, SIGNAL("clicked()"), self.pressed1)
        self.button2 = QPushButton("2")
        self.button2line = QLineEdit("#1!")
        self.button2.connect(self.button2, SIGNAL("clicked()"), self.pressed2)
        self.button3 = QPushButton("3")
        self.button3line = QLineEdit("#1!")
        self.button3.connect(self.button3, SIGNAL("clicked()"), self.pressed3)
        self.button4 = QPushButton("4")
        self.button4line = QLineEdit("#1!")
        self.button4.connect(self.button4, SIGNAL("clicked()"), self.pressed4)
        self.button5 = QPushButton("5")
        self.button5line = QLineEdit("#1!")
        self.button5.connect(self.button5, SIGNAL("clicked()"), self.pressed5)
        self.button6 = QPushButton("Set ppum x")
        self.button6line = QLineEdit("#1!")
        self.button6.connect(self.button6, SIGNAL("clicked()"), self.pressed6)
        self.button7 = QPushButton("Set ppum y")
        self.button7line = QLineEdit("#1!")
        self.button7.connect(self.button7, SIGNAL("clicked()"), self.pressed7)
        self.button8 = QPushButton("Zero All U0")
        self.button8line = QLineEdit("#1!")
        self.button8.connect(self.button8, SIGNAL("clicked()"), self.pressed8)
        self.mainLayout.addWidget(self.button1)
        self.mainLayout.addWidget(self.button1line)
        self.mainLayout.addWidget(self.button2)
        self.mainLayout.addWidget(self.button2line)
        self.mainLayout.addWidget(self.button3)
        self.mainLayout.addWidget(self.button3line)
        self.mainLayout.addWidget(self.button4)
        self.mainLayout.addWidget(self.button4line)
        self.mainLayout.addWidget(self.button5)
        self.mainLayout.addWidget(self.button5line)
        self.mainLayout.addWidget(self.button6)
        self.mainLayout.addWidget(self.button6line)
        self.mainLayout.addWidget(self.button7)
        self.mainLayout.addWidget(self.button7line)
        self.mainLayout.addWidget(self.button8)
        self.mainLayout.addWidget(self.button8line)
        self.setLayout(self.mainLayout)
    def pressed1(self):
        print MSSInterface.MyUnit[0].talk(str(self.button1line.text()))
    def pressed2(self):
        print MSSInterface.MyUnit[0].talk(str(self.button2line.text()))
    def pressed3(self):
        print MSSInterface.MyUnit[0].talk(str(self.button3line.text()))
    def pressed4(self):
        print MSSInterface.MyUnit[0].talk(str(self.button4line.text()))
    def pressed5(self):
        print MSSInterface.MyUnit[0].talk(str(self.button5line.text()))
    def pressed6(self):
        grid.pixelsperum[0] = float(self.button6line.text())
        print grid.pixelsperum
    def pressed7(self):
        grid.pixelsperum[1] = float(self.button7line.text())
        print grid.pixelsperum
    def pressed8(self):
        MSSInterface.MyUnit[0].talk("#1!@S")
        MSSInterface.MyUnit[0].talk("#2!@S")
        MSSInterface.MyUnit[0].talk("#3!@S")
        MSSInterface.MyUnit[0].talk("#4!@S")
        MSSInterface.MyUnit[0].talk("#5!@S")
        MSSInterface.MyUnit[0].talk("#6!@S")
        
    def keyPressEvent(self,event):
        self.parent.keyPressEvent(event)

    def keyReleaseEvent(self,event):
        self.parent.keyReleaseEvent(event)

#contains the video output as its qgraphicsscene, and uses DrawForeground 
#to redraw the grid, which is called whenever possible as far as I can tell.
#it also keeps track of what's being clicked on, and handles various mouse situations.
class VideoDisplay(QGraphicsView):
    def __init__(self, parent=None):
        QGraphicsView.__init__(self)
        
        self.parent = parent
        self.setFocusPolicy(Qt.NoFocus)
        self.myscene = cw.CameraScene(cameraDevice,self)
        self.setScene(self.myscene)
        
        self.setMouseTracking(True)
        #keeps track if the mouse is over a specific
        #item in the graphical field
        self.overRotator = False
        self.overScaler = 4 #4 means no scaler is under the mouse; otherwise it is the index of the associated scaler.
        self.overCenter = False
        self.overDragArea = False 
        
        #whether the mouse is dragging an item
        self.draggingScaler = False 
        self.draggingRotator = False
        self.draggingCenter = False
        self.draggingGrid = False
        
        #keeps track of where the mouse was last for active dragging
        self.lastMouseLocation = None
        
        self.moveLeft = False
        self.moveRight = False
        self.moveUp = False
        self.moveDown = False
        self.moveZUp= False
        self.moveZDown = False
        
        #mouse mode variables
        self.mmMousePressed = False
        self.mmMouseMovedWhilePressed = False
        
        self.lastcoords = MSSInterface.getCoords(0,0)
        
    
    #checks whether we're over a manipulable item, and also if something is being dragged it
    #tells the grid to perform the appropriate calculations
    def mouseMoveEvent(self, ev):     
        #print "MOUSE AT",ev.x(),ev.y()        
        
        clicktomoveon = False
        clicktomoveunit = None
        clicktomovemanip = None
        
        for u in range (0,len(MSSInterface.MyUnit)):
            for m in range (0,MSSInterface.portdata[u][2]):
                if self.parent.clicktomove[u][m] == True:
                    clicktomoveon = True
                    clicktomoveunit = u
                    clicktomovemanip = m
                    
        for u in range (0,len(MSSInterface.MyUnit)):
            for m in range (0,MSSInterface.portdata[u][2]):
                if (self.parent.calibrationstatus[u][m] != 0 and self.parent.calibrationstatus[u][m] != 4) or self.parent.axialcalibrationstatus[u][m] == True:
                    self.clicktomoveon = False
                    if self.mmMousePressed == True: #mm = mouse mode
                        if self.lastMouseLocation.x() != ev.pos().x() or self.lastMouseLocation.y() != ev.pos().y():
                            self.mmMouseMovedWhilePressed = True
                        else:
                            self.mmMouseMovedWhilePressed = False
                    self.lastMouseLocation = ev.pos()
                    self.setCursor(myCrosshairCursor)#Qt.CrossCursor)
                    return
        #if we're in click to move mode, bypass all the grid situation checking
        if clicktomoveon == False:
            self.setCursor(Qt.ArrowCursor)
            #if we're in grid mode (which we should be if CTM is off)
            if self.parent.mousegridmode:
                
                #reset these values so they can be rechecked
                self.overRotator = False 
                self.overCenter = False 
                if self.draggingScaler == False: 
                    self.overScaler = 4 #set the scaler value to the default no scaler value
                
                (currentcenterx,currentcentery) = grid.getCenter() #figure out how close we are the center
                (realcenterx,realcentery) = grid.getRealCenter() #also figure out where the pivot is
                
                #A number of checks are performed here, mainly to tell whether the mouse is hovering over
                #any grid components.  The first thing that is checked is whether the mouse is over the area
                #for dragging the entire grid, in which case the hand cursor is used.                               
                
                #if we're not currently dragging anything
                if self.draggingRotator == False and self.draggingCenter == False and self.draggingGrid == False and self.draggingScaler == False:
                    #this needs to go here so the hand cursor will remain constant            
#                    if self.overDragArea == False:
#                        self.setCursor(Qt.CrossCursor)
#                        self.setCursor(Qt.ArrowCursor)
                    #this changes it back to false, even if true, so it can be re checked on the next mouse motion
                    self.overDragArea = False
                    #this gets us the coordinates of the corners of the grid
                    cornerlist = grid.getCorners()
                    #while this does the same for the scaling handles (so we can see if the mouse pointer is nearby)
                    scalerlist = grid.getScalingHandles()
                    
                    #Check if the user is within 5 pixels of any of the corner rotator handles
                    for corner in cornerlist:  
                        #if we're within 5 pixels distance
                        if math.sqrt((ev.posF().x()-int(corner[0]))** 2+ (ev.posF().y()-int(corner[1]))**2) < 5:
                            #change the cursor
                            self.setCursor(Qt.PointingHandCursor)
                            self.overRotator = True
                            #print "overRotator" #currently in for deubugging
                    
                    #Do the same for the scaling handles
                    counter = 0
                    for scaler in scalerlist:
                        if math.sqrt((ev.posF().x()-int(scaler[0]))** 2+ (ev.posF().y()-int(scaler[1]))**2) < 5:
                            #change the cursor
                            self.setCursor(Qt.PointingHandCursor)
                            self.overScaler = counter #Since there are 4 scalers, 0-3 corresponds to which one we're over.  4 corresponds to no scaler.
                            #print "over scaler ", counter #currently in for deubugging
                        counter += 1
                            
                    #do the same for the center point
                    (cpoint1, cpoint2) = grid.getCenter()
                    distancefromcenter = math.sqrt((ev.posF().x()-int(cpoint1))** 2+ (ev.posF().y()-int(cpoint2))**2) 
                    
                    if distancefromcenter < 5:
                            self.setCursor(Qt.PointingHandCursor)
                            self.overCenter = True
                            #print "overCenter"
                            
                    #create a 15 pixel dead region around the center point AND the scaling points so the user can click
                    #on the center when it's hovering over the grid & so the scalers dont interfere with the drag area
                    elif distancefromcenter >15:
                        if math.sqrt((ev.posF().x()-int(realcenterx))**2 + (ev.posF().y()-int(realcentery))**2) < (grid.getSmallestDimension()-20)/2:
                            self.setCursor(Qt.OpenHandCursor)        
                            self.overDragArea = True
                            #print "overDragArea"
                            
                
                #if we're already dragging something, tell the grid to call the appropriate functions to update itself.
                #the graphics will update from this on their next refresh.            
                elif self.draggingRotator == True:
                    #find the theta difference with regard to the user's center point for this and the previous mouse positions.
                    theta1 = math.atan2(ev.posF().y()-currentcentery, ev.posF().x()-currentcenterx)
                    theta2 = math.atan2(self.lastMouseLocation.y()-currentcentery,self.lastMouseLocation.x()-currentcenterx)
                    grid.rotateGrid(theta2-theta1)
                    
                #change the center with the mouse
                elif self.draggingCenter == True:
                    grid.center = (ev.posF().x(), ev.posF().y())
                
                #perform the scaling function if we're dragging a scaling handle
                elif self.draggingScaler == True:
                    grid.scaleGrid(self.overScaler,self.lastMouseLocation,ev.posF())
                
                #translate the grid the distance between the current and previous positions.
                elif self.draggingGrid == True:
                    grid.translateGrid(ev.posF().x()-self.lastMouseLocation.x(), ev.posF().y()-self.lastMouseLocation.y())
                    
            ##########################MOUSE POINTS MODE####################################
            else:
                if self.mmMousePressed == True: #mm = mouse mode
                    self.mmMouseMovedWhilePressed = True
        
        else:
            self.setCursor(myCrosshairCursor)#Qt.CrossCursor)
            
        #store this mouse location for the next time this is run.
        self.lastMouseLocation = ev.pos()
                
    #If the mouse is pressed.  Since we already know from the above function whether we're above
    #a handle/region/etc, this just changes the status to the appropriate thing or calls the
    #appropriate function in each scenario.
    def mousePressEvent(self, ev): 
        clicktomoveon = False
        clicktomoveunit = None
        clicktomovemanip = None
        
        for u in range (0,len(MSSInterface.MyUnit)):
            for m in range (0,MSSInterface.portdata[u][2]):
                if self.parent.clicktomove[u][m] == True:
                    clicktomoveon = True
                    clicktomoveunit = u
                    clicktomovemanip = m
                    
        for u in range (0,len(MSSInterface.MyUnit)):
            for m in range (0,MSSInterface.portdata[u][2]):
                if (self.parent.calibrationstatus[u][m] != 0 and self.parent.calibrationstatus[u][m] != 4) or self.parent.axialcalibrationstatus[u][m] == True:
                    self.mmMousePressed = True
                    self.mmMouseMovedWhilePressed = False
                    return
                    
        if clicktomoveon == False:
            if self.parent.mousegridmode:
                if ev.button() == Qt.LeftButton:
                    self.lastMouseLocation = ev.pos()
                    
                    #if we clicked over a rotator, we're now dragging it
                    if self.overRotator:
                        self.draggingRotator = True
                    if self.overCenter:
                        self.draggingCenter = True
                    if self.overDragArea:
                        self.draggingGrid = True
                        self.setCursor(Qt.ClosedHandCursor)
                    if self.overScaler < 4:
                        self.draggingScaler = True
                    #These make sure that the center takes precedence over the scalers and rotators
                    if self.draggingRotator and self.draggingCenter:
                        self.draggingRotator = False
                    if self.draggingScaler == True and self.draggingCenter:
                        self.draggingScaler = False
                        
            ##########MOUSE MODE######################
            else:
                print("MOUSE PRESSED**************************")
                self.mmMousePressed = True
            
            
    #When the mouse is released, toggle or untoggle whatever statuses regarding the mouse position.
    def mouseReleaseEvent(self,ev):
        
        clicktomoveon = False
        clicktomoveunit = None
        clicktomovemanip = None
        
        calibrationval = False
        for u in range (0,len(MSSInterface.MyUnit)):
            for m in range (0,MSSInterface.portdata[u][2]):
                
                if self.parent.axialcalibrationstatus[u][m] == True:              
                    if self.mmMouseMovedWhilePressed == False:
                        if MSSInterface.areThreadsActive():
                            return
                        clickedpoint = grid.getDeltaToScreenCenterMouseToUM(ev)
                        devreadout = self.parent.myarrows.deviceReadout[u][m]
                        currentcoords = copy.deepcopy(MSSInterface.getCoords(0,0))
                        
                        devreadout.axialVector = [clickedpoint[0],clickedpoint[1],currentcoords[2]-devreadout.axialStartPoint[2]]
                        devreadout.axialMag = math.sqrt(math.pow(devreadout.axialVector[0],2)+math.pow(devreadout.axialVector[1],2)+math.pow(devreadout.axialVector[2],2))
                        self.parent.axialcalibrationstatus[u][m] = None   
                        print devreadout.axialVector
                        print devreadout.axialMag
                        devreadout.axialUnitVector = [devreadout.axialVector[0]/devreadout.axialMag,devreadout.axialVector[1]/devreadout.axialMag,devreadout.axialVector[2]/devreadout.axialMag]
                        print devreadout.axialUnitVector
                        self.parent.myarrows.deviceReadout[u][m].calibrateAxialButton.setText("Clear Axial Calibration")
                        
                elif self.parent.calibrationstatus[u][m] != 0 and self.parent.calibrationstatus[u][m] != 4:                                
                    print "MOUSE MOVED WHILE PRESSED: ",self.mmMouseMovedWhilePressed                    
                    if self.mmMouseMovedWhilePressed == False:           
                        if MSSInterface.areThreadsActive():
                            return
                        calibrationval = self.parent.calibrationstatus[u][m]
                        clickpointcoords = grid.getDeltaToScreenCenterMouseToUM(ev)
                        currentcoords = copy.deepcopy(MSSInterface.getCoords(0,0))
                        clickpointcoords[0] += currentcoords[0]
                        clickpointcoords[1] += currentcoords[1]
                        clickpointcoords.append(currentcoords[2])
                        
                        devreadout= self.parent.myarrows.deviceReadout[u][m]
                        print "CALIBRATIONVAL",calibrationval
                        
                        if calibrationval == 1:
                            
                            print "syncpointm",devreadout.syncPointM
                            print "syncpointstage",devreadout.syncPointStage                            
                            
                            print "calx1stage",devreadout.calX1Stage
                            print "calx1m",devreadout.calX1M                            
                            
                            devreadout.calX2Stage = copy.deepcopy(clickpointcoords)
                            print "calX2Stage",devreadout.calX2Stage
                            devreadout.calY1Stage = copy.deepcopy(clickpointcoords)
                            print "calY1Stage",devreadout.calY1Stage
                            devreadout.calX2M = copy.deepcopy(MSSInterface.getCoords(u,m))
                            print "calX2M",devreadout.calX2M
                            devreadout.calY1M = copy.deepcopy(MSSInterface.getCoords(u,m))
                            print "calY1M",devreadout.calY1M
                            
                                                        
                            
                            #magnitude = math.sqrt((devreadout.calX2Stage[0]-devreadout.calX1Stage[0])**2+(devreadout.calX2Stage[1]-devreadout.calX1Stage[1])**2+(devreadout.calX2Stage[2]-devreadout.calX1Stage[2])**2)                            
                            magnitude = devreadout.StageUMperXMcoord*550.0*(4.0/grid.currentmagnification)
                            
                            print "xmagnitude",magnitude
                            #devreadout.StageUMperXMcoord = (magnitude/(devreadout.calX2M[0]-devreadout.calX1M[0]))                            
                            print "stageumperxmcoord",devreadout.StageUMperXMcoord             
                            
                            zVal = magnitude**2-(devreadout.calX2Stage[0]-devreadout.calX1Stage[0])**2-(devreadout.calX2Stage[1]-devreadout.calX1Stage[1])**2
                            if zVal < 0:
                                zVal = 0
                            
                            devreadout.Xhat = [(devreadout.calX2Stage[0]-devreadout.calX1Stage[0])/magnitude,(devreadout.calX2Stage[1]-devreadout.calX1Stage[1])/magnitude,(math.sqrt(zVal))/magnitude]                            
                            
                            print "Xhat",devreadout.Xhat
                            self.parent.calibrationstatus[u][m] += 1
                            MSSInterface.waitForReady(u,m)
                            MSSInterface.moveToRel(u,m,0.0,self.parent.myarrows.axisdirections[u][m][1]*550.0*(4.0/grid.currentmagnification),0.0)
                            MSSInterface.waitForReady(u,m)
                            MSSInterface.askCoords(u,m)
                            
                        if calibrationval == 2:
                            print "CVAL = 2"
                            devreadout.calY2M = copy.deepcopy(MSSInterface.getCoords(u,m))
                            print "calY2M",devreadout.calY2M
                            devreadout.calZ1M = copy.deepcopy(MSSInterface.getCoords(u,m))
                            print "calZ1M",devreadout.calZ1M
                            devreadout.calY2Stage = copy.deepcopy(clickpointcoords)
                            print "calY2Stage",devreadout.calY2Stage
                            devreadout.calZ1Stage = copy.deepcopy(clickpointcoords)
                            print "calZ1Stage",devreadout.calZ1Stage
                            
                            magnitude = devreadout.StageUMperYMcoord*550.0*(4.0/grid.currentmagnification)
                            print "ymagnitude",magnitude                     
                            #devreadout.StageUMperYMcoord = magnitude/(devreadout.calY2M[1]-devreadout.calY1M[1])
                            print "stageumperym",devreadout.StageUMperYMcoord
                            
                            zVal = magnitude**2-(devreadout.calY2Stage[0]-devreadout.calY1Stage[0])**2-(devreadout.calY2Stage[1]-devreadout.calY1Stage[1])**2
                            #if the user has clicked a point that has a magnitude greater than the expected magnitude,
                            #set the value to 0 so we aren't taking the square root of a negative number for *hat[2]                            
                            if zVal < 0:
                                zVal = 0
                            
                            devreadout.Yhat = [(devreadout.calY2Stage[0]-devreadout.calY1Stage[0])/magnitude,(devreadout.calY2Stage[1]-devreadout.calY1Stage[1])/magnitude,math.sqrt(zVal)/magnitude]   #[(devreadout.calY2Stage[0]-devreadout.calY1Stage[0])/magnitude,(devreadout.calY2Stage[1]-devreadout.calY1Stage[1])/magnitude,math.sqrt(zVal)/magnitude]                            
                            print "Yhat",devreadout.Yhat                            
                            
                            self.parent.calibrationstatus[u][m] += 1
                            MSSInterface.waitForReady(u,m)
                            MSSInterface.moveToRel(u,m,0.0,0.0,self.parent.myarrows.axisdirections[u][m][2]*550.0*(4/grid.currentmagnification))
                            MSSInterface.waitForReady(u,m)
                            MSSInterface.askCoords(u,m)
                        if calibrationval == 3:
                            print "CVAL = 3"
                            devreadout.calZ2Stage = copy.deepcopy(clickpointcoords)
                            print "calZ2Stage",devreadout.calZ2Stage
                            devreadout.calZ2M = copy.deepcopy(MSSInterface.getCoords(u,m))
                            print "calZ2M", devreadout.calZ2M
                            magnitude = magnitude = devreadout.StageUMperZMcoord*550.0*(4.0/grid.currentmagnification)
                            print "zmagnitude",magnitude                            
                            #devreadout.StageUMperZMcoord = magnitude/(devreadout.calZ2M[2]-devreadout.calZ1M[2])
                            print "stageumperzm",devreadout.StageUMperZMcoord  
                            
                            zVal = magnitude**2-(devreadout.calZ2Stage[0]-devreadout.calZ1Stage[0])**2-(devreadout.calZ2Stage[1]-devreadout.calZ1Stage[1])**2
                            if zVal < 0:
                                zVal = 0
                            
                            devreadout.Zhat = [(devreadout.calZ2Stage[0]-devreadout.calZ1Stage[0])/magnitude,(devreadout.calZ2Stage[1]-devreadout.calZ1Stage[1])/magnitude,(math.sqrt(zVal)/magnitude)*(devreadout.parent.axisdirections[devreadout.unitnum][devreadout.manipnum][2])]
                            print "Zhat",devreadout.Zhat
                            self.parent.calibrationstatus[u][m] += 1
                            devreadout.getMPositionStage()
                            devreadout.calibrateX1.setText("Clear Calibration")
                            devreadout.calibrateX1.setStyleSheet("QWidget {background-color: rgb(139,137,137); color: rgb(255,0,0); font-weight: bold}")
                
                    self.mmMouseMovedWhilePressed = False
                    return
            
        
        for u in range (0,len(MSSInterface.MyUnit)):
            for m in range (0,MSSInterface.portdata[u][2]):
                if self.parent.clicktomove[u][m] == True:
                    clicktomoveon = True
                    clicktomoveunit = u
                    clicktomovemanip = m
        
        if clicktomoveon == False:
            if self.parent.mousegridmode:
                #stop dragging anything
                self.draggingRotator = False
                self.draggingCenter = False
                self.draggingGrid = False
                self.draggingScaler = False
            else:
                #if the user has clicked the mouse without dragging it, add a point at that location.
                if self.mmMouseMovedWhilePressed == False:
                    #MousePoints.addPoint(ev.pos())
                    currentpoint = MSSInterface.getCoords(0,0)
                    mousedelta = grid.getDeltaToScreenCenterMouseToUM(ev)
                    currentpoint[0] += mousedelta[0]
                    currentpoint[1] += mousedelta[1]
                    self.parent.storedCoordinates.addItem(0,0,currentpoint[0],currentpoint[1],currentpoint[2])
                self.mmMousePressed = False
                self.mmMouseMovedWhilePressed = False

        #If we're in click to move mode, then perform the necessary calculations/commands to move
        #the manipulator.  Sends these commands directly to MSSInterface, which instanitates them as
        #queue items.        
        else:
            #microscope click to move on
            if clicktomoveunit == 0 and clicktomovemanip == 0:
                diff = grid.getDeltaToScreenCenterPixToUM(ev.x(),ev.y())
                MSSInterface.waitForReady(0,0)
                MSSInterface.moveToRel(0,0,-round(diff[0],4),-round(diff[1],4),0.0000)
                MSSInterface.waitForReady(0,0)
                MSSInterface.askCoords(0,0)
                print "************THREAD STARTED, CONTINUING EXECUTION******************"
                #MSSInterface.waitForReady()
            #manip click to move on
            else:
                diff = grid.getDeltaToScreenCenterPixToUM(ev.x(),ev.y())
                clickedcoordstage = MSSInterface.getCoords(0,0)
                clickedcoordstage = [clickedcoordstage[0]-diff[0],clickedcoordstage[1]-diff[1],clickedcoordstage[2]]
                devreadout = self.parent.myarrows.deviceReadout[clicktomoveunit][clicktomovemanip]     
                if devreadout.Xhat != [None,None,None] and devreadout.Yhat != [None,None,None] and devreadout.Zhat != [None,None,None] and devreadout.Xhat != ["","",""]:
                    mcoords = devreadout.getMfromStageCoord(clickedcoordstage[0],clickedcoordstage[1],clickedcoordstage[2])
                    MSSInterface.waitForReady(clicktomoveunit,clicktomovemanip)
                    MSSInterface.moveTo(clicktomoveunit,clicktomovemanip,mcoords[0],mcoords[1],mcoords[2])
                    MSSInterface.waitForReady(clicktomoveunit,clicktomovemanip)
                    MSSInterface.askCoords(clicktomoveunit,clicktomovemanip,)
                    
                else:
                    print "UNIT",clicktomoveunit,"MANIP",clicktomovemanip,"NOT CALIBRATED"

        
            
    def drawForeground(self,painter,rect):
    
        #On the first run of this function, keep querying MSSInterface until it gets a valid set
        #of coordinates from the control box for the microscope's coordinates.
        while self.lastcoords == [None,None,None]:
            self.lastcoords=MSSInterface.getCoords(0,0)
        
        #Get the current coordinates stored in MSSInterface (without querying the box).
        #If this value has changed, update the grid offset accordingly by translating it
        #(in micrometers) by the corresponding amount.
        newcoords = MSSInterface.getCoords(0,0)
        if newcoords != [None,None,None]:
            
            grid.currentPoint = copy.deepcopy(newcoords)
            if (self.lastcoords != newcoords):
                deltax = newcoords[0]-self.lastcoords[0]
                deltay = newcoords[1]-self.lastcoords[1]
                deltaz = newcoords[2]-self.lastcoords[2]
                grid.translateUm(deltax,deltay)
                self.lastcoords = copy.deepcopy(newcoords)
        
        #color = green
        painter.setPen(QColor(0, 255, 0))
        
        #Write the SPEED and FPS readouts in the top left
        painter.drawText(QPoint(6,15),"SPEED "+MSSInterface.Speed)    
        painter.drawText(QPoint(6,30),"FPS "+str(self.myscene.FPSout))   
        

        unitmanip = [False,False]
        currentstate = False
        
        for unit in range (0,len(self.parent.calibrationstatus)):
            for manip in range(0,MSSInterface.portdata[unit][2]):
                if self.parent.calibrationstatus[unit][manip] != 0 and self.parent.calibrationstatus[unit][manip] != 4:
                    unitmanip = [unit,manip]
                    currentstate = self.parent.calibrationstatus[unit][manip]
                    break
                if currentstate != False:
                    break
                
                if self.parent.axialcalibrationstatus[unit][manip] == True:
                    currentstate = 99

        
        

        if currentstate != False:
            if currentstate == 1:
                painter.drawText(QPoint(500,45),"CURRENT POINT FOR CALIBRATION IS X2 and Y1")
                if MSSInterface.areThreadsActive() == False:
                    painter.drawText(QPoint(500,60),"ADJUST Z DIMENSION AND CLICK LOCATION OF UNIT "+str(unitmanip[0])+" DEVICE "+str(unitmanip[1]))
                else:
                    painter.setPen(QColor(255, 0, 0))
                    painter.drawText(QPoint(500,60),"WAITING FOR QUEUE TO CLEAR...")
                    painter.setPen(QColor(0, 255, 0))
            if currentstate == 2:
                painter.drawText(QPoint(500,45),"CURRENT POINT FOR CALIBRATION IS Y2 and Z1")
                if MSSInterface.areThreadsActive() == False:
                    painter.drawText(QPoint(500,60),"ADJUST Z DIMENSION AND CLICK LOCATION OF UNIT "+str(unitmanip[0])+" DEVICE "+str(unitmanip[1]))
                else:
                    painter.setPen(QColor(255, 0, 0))
                    painter.drawText(QPoint(500,60),"WAITING FOR QUEUE TO CLEAR...")
                    painter.setPen(QColor(0, 255, 0))
            if currentstate == 3:
                painter.drawText(QPoint(500,45),"CURRENT POINT FOR CALIBRATION IS Z2")
                if MSSInterface.areThreadsActive() == False:
                    painter.drawText(QPoint(500,60),"ADJUST Z DIMENSION AND CLICK LOCATION OF UNIT "+str(unitmanip[0])+" DEVICE "+str(unitmanip[1]))
                else:
                    painter.setPen(QColor(255, 0, 0))
                    painter.drawText(QPoint(500,60),"WAITING FOR QUEUE TO CLEAR...")
                    painter.setPen(QColor(0, 255, 0))
                    
            if currentstate == 99:
                painter.drawText(QPoint(500,45),"CALIBRATING AXIAL DIRECTION OF PIPETTE.")
                if MSSInterface.areThreadsActive() == False:
                    painter.drawText(QPoint(500,60),"CLICK POINT AT PIPETTE CENTER WHERE PIPETTE IS MOST IN FOCUS")
                else:
                    painter.setPen(QColor(255, 0, 0))
                    painter.drawText(QPoint(500,60),"WAITING FOR QUEUE TO CLEAR...")
                    painter.setPen(QColor(0, 255, 0))
        
        #center point on the screen
        centerpoint = [1344.0,1024.0]
        painter.drawLine(centerpoint[0]/2,centerpoint[1]/2+3,centerpoint[0]/2,centerpoint[1]/2-3)
        painter.drawLine(centerpoint[0]/2+3,centerpoint[1]/2,centerpoint[0]/2-3,centerpoint[1]/2)
        
        #if we're not in mouse click to add points mode or whatever, and thus the grid is visible
        if self.parent.mousegridmode:
            #draw the grid on the screen as a series of lines from their lists
            painter.setPen(QColor(0, 255, 0))
            for x in grid.rowlines:
                #x1,y1,x2,y2
                painter.drawLine(int(x[0]),int(x[1]),int(x[2]),int(x[3]))
            for x in grid.collines:
                painter.drawLine(int(x[0]),int(x[1]),int(x[2]),int(x[3]))
            
            #draw the center points as a series of points
            painter.setPen(QColor(255, 0, 0))
            for x in grid.centerpoints:
                painter.drawPoint(int(x[0]),int(x[1]))
            
            #draw the user controllable center point as a circle with a point in it
            painter.setPen(QColor(0, 0, 255))
            painter.drawEllipse(grid.getCenter()[0]-3,grid.getCenter()[1]-3,6,6)
            painter.drawPoint(grid.getCenter()[0],grid.getCenter()[1])
            #draw the rotation handles on the corners, shifting the circles up and left one pixel so theyre roughly centered.
            #note that any slighly off centerness generally corresponds to the translation from a higher data density than
            #the pixels, and does not correspond to any inaccuracy in the master data set.
            try:
                rotationhandles = grid.getCorners()
                for x in rotationhandles:
                    painter.drawEllipse(x[0]-2,x[1]-2,4,4)
                #draw the scaling handles on the midpoints of the outer edges of the grid
                painter.setPen(QColor(255,255,0))
                scalinghandles = grid.getScalingHandles()
                for x in scalinghandles:
                    painter.drawEllipse(x[0]-2,x[1]-2,4,4)
            except:
                print "NO VALID VALUES, WAIT FOR NEXT REFRESH, AKA FOR THE PROGRAM TO CRASH AND BURN"
                
        #if we are in mouse point mode then draw these points on the screen.  this is not
        #really refined and barely works, not how its supposed to
        else:
            storedpoints = self.parent.storedCoordinates.getAllPoints()
            #for i in range (0,len(storedpoints)):
            counter = 0
            for point in storedpoints[0]:
            
                painter.setPen(QColor(255,255,0))
                
                #These can be used once a manipulator is calibrated to show its saved points.
                #For now it just shows points from the screen
    #                    elif i == 1:
    #                        painter.setPen(QColor(255,165,0))
    #                    elif i == 2:
    #                        painter.setPen(QColor(0,250,154))
    #                    elif i == 3:
    #                        painter.setPen(QColor(255,20,147))
                    
                x = grid.getPointUMtoPix(point[0],point[1])
                painter.drawEllipse(x[0]-2,x[1]-2,4,4)
                #painter.setPen(QColor(0, 255, 0))
                painter.drawPoint(x[0],x[1])
                painter.drawText(QPoint(x[0]+6, x[1]+4), str(counter))
                counter += 1
        
#This is the grid control panel, which you can use to change the grid parameters.  It also
#contains a table with the current center points of the grid lines.
class GridControl(QDialog):
    def __init__(self, parent=None):
        super(GridControl, self).__init__(parent)
        self.setGeometry(1352,20,200,600)
        self.mainvboxlayout = QVBoxLayout()
        
        self.rowcoldivallcontainer = QWidget()
        self.rowcoldivalllayout = QHBoxLayout()
        self.rowcoldivcontainer = QWidget()
        self.rowcoldivlayout = QVBoxLayout()
        
        self.rownumcontainer = QWidget()
        self.rowcolhboxlayout = QHBoxLayout()
        self.rowslabel = QLabel("Rows")
        self.rowsfield = QLineEdit()
        self.rowsfield.setText(str(grid.rows))
        self.colslabel = QLabel("Cols")
        self.colsfield = QLineEdit()
        self.colsfield.setText(str(grid.cols))
        self.rowsfield.setMinimumWidth(75)
        self.colsfield.setMinimumWidth(75)
        self.rowsfield.setMaximumWidth(75)
        self.colsfield.setMaximumWidth(75)
        
        self.rowcolhboxlayout.addWidget(self.rowslabel)
        self.rowcolhboxlayout.addWidget(self.rowsfield)
        self.rowcolhboxlayout.addWidget(self.colslabel)
        self.rowcolhboxlayout.addWidget(self.colsfield)
        self.rownumcontainer.setLayout(self.rowcolhboxlayout)
        
        self.divcontainer = QWidget()
        self.divlayout = QHBoxLayout()
        self.vdivlabel = QLabel("Vdiv")
        self.vdivfield = QLineEdit()
        self.vdivfield.setText(str(grid.vdiv/grid.pixelsperum[0]))
        self.hdivlabel = QLabel("Hdiv")
        self.hdivfield = QLineEdit()
        self.hdivfield.setText(str(grid.hdiv/grid.pixelsperum[1]))
        self.vdivfield.setMaximumWidth(75)
        self.hdivfield.setMaximumWidth(75)
        self.vdivfield.setMinimumWidth(75)
        self.hdivfield.setMinimumWidth(75)
        
        self.divlayout.addWidget(self.vdivlabel)
        self.divlayout.addWidget(self.vdivfield)
        self.divlayout.addWidget(self.hdivlabel)
        self.divlayout.addWidget(self.hdivfield)
        self.divcontainer.setLayout(self.divlayout)
        
        self.rowcoldivlayout.addWidget(self.rownumcontainer)
        self.rowcoldivlayout.addWidget(self.divcontainer)
        self.rowcoldivcontainer.setLayout(self.rowcoldivlayout)
                
        self.buttoncontainer = QWidget()
        self.buttoncontainerlayout = QVBoxLayout()
        self.centerbuttoncontainer = QWidget()
        self.centerbuttoncontainerlayout = QHBoxLayout()
        
        self.updatebutton = QPushButton("Update")
        self.updatebutton.setMaximumHeight(35)
        self.updatebutton.setMaximumWidth(100)
        self.updatebutton.connect(self.updatebutton, SIGNAL("clicked()"), self.updateGrid)
        
        self.traverseButton = QPushButton("Traverse Points")
        self.traverseButton.connect(self.traverseButton, SIGNAL("clicked()"), self.traversePoints)
        self.traverseButton.setMaximumHeight(20)
        self.traverseButton.setMaximumWidth(100)
        
        self.centercenter = QPushButton("o>+")
        self.centercenter.setMinimumHeight(20)
        self.centercenter.connect(self.centercenter, SIGNAL("clicked()"), self.usercentertocenter)
        self.centergriduc = QPushButton("+>o")
        self.centergriduc.setMinimumHeight(20)
        self.centergriduc.connect(self.centergriduc, SIGNAL("clicked()"), self.gridtousercenter)
        
        self.centerbuttoncontainerlayout.addWidget(self.centercenter)
        self.centerbuttoncontainerlayout.addWidget(self.centergriduc)
        self.centerbuttoncontainerlayout.addWidget(self.traverseButton)
        self.centerbuttoncontainer.setLayout(self.centerbuttoncontainerlayout)
        
        self.buttoncontainerlayout.addWidget(self.updatebutton)
        self.buttoncontainerlayout.addWidget(self.centerbuttoncontainer)
        self.buttoncontainerlayout.addWidget(self.traverseButton)
        self.buttoncontainer.setLayout(self.buttoncontainerlayout)
        self.buttoncontainer.setMaximumWidth(100)
        
        self.rowcoldivalllayout.addWidget(self.rowcoldivcontainer)
        self.rowcoldivalllayout.addWidget(self.buttoncontainer)
        self.rowcoldivallcontainer.setLayout(self.rowcoldivalllayout)
        self.rowcoldivallcontainer.setMaximumHeight(120)
        
        self.pointstable = QTableView()
        self.pointstablemodel = GridTableModel(grid.getCenterPointsUM(),['x','y'])
        self.pointstable.setModel(self.pointstablemodel)
        
        
        self.mainvboxlayout.addWidget(self.rowcoldivallcontainer)
        self.mainvboxlayout.addWidget(self.pointstable)
        
        self.setLayout(self.mainvboxlayout)
        
    #triggered by the traverse points button; passes the center points to mssinterface
    #and has it move the microscope to these points, one by one
    def traversePoints(self):
        traversearray = grid.getCenterPointsUM()
        MSSInterface.waitForReady(0,0)
        MSSInterface.traversePoints(traversearray)

            
    #Passes new grid parameters to the grid class
    def updateGrid(self):
        grid.updateDimensions(int(self.rowsfield.text()),int(self.colsfield.text()),float(self.vdivfield.text())*grid.pixelsperum[0],float(self.hdivfield.text())*grid.pixelsperum[1])
    
    #Updates the text fields in the grid control box with the current stored values.
    def updateText(self):
        self.rowsfield.setText(QString(str(grid.rows)))
        self.colsfield.setText(QString(str(grid.cols)))
        self.vdivfield.setText(QString(str(grid.vdiv/grid.pixelsperum[0])[0:10]))
        self.hdivfield.setText(QString(str(grid.hdiv/grid.pixelsperum[1])[0:10]))
        
    def usercentertocenter(self):
        grid.reCenterUserCenter()
    def gridtousercenter(self):
        grid.centerGridonUserCenter()
        
    #called pretty frequently, this just updates the table.  I did not write the table code,
    #I just directed it to use the proper variables for columns etc
    def updatetable(self):
        self.pointstablemodel = GridTableModel(grid.getCenterPointsUM(),['x','y'])
        self.pointstable.setModel(self.pointstablemodel)

#I didn't write any of this, it's just a basic bare bones table class.  Pretty straightforward, I guess
class GridTableModel(QAbstractTableModel): 
    def __init__(self, datain, headerdata, parent=None, *args): 
        """ datain: a list of lists
            headerdata: a list of strings
        """
        QAbstractTableModel.__init__(self, parent, *args) 
        self.arraydata = datain
        self.headerdata = headerdata
 
    def rowCount(self, parent): 
        return len(self.arraydata) 
 
    def columnCount(self, parent): 
        return 2 
 
    def data(self, index, role): 
        if not index.isValid(): 
            return QVariant() 
        elif role != Qt.DisplayRole: 
            return QVariant() 
        return QVariant(grid.getCenterPointsUM()[index.row()][index.column()]) 

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[col])
        return QVariant()

    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))        
        if order == Qt.DescendingOrder:
            self.arraydata.reverse()
        self.emit(SIGNAL("layoutChanged()"))
        

#This class corresponds to the individual readouts for the manipulator coordinates and calibration.
#It is added to the widget Arrows based on how many manipulators etc are present.
class DeviceReadout(QWidget):
    def __init__(self,unitnum,manip,isStage,parent=None):
        super(DeviceReadout,self).__init__(parent)
        
        #main layout
        self.deviceReadoutLayout = QVBoxLayout()
        self.deviceReadoutLayout.setSpacing(1)
        
        self.unitnum = unitnum
        self.manipnum = manip
        self.isStage = isStage
        self.parent = parent        
        
        if isStage == True:        
            self.calSurfaceZ = None #this will be able to be given a value for the slide surface.
                                    #currently unused.
        else:
            #Initialization of calibration variables
            self.calX1Stage = [None,None,None]
            self.calX1M = [None,None,None]
            self.calY1Stage = [None,None,None]
            self.calY1M = [None,None,None]
            self.calZ1Stage = [None,None,None]
            self.calZ1M = [None,None,None]        
                
            self.calX2Stage = [None,None,None]
            self.calY2Stage = [None,None,None]
            self.calZ2Stage = [None,None,None]
            
            self.calX2M = [None,None,None]
            self.calY2M = [None,None,None]
            self.calZ2M = [None,None,None]
            
            self.syncPointM = [None,None,None]
            self.syncPointStage = [None,None,None]
            
            self.Xhat = [None,None,None]
            self.Yhat = [None,None,None]
            self.Zhat = [None,None,None]
            
            self.StageUMperXMcoord = 1.1
            self.StageUMperYMcoord = 1.1
            self.StageUMperZMcoord = 1.6
            
            self.MStageCoordinates = [None,None,None]
            self.Mmotorcoords = [None,None,None]
            
            self.axialStartPoint = [None,None,None]
            self.axialVector = [None,None,None]
            self.axialMag = None
            self.axialUnitVector = [None,None,None]
              
        #Microscope components
        if isStage == True:
            self.deviceLabel = QLabel("Microscope:")
            self.xAxis = QLabel("X:")    
            #The pixels-per-um readout, only relevant to the stage
            self.magnificationControlContainer = QWidget()
            self.magnificationControlLayout = QVBoxLayout()
            self.magnificationControlLayout.setSpacing(1)
            self.magnificationControlLayout.setMargin(3)
            self.magnificationLabel = QLabel("Magnification:")            
            self.magnificationLabel.setStyleSheet("QWidget {font-weight:bold}")
            
            #magnification radio buttons
            self.magRadioContainer = QWidget()
            self.magRadioLayout = QHBoxLayout()
            self.magRadioLayout.setSpacing(1)
            self.magRadioButton4x = QRadioButton("4x")
            self.magRadioButton4x.connect(self.magRadioButton4x,  SIGNAL("clicked()"), self.radioButtonChange) 
            self.magRadioButton4x.setChecked(True) 
            self.magRadioButton10x = QRadioButton("10x")
            self.magRadioButton4x.connect(self.magRadioButton10x,  SIGNAL("clicked()"), self.radioButtonChange)
            self.magRadioButton40x = QRadioButton("40x")
            self.magRadioButton4x.connect(self.magRadioButton40x,  SIGNAL("clicked()"), self.radioButtonChange)
            self.magRadioLayout.addWidget(self.magRadioButton4x)
            self.magRadioLayout.addWidget(self.magRadioButton10x)
            self.magRadioLayout.addWidget(self.magRadioButton40x)
            self.magRadioContainer.setLayout(self.magRadioLayout)
            
            #used to show pixels per micrometer for the microscope.
            #Can be set in grid.py
            self.ppumContainer = QWidget()
            self.ppumLayout = QHBoxLayout()
            self.ppumLayout.setSpacing(1)
            self.ppumLayout.setMargin(3)
            self.ppum = QLabel("ppum:")
            self.ppumField = QLineEdit()
            self.ppumField.setText(QString(str(grid.pixelsperum)))
            self.ppumCurrentMag = QLabel("(4X)")
            self.ppumCurrentMag.setStyleSheet("QWidget {font-weight:bold}")
            self.ppumLayout.addWidget(self.ppum)
            self.ppumLayout.addWidget(self.ppumField)
            self.ppumLayout.addWidget(self.ppumCurrentMag)
            self.ppumContainer.setLayout(self.ppumLayout)
            
            self.magnificationControlLayout.addWidget(self.magnificationLabel)
            self.magnificationControlLayout.addWidget(self.magRadioContainer)
            self.magnificationControlLayout.addWidget(self.ppumContainer)
            
            self.magnificationControlContainer.setLayout(self.magnificationControlLayout)
         
        #Manipulator components
        else:
            self.deviceLabel = QLabel("Manipulator "+str(manip)+":")
            self.xAxis = QLabel("F/B:")
            #The labels and fields for manipulator positions in stage coordinates;
            #only used by manipulators
            self.xFieldStageContainer = QWidget()
            self.xFieldStageLayout = QHBoxLayout()
            self.xFieldStageLayout.setMargin(3)
            self.xFieldStageContainer.setLayout(self.xFieldStageLayout)
            self.xFieldStageLabel = QLabel("X (Stage):")
            self.xFieldStage = QLineEdit()
            self.xFieldStage.setMinimumWidth(75)
            self.xFieldStageLayout.addWidget(self.xFieldStageLabel)
            self.xFieldStageLayout.addWidget(self.xFieldStage)     
            
            self.yFieldStageContainer = QWidget()
            self.yFieldStageLayout = QHBoxLayout()
            self.yFieldStageLayout.setMargin(3)
            self.yFieldStageContainer.setLayout(self.yFieldStageLayout)
            self.yFieldStageLabel = QLabel("Y (Stage):")
            self.yFieldStage = QLineEdit()
            self.yFieldStage.setMinimumWidth(75)
            self.yFieldStageLayout.addWidget(self.yFieldStageLabel)
            self.yFieldStageLayout.addWidget(self.yFieldStage)
            
            self.zFieldStageContainer = QWidget()
            self.zFieldStageLayout = QHBoxLayout()
            self.zFieldStageLayout.setMargin(3)
            self.zFieldStageContainer.setLayout(self.zFieldStageLayout)
            self.zFieldStageLabel = QLabel("Z (Stage):")
            self.zFieldStage = QLineEdit()
            self.zFieldStage.setMinimumWidth(75)
            self.zFieldStageLayout.addWidget(self.zFieldStageLabel)
            self.zFieldStageLayout.addWidget(self.zFieldStage)

        
                    
            
        self.deviceLabel.setStyleSheet("QWidget {font-weight:bold}")
        self.deviceLabel.setMargin(5)

        self.rememberCoordButton = QPushButton("+")       
        self.rememberCoordButton.setStyleSheet("QWidget {font-weight:bold; background-color: rgb(0,255,127); color:rgb(248,248,255);}")
        self.rememberCoordButton.setMaximumWidth(25)  
        self.rememberCoordButton.connect(self.rememberCoordButton, SIGNAL("clicked()"), self.rememberCoords)
        
        self.deviceLabelContainer = QWidget()
        self.deviceLabelContainerLayout = QHBoxLayout()
        self.deviceLabelContainer.setLayout(self.deviceLabelContainerLayout)
        self.deviceLabelContainerLayout.addWidget(self.deviceLabel)
        self.deviceLabelContainerLayout.addWidget(self.rememberCoordButton)
        
        self.xField = QLineEdit()
        self.xField.setMinimumWidth(75)
 
        self.yAxis = QLabel("Y:")
        self.yField = QLineEdit()
        self.yField.setMinimumWidth(75)
        
        self.zAxis = QLabel("Z:")
        self.zField = QLineEdit()
        self.zField.setMinimumWidth(75)
        
        self.xAxisContainer = QWidget()
        self.yAxisContainer = QWidget()
        self.zAxisContainer = QWidget()
        
        #All the little plus/minus buttons to tell if an axis is at its max/min
        self.xAxisLayout = QHBoxLayout()
        self.xAxisLayout.setMargin(3)
        self.xEndPosContainer = QWidget()
        self.xEndPosLayout = QVBoxLayout()
        self.xEndPosLayout.setSpacing(1)
        self.xEndPosLayout.setMargin(1)
        self.xEndPosPlus = QPushButton("+")
        self.xEndPosPlus.setStyleSheet("QWidget {background-color: rgb(0,255,127)}")
        self.xEndPosMinus = QPushButton("-")
        self.xEndPosMinus.setStyleSheet("QWidget {background-color: rgb(0,255,127)}")
        self.xEndPosPlus.setMaximumHeight(10)
        self.xEndPosPlus.setMaximumWidth(10)
        
        self.xEndPosMinus.setMaximumHeight(10)
        self.xEndPosMinus.setMaximumWidth(10)
        
        self.xEndPosLayout.addWidget(self.xEndPosPlus)
        self.xEndPosLayout.addWidget(self.xEndPosMinus)
        self.xEndPosContainer.setLayout(self.xEndPosLayout)
        
        self.yAxisLayout = QHBoxLayout()
        self.yAxisLayout.setMargin(3)
        self.yEndPosContainer = QWidget()
        self.yEndPosLayout = QVBoxLayout()
        self.yEndPosLayout.setSpacing(1)
        self.yEndPosLayout.setMargin(1)
        self.yEndPosPlus = QPushButton("+")
        self.yEndPosPlus.setStyleSheet("QWidget {background-color: rgb(0,255,127)}")
        self.yEndPosMinus = QPushButton("-")
        self.yEndPosMinus.setStyleSheet("QWidget {background-color: rgb(0,255,127)}")
        self.yEndPosPlus.setMaximumHeight(10)
        self.yEndPosPlus.setMaximumWidth(10)
        self.yEndPosMinus.setMaximumHeight(10)
        self.yEndPosMinus.setMaximumWidth(10)
        self.yEndPosLayout.addWidget(self.yEndPosPlus)
        self.yEndPosLayout.addWidget(self.yEndPosMinus)
        self.yEndPosContainer.setLayout(self.yEndPosLayout)
        
        self.zAxisLayout = QHBoxLayout()
        self.zAxisLayout.setMargin(3)
        self.zEndPosContainer = QWidget()
        self.zEndPosLayout = QVBoxLayout()
        self.zEndPosLayout.setSpacing(1)
        self.zEndPosLayout.setMargin(1)
        self.zEndPosPlus = QPushButton("+")
        self.zEndPosPlus.setStyleSheet("QWidget {background-color: rgb(0,255,127)}")
        self.zEndPosMinus = QPushButton("-")
        self.zEndPosMinus.setStyleSheet("QWidget {background-color: rgb(0,255,127)}")
        self.zEndPosPlus.setMaximumHeight(10)
        self.zEndPosPlus.setMaximumWidth(10)
        self.zEndPosMinus.setMaximumHeight(10)
        self.zEndPosMinus.setMaximumWidth(10)
        self.zEndPosLayout.addWidget(self.zEndPosPlus)
        self.zEndPosLayout.addWidget(self.zEndPosMinus)
        self.zEndPosContainer.setLayout(self.zEndPosLayout)        
        
        self.xAxisLayout.addWidget(self.xAxis)
        self.xAxisLayout.addWidget(self.xField)
        self.xAxisLayout.addWidget(self.xEndPosContainer)
        self.xAxisContainer.setLayout(self.xAxisLayout)
        
    
        self.yAxisLayout.addWidget(self.yAxis)
        self.yAxisLayout.addWidget(self.yField)
        self.yAxisLayout.addWidget(self.yEndPosContainer)
        self.yAxisContainer.setLayout(self.yAxisLayout)
    
        self.zAxisLayout.addWidget(self.zAxis)
        self.zAxisLayout.addWidget(self.zField)
        self.zAxisLayout.addWidget(self.zEndPosContainer)
        self.zAxisContainer.setLayout(self.zAxisLayout)
        
#        self.MxAxisLayout.setSpacing(1)
#        self.MxAxisLayout.setMargin(5)
#        self.MyAxisLayout.setSpacing(1)
#        self.MyAxisLayout.setMargin(5)
#        self.MzAxisLayout.setSpacing(1)
#        self.MzAxisLayout.setMargin(5)
        
        self.deviceReadoutLayout.setSpacing(1)
        self.deviceReadoutLayout.setMargin(3)
        self.deviceReadoutLayout.addWidget(self.deviceLabelContainer)
        self.deviceReadoutLayout.addWidget(self.xAxisContainer)
        self.deviceReadoutLayout.addWidget(self.yAxisContainer)
        self.deviceReadoutLayout.addWidget(self.zAxisContainer)
        if self.isStage == False:
            self.deviceReadoutLayout.addWidget(self.xFieldStageContainer)
            self.deviceReadoutLayout.addWidget(self.yFieldStageContainer)
            self.deviceReadoutLayout.addWidget(self.zFieldStageContainer)
            
            self.clicktomovecontainer = QWidget()
            self.clicktomovelayout = QVBoxLayout()
            self.clicktomovebutton = QPushButton("CTM Off")
            self.clicktomovebutton.connect(self.clicktomovebutton, SIGNAL("clicked()"), self.ctmPressed)
            #self.clicktomovebutton.setStyleSheet("QWidget {background-color: rgb(220,20,60)}")
            self.clicktomovelayout.addWidget(self.clicktomovebutton)
            self.clicktomovecontainer.setLayout(self.clicktomovelayout)
            
            self.deviceReadoutLayout.addWidget(self.clicktomovecontainer)
            
        else:
            self.deviceReadoutLayout.addWidget(self.magnificationControlContainer)            
            
            self.dialContainer = QWidget()
            self.dialContainerLayout = QHBoxLayout()
            self.dialContainerLayout.setSpacing(1)
            self.dialContainerLayout.setMargin(3)
            self.dialContainer.setLayout(self.dialContainerLayout)
            self.brightnessContainer = QWidget()
            self.brightnessContainerLayout = QVBoxLayout()
            self.brightnessContainerLayout.setSpacing(1)
            self.brightnessContainerLayout.setMargin(0)
            self.brightnessContainer.setLayout(self.brightnessContainerLayout) 
            self.contrastContainer = QWidget()
            self.contrastContainerLayout = QVBoxLayout()
            self.contrastContainerLayout.setSpacing(1)
            self.contrastContainerLayout.setMargin(0)
            self.contrastContainer.setLayout(self.contrastContainerLayout)
            self.dialContainerLayout.addWidget(self.brightnessContainer)
            self.dialContainerLayout.addWidget(self.contrastContainer)
            
            self.brightnessLabel = QLabel("Brightness")
            self.brightnessReadout = QLabel(str(cameraDevice.brightness))
            self.brightnessReadout.setAlignment(Qt.AlignHCenter)
            self.contrastLabel = QLabel("Contrast")
            self.contrastReadout = QLabel(str(cameraDevice.contrast))
            self.contrastReadout.setAlignment(Qt.AlignHCenter)
            self.brightnessDial = QDial()
            self.brightnessDial.setRange(-100,100)
            self.brightnessDial.setValue(0)
            self.brightnessDial.setWrapping(False)
            self.brightnessDial.setNotchesVisible(True)
            self.brightnessDial.connect(self.brightnessDial, SIGNAL("sliderMoved(int)"), self.changeBrightness)
            self.contrastDial = QDial()
            self.contrastDial.setNotchesVisible(True)
            self.contrastDial.setWrapping(False)
            self.contrastDial.setRange(0,1000) # (0,500) value working as of 11/27/12
            self.contrastDial.setValue(100)
            self.contrastDial.connect(self.contrastDial, SIGNAL("sliderMoved(int)"), self.changeContrast)
            
            self.brightnessContainerLayout.addWidget(self.brightnessLabel)
            self.brightnessContainerLayout.addWidget(self.brightnessDial)
            self.brightnessContainerLayout.addWidget(self.brightnessReadout)
            self.contrastContainerLayout.addWidget(self.contrastLabel)
            self.contrastContainerLayout.addWidget(self.contrastDial)
            self.contrastContainerLayout.addWidget(self.contrastReadout)
            
            
#            self.togglecontainer = QWidget()
#            self.togglecontainerlayout = QVBoxLayout()
#            self.togglecontainerlayout.setSpacing(1)
            #self.togglecontainerlayout.setMargin(3)
            self.togglebutton = QPushButton("Grid Mode")
            self.togglebutton.setStyleSheet("QWidget {background-color: rgb(79,148,205)}")
#            self.togglecontainerlayout.addWidget(self.togglebutton)
#            self.togglecontainer.setLayout(self.togglecontainerlayout)
            self.togglebutton.connect(self.togglebutton, SIGNAL("clicked()"), self.togglePressed)
            
#            self.clicktomovecontainer = QWidget()
#            self.clicktomovelayout = QVBoxLayout()
#            self.clicktomovelayout.setSpacing(1)
            #self.clicktomovelayout.setMargin(3)
            self.clicktomovebutton = QPushButton("CTM Off")
            self.clicktomovebutton.setStyleSheet("QWidget {background-color: rgb(220,20,60)}")
#            self.clicktomovelayout.addWidget(self.clicktomovebutton)
#            self.clicktomovecontainer.setLayout(self.clicktomovelayout)
            
#            self.autopatchercontainer = QWidget()
#            self.autopatchercontainerlayout = QVBoxLayout()
#            self.autopatchercontainerlayout.setSpacing(1)
            #self.autopatchercontainerlayout.setMargin(3)
            self.autopatcherbutton = QPushButton("Auto Patcher")
            self.autopatcherbutton.setStyleSheet("QWidget {background-color: rgb(51,102,255)}")
#            self.autopatchercontainerlayout.addWidget(self.autopatcherbutton)
#            self.autopatchercontainer.setLayout(self.autopatchercontainerlayout)
            self.autopatcherbutton.connect(self.autopatcherbutton, SIGNAL("clicked()"), self.autopatcherPressed)

#            self.setzerocontainer = QWidget()
#            self.setzerolayout = QVBoxLayout()
#            self.setzerolayout.setSpacing(1)
#            self.setzerocontainer.setLayout(self.setzerolayout)
            self.setzerobutton = QPushButton("Set Origin")
            self.setzerobutton.connect(self.setzerobutton, SIGNAL("clicked()"), self.setzeroPressed)
            self.setzerobutton.setStyleSheet("QWidget {background-color: rgb(248,248,255); color:rgb(0,0,0);}")         
#            self.setzerolayout.addWidget(self.setzerobutton)
        
            self.clicktomovebutton.connect(self.clicktomovebutton, SIGNAL("clicked()"), self.ctmPressed)
            
            self.deviceReadoutLayout.addWidget(self.dialContainer)
            self.deviceReadoutLayout.addWidget(self.clicktomovebutton)
            self.deviceReadoutLayout.addWidget(self.togglebutton)            
            self.deviceReadoutLayout.addWidget(self.autopatcherbutton)
            self.deviceReadoutLayout.addWidget(self.setzerobutton)
            
            
        
        
        self.calibrationContainer = QWidget()
        self.calibrationContainerLayout = QVBoxLayout()        
        
        if self.isStage == True:
            self.calibrateSurface = QPushButton("Calibrate surface")
            self.calibrateSurface.connect(self.calibrateSurface, SIGNAL("clicked()"), self.calibrateSurfaceClicked)
            self.calibrationContainerLayout.addWidget(self.calibrateSurface)
            
        #Calibration buttons
        else:
#            self.calibrationButtonBox = QWidget()
#            self.calibrationButtonBoxLayout = QGridLayout()
            self.calibrationLabel = QLabel("Calibration:")
            self.calibrationLabel.setStyleSheet("QWidget {font-weight:bold}")
    
            self.calibrateX1 = QPushButton("Start Calibration")
            self.calibrateX1.setStyleSheet("QWidget {background-color: rgb(139,137,137); color: rgb(255,255,255); font-weight: bold}")
            self.calibrateX1.connect(self.calibrateX1, SIGNAL("clicked()"), self.calibrateFirstX)

            self.calibrateMoveScreenM = QPushButton("Move SC to M")
            self.calibrateMoveScreenM.connect(self.calibrateMoveScreenM, SIGNAL("clicked()"), self.calibrateMoveScreenToM)
            self.calibrateMoveMScreen = QPushButton("Move M to SC")
            self.calibrateMoveMScreen.connect(self.calibrateMoveMScreen, SIGNAL("clicked()"), self.calibrateMoveMToScreen)
            self.calibrateAxialButton = QPushButton("Axial Calibration")
            self.calibrateAxialButton.connect(self.calibrateAxialButton, SIGNAL("clicked()"), self.calibrateAxial)
            self.calibrateAxialButton.setStyleSheet("QWidget {background-color: rgb(139,137,137); color: rgb(255,255,255); font-weight: bold}")
            self.calibrationContainerLayout.addWidget(self.calibrationLabel)
            #self.calibrationContainerLayout.addWidget(self.calibrationButtonBox)
            self.calibrationContainerLayout.addWidget(self.calibrateX1)
            self.calibrationContainerLayout.addWidget(self.calibrateMoveScreenM)
            self.calibrationContainerLayout.addWidget(self.calibrateMoveMScreen)
            self.calibrationContainerLayout.addWidget(self.calibrateAxialButton)            
            self.calibrationContainer.setLayout(self.calibrationContainerLayout)
            self.calibrationContainerLayout.setMargin(0)
        
        self.deviceReadoutLayout.addWidget(self.calibrationContainer)
        self.setLayout(self.deviceReadoutLayout)
        
    def changeBrightness(self):
        dialval = self.brightnessDial.value()
        cameraDevice.brightness = dialval
        self.brightnessReadout.setText(str(dialval))
        
    def changeContrast(self):
        dialval = self.contrastDial.value()
        cameraDevice.contrast = dialval/100.0
        self.contrastReadout.setText(str(dialval/100.0))
        
    def setzeroPressed(self):
        unit0startcoords = MSSInterface.getCoords(0,0)
        grid.translateUm(unit0startcoords[0],unit0startcoords[1])
        
        for i in range (1,len(self.parent.deviceReadout[0])):
            self.parent.deviceReadout[0][i].shiftSynchronizationPointToNewZero(unit0startcoords)
        MSSInterface.setZero(0,0)
        MSSInterface.askCoords(0,0)
        
    def shiftSynchronizationPointToNewZero(self,shiftin):
        if self.syncPointStage[0] != None:
            self.syncPointStage = [self.syncPointStage[0]-shiftin[0],self.syncPointStage[1]-shiftin[1],self.syncPointStage[2]-shiftin[2]]
    
    def calibrateAxial(self):
        if self.calibrateAxialButton.text() == "Cancel Axial Calibration":
            self.parent.parent.axialcalibrationstatus[self.unitnum][self.manipnum] = None
            self.calibrateAxialButton.setText("Axial Calibration")
            self.calibrateAxialButton.setStyleSheet("QWidget {background-color: rgb(139,137,137); color: rgb(255,255,255); font-weight: bold}")
            self.parent.purgeQueue(0)
            
        elif self.calibrateAxialButton.text() == "Clear Axial Calibration":
            self.parent.purgeQueue(0)
            self.axialStartPoint = [None,None,None]
            self.axialVector = [None,None,None]
            self.axialUnitVector = [None,None,None]
            self.axialMag = None
            self.calibrateAxialButton.setText("Axial Calibration")         
            self.calibrateAxialButton.setStyleSheet("QWidget {background-color: rgb(139,137,137); color: rgb(255,255,255); font-weight: bold}")

        else:
            self.axialStartPoint = copy.deepcopy(MSSInterface.getCoords(0,0))
            self.axialVector = [None,None,None]
            self.axialMag = None
            self.parent.parent.axialcalibrationstatus[self.unitnum][self.manipnum] = True
            MSSInterface.waitForReady(self.unitnum,self.manipnum)
            MSSInterface.moveToRel(0,0,0.0,0.0,self.parent.axisdirections[0][0][2]*(300.0)*(4/grid.currentmagnification))
            self.calibrateAxialButton.setText("Cancel Axial Calibration")
            self.calibrateAxialButton.setStyleSheet("QWidget {background-color: rgb(139,137,137); color: rgb(255,0,0); font-weight: bold}")
            MSSInterface.waitForReady(0,0)
            MSSInterface.askCoords(0,0) 
        
        
    def rememberCoords(self):
        currentcoords = MSSInterface.getCoords(self.unitnum,self.manipnum)
        self.parent.parent.storedCoordinates.addItem(self.unitnum,self.manipnum,currentcoords[0],currentcoords[1],currentcoords[2])
        
    #Changes magnification by calling a method in grid
    def radioButtonChange(self):
        if self.magRadioButton4x.isChecked() == True:
            grid.setPixelsPerUM(4.0)
            self.ppumCurrentMag.setText("(4X)")
            self.ppumCurrentMag.setStyleSheet("QWidget {font-weight:bold}")
        elif self.magRadioButton10x.isChecked() == True:
            grid.setPixelsPerUM(10.0)
            self.ppumCurrentMag.setText("(10X)")
            self.ppumCurrentMag.setStyleSheet("QWidget {font-weight:bold}")
        elif self.magRadioButton40x.isChecked() == True:
            grid.setPixelsPerUM(40.0)
            self.ppumCurrentMag.setText("(40X)")
            self.ppumCurrentMag.setStyleSheet("QWidget {font-weight:bold}")
        self.ppumField.setText(QString(str(grid.pixelsperum)))
       
    #used to determine the current coordinates of the manipulators in stage coordinates, given
    #the manipulators' positions in manipulator coordinates.
    def getMPositionStage(self):
        if self.Xhat != [None,None,None] and self.Yhat != [None,None,None] and self.Zhat != [None,None,None] and self.Xhat != ["","",""]:
            self.Mmotorcoords = MSSInterface.getCoords(self.unitnum,self.manipnum)
            Mxoffset = (self.Mmotorcoords[0]-self.syncPointM[0])*self.StageUMperXMcoord
            Myoffset = (self.Mmotorcoords[1]-self.syncPointM[1])*self.StageUMperYMcoord
            Mzoffset = (self.Mmotorcoords[2]-self.syncPointM[2])*self.StageUMperZMcoord
            #print "X^: ",self.Xhat,"Y^: ",self.Yhat,"Z^: ",self.Zhat
            #print "X offset: ",Mxoffset,"Y offset: ",Myoffset,"Z offset: ",Mzoffset
            MStagePos = [None,None,None]
            MStagePos[0] = self.syncPointStage[0] + self.Xhat[0]*Mxoffset+self.Yhat[0]*Myoffset+self.Zhat[0]*Mzoffset
            MStagePos[1] = self.syncPointStage[1] + self.Xhat[1]*Mxoffset+self.Yhat[1]*Myoffset+self.Zhat[1]*Mzoffset
            MStagePos[2] = self.syncPointStage[2] + self.Xhat[2]*Mxoffset+self.Yhat[2]*Myoffset+self.Zhat[2]*Mzoffset
            self.xFieldStage.setText(QString(str(MStagePos[0])))
            self.yFieldStage.setText(QString(str(MStagePos[1])))
            self.zFieldStage.setText(QString(str(MStagePos[2])))
            self.MStageCoordinates = copy.deepcopy(MStagePos)
            
            if self.parent.parent.calibrationstatus[self.unitnum][self.manipnum] != 4:
                self.parent.parent.calibrationstatus[self.unitnum][self.manipnum] = 4
                self.calibrateX1.setText("Clear Calibration")
                self.calibrateX1.setStyleSheet("QWidget {background-color: rgb(139,137,137); color: rgb(255,0,0); font-weight: bold}")
            #print self.MStageCoordinates
            
        
    #not currently used
    def calibrateSurfaceClicked(self):
        self.calSurfaceZ = MSSInterface.getCoords()[2]
        print "SURFACE Z SET TO ",self.calSurfaceZ      
        
    #Note - this only takes care of the first point.  There are no functions here to handle the subsequent
    #points because those are handled through interaction with the screen.  See mouseReleaseEvent under
    #the VideoDisplay class for the rest of the code that handles calibration.
    def calibrateFirstX(self):
        if self.parent.parent.calibrationstatus[self.unitnum][self.manipnum] == 0:
            self.syncPointStage = copy.deepcopy(MSSInterface.getCoords(0,0))
            self.syncPointM = copy.deepcopy(MSSInterface.getCoords(self.unitnum,self.manipnum))
            #MSSInterface.askCoords()
            self.calX1Stage = copy.deepcopy(MSSInterface.getCoords(0,0))
            self.calX1M = copy.deepcopy(MSSInterface.getCoords(self.unitnum,self.manipnum))
            print "FIRST X POINT IS ",self.calX1Stage
            
            MSSInterface.waitForReady(self.unitnum,self.manipnum)
            MSSInterface.moveToRel(self.unitnum,self.manipnum,self.parent.axisdirections[self.unitnum][self.manipnum][0]*(550.0)*(4/grid.currentmagnification),0.0,0.0)
            #MSSInterface.waitForReady(self.unitnum,self.manipnum)
            #MSSInterface.moveToRel(0,0,150.0*(4/grid.currentmagnification),0.0,0.0)
            MSSInterface.waitForReady(self.unitnum,self.manipnum)
            #MSSInterface.askCoords(0,0)
            MSSInterface.askCoords(self.unitnum,self.manipnum)
            self.parent.parent.calibrationstatus[self.unitnum][self.manipnum] += 1
            self.calibrateX1.setText("Cancel Calibration")
            self.calibrateX1.setStyleSheet("QWidget {background-color: rgb(139,137,137); color: rgb(255,0,0); font-weight: bold}")
        elif self.parent.parent.calibrationstatus[self.unitnum][self.manipnum] > 0:
            self.clearCalibration()
            
    def clearCalibration(self):
        self.parent.purgeQueue(0)
        self.parent.purgeQueue(self.unitnum)
        self.parent.parent.calibrationstatus[self.unitnum][self.manipnum] = 0
        self.calX1Stage = [None,None,None]
        self.calX1M = [None,None,None]
        self.calY1Stage = [None,None,None]
        self.calY1M = [None,None,None]
        self.calZ1Stage = [None,None,None]
        self.calZ1M = [None,None,None]        
            
        self.calX2Stage = [None,None,None]
        self.calY2Stage = [None,None,None]
        self.calZ2Stage = [None,None,None]
        
        self.calX2M = [None,None,None]
        self.calY2M = [None,None,None]
        self.calZ2M = [None,None,None]
        
        self.syncPointM = [None,None,None]
        self.syncPointStage = [None,None,None]
        
        self.Xhat = [None,None,None]
        self.Yhat = [None,None,None]
        self.Zhat = [None,None,None]
        
        self.MStageCoordinates = [None,None,None]
        self.Mmotorcoords = [None,None,None]
        self.xFieldStage.setText("")
        self.yFieldStage.setText("")
        self.zFieldStage.setText("")
        self.calibrateX1.setStyleSheet("QWidget {background-color: rgb(139,137,137); color: rgb(255,255,255); font-weight: bold}")
        self.calibrateX1.setText("Start Calibration")

    def calibrateMoveScreenToM(self):
        MSSInterface.waitForReady(0)
        MSSInterface.moveTo(0,0,self.MStageCoordinates[0],self.MStageCoordinates[1],self.MStageCoordinates[2])
        MSSInterface.waitForReady(0)
        MSSInterface.askCoords(0,0)
    def calibrateMoveMToScreen(self):
        MSSInterface.askCoords(self.unitnum,self.manipnum)
        time.sleep(1)
        currentStageCoord = copy.deepcopy(MSSInterface.getCoords(0,0))
        diffX = currentStageCoord[0]-self.MStageCoordinates[0]
        diffY = currentStageCoord[1]-self.MStageCoordinates[1]
        diffZ = currentStageCoord[2]-self.MStageCoordinates[2]
        eqns = numpy.array([[self.Xhat[0],self.Yhat[0],self.Zhat[0]],[self.Xhat[1],self.Yhat[1],self.Zhat[1]],[self.Xhat[2],self.Yhat[2],self.Zhat[2]]])
        solns = numpy.array([diffX,diffY,diffZ])
        deltaM = numpy.linalg.solve(eqns,solns)
        MSSInterface.waitForReady(self.unitnum,self.manipnum)
        print "DELTAS: ",deltaM[0],deltaM[1],deltaM[2]
        MSSInterface.moveToRel(self.unitnum,self.manipnum,deltaM[0]/self.StageUMperXMcoord,deltaM[1]/self.StageUMperYMcoord,deltaM[2]/self.StageUMperZMcoord)
        MSSInterface.waitForReady(self.unitnum,self.manipnum)
        MSSInterface.askCoords(self.unitnum,self.manipnum)   
    
    def togglePressed(self):
        if self.parent.parent.mousegridmode == True:
            self.togglebutton.setStyleSheet("QWidget { background-color: rgb(238,238,0) }")
            self.togglebutton.setText("Mouse Mode")
            self.parent.parent.mousegridmode = False
        else:
            self.togglebutton.setText("Grid Mode")
            self.togglebutton.setStyleSheet("QWidget {background-color: rgb(79,148,205)}")
            self.parent.parent.mousegridmode = True
    
    def ctmPressed(self):        
        self.parent.parent.ctmPressed(self.unitnum,self.manipnum)
            
    def autopatcherPressed(self):
        myautopatcher = autopatcher.ApplicationWindow(MSSInterface,self)#.autopatcherwindow)
        myautopatcher.setAttribute(Qt.WA_DeleteOnClose)
        myautopatcher.setWindowTitle("Auto Patcher")
        myautopatcher.show()
        
    def getMfromStageCoord(self,x,y,z=None):
        
        if z == None:
            z = MSSInterface.getCoords(0,0)[2]
        
        if self.Xhat != [None,None,None] and self.Yhat != [None,None,None] and self.Zhat != [None,None,None] and self.Xhat != ["","",""]:
            currentStageCoord = copy.deepcopy(MSSInterface.getCoords(0,0))
            diffX = x-self.syncPointStage[0]
            diffY = y-self.syncPointStage[1]
            diffZ = z-self.syncPointStage[2]
            eqns = numpy.array([[self.Xhat[0],self.Yhat[0],self.Zhat[0]],[self.Xhat[1],self.Yhat[1],self.Zhat[1]],[self.Xhat[2],self.Yhat[2],self.Zhat[2]]])
            solns = numpy.array([diffX,diffY,diffZ])
            deltaM = numpy.linalg.solve(eqns,solns)
            return [self.syncPointM[0]+deltaM[0]/self.StageUMperXMcoord, self.syncPointM[1]+deltaM[1]/self.StageUMperYMcoord,self.syncPointM[2]+deltaM[2]/self.StageUMperZMcoord]
        
    def getStagefromMCoord(self,x,y,z):
        
            self.Mmotorcoords = [x,y,z]
            Mxoffset = (self.Mmotorcoords[0]-self.syncPointM[0])*self.StageUMperXMcoord
            Myoffset = (self.Mmotorcoords[1]-self.syncPointM[1])*self.StageUMperYMcoord
            Mzoffset = (self.Mmotorcoords[2]-self.syncPointM[2])*self.StageUMperZMcoord
            #print "X^: ",self.Xhat,"Y^: ",self.Yhat,"Z^: ",self.Zhat
            #print "X offset: ",Mxoffset,"Y offset: ",Myoffset,"Z offset: ",Mzoffset
            MStagePos = [None,None,None]
            MStagePos[0] = self.syncPointStage[0] + self.Xhat[0]*Mxoffset+self.Yhat[0]*Myoffset+self.Zhat[0]*Mzoffset
            MStagePos[1] = self.syncPointStage[1] + self.Xhat[1]*Mxoffset+self.Yhat[1]*Myoffset+self.Zhat[1]*Mzoffset
            MStagePos[2] = self.syncPointStage[2] + self.Xhat[2]*Mxoffset+self.Yhat[2]*Myoffset+self.Zhat[2]*Mzoffset
            self.MStageCoordinates = copy.deepcopy(MStagePos)
            
            return self.MStageCoordinates

#Creates & contains the device readouts for the various manipulator units.  This is the master
#class for these readouts - other classes can and should modify their values
#through this class, either directly or using the functions that this class contains.
class Arrows(QDialog):
    def __init__(self, parent=None):
        super(Arrows, self).__init__(parent)
        
        self.parent = parent
        #put it next to the main window
        self.setGeometry(1300,20,35,600)
        self.mainvboxlayout = QVBoxLayout()
        
        self.columnContainer = QWidget()
        self.columnContainerLayout = QHBoxLayout()
        self.columnContainer.setLayout(self.columnContainerLayout)
        
        self.deviceReadout = [] #the actual control/readout for the manipulators
        self.readoutHLayout = []
        self.readoutHContainer = []
        self.readoutColumn = [] #the column for two control/readout boxes corresponding to a single MSS unit
        self.readoutLayout = [] #the entire layout for all readout columns
        
        self.readoutHContainerInternalV = []
        self.readoutHContainerInternalVLayout = []
        
        self.threadStatusContainer = [] #has the thread queue length info
        self.threadStatusLayout = []
        self.threadNameLabel = []
        self.threadStatusLabel = []
        
        #used to check if the end position for an axis has changed by storing the previous end position
        self.previousendpos = []

        #Create the graphical elements of the device readouts and associated containers.
        #Could be done at the same time as the following for statement but not a big deal since
        #it's only executed at program launch and this makes it more organized.
        for unit in range(0,len(MSSInterface.MyUnit)):
            if MSSInterface.portdata[unit][1] == "MSS":            
                self.addMSS(unit)
            elif MSSInterface.portdata[unit][1] == "SX":
                self.addSX(unit)
            #vertical line to separate unit readouts
            if unit < len(MSSInterface.MyUnit)-1:
                newwidget = QWidget()
                newwidget.setMaximumWidth(1)
                newwidget.setMinimumWidth(1)
                newwidget.setMinimumHeight(775)
                newwidget.setMaximumHeight(775)
                newwidget.setStyleSheet("QWidget {background-color: rgb(139,137,137);}")
                self.columnContainerLayout.addWidget(newwidget)
            
        
#        for unit in range (0,len(MSSInterface.MyUnit)):
#            self.readoutLayout[unit].addWidget(self.threadStatusContainer[unit])
#            for device in range (0,2):
#                if device == 1:
#                    self.readoutLayout[unit].addStretch()
#                self.readoutLayout[unit].addWidget(self.deviceReadout[unit][device])                
#            self.readoutColumn[unit].setLayout(self.readoutLayout[unit])
#            
            
        
        self.toggle = True
        self.clicktomove = True
        
        self.calibrationContainer = QWidget()
        self.calibrationContainerLayout = QHBoxLayout()
        self.calibrateSave = QPushButton("Save Calibration")
        self.calibrateSave.connect(self.calibrateSave, SIGNAL("clicked()"), self.calibrateSaveToFile)
        self.calibrateLoad = QPushButton("Load Calibration")
        self.calibrateLoad.connect(self.calibrateLoad, SIGNAL("clicked()"), self.calibrateLoadFromFile)
        self.calibrationContainer.setLayout(self.calibrationContainerLayout)
        
        
        self.calibrationContainerLayout.addWidget(self.calibrateSave)
        self.calibrationContainerLayout.addWidget(self.calibrateLoad)
        
        #set unit 0 device 1 (the default selected device for keyboard movement) as 
        #highlighted in green; this will later be taken care of during the process of changing the device         

        ######################################NEEDS TO BE CHANGED OVER#################        
        
        #self.deviceReadout[0][1].deviceLabel.setStyleSheet("QWidget {background-color: rgb(0,255,127); font-weight:bold;}")
        
        self.axisdirections = []
        axisReader = csv.reader(open('C:\\axisdirections.csv'),quoting=csv.QUOTE_NONNUMERIC)
        print self.deviceReadout
        for unit in self.deviceReadout:
            self.axisdirections.append([])
            for manip in unit:              
                self.axisdirections[manip.unitnum].append(axisReader.next())
                
        print self.axisdirections
        
        #THIS IS FOR EXTRA STUFF AT THE BOTTOM
        self.mainvboxlayout.addWidget(self.columnContainer)
        self.mainvboxlayout.addWidget(self.calibrationContainer)
        
        #self.mainvboxlayout.addWidget(self.calibrationContainer)
        
        
        self.setLayout(self.mainvboxlayout)
        
#        self.buttonUp = QPushButton(u'\u25B2')
#        self.buttonDown = QPushButton(u'\u25BC')
#        self.buttonLeft = QPushButton(u'\u25C4')
#        self.buttonRight = QPushButton(u'\u25BA')
#        
#        self.buttonResult = QLabel(" ")
#        self.buttonResult.setAlignment(Qt.AlignCenter);
#        
#        self.buttonUp.connect(self.buttonUp, SIGNAL("clicked()"), self.upPressed)
#        self.buttonRight.connect(self.buttonRight, SIGNAL("clicked()"), self.rightPressed)
#        self.buttonDown.connect(self.buttonDown, SIGNAL("clicked()"), self.downPressed)
#        self.buttonLeft.connect(self.buttonLeft, SIGNAL("clicked()"), self.leftPressed)
#        
#        self.buttonUp.setMaximumSize(50,50)   
#        self.buttonRight.setMaximumSize(50,50)    
#        self.buttonDown.setMaximumSize(50,50)    
#        self.buttonLeft.setMaximumSize(50,50)
#        
#        
#        self.arrowcontainer = QWidget()
#        self.arrowbox = QGridLayout()
#        self.arrowbox.addWidget(self.buttonUp,0,1)
#        self.arrowbox.addWidget(self.buttonDown,2,1)
#        self.arrowbox.addWidget(self.buttonLeft,1,0)
#        self.arrowbox.addWidget(self.buttonRight,1,2)
#        self.arrowbox.addWidget(self.buttonResult,1,1)
#        self.arrowcontainer.setLayout(self.arrowbox)
#        self.arrowcontainer.setMaximumSize(100,100)

    def addMSS(self,unit):
        #Used to tell if the end position status of the various motors has changed
        self.previousendpos.append([False,False,False,False,False,False,False,False,False,False,False,False])            
        
        self.deviceReadout.append([])
        for i in range (0,MSSInterface.portdata[unit][2]):
            self.deviceReadout[-1].append(None)
        self.readoutHContainer.append(None)
        self.readoutHLayout.append(None)
        self.readoutHContainerInternalV.append(None)
        self.readoutHContainerInternalVLayout.append(None)
        
        self.threadStatusContainer.append(QWidget())
        self.threadStatusLayout.append(QHBoxLayout())
        self.threadNameLabel.append(QLabel(" Unit "+str(unit)+" "))
        self.threadNameLabel[-1].setStyleSheet("QWidget {background-color: rgb(139,137,137); color: rgb(255,255,255); font-size: 20pt; font-weight: bold}")
        self.threadStatusLabel.append(QPushButton("0"))
        self.threadStatusLabel[-1].setMinimumWidth(40)
        self.threadStatusLabel[-1].setMaximumWidth(40)
        self.threadStatusLabel[-1].setStyleSheet("QWidget {background-color: rgb(0,255,127); color: rgb(255,255,255); font-size: 20pt}")
        self.threadStatusLayout[-1].addWidget(self.threadNameLabel[-1])
        self.threadStatusLayout[-1].addWidget(self.threadStatusLabel[-1])
        self.threadStatusContainer[-1].setMaximumHeight(60)
        self.threadStatusContainer[-1].setLayout(self.threadStatusLayout[-1])
        
        self.readoutColumn.append(QWidget())
        self.readoutLayout.append(QVBoxLayout())
        self.readoutColumn[-1].setLayout(self.readoutLayout[-1])
        self.readoutLayout[-1].setSpacing(1)
        self.readoutLayout[-1].addWidget(self.threadStatusContainer[-1])
        
        if unit == 0:
            self.threadStatusLabel[0].clicked.connect(lambda: self.purgeQueue(0))
        if unit == 1:
            self.threadStatusLabel[1].clicked.connect(lambda: self.purgeQueue(1))
        
        for device in range(0,MSSInterface.portdata[unit][2]):
            #It is assumed that MSSUnit 0, device 0 is the stage
            if unit == 0 and device == 0:
                self.deviceReadout[0][0] = DeviceReadout(0,0,True,self)
                self.readoutLayout[-1].addWidget(self.deviceReadout[0][0])
            else:
                self.deviceReadout[unit][device] = DeviceReadout(unit,device,False,self)
                self.readoutLayout[-1].addWidget(self.deviceReadout[unit][device])
            if MSSInterface.portdata[unit][2] == 1:
                self.readoutLayout[-1].addStretch()
        self.columnContainerLayout.addWidget(self.readoutColumn[-1])
    def addSX(self,unit):
        #Used to tell if the end position status of the various motors has changed
        self.previousendpos.append([False,False,False,False,False,False,False,False,False,False,False,False])            
        
        numdevices = int(MSSInterface.portdata[unit][2])    
        
        self.readoutHContainerInternalV.append(None)
        self.readoutHContainerInternalVLayout.append(None)
        
        self.threadStatusContainer.append(QWidget())
        self.threadStatusLayout.append(QHBoxLayout())
        self.threadNameLabel.append(QLabel(" Unit "+str(unit)+" "))
        self.threadNameLabel[-1].setStyleSheet("QWidget {background-color: rgb(139,137,137); color: rgb(255,255,255); font-size: 20pt; font-weight: bold}")
        self.threadStatusLabel.append(QPushButton("0"))
        self.threadStatusLabel[-1].setMinimumWidth(40)
        self.threadStatusLabel[-1].setMaximumWidth(40)
        self.threadStatusLabel[-1].setStyleSheet("QWidget {background-color: rgb(0,255,127); color: rgb(255,255,255); font-size: 20pt}")
        self.threadStatusLayout[-1].addWidget(self.threadNameLabel[-1])
        self.threadStatusLayout[-1].addWidget(self.threadStatusLabel[-1])
        self.threadStatusContainer[-1].setMaximumHeight(60)
        self.threadStatusContainer[-1].setLayout(self.threadStatusLayout[-1])
        
        self.readoutColumn.append(QWidget())
        self.readoutLayout.append(QVBoxLayout())
        self.readoutColumn[-1].setLayout(self.readoutLayout[-1])
        self.readoutLayout[-1].setSpacing(1)
        self.readoutLayout[-1].addWidget(self.threadStatusContainer[-1])
        
        self.deviceReadout.append([])
        for i in range (0,numdevices):
            self.deviceReadout[-1].append(None)
        
        if numdevices > 2:
            self.readoutHContainer.append(QWidget())
            self.readoutHLayout.append(QHBoxLayout())
            self.readoutHLayout[-1].setSpacing(1)
            self.readoutHLayout[-1].setMargin(3)
            
            self.readoutHContainerInternalV[-1] = []
            self.readoutHContainerInternalVLayout[-1] = []
            
            self.readoutHContainer[-1].setLayout(self.readoutHLayout[-1])
            
            for device in range(0,numdevices):
                if device%2 == 1 or device == numdevices-1:
                    
                    self.readoutHContainerInternalV[-1].append(QWidget())
                    self.readoutHContainerInternalVLayout[-1].append(QVBoxLayout())
                    self.readoutHContainerInternalVLayout[-1][-1].setSpacing(1)
                    self.readoutHContainerInternalVLayout[-1][-1].setMargin(3)
                    self.readoutHContainerInternalV[-1][-1].setLayout(self.readoutHContainerInternalVLayout[-1][-1])
                    
                    self.deviceReadout[unit][device] = DeviceReadout(unit,device,False,self)
                    self.readoutColumn[-1].setLayout(self.readoutLayout[-1])
                    self.readoutLayout[unit].setSpacing(1)   
                    if device == numdevices-1 and device%2 == 0:
                        self.readoutHContainerInternalVLayout[-1][-1].addWidget(self.deviceReadout[unit][device]) 
                        self.readoutHContainerInternalVLayout[-1][-1].addStretch()
                    else:
                        self.readoutHContainerInternalVLayout[-1][-1].addWidget(self.deviceReadout[unit][device-1])       
                        self.readoutHContainerInternalVLayout[-1][-1].addWidget(self.deviceReadout[unit][device]) 
                    self.readoutHLayout[-1].addWidget(self.readoutHContainerInternalV[-1][-1])
                else:
                    self.deviceReadout[unit][device] = DeviceReadout(unit,device,False,self)
                    
            self.readoutLayout[-1].addWidget(self.readoutHContainer[-1])
            #self.columnContainerLayout.addWidget(self.readoutHContainer[-1])
        else:
            self.readoutHContainer.append(None)
            self.readoutHLayout.append(None)
            
            for device in range (0,numdevices):
                self.deviceReadout[unit][device] = DeviceReadout(unit,device,False,self)
                self.readoutLayout[-1].addWidget(self.deviceReadout[unit][device]) 
            if numdevices == 1:
                self.readoutLayout[-1].addStretch()
        self.columnContainerLayout.addWidget(self.readoutColumn[-1])
        

        
        if unit == 0:
            self.threadStatusLabel[0].clicked.connect(lambda: self.purgeQueue(0))
        if unit == 1:
            self.threadStatusLabel[1].clicked.connect(lambda: self.purgeQueue(1))
        if unit == 2:
            self.threadStatusLabel[2].clicked.connect(lambda: self.purgeQueue(2))
        if unit == 3:
            self.threadStatusLabel[3].clicked.connect(lambda: self.purgeQueue(3))
        if unit == 4:
            self.threadStatusLabel[4].clicked.connect(lambda: self.purgeQueue(4))
        if unit == 5:
            self.threadStatusLabel[5].clicked.connect(lambda: self.purgeQueue(5))
        if unit == 6:
            self.threadStatusLabel[6].clicked.connect(lambda: self.purgeQueue(6))
        if unit == 7:
            self.threadStatusLabel[7].clicked.connect(lambda: self.purgeQueue(7))
        if unit == 8:
            self.threadStatusLabel[8].clicked.connect(lambda: self.purgeQueue(8))
        if unit == 9:
            self.threadStatusLabel[9].clicked.connect(lambda: self.purgeQueue(9))

    def keyPressEvent(self,event):
        self.parent.keyPressEvent(event)

    def keyReleaseEvent(self,event):
        self.parent.keyReleaseEvent(event)
        
    #save the calibration info to file
    def calibrateSaveToFile(self):
        
        for unit in range(0,len(MSSInterface.MyUnit)):
            for device in range(0,MSSInterface.portdata[unit][2]):
                if unit == 0 and device == 0:
                    pass
                else:
                    print "unit",unit,"device",device
                    calWriter = csv.writer(open('C:\calibration'+str(unit)+str(device)+'.csv','wb'))
                    calWriter.writerow([self.deviceReadout[unit][device].syncPointStage[0]]+[self.deviceReadout[unit][device].syncPointStage[1]]+[self.deviceReadout[unit][device].syncPointStage[2]])
                    calWriter.writerow([self.deviceReadout[unit][device].syncPointM[0]]+[self.deviceReadout[unit][device].syncPointM[1]]+[self.deviceReadout[unit][device].syncPointM[2]])
                    calWriter.writerow([self.deviceReadout[unit][device].Xhat[0]]+[self.deviceReadout[unit][device].Xhat[1]]+[self.deviceReadout[unit][device].Xhat[2]])
                    calWriter.writerow([self.deviceReadout[unit][device].Yhat[0]]+[self.deviceReadout[unit][device].Yhat[1]]+[self.deviceReadout[unit][device].Yhat[2]])
                    calWriter.writerow([self.deviceReadout[unit][device].Zhat[0]]+[self.deviceReadout[unit][device].Zhat[1]]+[self.deviceReadout[unit][device].Zhat[2]])
                    calWriter.writerow([self.deviceReadout[unit][device].StageUMperXMcoord])
                    calWriter.writerow([self.deviceReadout[unit][device].StageUMperYMcoord])
                    calWriter.writerow([self.deviceReadout[unit][device].StageUMperZMcoord])
                    calWriter.writerow([self.deviceReadout[unit][device].axialStartPoint[0]]+[self.deviceReadout[unit][device].axialStartPoint[1]]+[self.deviceReadout[unit][device].axialStartPoint[2]])
                    calWriter.writerow([self.deviceReadout[unit][device].axialVector[0]]+[self.deviceReadout[unit][device].axialVector[1]]+[self.deviceReadout[unit][device].axialVector[2]])
                    calWriter.writerow([self.deviceReadout[unit][device].axialMag])
                    calWriter.writerow([self.deviceReadout[unit][device].axialUnitVector[0]]+[self.deviceReadout[unit][device].axialUnitVector[1]]+[self.deviceReadout[unit][device].axialUnitVector[2]])
    #load the calibration info from file
    def calibrateLoadFromFile(self):
        for unit in range(0,len(MSSInterface.MyUnit)):
            for device in range(0,MSSInterface.portdata[unit][2]):
                if unit == 0 and device == 0:
                    pass
                else:
                    print "unit",unit,"device",device
                    calReader = csv.reader(open('C:\calibration'+str(unit)+str(device)+'.csv'),quoting=csv.QUOTE_NONNUMERIC)
                    self.deviceReadout[unit][device].syncPointStage = calReader.next()
                    self.deviceReadout[unit][device].syncPointM = calReader.next()
                    self.deviceReadout[unit][device].Xhat = calReader.next()
                    self.deviceReadout[unit][device].Yhat = calReader.next()
                    self.deviceReadout[unit][device].Zhat = calReader.next()
                    self.deviceReadout[unit][device].StageUMperXMcoord = calReader.next()[0]
                    self.deviceReadout[unit][device].StageUMperYMcoord = calReader.next()[0]
                    self.deviceReadout[unit][device].StageUMperZMcoord = calReader.next()[0]
                    self.deviceReadout[unit][device].axialStartPoint = calReader.next()
                    self.deviceReadout[unit][device].axialVector = calReader.next()
                    self.deviceReadout[unit][device].axialMag = calReader.next()[0]
                    self.deviceReadout[unit][device].axialUnitVector = calReader.next()
                    
                    if self.deviceReadout[unit][device].axialUnitVector[0] != '':
                        self.deviceReadout[unit][device].calibrateAxialButton.setText("Clear Axial Calibration")
                        self.deviceReadout[unit][device].calibrateAxialButton.setStyleSheet("QWidget {background-color: rgb(139,137,137); color: rgb(255,0,0); font-weight: bold}")
                    #self.StageUMperXMcoord = self.StageUMperXMcoord[0]
                    #self.StageUMperYMcoord = self.StageUMperYMcoord[0]
                    #self.StageUMperZMcoord = self.StageUMperZMcoord[0]
                    print self.deviceReadout[unit][device].syncPointStage
                    print self.deviceReadout[unit][device].syncPointM
                    print self.deviceReadout[unit][device].Xhat
                    print self.deviceReadout[unit][device].Yhat
                    print self.deviceReadout[unit][device].Zhat
                    print self.deviceReadout[unit][device].StageUMperXMcoord
                    print self.deviceReadout[unit][device].StageUMperYMcoord
                    print self.deviceReadout[unit][device].StageUMperZMcoord
                    self.deviceReadout[unit][device].getMPositionStage()
    
    
#    def upPressed(self):
#        self.buttonResult.setText("Up")
#    def rightPressed(self):
#        self.buttonResult.setText("Right")
#    def downPressed(self):
#        self.buttonResult.setText("Down")
#    def leftPressed(self):
#        self.buttonResult.setText("Left")
        
        
    def purgeQueue(self,unit):
        MSSInterface.purgeQueue[unit] = True
        print "PURGING QUEUE, UNIT",unit
#        while len(MSSInterface.threadqueue[0]) != 0:
#            MSSInterface.threadqueue.pop(0)
#        
#        if MSSInterface.currentthread[unit] != None:
#            MSSInterface.currentthread[unit].stop()
        
    #If the previous end position for a motor has changed, update the graphics.
    #It's not good to update the graphics every cycle as this consumes a lot of processing power
    def updateText(self):
        if MSSInterface.motorcoordinates != None:
            self.motorcoords = MSSInterface.getCoords() #unit 0, manip 0
        
        for unit in range(0,len(MSSInterface.MyUnit)):
            for device in range (0,MSSInterface.portdata[unit][2]):

                self.deviceReadout[unit][device].xField.setText(QString(str(self.motorcoords[unit][device][0])))
                self.deviceReadout[unit][device].yField.setText(QString(str(self.motorcoords[unit][device][1])))
                self.deviceReadout[unit][device].zField.setText(QString(str(self.motorcoords[unit][device][2])))

        #grid.pixelsperum = float(self.deviceReadout[0][0].ppumField.text())
        
        for unit in range (0,len(MSSInterface.MyUnit)):
            #STAGE END POSITIONS
            if self.previousendpos[unit][0] != MSSInterface.MyUnit[unit].x0EndPosPlus:
                self.previousendpos[unit][0] = MSSInterface.MyUnit[unit].x0EndPosPlus
                if MSSInterface.MyUnit[unit].x0EndPosPlus == True:
                    self.deviceReadout[unit][0].xEndPosPlus.setStyleSheet("QWidget {background-color: rgb(220,20,60)}")
                else:
                    self.deviceReadout[unit][0].xEndPosPlus.setStyleSheet("QWidget {background-color: rgb(0,255,127)}")

            if self.previousendpos[unit][1] != MSSInterface.MyUnit[unit].y0EndPosPlus:
                self.previousendpos[unit][1] = MSSInterface.MyUnit[unit].y0EndPosPlus
                if MSSInterface.MyUnit[unit].y0EndPosPlus == True:
                    self.deviceReadout[unit][0].yEndPosPlus.setStyleSheet("QWidget {background-color: rgb(220,20,60)}")
                else:
                    self.deviceReadout[unit][0].yEndPosPlus.setStyleSheet("QWidget {background-color: rgb(0,255,127)}")

            if self.previousendpos[unit][2] != MSSInterface.MyUnit[unit].z0EndPosPlus:
                self.previousendpos[unit][2] = MSSInterface.MyUnit[unit].z0EndPosPlus
                if MSSInterface.MyUnit[unit].z0EndPosPlus == True:
                    self.deviceReadout[unit][0].zEndPosPlus.setStyleSheet("QWidget {background-color: rgb(220,20,60)}")
                else:
                    self.deviceReadout[unit][0].zEndPosPlus.setStyleSheet("QWidget {background-color: rgb(0,255,127)}")

            if self.previousendpos[unit][3] != MSSInterface.MyUnit[unit].x0EndPosMinus:
                self.previousendpos[unit][3] = MSSInterface.MyUnit[unit].x0EndPosMinus
                if MSSInterface.MyUnit[unit].x0EndPosMinus == True:
                    self.deviceReadout[unit][0].xEndPosMinus.setStyleSheet("QWidget {background-color: rgb(220,20,60)}")
                else:
                    self.deviceReadout[unit][0].xEndPosMinus.setStyleSheet("QWidget {background-color: rgb(0,255,127)}")

            if self.previousendpos[unit][4] != MSSInterface.MyUnit[unit].y0EndPosMinus:
                self.previousendpos[unit][4] = MSSInterface.MyUnit[unit].y0EndPosMinus
                if MSSInterface.MyUnit[unit].y0EndPosMinus == True:
                    self.deviceReadout[unit][0].yEndPosMinus.setStyleSheet("QWidget {background-color: rgb(220,20,60)}")
                else:
                    self.deviceReadout[unit][0].yEndPosMinus.setStyleSheet("QWidget {background-color: rgb(0,255,127)}")

            if self.previousendpos[unit][5] != MSSInterface.MyUnit[unit].z0EndPosMinus:
                self.previousendpos[unit][5] = MSSInterface.MyUnit[unit].z0EndPosMinus
                if MSSInterface.MyUnit[unit].z0EndPosMinus == True:
                    self.deviceReadout[unit][0].zEndPosMinus.setStyleSheet("QWidget {background-color: rgb(220,20,60)}")
                else:
                    self.deviceReadout[unit][0].zEndPosMinus.setStyleSheet("QWidget {background-color: rgb(0,255,127)}")
            #MANIPULATOR END POSITIONS
            if MSSInterface.portdata[unit][2] > 1:
                if self.previousendpos[unit][6] != MSSInterface.MyUnit[unit].x1EndPosPlus:
                    self.previousendpos[unit][6] = MSSInterface.MyUnit[unit].x1EndPosPlus
                    if MSSInterface.MyUnit[unit].x1EndPosPlus == True:
                        self.deviceReadout[unit][1].xEndPosPlus.setStyleSheet("QWidget {background-color: rgb(220,20,60)}")
                    else:
                        self.deviceReadout[unit][1].xEndPosPlus.setStyleSheet("QWidget {background-color: rgb(0,255,127)}")
    
                if self.previousendpos[unit][7] != MSSInterface.MyUnit[unit].y1EndPosPlus:
                    self.previousendpos[unit][7] = MSSInterface.MyUnit[unit].y1EndPosPlus
                    if MSSInterface.MyUnit[unit].y1EndPosPlus == True:
                        self.deviceReadout[unit][1].yEndPosPlus.setStyleSheet("QWidget {background-color: rgb(220,20,60)}")
                    else:
                        self.deviceReadout[unit][1].yEndPosPlus.setStyleSheet("QWidget {background-color: rgb(0,255,127)}")
    
                if self.previousendpos[unit][8] != MSSInterface.MyUnit[unit].z1EndPosPlus:
                    self.previousendpos[unit][8] = MSSInterface.MyUnit[unit].z1EndPosPlus
                    if MSSInterface.MyUnit[unit].z1EndPosPlus == True:
                        self.deviceReadout[unit][1].zEndPosPlus.setStyleSheet("QWidget {background-color: rgb(220,20,60)}")
                    else:
                        self.deviceReadout[unit][1].zEndPosPlus.setStyleSheet("QWidget {background-color: rgb(0,255,127)}")
    
                if self.previousendpos[unit][9] != MSSInterface.MyUnit[unit].x1EndPosMinus:
                    self.previousendpos[unit][9] = MSSInterface.MyUnit[unit].x1EndPosMinus
                    if MSSInterface.MyUnit[unit].x1EndPosMinus == True:
                        self.deviceReadout[unit][1].xEndPosMinus.setStyleSheet("QWidget {background-color: rgb(220,20,60)}")
                    else:
                        self.deviceReadout[unit][1].xEndPosMinus.setStyleSheet("QWidget {background-color: rgb(0,255,127)}")
    
                if self.previousendpos[unit][10] != MSSInterface.MyUnit[unit].y1EndPosMinus:
                    self.previousendpos[unit][10] = MSSInterface.MyUnit[unit].y1EndPosMinus
                    if MSSInterface.MyUnit[unit].y1EndPosMinus == True:
                        self.deviceReadout[unit][1].yEndPosMinus.setStyleSheet("QWidget {background-color: rgb(220,20,60)}")
                    else:
                        self.deviceReadout[unit][1].yEndPosMinus.setStyleSheet("QWidget {background-color: rgb(0,255,127)}")
    
                if self.previousendpos[unit][11] != MSSInterface.MyUnit[unit].z1EndPosMinus:
                    self.previousendpos[unit][11] = MSSInterface.MyUnit[unit].z1EndPosMinus
                    if MSSInterface.MyUnit[unit].z1EndPosMinus == True:
                        self.deviceReadout[unit][1].zEndPosMinus.setStyleSheet("QWidget {background-color: rgb(220,20,60)}")
                    else:
                        self.deviceReadout[unit][1].zEndPosMinus.setStyleSheet("QWidget {background-color: rgb(0,255,127)}")
            
        for unit in range(0,len(MSSInterface.MyUnit)):
            for device in range (0,MSSInterface.portdata[unit][2]):
                if unit == 0 and device == 0:
                    pass
                else:
                    self.deviceReadout[unit][device].getMPositionStage()
        
        #self.hdivfield.setText(QString(str(grid.hdiv)[0:10]))
  
class GarbageCollector(QObject):

    '''
    Disable automatic garbage collection and instead collect manually
    every INTERVAL milliseconds.

    This is done to ensure that garbage collection only happens in the GUI
    thread, as otherwise Qt can crash.
    '''

    INTERVAL = 1000

    def __init__(self, parent, debug=False):
        QObject.__init__(self, parent)
        self.debug = debug

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check)

        self.threshold = gc.get_threshold()
        gc.disable()
        self.timer.start(self.INTERVAL)
        #gc.set_debug(gc.DEBUG_SAVEALL)

    def check(self):
        #return self.debug_cycles()
        l0, l1, l2 = gc.get_count()
        if self.debug:
            print ('gc_check called:', l0, l1, l2)
        if l0 > self.threshold[0]:
            num = gc.collect(0)
            if self.debug:
                print ('collecting gen 0, found:', num, 'unreachable')
            if l1 > self.threshold[1]:
                num = gc.collect(1)
                if self.debug:
                    print ('collecting gen 1, found:', num, 'unreachable')
                if l2 > self.threshold[2]:
                    num = gc.collect(2)
                    if self.debug:
                        print ('collecting gen 2, found:', num, 'unreachable')

    def debug_cycles(self):
        gc.collect()
        for obj in gc.garbage:
            print (obj, repr(obj), type(obj))

#start the app, or something
mainwindow = MainDisplay()
mainwindow.show()  

app.exec_()