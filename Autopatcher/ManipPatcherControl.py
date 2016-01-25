# -*- coding: utf-8 -*-
"""
Created on Wed May 09 15:17:10 2012

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

@Author: Brendan Callahan, Zhaolun Su, Alexander A. Chubykin

"""

import copy
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import time
import copy
import csv
import random
import functools

#How these classes work:  ManipPatcherControl = main window -> ListItemLayout = contains list items ->
#                         ManipPatcherListItem -> listiteminfo, contains commandlayout -> CommandLayout ->
#                         CommandItem.  Base window has to be passed at least down to MPListItems, 
#                         as ListItems need to update the right window with their stored commands.
#                         (This can also be accomplished with parent.parent.parent etc)   


#This is the window that contains all the items for executing scripted sequences of commands, possibly
#using the logic parser or whatever.

class ManipPatcherControl(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self)
        self.mainLayout = QVBoxLayout()
        self.setGeometry(980,40,800,400)  
        self.setWindowTitle('Command Sequence')
        #These will be randomly used to color the numerical ID button for the list items,
        #so that it's more obvious what's happening when you change their order.
        self.colorlist = [[25,25,112],[0,0,128],[100,149,237],[0,0,205],[65,105,255],[0,0,255],[30,144,255],[0,191,255],[135,206,250],[70,130,180],[176,196,222],[173,216,230],[176,224,230],[175,238,238],[0,206,209],[72,209,204],[64,224,208],[0,255,255],[95,158,160],[32,178,170]]
        
        self.parent = parent         
        self.grid = None
        self.ItemList = []
        self.currentunit = 0
        self.currentmanip = 1
        
        self.zlift = 0.0 #how many um the manipulator lifts vertically before approaching a target
        self.axiallift = 0.0#"" "" lifts axially "" ""
        self.lifttype = None
        
        #Contains radio buttons for selecting current device
        self.topContainer = QWidget()
        self.topLayout = QHBoxLayout()
        self.unitLabel = QLabel()
        self.unitLabel.setText("Unit")
        self.unitNumLabel = QLabel()
        self.unitNumLabel.setText("0")
        self.manipLabel = QLabel()
        self.manipLabel.setText("Manipulator")
        self.manipNumLabel = QLabel()
        self.manipNumLabel.setText("1")
        #self.topLayout.addWidget(self.unitLabel)
        #self.topLayout.addWidget(self.unitNumLabel)
        #self.topLayout.addWidget(self.manipLabel)
        #self.topLayout.addWidget(self.manipNumLabel)
        self.topContainer.setLayout(self.topLayout)

        #contains the list item and command item displays
        self.middleContainer = QWidget()
        self.middleLayout = QHBoxLayout()
        
        #contains list items
        self.leftContainerFull = QWidget()
        self.leftContainerFullLayout = QVBoxLayout()
        self.leftContainerLabelContainer = QWidget()
        self.leftContainerLabelContainerLayout = QHBoxLayout()
        self.leftContainerLabel = QLabel("Coordinates")
        self.leftContainerLabel.setMaximumHeight(20)
        self.leftContainerLabel.setStyleSheet("QWidget {font-weight:bold}")
        
        self.leftContainerLabelSaveButton = QPushButton("Save")
        self.leftContainerLabelSaveButton.setStyleSheet("QWidget {font-weight:bold; background-color: rgb(248,248,255); color:rgb(0,0,0);}")
        self.leftContainerLabelSaveButton.connect(self.leftContainerLabelSaveButton, SIGNAL("clicked()"), self.saveList)          
        self.leftContainerLabelSaveButton.setMaximumWidth(40)

        self.leftContainerLabelLoadButton = QPushButton("Load")
        self.leftContainerLabelLoadButton.setStyleSheet("QWidget {font-weight:bold; background-color: rgb(248,248,255); color:rgb(0,0,0);}")
        self.leftContainerLabelLoadButton.connect(self.leftContainerLabelLoadButton, SIGNAL("clicked()"), self.loadList)        
        self.leftContainerLabelLoadButton.setMaximumWidth(40)        
        
        self.leftContainerLabelLoadGridButton = QPushButton("Load Grid")
        self.leftContainerLabelLoadGridButton.setStyleSheet("QWidget {font-weight:bold; background-color: rgb(79,148,205); color:rgb(248,248,255);}")
        self.leftContainerLabelLoadGridButton.connect(self.leftContainerLabelLoadGridButton, SIGNAL("clicked()"), self.loadGrid)        
        self.leftContainerLabelLoadGridButton.setMaximumWidth(70) 
            
        
        self.leftContainerLabelLoadMouseButton = QPushButton("Load Mouse Points")
        self.leftContainerLabelLoadMouseButton.setStyleSheet("QWidget {font-weight:bold; background-color: rgb(79,148,205); color:rgb(248,248,255);}")
        self.leftContainerLabelLoadMouseButton.connect(self.leftContainerLabelLoadMouseButton, SIGNAL("clicked()"), self.loadMousePoints)        
        
        self.leftContainerLabelAddButton = QPushButton("+")
        self.leftContainerLabelAddButton.setMaximumWidth(25)
        self.leftContainerLabelAddButton.setStyleSheet("QWidget {font-weight:bold; background-color: rgb(0,255,127); color:rgb(248,248,255);}")
        self.leftContainerLabelAddButton.connect(self.leftContainerLabelAddButton, SIGNAL("clicked()"), self.addNewListItem)  

        self.leftContainerLabelRunButton = QPushButton("Run")
        #self.rightContainerLabelAddButton.setMaximumWidth(25)
        self.leftContainerLabelRunButton.setStyleSheet("QWidget {font-weight:bold; background-color: rgb(0,0,0); color:rgb(248,248,255);}")        
        self.leftContainerLabelRunButton.connect(self.leftContainerLabelRunButton, SIGNAL("clicked()"), self.runAllListItems)        
        self.leftContainerLabelRunButton.setMaximumWidth(50)     
        
        self.leftContainerLabelContainerLayout.addWidget(self.leftContainerLabel)  
        self.leftContainerLabelContainerLayout.addWidget(self.leftContainerLabelSaveButton)
        self.leftContainerLabelContainerLayout.addWidget(self.leftContainerLabelLoadButton)
        self.leftContainerLabelContainerLayout.addWidget(self.leftContainerLabelLoadGridButton)
        self.leftContainerLabelContainerLayout.addWidget(self.leftContainerLabelLoadMouseButton)        
        self.leftContainerLabelContainerLayout.addWidget(self.leftContainerLabelRunButton)
        self.leftContainerLabelContainerLayout.addWidget(self.leftContainerLabelAddButton)
        self.leftContainerLabelContainer.setLayout(self.leftContainerLabelContainerLayout)        
        self.leftContainerFull.setLayout(self.leftContainerFullLayout)
        
        #contains command items
        self.rightContainerFull = QWidget()
        self.rightContainerFullLayout = QVBoxLayout()
        self.rightContainerLabelContainer = QWidget()
        self.rightContainerLabelContainerLayout = QHBoxLayout()
        self.rightContainerLabel = QLabel("Commands")
        self.rightContainerLabel.setMaximumHeight(20)
        self.rightContainerLabel.setStyleSheet("QWidget {font-weight:bold}")
        
        
        self.rightContainerLabelSaveButton = QPushButton("Save")
        self.rightContainerLabelSaveButton.setStyleSheet("QWidget {font-weight:bold; background-color: rgb(248,248,255); color:rgb(0,0,0);}")
        self.rightContainerLabelSaveButton.connect(self.rightContainerLabelSaveButton, SIGNAL("clicked()"), self.saveCommands)          
        self.rightContainerLabelSaveButton.setMaximumWidth(40)   

        self.rightContainerLabelLoadButton = QPushButton("Load")
        self.rightContainerLabelLoadButton.setStyleSheet("QWidget {font-weight:bold; background-color: rgb(248,248,255); color:rgb(0,0,0);}")
        self.rightContainerLabelLoadButton.connect(self.rightContainerLabelLoadButton, SIGNAL("clicked()"), self.loadCommands)
        self.rightContainerLabelLoadButton.setMaximumWidth(40)   
        
        self.rightContainerLabelAddButton = QPushButton("+")
        self.rightContainerLabelAddButton.setMaximumWidth(25)
        self.rightContainerLabelAddButton.setStyleSheet("QWidget {font-weight:bold; background-color: rgb(0,255,127); color:rgb(248,248,255);}")
        self.rightContainerLabelAddButton.connect(self.rightContainerLabelAddButton, SIGNAL("clicked()"), self.addNewCommandItem)  
    
        self.rightContainerLabelRunButton = QPushButton("Run")
        self.rightContainerLabelRunButton.connect(self.rightContainerLabelRunButton, SIGNAL("clicked()"), self.runAllCommands)
        self.rightContainerLabelRunButton.setMaximumWidth(50)   
        #self.rightContainerLabelAddButton.setMaximumWidth(25)
        self.rightContainerLabelRunButton.setStyleSheet("QWidget {font-weight:bold; background-color: rgb(0,0,0); color:rgb(248,248,255);}")        
        
        self.rightContainerLabelContainerLayout.addWidget(self.rightContainerLabel)  
        self.rightContainerLabelContainerLayout.addWidget(self.rightContainerLabelSaveButton)
        self.rightContainerLabelContainerLayout.addWidget(self.rightContainerLabelLoadButton)
        self.rightContainerLabelContainerLayout.addWidget(self.rightContainerLabelRunButton)
        self.rightContainerLabelContainerLayout.addWidget(self.rightContainerLabelAddButton)
        self.rightContainerLabelContainer.setLayout(self.rightContainerLabelContainerLayout) 
        self.rightContainerFull.setLayout(self.rightContainerFullLayout)
        
        
        self.leftContainer =  QWidget()
        self.leftContainerLayout = QVBoxLayout()
        #self.leftContainer.setFixedSize(QSize(400,500))
        self.leftContainer.setMinimumWidth(500)
        self.leftContainer.setMaximumWidth(500)
        #self.leftContainer.setMaximumHeight(500)
        #self.leftContainer.setMinimumHeight(500)
        self.leftContainer.setStyleSheet("QWidget {background-color: rgb(248,248,255);}")
        self.leftContainer.setLayout(self.leftContainerLayout)
        
        
        self.rightContainer = QWidget()
        self.rightContainer.setMinimumWidth(400)
        self.rightContainer.setMaximumWidth(400)
        #self.rightContainer.setMinimumHeight(500)
