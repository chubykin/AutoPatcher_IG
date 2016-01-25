# -*- coding: utf-8 -*-
"""
Created on Sat July 04 20:17:10 2015

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

@Author: Zhaolun Su, Brendan Callahan, Alexander A. Chubykin

"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
#import argl as argl
import sys
import cv2
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
MSSInterface = MSSInterface.MSSInterface()
grid = Grid.Grid()

myCrosshairCursor = QCursor(QBitmap("mycrosshair.bmp"),QBitmap("mycrosshairmask.bmp"),10,10)

useDummyArrowsWindow = False
cameraDevice = cw.CameraDevice()

width = 0 #width & height of video
height = 0

class MainDisplay(QMainWindow):
    def __init__(self, parent=None):
    	QMainWindow.__init__(self)
    	self.myarrows = Arrows(self)
        self.myarrows.show()
        
        self.myarrowsalternate = None
        MSSInterface.setArrows(self.myarrows)
        MSSInterface.setArrowsAlternate(self.myarrowsalternate)


class DeviceReadout(QWidget):
    def __init__(self,unitnum,manip,isStage,parent=None):
        super(DeviceReadout,self).__init__(parent)
        
        #main layout
        self.deviceReadoutLayout = QVBoxLayout()
        self.deviceReadoutLayout.setSpacing(1)
        self.setWindowTitle('DeviceReadOut')
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
            
            self.StageUMperXMcoord = None
            self.StageUMperYMcoord = None
            self.StageUMperZMcoord = None
            
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
            self.ppumField.setText(str(grid.pixelsperum))
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
    
            self.calibrateX1 = QPushButton("Start Arm Calibration")
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
        if useDummyArrowsWindow == True:
            altarrows = self.parent.parent.myarrowsalternate.deviceReadout[self.unitnum][self.manipnum]
            altarrows.brightnessReadout.setText(str(dialval))
            altarrows.brightnessDial.setValue(dialval)
    def changeContrast(self):
        dialval = self.contrastDial.value()
        cameraDevice.contrast = dialval/100.0
        self.contrastReadout.setText(str(dialval/100.0))
        if useDummyArrowsWindow == True:
            altarrows = self.parent.parent.myarrowsalternate.deviceReadout[self.unitnum][self.manipnum]
            altarrows.contrastReadout.setText(str(dialval))
            altarrows.contrastDial.setValue(dialval)
        
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
        altarrows = None
        if useDummyArrowsWindow == True:
            altarrows = self.parent.parent.myarrowsalternate.deviceReadout[self.unitnum][self.manipnum]
        if self.magRadioButton4x.isChecked() == True:
            grid.setPixelsPerUM(4.0)
            self.ppumCurrentMag.setText("(4X)")
            self.ppumCurrentMag.setStyleSheet("QWidget {font-weight:bold}")
            if (altarrows != None):
                altarrows.magRadioButton4x.setChecked(True)
        elif self.magRadioButton10x.isChecked() == True:
            grid.setPixelsPerUM(10.0)
            self.ppumCurrentMag.setText("(10X)")
            self.ppumCurrentMag.setStyleSheet("QWidget {font-weight:bold}")
            if (altarrows != None):
                altarrows.magRadioButton10x.setChecked(True)
        elif self.magRadioButton40x.isChecked() == True:
            grid.setPixelsPerUM(40.0)
            self.ppumCurrentMag.setText("(40X)")
            self.ppumCurrentMag.setStyleSheet("QWidget {font-weight:bold}")
            if (altarrows != None):
                altarrows.magRadioButton40x.setChecked(True)
        
        self.ppumField.setText(QString(str(grid.pixelsperum)))
        if altarrows != None:
            altarrows.ppumField.setText(QString(str([round(grid.pixelsperum[0],6),round(grid.pixelsperum[1],6)])))
       
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
            if useDummyArrowsWindow == True:
                self.parent.parent.myarrowsalternate.updateText()
        
    #not currently used
    def calibrateSurfaceClicked(self):
        self.calSurfaceZ = MSSInterface.getCoords()[2]
        print "SURFACE Z SET TO ",self.calSurfaceZ      
        
        
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
        
        self.StageUMperXMcoord = None
        self.StageUMperYMcoord = None
        self.StageUMperZMcoord = None
        
        self.MStageCoordinates = [None,None,None]
        self.Mmotorcoords = [None,None,None]
        self.xFieldStage.setText("")
        self.yFieldStage.setText("")
        self.zFieldStage.setText("")
        self.calibrateX1.setStyleSheet("QWidget {background-color: rgb(139,137,137); color: rgb(255,255,255); font-weight: bold}")
        self.calibrateX1.setText("Start Calibration")
        
        if useDummyArrowsWindow == True:
            self.parent.parent.myarrowsalternate.updateText()
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


class Arrows(QDialog):
    def __init__(self, parent=None):
        super(Arrows, self).__init__(parent)
        
        self.parent = parent
        self.setWindowTitle('Arrows')
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
            elif MSSInterface.portdata[unit][1] == "SCI":
                self.addSCI(unit)
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
    @pyqtSlot()
    def updateUnit(self):
        for thisunit in range(0,len(MSSInterface.MyUnit)):
            if MSSInterface.currentthread[thisunit] != None:
                #if there's a thread going or theres something in the queue, update
                if MSSInterface.currentthread[thisunit].isAlive() == True or len(MSSInterface.threadqueue[thisunit]) > 0:
                    print "THREATDD" + str(len(MSSInterface.threadqueue[0]))
                    MSSInterface.myarrows.threadStatusLabel[thisunit].setText(str(len(MSSInterface.threadqueue[thisunit])))
                    MSSInterface.myarrows.threadStatusLabel[thisunit].setStyleSheet("QWidget {background-color: rgb(220,20,60); color: rgb(255,255,255); font-size: 20pt;}")
                else:
                    #otherwise theres nothing in the queue, set it to 0
                    MSSInterface.myarrows.threadStatusLabel[thisunit].setText("0")
                    MSSInterface.myarrows.threadStatusLabel[thisunit].setStyleSheet("QWidget {background-color: rgb(0,255,127); color: rgb(255,255,255); font-size: 20pt;}")
            else:
                MSSInterface.myarrows.threadStatusLabel[thisunit].setText("0")
                MSSInterface.myarrows.threadStatusLabel[thisunit].setStyleSheet("QWidget {background-color: rgb(0,255,127); color: rgb(255,255,255); font-size: 20pt;}")
    
    @pyqtSlot()
    def updateTextSlot(self):
        self.updateText()
        
    def addSCI(self,unit):
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

                self.deviceReadout[unit][device].xField.setText(str(self.motorcoords[unit][device][0]))
                self.deviceReadout[unit][device].yField.setText(str(self.motorcoords[unit][device][1]))
                self.deviceReadout[unit][device].zField.setText(str(self.motorcoords[unit][device][2]))

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
  


class ArrowsDummy(QDialog):
    def __init__(self, parent=None):
        super(ArrowsDummy, self).__init__(parent)
         
        self.parent = parent
        self.setGeometry(1300,20,35,600)
         
         
        self.mainvboxlayout = QVBoxLayout()
        
        self.columnContainer = QWidget()
        self.columnContainerLayout = QHBoxLayout()

        self.columnContainer.setLayout(self.columnContainerLayout)
        self.columnContainerLayout.setSpacing(30)
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
            elif MSSInterface.portdata[unit][1] == "SCI":
                self.addSCI(unit)
            #vertical line to separate unit readouts
            if unit < len(MSSInterface.MyUnit)-1:
                newwidget = QWidget()
                newwidget.setMaximumWidth(1)
                newwidget.setMinimumWidth(1)
                newwidget.setMinimumHeight(775)
                newwidget.setMaximumHeight(775)
                newwidget.setStyleSheet("QWidget {background-color: rgb(139,137,137);}")
                self.columnContainerLayout.addWidget(newwidget)
        
        for unit in range (0,len(MSSInterface.MyUnit)):
            self.readoutLayout[unit].addWidget(self.threadStatusContainer[unit])
            for device in range (0,2):
                if device == 1:
                    self.readoutLayout[unit].addStretch()
                self.readoutLayout[unit].addWidget(self.deviceReadout[unit][device])                
            self.readoutColumn[unit].setLayout(self.readoutLayout[unit])
#            
            
        
        self.toggle = True
        self.clicktomove = True
        
        self.calibrationContainer = QWidget()
        self.calibrationContainerLayout = QHBoxLayout()
        self.calibrateSave = QPushButton("Save Calibration")
        #self.calibrateSave.connect(self.calibrateSave, SIGNAL("clicked()"), self.calibrateSaveToFile)
        self.calibrateLoad = QPushButton("Load Calibration")
        #self.calibrateLoad.connect(self.calibrateLoad, SIGNAL("clicked()"), self.calibrateLoadFromFile)
        self.calibrationContainer.setLayout(self.calibrationContainerLayout)
        
        
        self.calibrationContainerLayout.addWidget(self.calibrateSave)
        self.calibrationContainerLayout.addWidget(self.calibrateLoad)
        
        #set unit 0 device 1 (the default selected device for keyboard movement) as 
        #highlighted in green; this will later be taken care of during the process of changing the device         

        ######################################NEEDS TO BE CHANGED OVER#################        
        
        #self.deviceReadout[0][1].deviceLabel.setStyleSheet("QWidget {background-color: rgb(0,255,127); font-weight:bold;}")
        
        #self.axisdirections = []
        #axisReader = csv.reader(open('C:\\axisdirections.csv'),quoting=csv.QUOTE_NONNUMERIC)
        #print self.deviceReadout
        #for unit in self.deviceReadout:
        #    self.axisdirections.append([])
        #    for manip in unit:              
        #        self.axisdirections[manip.unitnum].append(axisReader.next())
        #        
        #print self.axisdirections
        
        #THIS IS FOR EXTRA STUFF AT THE BOTTOM
        self.mainvboxlayout.addWidget(self.columnContainer)
        #self.mainvboxlayout.addWidget(self.calibrationContainer)
        
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
    @pyqtSlot()
    def updateTextSlot(self):
        self.updateText()
        
    @pyqtSlot()
    def updateUnitAlternate(self):
        for thisunit in range(0,len(MSSInterface.MyUnit)):
            if MSSInterface.currentthread[thisunit] != None:
                #if there's a thread going or theres something in the queue, update
                if MSSInterface.currentthread[thisunit].isAlive() == True or len(MSSInterface.threadqueue[thisunit]) > 0:
                    self.threadStatusLabel[thisunit].setText(str(len(MSSInterface.threadqueue[thisunit])))
                    self.threadStatusLabel[thisunit].setStyleSheet("QWidget {background-color: rgb(220,20,60); color: rgb(255,255,255); font-size: 20pt;;font-weight:bold}")
                else:
                    #otherwise theres nothing in the queue, set it to 0
                    self.threadStatusLabel[thisunit].setText("0")
                    self.threadStatusLabel[thisunit].setStyleSheet("QWidget {background-color: rgb(0,255,127); color: rgb(255,255,255); font-size: 20pt;;font-weight:bold}")
            else:
                self.threadStatusLabel[thisunit].setText("0")
                self.threadStatusLabel[thisunit].setStyleSheet("QWidget {background-color: rgb(0,255,127); color: rgb(255,255,255); font-size: 20pt;font-weight:bold}")
        
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
        self.threadStatusLabel[-1].setStyleSheet("QWidget {background-color: rgb(0,255,127); color: rgb(255,255,255); font-size: 20pt; font-weight:bold}")
        self.threadStatusLayout[-1].addWidget(self.threadNameLabel[-1])
        self.threadStatusLayout[-1].addWidget(self.threadStatusLabel[-1])
        self.threadStatusContainer[-1].setMaximumHeight(60)
        #self.threadStatusContainer[-1].setMaximumWidth(450)
        self.threadStatusContainer[-1].setLayout(self.threadStatusLayout[-1])
        
        self.readoutColumn.append(QWidget())
        self.readoutLayout.append(QHBoxLayout())
        self.readoutColumn[-1].setLayout(self.readoutLayout[-1])
        self.readoutLayout[-1].setSpacing(1)
        self.mainvboxlayout.addWidget(self.threadStatusContainer[-1])
        
        #if unit == 0:
        #    self.threadStatusLabel[0].clicked.connect(lambda: self.purgeQueue(0))
        #if unit == 1:
        #    self.threadStatusLabel[1].clicked.connect(lambda: self.purgeQueue(1))
        #
        for device in range(0,MSSInterface.portdata[unit][2]):
            #It is assumed that MSSUnit 0, device 0 is the stage
            if unit == 0 and device == 0:
                self.deviceReadout[0][0] = DeviceReadoutDummy(0,0,True,self)
                self.readoutLayout[-1].addWidget(self.deviceReadout[0][0])
            else:
                self.deviceReadout[unit][device] = DeviceReadoutDummy(unit,device,False,self)
                self.readoutLayout[-1].addWidget(self.deviceReadout[unit][device])
            if MSSInterface.portdata[unit][2] == 1:
                self.readoutLayout[-1].addStretch()
        self.columnContainerLayout.addWidget(self.readoutColumn[-1])
    def updateText(self):
        if MSSInterface.motorcoordinates != None:
            self.motorcoords = MSSInterface.getCoords() #unit 0, manip 0
        
        for unit in range(0,len(MSSInterface.MyUnit)):
            for device in range (0,MSSInterface.portdata[unit][2]):
                if (unit == 0) and (device == 0):
                    self.deviceReadout[unit][device].xField.setText(str(self.motorcoords[unit][device][0]))
                    self.deviceReadout[unit][device].yField.setText(str(self.motorcoords[unit][device][1]))
                    self.deviceReadout[unit][device].zField.setText(str(self.motorcoords[unit][device][2]))

            
        for unit in range(0,len(MSSInterface.MyUnit)):
            for device in range (0,MSSInterface.portdata[unit][2]):
                if unit == 0 and device == 0:
                    pass
                else:
                    realReadout = self.parent.myarrows.deviceReadout[unit][device]
                    
                    self.deviceReadout[unit][device].xFieldStage.setText(realReadout.xFieldStage.text())
                    self.deviceReadout[unit][device].yFieldStage.setText(realReadout.yFieldStage.text())
                    self.deviceReadout[unit][device].zFieldStage.setText(realReadout.zFieldStage.text())
                    self.MStageCoordinates = copy.deepcopy(realReadout.MStageCoordinates)
         
     

mainwindow = MainDisplay()
mainwindow.show()  

app.exec_()
MSSInterface.speedFast()



while True:
	print 'Moving up'
	MSSInterface.moveYPlus(0,0)
	time.sleep(0.5)
	MSSInterface.stopY(0,0)

	print 'Moving Down'
	MSSInterface.moveYMinus(0,0)
	time.sleep(0.5)
	MSSInterface.stopY(0,0)

    
  