#        self.rightContainer.setFixedSize(QSize(400,500))
        self.rightContainerLayout = QVBoxLayout()
        self.rightContainer.setStyleSheet("QWidget {background-color: rgb(248,248,255);}")
        
        self.rightContainer.setLayout(self.rightContainerLayout)
        
        self.leftContainerFullLayout.addWidget(self.leftContainerLabelContainer)
        
        self.leftScrollArea = QScrollArea()
        
        self.leftScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.leftScrollArea.setFixedSize(QSize(500,500))
        self.leftScrollArea.setWidgetResizable(True)
        
        self.leftScrollArea.setWidget(self.leftContainer) 
        self.leftContainerFullLayout.addWidget(self.leftScrollArea)

        self.rightContainerFullLayout.addWidget(self.rightContainerLabelContainer)
        
        self.rightScrollArea = QScrollArea()
        self.rightScrollArea.setWidget(self.rightContainer)
        self.rightScrollArea.setFixedSize(QSize(400,500))
        self.rightScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.rightContainerFullLayout.addWidget(self.rightScrollArea)
        self.rightScrollArea.setWidgetResizable(True)
        
        self.middleLayout.addWidget(self.leftContainerFull)
        self.middleLayout.addWidget(self.rightContainerFull)
        
        self.middleContainer.setLayout(self.middleLayout)
        
        self.bottomContainer = QWidget()
        self.bottomLayout = QHBoxLayout()
        self.zLiftButton = QRadioButton("Vertical Offset (um)")
        #self.zLiftButton.setStyleSheet("QWidget {font-weight:bold;}")
        self.zLiftField = QLineEdit("0")
        self.zLiftField.setMaximumWidth(50)
        self.zLiftField.connect(self.zLiftField, SIGNAL("textChanged(const QString&)"), self.zLiftChanged)
        zliftfunction = lambda: self.liftTypeChanged("zlift")   
        self.zLiftButton.clicked.connect(zliftfunction)
        
        self.axialButton = QRadioButton("Axial Offset (um)") 
        axialfunction = lambda: self.liftTypeChanged("axial")   
        self.axialButton.clicked.connect(axialfunction)       

        self.axialField = QLineEdit("0")
        self.axialField.connect(self.axialField, SIGNAL("textChanged(const QString&)"), self.axialChanged)
        self.axialField.setMaximumWidth(50)
        
        
        self.noneButton = QRadioButton("No offset")
        nonefunction = lambda: self.liftTypeChanged(None)   
        self.noneButton.clicked.connect(nonefunction)  
        
        
        self.bottomLayout.addWidget(self.axialButton,0,Qt.AlignRight)
        self.bottomLayout.addWidget(self.axialField,0,Qt.AlignRight)
        self.bottomLayout.addWidget(self.zLiftButton,0,Qt.AlignRight)
        self.bottomLayout.addWidget(self.zLiftField,0,Qt.AlignRight)
        self.bottomLayout.addWidget(self.noneButton,0,Qt.AlignRight)
        
        self.bottomContainer.setLayout(self.bottomLayout)
        self.bottomLayout.setAlignment(Qt.AlignRight)

        self.mainLayout.addWidget(self.topContainer)
        self.mainLayout.addWidget(self.middleContainer)
        self.mainLayout.addWidget(self.bottomContainer)
        self.setLayout(self.mainLayout)        
        
        self.listItemLayouts = []
        self.radioButtons = []
        
        self.currentcommanditem = None
        self.currentlistitem = None
        
        self.storedCoordinates = None
        
    def keyPressEvent(self, event):
        self.parent.keyPressEvent(event)

    def axialChanged(self):
        if self.axialField.text() == None:
            self.axiallift = 0
        else:
            try:        
                self.axiallift = float(self.axialField.text())
            except:
                print "MUST ENTER A VALID FLOAT, AXIAL LIFT STILL EQUALS",self.axiallift   
    
    def zLiftChanged(self):
        if self.zLiftField.text() == None:
            self.zlift = 0
        else:
            try:        
                self.zlift = float(self.zLiftField.text())
            except:
                print "MUST ENTER A VALID FLOAT, ZLIFT STILL EQUALS",self.zlift   
    
    def liftTypeChanged(self,ltype):
        self.lifttype = ltype
        print self.lifttype
                
    #loads a grid from the grid points.
    def loadGrid(self):
        #clears out the current displayed data
        if self.currentunit == 0 and self.currentmanip == 0:
            self.clearOne(self.currentunit,self.currentmanip)
            
            stopparsing = False
            
            #get the center p oints from the grid
            gridcenterpoints = self.grid.getCenterPointsUM()
            
            for point in gridcenterpoints:
                #Creates new item for each grid center point.
                #x,y,z,t,n=1,index=None                
                newlistitemobject = self.listItemLayouts[0][0].addItem(point[0],point[1],0.0,0,1)
                            
                stopparsing = False
                #load the default list of grid commands
                listReader = csv.reader(open('C:\grid.cmm'),quoting=csv.QUOTE_NONNUMERIC)
                
                #parse the default grid commands.  this could possibly be a separate function
                while stopparsing == False:
                    try:
                        newcommanditem = listReader.next()
                        newcommanditem[2] = list(newcommanditem[2])
                        booleancontainer = []
                        for char in newcommanditem[2]:
                            if char == '0':
                                booleancontainer.append(False)
                            elif char == '1':
                                booleancontainer.append(True)
                        newlistitemobject.commandLayout.addItem(0,0,newcommanditem[1],newlistitemobject.commandLayout,booleancontainer)
                        #self.listItemLayouts[unit][device].containedItems[-1].commandLayout.addItem(unit,device,newcommanditem[1],parent,newcommanditem[0])                
                    except StopIteration:
                        stopparsing = True
        
        #If it's not the microscope that's selected the grid poitns will need to be converted over to
        #manipulator coordinates, if the manipulator is calibrated
        else:
            if self.parent.myarrows.deviceReadout[self.currentunit][self.currentmanip].MStageCoordinates != [None,None,None]:
                devreadout = self.parent.myarrows.deviceReadout[self.currentunit][self.currentmanip]
                gridcenterpoints = self.grid.getCenterPointsUM()
                for point in gridcenterpoints:
                    manippoint = devreadout.getMfromStageCoord(point[0],point[1])
                    print manippoint
                    newlistitemobject = self.listItemLayouts[self.currentunit][self.currentmanip].addItem(manippoint[0],manippoint[1],manippoint[2],0,1)
                    #grid1.cmm is the defualt grid commands for a manipulator                    
                    listReader = csv.reader(open('C:\grid1.cmm'),quoting=csv.QUOTE_NONNUMERIC)
                    stopparsing = False
                    while stopparsing == False:
                        try:
                            newcommanditem = listReader.next()
                            newcommanditem[2] = list(newcommanditem[2])
                            booleancontainer = []
                            for char in newcommanditem[2]:
                                if char == '0':
                                    booleancontainer.append(False)
                                elif char == '1':
                                    booleancontainer.append(True)
                            newlistitemobject.commandLayout.addItem(0,0,newcommanditem[1],newlistitemobject.commandLayout,booleancontainer)
                            #self.listItemLayouts[unit][device].containedItems[-1].commandLayout.addItem(unit,device,newcommanditem[1],parent,newcommanditem[0])                
                        except StopIteration:
                            stopparsing = True
            else:
                print "UNIT ",self.currentunit,"MANIP",self.currentmanip,"not calibrated"
    
    #load up the stored mouse points, using more or less the same method as loading the grid points
    def loadMousePoints(self):
        
        if self.currentunit == 0 and self.currentmanip == 0:
            self.clearOne(self.currentunit,self.currentmanip)       
    #        self.listItemLayouts[0][0].setShown(False)
    #        self.listItemLayouts[0][0].setShown(True)
            
            stopparsing = False
            
            mousepoints = self.storedCoordinates.getAllPointsDevice(0,0)
            
            for point in mousepoints:
                #x,y,z,t,n=1,index=None
                #newlistitemobject = self.listItemLayouts[0][0].addItem(point[0],point[1],0.0,0,1)
                newlistitemobject = self.listItemLayouts[0][0].addItem(point[0],point[1],point[2],0,1)
                print point            
                stopparsing = False
                listReader = csv.reader(open('C:\grid.cmm'),quoting=csv.QUOTE_NONNUMERIC)
                            
                while stopparsing == False:
                    try:
                        newcommanditem = listReader.next()
                        newcommanditem[2] = list(newcommanditem[2])
                        booleancontainer = []
                        for char in newcommanditem[2]:
                            if char == '0':
                                booleancontainer.append(False)
                            elif char == '1':
                                booleancontainer.append(True)
                        newlistitemobject.commandLayout.addItem(0,0,newcommanditem[1],newlistitemobject.commandLayout,booleancontainer)
                        #self.listItemLayouts[unit][device].containedItems[-1].commandLayout.addItem(unit,device,newcommanditem[1],parent,newcommanditem[0])                
                    except StopIteration:
                        stopparsing = True
        
        else:
            if self.parent.myarrows.deviceReadout[self.currentunit][self.currentmanip].MStageCoordinates != [None,None,None]:
                devreadout = self.parent.myarrows.deviceReadout[self.currentunit][self.currentmanip]
                mousepoints = self.storedCoordinates.getAllPointsDevice(0,0)
                Mmousepoints = []
                for point in mousepoints:
                    Mmousepoints.append(devreadout.getMfromStageCoord(point[0],point[1],point[2]))
                
                for manippoint in Mmousepoints:
                    #Do we want Z to be the current Z when selected or have the user choose it?
                    #manippoint = devreadout.getMfromStageCoord(point[0],point[1])
                    newlistitemobject = self.listItemLayouts[self.currentunit][self.currentmanip].addItem(manippoint[0],manippoint[1],manippoint[2],0,1)
                    listReader = csv.reader(open('C:\grid1.cmm'),quoting=csv.QUOTE_NONNUMERIC)
                    stopparsing = False
                    while stopparsing == False:
                        try:
                            newcommanditem = listReader.next()
                            newcommanditem[2] = list(newcommanditem[2])
                            booleancontainer = []
                            for char in newcommanditem[2]:
                                if char == '0':
                                    booleancontainer.append(False)
                                elif char == '1':
                                    booleancontainer.append(True)
                            newlistitemobject.commandLayout.addItem(0,0,newcommanditem[1],newlistitemobject.commandLayout,booleancontainer)
                            #self.listItemLayouts[unit][device].containedItems[-1].commandLayout.addItem(unit,device,newcommanditem[1],parent,newcommanditem[0])                
                        except StopIteration:
                            stopparsing = True
            else:
                print "UNIT ",self.currentunit,"MANIP",self.currentmanip,"not calibrated"


    #exports the list of points and commands to file    
    def saveList(self):
#now can only save for one device at a time
#        for unit in range (0,len(self.listItemLayouts)):
#            for device in range (0,2):
    
    
        unit = self.currentunit
        device = self.currentmanip
    
        filename = QFileDialog.getSaveFileName(self, 'Save File',"C:\\","*.csv")
        listWriter = csv.writer(open(filename,'wb'))
        
        listWriter.writerow([unit])
        listWriter.writerow([device])
        
        for listitem in self.listItemLayouts[unit][device].containedItems:
            ddenablednumeric = None
            if listitem.dropdownEnabled == True:
                ddenablednumeric = 1
            else:
                ddenablednumeric = 0
            listWriter.writerow([listitem.index]+[listitem.x]+[listitem.y]+[listitem.z]+[listitem.t]+[listitem.n]+[len(listitem.commandLayout.containedItems)]+[listitem.goto]+[listitem.times]+[ddenablednumeric])
            listWriter.writerow(["\""+listitem.logic+"\""])             
            for commanditem in listitem.commandLayout.containedItems:
                storebinvals = []
                for boolval in commanditem.binvals:
                    if boolval == True:
                        storebinvals.append(1)
                    else:
                        storebinvals.append(0)
                listWriter.writerow([commanditem.index]+[commanditem.t]+[storebinvals])
    
    #loads the list of commands from file
    def loadList(self):
        
#        self.clearAll()        
        
        stopparsing = False
        
#        for unit in range (0,len(self.listItemLayouts)):
#            for device in range (0,2):
        filename = QFileDialog.getOpenFileName(self, 'Open File', 'C:\\',"*.csv")        
        listReader = csv.reader(open(filename),quoting=csv.QUOTE_NONNUMERIC)
        
        unit = int(listReader.next()[0])
        device = int(listReader.next()[0])
        
        self.clearOne(unit,device)
        
        #listReader = csv.reader(open('C:\list'+str(unit)+str(device)+'.csv'),quoting=csv.QUOTE_NONNUMERIC)
        stopparsing = False
        while stopparsing == False:
            try:        
                newlistitem = listReader.next()
                print newlistitem
                newlistitem.append(listReader.next()[0][1:-1]) #appending command item
                if newlistitem != None:
                    #if len(newlistitem) == 6:
                    try:
                        ddenabled = None
                        if newlistitem[9] == 0:
                            ddenabled = False
                        else:
                            ddenabled = True
                        
                        for i in range(0,len(newlistitem)):
                            if newlistitem[i] == '':
                                print "BLANK FOUND"
                                newlistitem[i] = None
                        print newlistitem
                        if newlistitem[7] != None:
                            newlistitem[7] = int(newlistitem[7])

                        newlistitemobject = self.listItemLayouts[unit][device].addItem(newlistitem[1],newlistitem[2],newlistitem[3],newlistitem[4],int(newlistitem[5]),None,newlistitem[10],newlistitem[7],int(newlistitem[8]),ddenabled)
                        for i in range (0,int(newlistitem[6])):
                            newcommanditem = listReader.next()
                            newcommanditem[2] = list(newcommanditem[2])
                            booleancontainer = []
                            for char in newcommanditem[2]:
                                if char == '0':
                                    booleancontainer.append(False)
                                elif char == '1':
                                    booleancontainer.append(True)
                            newlistitemobject.commandLayout.addItem(unit,device,newcommanditem[1],newlistitemobject.commandLayout,booleancontainer)
                            #self.listItemLayouts[unit][device].containedItems[-1].commandLayout.addItem(unit,device,newcommanditem[1],parent,newcommanditem[0])
                    except StopIteration:
                        stopparsing = True
            except StopIteration:
                stopparsing = True


    def saveCommands(self):
        if self.currentcommanditem != None:
            filename = QFileDialog.getSaveFileName(self, 'Save File',"C:\\","*.cmm")
            listWriter = csv.writer(open(filename,'wb'))
            
            for item in self.currentcommanditem.layout().containedItems:
                storebinvals = []
                for boolval in item.binvals:
                    if boolval == True:
                        storebinvals.append(1)
                    else:
                        storebinvals.append(0)
                listWriter.writerow([item.index]+[item.t]+[storebinvals])
        
    def loadCommands(self):
        if self.currentcommanditem != None:
            filename = QFileDialog.getOpenFileName(self, 'Open File', 'C:\\',"*.cmm")        
            listReader = csv.reader(open(filename),quoting=csv.QUOTE_NONNUMERIC)
            stopparsing = False
            while stopparsing == False:
                try:
                    newcommanditem = listReader.next()
                    newcommanditem[2] = list(newcommanditem[2])
                    booleancontainer = []
                    for char in newcommanditem[2]:
                        if char == '0':
                            booleancontainer.append(False)
                        elif char == '1':
                            booleancontainer.append(True)
                    commlayout = self.currentcommanditem.layout()
                    commlayout.addItem(commlayout.unit,commlayout.manip,newcommanditem[1],commlayout,booleancontainer)
                except StopIteration:
                    stopparsing = True
    
    def clearOne(self,unit,manip):
        self.clearCommandWindow()
        self.listItemLayouts[unit][manip] = ListItemLayout(unit,manip,self)
        self.listItemLayouts[unit][manip].setAlignment(Qt.AlignTop)
        self.switchList(unit,manip)
    
    def clearAll(self):
        self.clearCommandWindow()
        self.listItemLayouts = []
        
        for unit in range (0,len(self.MSSInterface.MyUnit)):
            self.listItemLayouts.append([])
            for device in range (0,self.MSSInterface.portdata[unit][2]):
#            if i == 0:
#                self.listItemLayouts.append([None,ListItemLayout(i,1,self)])
#                self.listItemLayouts[i][1].setAlignment(Qt.AlignTop)
#            else:
                self.listItemLayouts[-1].append(ListItemLayout(unit,device,self))
                self.listItemLayouts[-1][-1].setAlignment(Qt.AlignTop) 
        self.switchList(0,0)
    
    def addNewListItem(self):
        self.listItemLayouts[self.currentlistitem.layout().unit][self.currentlistitem.layout().manip].addItem(0,0,0,0)
    
    def addNewCommandItem(self):
        if self.currentcommanditem != None:
            self.currentcommanditem.layout().addItem(self.currentcommanditem.layout().unit,self.currentcommanditem.layout().manip,0,self.currentcommanditem.layout().parent)
    def setStoredCoordinates(self,storedcoordinates):
        self.storedCoordinates = storedcoordinates
        

    def runAllCommands(self,listItem=None):
        if listItem != None:
            LI = listItem
        elif self.currentcommanditem != None:
            LI = self.currentcommanditem.layout().parent          
        else:
            return
        
        #if self.MSSInterface.getCoords(LI.unit,LI.manip) != [LI.x,LI.y,LI.z]:
        if LI.manip == 1 or LI.unit == 1:
            print "moving to", LI.unit,LI.manip,LI.x,LI.y,LI.z
            self.MSSInterface.waitForReady(LI.unit,LI.manip)
            self.MSSInterface.moveToWithoutWaiting(LI.unit,LI.manip,LI.x,LI.y,LI.z)
            self.MSSInterface.waitForReady(LI.unit,LI.manip)
            self.MSSInterface.askCoords(LI.unit,LI.manip)
        else:
            print "moving to", LI.unit,LI.manip,LI.x,LI.y
            self.MSSInterface.waitForReady(LI.unit,LI.manip)
            self.MSSInterface.moveToWithoutWaiting(LI.unit,LI.manip,LI.x,LI.y)
            self.MSSInterface.waitForReady(LI.unit,LI.manip)
            self.MSSInterface.askCoords(LI.unit,LI.manip)
#        else:
#            print "Already in position, sending binary"
        commandarray = []
        for commandItem in LI.commandContainer.layout().containedItems:
            commandarray.append([LI.unit,LI.manip,commandItem.t,commandItem.binvals])
        self.MSSInterface.sendBinary(commandarray)

    def runAllListItems(self):
        liftoffset = None        
        if self.lifttype == "zlift":
            liftoffset = self.zlift
        elif self.lifttype == "axial":
            if self.currentunit != 0 and self.currentmanip != 0:
                if self.MSSInterface.myarrows.deviceReadout[self.currentunit][self.currentmanip].axialMag == None:
                    print "AXIAL SELECTED, AXIAL NOT CALIBRATED FOR UNIT",self.currentunit,"MANIP",self.currentmanip,"CANCELING"
                    return
            liftoffset = self.axiallift
        else:
            liftoffset = 0
        
        
        self.MSSInterface.startDigitalInput()
        self.MSSInterface.runListItems(self.currentunit,self.currentmanip,self.listItemLayouts[self.currentunit][self.currentmanip].containedItems,self.lifttype,liftoffset)


#        for listitem in self.LIlayout.containedItems:
#            print "RUNNING LISTITEM",listitem.index,"X:",listitem.x,"Y:",listitem.y,"Z:",listitem.z,"T:",listitem.t,"n:",listitem.n
#            for i in range (0,listitem.n):
#                self.runAllCommands(listitem)
#                time.sleep(listitem.t*.001)
        
#        self.testListItem = ManipPatcherListItem(0,1,0,0,0,0,0,self)
#        self.leftContainerLayout.addWidget(self.testListItem)        
#        
#        self.testCommandItem = ManipPatcherCommandItem(0,1,0,0,self)
#        self.rightContainerLayout.addWidget(self.testCommandItem)
#        
#        self.testListItem2 = ManipPatcherListItem(0,1,0,0,0,0,0,self)
#        self.leftContainerLayout.addWidget(self.testListItem2)
#        self.testListItem2.indexButton.setStyleSheet("QWidget {font-weight:bold;background-color: rgb(0,191,255); color: rgb(248,248,255)}")
#        self.testListItem2.setStyleSheet("QWidget {background-color: rgb(248,248,255);}")
        
    def setInterface(self,interfacein,gridin):
        self.MSSInterface = interfacein
        self.grid = gridin
        for unit in range (0,len(self.MSSInterface.MyUnit)):
            self.listItemLayouts.append([])
            self.radioButtons.append([])
            for device in range (0,self.MSSInterface.portdata[unit][2]):
#            if i == 0:
#                self.listItemLayouts.append([None,ListItemLayout(i,1,self)])
#                self.listItemLayouts[i][1].setAlignment(Qt.AlignTop)
#                self.radioButtons.append(QRadioButton("Unit 0 Manip 1"))
#                self.radioButtons[0].clicked.connect(lambda: self.switchList(0,1)) 
#                self.radioButtons[0].setChecked(True)   
#            else:
                self.listItemLayouts[-1].append(ListItemLayout(unit,device,self))
                self.listItemLayouts[-1][-1].setAlignment(Qt.AlignTop)
                
                if unit == 0 and device == 0:
                    self.radioButtons[-1].append(QRadioButton("Unit "+str(unit)+" Microscope"))
                    self.radioButtons[-1][-1].clicked.connect(lambda: self.switchList(0,0))
                else:
                    self.radioButtons[-1].append(QRadioButton("Unit "+str(unit)+" Manip "+str(device)))
                    unitvalfixed = copy.deepcopy(unit)
                    devicevalfixed = copy.deepcopy(device)
                    print unitvalfixed
                    print devicevalfixed
                    #This helper function is necessary to assign the button connections using
                    #a loop.  Due to some Python intricacies, the connection isn't made until after
                    #this code executes, meaning that the final unit and manipulator values will
                    #be set as the connection for each value.  This function isolates the values
                    #into their own distinct definition...something like that, see
                    #http://stackoverflow.com/questions/4578861/connecting-slots-and-signals-in-pyqt4-in-a-loop
                    helper = lambda unitvalfixed,devicevalfixed: (lambda: self.switchList(unitvalfixed,devicevalfixed))
                    self.radioButtons[-1][-1].clicked.connect(helper(unitvalfixed,devicevalfixed))
    
        #self.leftContainer.setLayout(self.listItemLayouts[0][1])
#        self.listItemLayouts[0][1].addItem(0,0,0,0)
#        self.listItemLayouts[0][1].addItem(0,0,0,0)
#        self.listItemLayouts[0][1].addItem(0,0,0,0)
#        self.listItemLayouts[0][1].addItem(0,0,0,0)
#        self.listItemLayouts[0][1].addItem(0,0,0,0)
#        
#        self.listItemLayouts[0][1].addItem(0,0,0,0)
#        self.listItemLayouts[0][1].addItem(0,0,0,0)
#        self.listItemLayouts[0][1].addItem(0,0,0,0)
#        self.listItemLayouts[0][1].addItem(0,0,0,0)
#        self.listItemLayouts[0][1].addItem(0,0,0,0)        
        
        #Add the radio buttons sequentially to the top of the screen
        for unit in self.radioButtons:
            for button in unit:
                self.topLayout.addWidget(button)
        
        self.switchList(0,0)
    
            
    def resetRadioButtonStyle(self):
        for unit in self.radioButtons:
            for button in unit:
                button.setStyleSheet("QWidget {font-size:14pt;}")
    
    def switchList(self,unit,manip):
        print "unit",unit,"manip",manip
        self.resetRadioButtonStyle()
        self.radioButtons[unit][manip].setStyleSheet("QWidget {font-size:14pt; font-weight:bold; background-color: rgb(0,255,127); }" )
        self.radioButtons[unit][manip].setChecked(True)
        self.setListWindow(self.listItemLayouts[unit][manip])
        self.currentunit = unit
        self.currentmanip = manip
    
    def setCommandWindow(self,listitemin):
        if self.currentcommanditem != None:
            self.currentcommanditem.setShown(False)
        self.rightContainerLayout.addWidget(listitemin)
        listitemin.setShown(True)

        self.currentcommanditem = listitemin
        
    def setListWindow(self,listcontainerin):
        self.clearCommandWindow()
        if self.currentlistitem != None:
            self.currentlistitem.setShown(False)
        self.leftContainerLayout.addWidget(listcontainerin.ownContainer)
        listcontainerin.ownContainer.setShown(True)
        self.currentlistitem = listcontainerin.ownContainer
        
    def clearCommandWindow(self):
        if self.currentcommanditem != None:
            self.currentcommanditem.setShown(False)
            self.currentcommanditem = None
        
        
            
    
    
    
            

class ListItemLayout(QVBoxLayout):
    def __init__(self,unit,manip,parent):
        QVBoxLayout.__init__(self)
        self.ownContainer = QWidget()
        self.ownContainer.setLayout(self)
        self.unit = unit
        self.manip = manip
        self.parent = parent
        
        
        #self.highestIndex = 
        
        self.containedItems = []
        
        self.previousCommandItem = None
    
    def addItem(self,x,y,z,t,n=1,index=None,logic="",goto=None,times=1,ddenabled=False):
        
        if index == None:
            index = len(self.containedItems)
        print "n",n
        self.containedItems.insert(index,ManipPatcherListItem(self.unit,self.manip,index,x,y,z,t,n,logic,goto,times,ddenabled,self))
        self.insertWidget(index,self.containedItems[index])
        self.traceIndices()
        return self.containedItems[index]
    
    def updateItemsByGraphics():
        for i in range (0,len(self.containedItems)):
            self.containedItems[i].index = self.indexOf(containedItems[i])
            self.containedItems[i].indexButton.setText(" #"+str(self.containedItems[i].index)+" ")
            
    def moveListItemUp(self,item):
        thisindex = self.indexOf(item)
        #print "THISINDEX:",item,"AT CI INDEX:",self.containedItems[thisindex]
        if thisindex != 0:
            self.containedItems.pop(thisindex)
            self.containedItems.insert(thisindex-1,item)
            self.removeWidget(item)
            self.insertWidget(thisindex-1,item)
        #self.traceIndices()
        #self.updateGraphicsByItems()
        
    def moveListItemDown(self,item):
        thisindex = self.indexOf(item)
        #print "THISINDEX:",item,"AT CI INDEX:",self.containedItems[thisindex]
        if thisindex < len(self.containedItems):
            self.containedItems.pop(thisindex)
            self.containedItems.insert(thisindex+1,item)
            self.removeWidget(item)
            self.insertWidget(thisindex+1,item)
        #self.traceIndices()
        #self.updateGraphicsByItems()
        
    def traceIndices(self):
        pass
        #print "INDICES:"
        #for listitem in self.containedItems:
            #print listitem.index
    
#    def updateGraphicsByItems(self):
#        for i in range (0,self.count()):
#            if self.itemAt(i) != self.containedItems[i]:
#                self.removeWidget(self.itemAt(i).widget())
#                self.insertWidget(i,self.containedItems[i])

    def updateIndices(self):
        counter = 0
        
        
        for item in self.containedItems:       
            gotofound = False
            for otheritem in self.containedItems:
                if otheritem.index == item.goto:
                    gotofound = True
            if gotofound == False:
                item.goto = None
                item.dropdownGotoField.setText("")
        for item in self.containedItems:
            if item.index != counter:
                for otheritem in self.containedItems:
                    if otheritem.goto == item.index:
                        otheritem.goto = counter
                        otheritem.dropdownGotoField.setText(str(counter))
                
                item.index = counter
                item.indexButton.setText(" #"+str(item.index)+" ")
            counter +=1
    
    def deleteListItem(self,item):
        index = self.indexOf(item)
        #print "DELINDEX:",item,"AT CI INDEX:",self.containedItems[index]
        #print "CURRENTCOUNT:",self.count()
        self.removeWidget(item)
        self.containedItems[index].deleteLater()
        self.containedItems.pop(index)
        self.updateIndices()
        
        

class ManipPatcherListItem(QFrame):
    def __init__(self,unit,manip,index,x,y,z,t=0,n=1,logic="",goto=None,times=1,ddenabled=False,parent=None):
        QFrame.__init__(self)
        
        self.dropdownDisplayed = False
        self.dropdownEnabled = ddenabled
        
        self.setMaximumHeight(40)
        self.setMinimumHeight(40)        
        
        #one of these per list item
        self.commandContainer = QWidget()
        self.commandLayout = CommandItemLayout(unit,manip,self)        
#        self.commandLayout.addItem(unit,manip,0,self,0)
#        self.commandLayout.addItem(unit,manip,0,self,1)
#        self.commandLayout.addItem(unit,manip,0,self,2)
#        self.commandLayout.addItem(unit,manip,0,self,3)
        self.commandContainer.setLayout(self.commandLayout)
        
        self.setStyleSheet("QWidget {background-color: rgb(230,230,230);}")
        self.unit = unit
        self.x = x
        self.y = y
        self.z = z
        self.n = n
        self.currentcoordinateitem = None
        self.t = t
        self.parent = parent
        self.manip = manip
        self.index = index
        self.goto = goto
        
        self.times = times
        self.logic = logic
        if self.logic == None:
            self.logic = ""

        self.wholeLayout = QVBoxLayout()
        self.wholeLayout.setMargin(0)
        self.wholeLayout.setSpacing(0)
        
        self.itemContainer = QWidget()        
        self.itemLayout = QHBoxLayout()    
        
        #self.itemLayout.setSpacing(0)
        self.indexButton = QPushButton()
        self.indexButton.setText(" #"+str(index)+" ")
        self.indexButton.setMaximumWidth(35)
        self.indexButton.setMinimumWidth(35)
        
        colors = []        
        
        colors = parent.parent.colorlist[random.randint(0,len(parent.parent.colorlist))-1]
        
        self.indexButton.setStyleSheet("QWidget {font-weight:bold;background-color: rgb("+str(colors[0])+","+str(colors[1])+","+str(colors[2])+"); color: rgb(248,248,255)}")
        self.indexButton.connect(self.indexButton, SIGNAL("clicked()"), self.selectThisItem)
        
        self.xLabel = QLabel("X:")
        self.xLabel.setStyleSheet("QWidget {font-weight:bold;}")
        self.xValue = QLineEdit(str(self.x))
        self.xValue.connect(self.xValue, SIGNAL("textChanged(const QString&)"), self.xChanged)
        self.xValue.setStyleSheet("QWidget {background-color: rgb(248,248,255)}")
        self.xValue.setCursorPosition (0)
        self.yLabel = QLabel("Y:")
        self.yLabel.setStyleSheet("QWidget {font-weight:bold;}")
        self.yValue = QLineEdit(str(self.y))
        self.yValue.connect(self.yValue, SIGNAL("textChanged(const QString&)"), self.yChanged)
        self.yValue.setStyleSheet("QWidget {background-color: rgb(248,248,255)}")
        self.yValue.setCursorPosition (0)
        self.zLabel = QLabel("Z:")
        self.zLabel.setStyleSheet("QWidget {font-weight:bold;}")
        self.zValue = QLineEdit(str(self.z))
        self.zValue.connect(self.zValue, SIGNAL("textChanged(const QString&)"), self.zChanged)
        self.zValue.setStyleSheet("QWidget {background-color: rgb(248,248,255)}")
        self.zValue.setCursorPosition (0)
        self.coordButton = QPushButton("xyz")
        self.coordButton.setMaximumWidth(25)
        #self.coordButton.connect(self.coordButton, SIGNAL("clicked()"), self.coordpressed)      
        
        #self.coordButton.setContextMenuPolicy(Qt.CustomContextMenu)
        self.coordButton.connect(self.coordButton, SIGNAL('clicked()'), self.coordbuttclicked)

        # create context menu
        self.popMenu = QMenu(self)
        
        self.timeLabel = QLabel("T:")
        self.timeLabel.setStyleSheet("QWidget {font-weight:bold;}")
        self.timeValue = QLineEdit(str(t))
        self.timeValue.setMaximumWidth(40)
        self.timeValue.setStyleSheet("QWidget {background-color: rgb(248,248,255)}")
        self.timeValue.connect(self.timeValue, SIGNAL("textChanged(const QString&)"), self.timeChanged)
        
        self.nLabel = QLabel("n:")
        self.nLabel.setStyleSheet("QWidget {font-weight:bold;}")
        self.nValue = QLineEdit(str(n))
        self.nValue.setMaximumWidth(40)
        self.nValue.setStyleSheet("QWidget {background-color: rgb(248,248,255)}")
        self.nValue.connect(self.nValue, SIGNAL("textChanged(const QString&)"), self.nChanged)
        
        self.delButton = QPushButton()
        self.delButton.setText("X")
        self.delButton.setStyleSheet("QWidget {font-weight:bold; background-color: rgb(220,20,60); color:rgb(248,248,255);}")
        self.delButton.setMaximumWidth(25)
        self.delButton.connect(self.delButton, SIGNAL("clicked()"), self.deleteSelf)
        self.newButton = QPushButton()
        self.newButton.setText("+")
        self.newButton.setMaximumWidth(25)
        self.newButton.setStyleSheet("QWidget {font-weight:bold; background-color: rgb(0,255,127); color:rgb(248,248,255);}")
        self.delButton.connect(self.newButton, SIGNAL("clicked()"), self.newItem)        
        
        self.arrowsContainer = QWidget()
        self.arrowsLayout = QVBoxLayout()
        self.arrowsLayout.setSpacing(1)
        self.arrowsLayout.setMargin(1)
        self.upArrow = QPushButton(u'\u25B2')
        self.downArrow = QPushButton(u'\u25BC')
        self.upArrow.setMinimumHeight(10)
        self.upArrow.setMaximumWidth(12)
        self.upArrow.setStyleSheet("QWidget {background-color: rgb(32,178,170); color:rgb(248,248,255);}")
        self.upArrow.connect(self.upArrow, SIGNAL("clicked()"), self.moveUp)        
        self.downArrow.setMinimumHeight(10)
        self.downArrow.setMaximumWidth(12)
        self.downArrow.setStyleSheet("QWidget {background-color: rgb(32,178,170); color:rgb(248,248,255);}")
        self.downArrow.connect(self.downArrow, SIGNAL("clicked()"), self.moveDown)          
        
        self.arrowsLayout.addWidget(self.upArrow)
        self.arrowsLayout.addWidget(self.downArrow)
        self.arrowsContainer.setLayout(self.arrowsLayout)        
        
        self.dropdownButton = QPushButton(u'\u25BC')
        self.dropdownButton.setMaximumWidth(15)
        self.dropdownButton.setMaximumHeight(17)
        self.dropdownButton.setStyleSheet("QWidget {background-color: rgb(0,0,0); color:rgb(248,248,255);}")
        self.dropdownButton.connect(self.dropdownButton, SIGNAL("clicked()"), self.dropdownClicked)        
        
        self.dropdownContainer = QWidget()
        self.dropdownLayout = QHBoxLayout()
        self.dropdownLogicLabel = QLabel("Logic:")
        self.dropdownLogicLabel.setStyleSheet("QWidget {font-weight:bold;}")
        self.dropdownLogicField = QLineEdit(self.logic)   
        self.dropdownLogicField.connect(self.dropdownLogicField, SIGNAL("textChanged(const QString&)"), self.logicChanged)
        self.dropdownLogicField.setStyleSheet("QWidget {background-color:rgb(248,248,255);font-family:Courier,sans-serif;}")#font-size:11pt;
        self.dropdownGotoLabel = QLabel("Goto:")
        self.dropdownGotoLabel.setStyleSheet("QWidget {font-weight:bold;}")
        self.dropdownGotoField = QLineEdit(str(self.goto))  
        self.dropdownGotoField.setMaximumWidth(25)
        self.dropdownGotoField.connect(self.dropdownGotoField, SIGNAL("textChanged(const QString&)"), self.gotoChanged)
        self.dropdownGotoField.setStyleSheet("QWidget {background-color:rgb(248,248,255);}")
        self.dropdownTimesLabel = QLabel("Times:")
        self.dropdownTimesLabel.setStyleSheet("QWidget {font-weight:bold;}")
        self.dropdownTimesField = QLineEdit(str(self.times))
        self.dropdownTimesField.connect(self.dropdownTimesField, SIGNAL("textChanged(const QString&)"), self.timesChanged)
        self.dropdownTimesField.setMaximumWidth(25)
        self.dropdownTimesField.setStyleSheet("QWidget {background-color:rgb(248,248,255);}")
        self.dropdownEnabledButton = QPushButton("Off")
        self.dropdownEnabledButton.setMaximumWidth(25)
        self.dropdownEnabledButton.setMinimumWidth(25)
        self.dropdownEnabledButton.setStyleSheet("QWidget {font-weight:bold; background-color: rgb(205,51,51); color:rgb(248,248,255);}")
        self.dropdownEnabledButton.connect(self.dropdownEnabledButton, SIGNAL("clicked()"), self.dropdownEnabledClicked)        
        
        self.dropdownLayout.addWidget(self.dropdownLogicLabel)
        self.dropdownLayout.addWidget(self.dropdownLogicField)
        self.dropdownLayout.addWidget(self.dropdownGotoLabel)
        self.dropdownLayout.addWidget(self.dropdownGotoField)
        self.dropdownLayout.addWidget(self.dropdownTimesLabel)
        self.dropdownLayout.addWidget(self.dropdownTimesField)
        self.dropdownLayout.addWidget(self.dropdownEnabledButton)
        self.dropdownContainer.setLayout(self.dropdownLayout)
        
        
        self.itemLayout.addWidget(self.indexButton)
        self.itemLayout.addWidget(self.xLabel)
        self.itemLayout.addWidget(self.xValue)
        self.itemLayout.addWidget(self.yLabel)
        self.itemLayout.addWidget(self.yValue)
        self.itemLayout.addWidget(self.zLabel)
        self.itemLayout.addWidget(self.zValue)
        self.itemLayout.addWidget(self.coordButton)
        self.itemLayout.addWidget(self.timeLabel)
        self.itemLayout.addWidget(self.timeValue)
        self.itemLayout.addWidget(self.nLabel)
        self.itemLayout.addWidget(self.nValue)
        self.itemLayout.addWidget(self.delButton)
        self.itemLayout.addWidget(self.newButton)
        self.itemLayout.addWidget(self.arrowsContainer)
        self.itemLayout.addWidget(self.dropdownButton)
        
        self.itemContainer.setMinimumHeight(40)
        self.itemContainer.setMaximumHeight(40)
        self.itemContainer.setLayout(self.itemLayout)
        
        self.wholeLayout.addWidget(self.itemContainer)
        self.wholeLayout.addWidget(self.dropdownContainer)        
        
        self.dropdownContainer.setShown(False)
        self.dropdownContainer.setMaximumHeight(1)
        
        if self.dropdownEnabled == True:
            self.dropdownEnabledButton.setText("On")
            self.dropdownEnabledButton.setStyleSheet("QWidget {font-weight:bold; background-color: rgb(0,205,102); color:rgb(248,248,255);}")
        
        self.setLayout(self.wholeLayout)
        
    def dropdownEnabledClicked(self):
        if self.dropdownEnabled == True:
            self.dropdownEnabled = False
            self.dropdownEnabledButton.setText("Off")
            self.dropdownEnabledButton.setStyleSheet("QWidget {font-weight:bold; background-color: rgb(205,51,51); color:rgb(248,248,255);}")#220,20,60
        else:
            self.dropdownEnabled = True
            self.dropdownEnabledButton.setText("On")
            self.dropdownEnabledButton.setStyleSheet("QWidget {font-weight:bold; background-color: rgb(0,205,102); color:rgb(248,248,255);}")#0,255,127
    
    def dropdownClicked(self):
        if self.dropdownDisplayed == False:
            self.dropdownContainer.setShown(True)
            self.dropdownContainer.setMinimumHeight(40)
            self.dropdownContainer.setMaximumHeight(40)
            self.dropdownButton.setText(u'\u25B2')
            self.setMinimumHeight(80)
            self.setMaximumHeight(80)
            self.dropdownDisplayed = True
        else:
            self.dropdownContainer.setShown(False)
            self.dropdownContainer.setMinimumHeight(1)
            self.dropdownContainer.setMaximumHeight(1)
            self.dropdownButton.setText(u'\u25BC')
            self.setMinimumHeight(40)
            self.setMaximumHeight(40)
            self.dropdownDisplayed = False
            
    def deleteSelf(self):
        self.parent.deleteListItem(self)
    
    def moveUp(self):
        self.parent.moveListItemUp(self)
        self.parent.updateIndices()
    
    def moveDown(self):
        self.parent.moveListItemDown(self)
        self.parent.updateIndices()
        
    def newItem(self):
        self.parent.addItem(0,0,0,0,1,self.parent.indexOf(self)+1)
        self.parent.updateIndices()
        
    def selectThisItem(self):
        self.parent.parent.setCommandWindow(self.commandContainer)

    def coordbuttclicked(self):
        
        self.popMenu = QMenu(self)
        
        counter = 0
        for storeditem in self.parent.parent.storedCoordinates.coordinatebox[self.unit][self.manip].containedItems:            
            newitem = QAction(str(counter)+". "+storeditem.toString(), self)
            newitem.setData(counter)
            self.popMenu.addAction(newitem)
            
            self.connect(newitem, SIGNAL("triggered()"), lambda newitem=newitem: self.chooseItem(newitem))
            counter +=1
            
        if counter == 0:
            self.popMenu.addAction(QAction('None stored',self))
            
        # show context menu
        point = QCursor.pos()
        self.popMenu.exec_(point)
        #self.popMenu.exec_(self.coordButton.mapToGlobal(point))
    
    def chooseItem(self,item):
        counter = item.data().toInt()[0]
        self.currentcoordinateitem = self.parent.parent.storedCoordinates.coordinatebox[self.unit][self.manip].containedItems[counter]
        self.x = self.currentcoordinateitem.x
        self.y = self.currentcoordinateitem.y
        self.z = self.currentcoordinateitem.z
        self.xValue.setText(str(self.x))
        self.yValue.setText(str(self.y))
        self.zValue.setText(str(self.z))
    
    def timeChanged(self):
        self.t = float(self.timeValue.text())
        
    def xChanged(self):
        #print "float",self.timeValue.text().toFloat()
        self.x = float(self.xValue.text())
        print "x now equals",self.x        
    
    def yChanged(self):
        #print "float",self.timeValue.text().toFloat()
        self.y = float(self.yValue.text())
        print "y now equals",self.y      
        
    def zChanged(self):
        #print "float",self.timeValue.text().toFloat()
        self.z = float(self.zValue.text())
        print "z now equals",self.z      
        
        
    def nChanged(self):
        #print "float",self.timeValue.text().toFloat()
        self.n = int(self.nValue.text())
        print "n now equals",self.n
        
    def logicChanged(self):
        self.logic = str(self.dropdownLogicField.text())
        print "logic now equals",self.logic
        
    def timesChanged(self):
        self.times = int(self.dropdownTimesField.text())
        
    def gotoChanged(self):
        if self.dropdownGotoField.text() == "":
            self.goto = None
        else:
            self.goto = int(self.dropdownGotoField.text())

class CommandItemLayout(QVBoxLayout):
    def __init__(self,unit,manip,parent):
        QVBoxLayout.__init__(self)
        self.setAlignment(Qt.AlignTop)
        self.containedItems = []
        
        self.unit = unit
        self.manip = manip
        self.parent = parent
        
        
        
        
    def addItem(self,unit,manip,t,parent,binary=None,index=None):
        if index == None:
            index = len(self.containedItems)
        self.containedItems.insert(index,ManipPatcherCommandItem(unit,manip,t,self,index,binary))
        self.insertWidget(index,self.containedItems[index])
#        self.traceIndices()
            
    def moveCommandItemUp(self,item):
        thisindex = self.indexOf(item)
        #print "THISINDEX:",item,"AT CI INDEX:",self.containedItems[thisindex]
        if thisindex != 0:
            self.containedItems.pop(thisindex)
            self.containedItems.insert(thisindex-1,item)
            self.removeWidget(item)
            self.insertWidget(thisindex-1,item)
        #self.traceIndices()
        #self.updateGraphicsByItems()
        
    def moveCommandItemDown(self,item):
        thisindex = self.indexOf(item)
        #print "THISINDEX:",item,"AT CI INDEX:",self.containedItems[thisindex]
        if thisindex < len(self.containedItems):
            self.containedItems.pop(thisindex)
            self.containedItems.insert(thisindex+1,item)
            self.removeWidget(item)
            self.insertWidget(thisindex+1,item)
        #self.traceIndices()
        #self.updateGraphicsByItems()
        
#    def traceIndices(self):
#        print "INDICES:"
#        for commanditem in self.containedItems:
#            print commanditem.index
#    
#    def updateGraphicsByItems(self):
#        for i in range (0,self.count()):
#            if self.itemAt(i) != self.containedItems[i]:
#                self.removeWidget(self.itemAt(i).widget())
#                self.insertWidget(i,self.containedItems[i])
    
    def deleteCommandItem(self,item):
        index = self.indexOf(item)
        print "DELINDEX:",item,"AT CI INDEX:",self.containedItems[index]
        print "CURRENTCOUNT:",self.count()
        self.removeWidget(item)
        self.containedItems[index].deleteLater()
        self.containedItems.pop(index)
        

        
class ManipPatcherCommandItem(QFrame):
    def __init__(self,unit,manip,t,parent,index=None, binary=None):
        QFrame.__init__(self)
        self.setMaximumHeight(40)
        self.setMinimumHeight(40)
        self.setStyleSheet("QWidget {background-color: rgb(230,230,230);}")
        self.unit = unit
        self.t = t
        self.parent = parent
        self.manip = manip
        self.index = index
        self.itemLayout = QHBoxLayout()
        self.itemLayout.setSpacing(1)
        
        self.indexButton = QPushButton()
        self.indexButton.setText(" #"+str(index)+" ")
        self.indexButton.setMaximumWidth(40)
        self.indexButton.setStyleSheet("QWidget {font-weight:bold;background-color: rgb(79,148,205); color: rgb(248,248,255)}")
        self.timeLabel = QLabel(" T:")
        self.timeLabel.setStyleSheet("QWidget {font-weight:bold;}")
        self.timeValue = QLineEdit(str(t))
        self.timeValue.setMaximumWidth(40)
        self.timeValue.setStyleSheet("QWidget {background-color: rgb(248,248,255)}")
        self.timeValue.connect(self.timeValue, SIGNAL("textChanged(const QString&)"), self.timeChanged) 
        self.delButton = QPushButton()
        self.delButton.setText("X")
        self.delButton.setStyleSheet("QWidget {font-weight:bold; background-color: rgb(220,20,60); color:rgb(248,248,255);}")
        self.delButton.setMaximumWidth(25)
        self.delButton.connect(self.delButton, SIGNAL("clicked()"), self.deleteSelf) 
        self.newButton = QPushButton()
        self.newButton.setText("+")
        self.newButton.setMaximumWidth(25)
        self.newButton.connect(self.newButton, SIGNAL("clicked()"), self.newItem) 
        self.newButton.setStyleSheet("QWidget {font-weight:bold; background-color: rgb(0,255,127); color:rgb(248,248,255);}")
        
        self.itemLayout.addWidget(self.indexButton)
        
        self.binbuttons = []
        self.binbuttons.append(QPushButton())        
        self.binbuttons[0].clicked.connect(lambda: self.binpressed(0))      
        self.binbuttons.append(QPushButton())        
        self.binbuttons[1].clicked.connect(lambda: self.binpressed(1))   
        self.binbuttons.append(QPushButton())        
        self.binbuttons[2].clicked.connect(lambda: self.binpressed(2))   
        self.binbuttons.append(QPushButton())        
        self.binbuttons[3].clicked.connect(lambda: self.binpressed(3))   
        self.binbuttons.append(QPushButton())        
        self.binbuttons[4].clicked.connect(lambda: self.binpressed(4))   
        self.binbuttons.append(QPushButton())        
        self.binbuttons[5].clicked.connect(lambda: self.binpressed(5))   
        self.binbuttons.append(QPushButton())        
        self.binbuttons[6].clicked.connect(lambda: self.binpressed(6))   
        self.binbuttons.append(QPushButton())        
        self.binbuttons[7].clicked.connect(lambda: self.binpressed(7))   
        
        for i in range (0,8):
            self.binbuttons.append(QPushButton())
            self.binbuttons[i].setStyleSheet("QWidget {font-weight:bold; color: rgb(248,248,255); background-color: rgb(0,0,0);}")
            self.binbuttons[i].setText("0");
            self.binbuttons[i].setMaximumWidth(13)
            self.binbuttons[i].setContentsMargins(0,0,0,0)
            
            self.itemLayout.addWidget(self.binbuttons[i])
        
        self.binvals = [False,False,False,False,False,False,False,False]
        
        if binary != None:
            self.binvals = binary
            bincounter = 0
            for boolval in binary:
                if self.binvals[bincounter] == True:
                    self.binbuttons[bincounter].setStyleSheet("QWidget {font-weight:bold; color: rgb(0,0,0); background-color: rgb(248,248,255);}")
                    self.binbuttons[bincounter].setText("1")
                bincounter +=1
                    
        self.arrowsContainer = QWidget()
        self.arrowsLayout = QVBoxLayout()
        self.arrowsLayout.setSpacing(1)
        self.arrowsLayout.setMargin(1)
        self.upArrow = QPushButton(u'\u25B2')
        self.downArrow = QPushButton(u'\u25BC')
        self.upArrow.setMinimumHeight(10)
        self.upArrow.setMaximumWidth(12)
        self.upArrow.setStyleSheet("QWidget {background-color: rgb(32,178,170); color:rgb(248,248,255);}")
        self.upArrow.connect(self.upArrow, SIGNAL("clicked()"), self.moveUp)        
        self.downArrow.setMinimumHeight(10)
        self.downArrow.setMaximumWidth(12)
        self.downArrow.setStyleSheet("QWidget {background-color: rgb(32,178,170); color:rgb(248,248,255);}")
        self.downArrow.connect(self.downArrow, SIGNAL("clicked()"), self.moveDown)          
        
        self.arrowsLayout.addWidget(self.upArrow)
        self.arrowsLayout.addWidget(self.downArrow)
        self.arrowsContainer.setLayout(self.arrowsLayout)
        
        self.itemLayout.addWidget(self.timeLabel)
        self.itemLayout.addWidget(self.timeValue)
        self.itemLayout.addWidget(self.delButton)
        self.itemLayout.addWidget(self.newButton)
        self.itemLayout.addWidget(self.arrowsContainer)
        
        self.setLayout(self.itemLayout)
        
    def timeChanged(self):
        self.t = float(self.timeValue.text())
    
    def binpressed(self,button):
        if (self.binvals[button] == False):
            self.binbuttons[button].setText("1")
            self.binbuttons[button].setStyleSheet("QWidget {font-weight:bold; color: rgb(0,0,0); background-color: rgb(248,248,255);}")
            self.binvals[button] = True
        else:
            self.binbuttons[button].setText("0")
            self.binbuttons[button].setStyleSheet("QWidget {font-weight:bold; color: rgb(248,248,255); background-color: rgb(0,0,0);}")
            self.binvals[button] = False
            
    def deleteSelf(self):
        self.parent.deleteCommandItem(self)
    
    def moveUp(self):
        self.parent.moveCommandItemUp(self)
    
    def moveDown(self):
        self.parent.moveCommandItemDown(self)
        
    def newItem(self):
        self.parent.addItem(0,0,0,0,[False,False,False,False,False,False,False,False],self.parent.indexOf(self)+1)
        
    def selectThisItem(self):
        self.parent.parent.setCommandWindow(self.commandContainer)
            
            
            