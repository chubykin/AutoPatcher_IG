# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 13:51:22 2012


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
from PyQt4.QtCore import *
from PyQt4.QtGui import *


#This class is model, view, and controller for storing coordinates from the screen.
#CoordinateBoxes are created for each manipulator of each unit, and CoordinateItems
#are created for each stored set of coordinates for that particular unit.

#CoordinateItems contain both their data and their graphical components.

class StoredCoordinates(QDialog):
    def __init__(self,interface,parent):
        super(StoredCoordinates, self).__init__(parent)
    
        self.setGeometry(980,600,300,300)        
        
        self.interface = interface
        self.parent = parent
        self.coordinatebox = []
        self.unitLayouts = []
        self.unitContainers = []
        
        self.mainLayout = QHBoxLayout()
        self.setLayout(self.mainLayout)
        
        self.setMaximumWidth(400)
        self.setWindowTitle('Memory Postitions')
    
        #Coordinates are stored as objects with 
        counter = 0
        
        for unit in self.interface.MyUnit: #for each unit that we're using
            self.unitContainers.append(QWidget()) #create a container
            self.unitLayouts.append(QVBoxLayout()) #store its layout (vertical)
            self.unitContainers[counter].setLayout(self.unitLayouts[counter]) 
            self.coordinatebox.append([]) #get ready to make a coordinatebox
            for i in range (0,interface.portdata[unit.unitID][2]): #for each manipulator this unit has
                self.coordinatebox[-1].append(CoordinateBox(counter,i,self)) #add coordinatebox
                self.unitLayouts[counter].addWidget(self.coordinatebox[-1][-1]) #add to unit layout
            self.mainLayout.addWidget(self.unitContainers[counter]) #add all of the above to main layout
            counter +=1
            
        self.updateIndices()
            
#        self.addItem(0,0,0,0,0)
#        self.addItem(0,1,0,0,0)
#        self.addItem(1,0,0,0,0)
#        self.addItem(1,1,0,0,0)
    def keyPressEvent(self, event):
        self.parent.keyPressEvent(event) 
    #just calls the function to create a new CoordinateItem in the appropriate
    #coordinatebox
    def addItem(self,unit,manip,x,y,z):
        x = round(x,5)
        y = round(y,5)
        z = round(z,5)
        self.coordinatebox[unit][manip].addItem(x,y,z)
        self.updateIndices()
        
    #returns all points from all layouts as an array, ordered by unit and manip i hope
    #apparently only orders by unit?  i don't think this function is ever used.
    def getAllPoints(self):
        coordinatearray = []
        for layout in self.unitLayouts:
            coordinatearray.append([])
            for unit in self.coordinatebox:
                for cbox in unit:
                    for item in cbox.containedItems:
                        coordinatearray[-1].append([item.x,item.y,item.z])
        return coordinatearray
        
    #this is used; clicking "load mouse points" or "load stored coordinates" or whatever on the 
    #system for queueing up moves and binary commands uses this to get the stored coordinates for a device.
    def getAllPointsDevice(self,unit,manip):
        coordinatearray = []
        for item in self.coordinatebox[unit][manip].containedItems:
            coordinatearray.append([item.x,item.y,item.z])
        return coordinatearray
        
    #if an item is added, inserted, or removed, update the indices of the items such that they
    #reflect their position in the list for that particular device.
    def updateIndices(self):
        for unit in self.coordinatebox:
            for manip in unit:
                counter = 0
                for item in manip.containedItems:
                    item.setIndex(counter)
                    counter += 1

#just contains the devices for a particular unit, pretty straightforward.
#it keeps all of its contained items in the containedItems list.  This is the master reference
#for what a coordinate's index is.  The order in the layout should always be kept the same as the order of
#the list, and vice versa.
class CoordinateBox(QWidget):
    def __init__(self,unit,manip,parent):
        QWidget.__init__(self)
        self.unit = unit
        self.manip = manip        
        self.parent = parent
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.title = QLabel("Unit "+str(unit)+" Manip "+str(manip))
        self.title.setStyleSheet("QWidget {font-weight:bold; font-size:13pt; background-color: rgb(0,255,127);}")
        self.title.setMaximumHeight(30)        
        self.layout.addWidget(self.title)
        self.containedItems = []
    
    def addItem(self,x,y,z):
        self.containedItems.append(CoordinateItem(self.unit,self.manip,x,y,z,self))
        self.layout.addWidget(self.containedItems[-1])
        
    def delItem(self,item):
        index = self.layout.indexOf(item)
        #print "DELINDEX:",item,"AT CI INDEX:",self.containedItems[index]
        #print "CURRENTCOUNT:",self.count()
        self.layout.removeWidget(item)
        self.containedItems[index-1].deleteLater()
        self.containedItems.pop(index-1)
        self.parent.updateIndices()
    
#contians both the data and graphical stuff for one stored coordinate items.
#also allows you to manually edit the coordinate values; see the xchanged, ychanged, zchanged stuff.
class CoordinateItem(QFrame):
    def __init__(self,unit,manip,x,y,z,parent):
        QFrame.__init__(self)        
        
        self.parent = parent
        self.unit = unit
        self.manip = manip
        self.x = x
        self.y = y
        self.z = z
        self.currentindex = None
        
        self.setMaximumHeight(30) 
        
        self.layout = QHBoxLayout()
        self.layout.setMargin(5)
        self.setLayout(self.layout)
        
        self.setStyleSheet("QWidget {background-color: rgb(255,255,255);}")        
        
        self.xlabel = QLabel("X:")
        self.xval = QLineEdit(str(self.x))
        self.xval.setMinimumWidth(65)
        self.xval.connect(self.xval, SIGNAL("textChanged(const QString&)"), self.xchanged)
        self.ylabel = QLabel("Y:")
        self.yval = QLineEdit(str(self.y))
        self.yval.setMinimumWidth(65)
        self.yval.connect(self.xval, SIGNAL("textChanged(const QString&)"), self.ychanged)
        self.zlabel = QLabel("Z:")
        self.zval = QLineEdit(str(self.z))
        self.zval.setMinimumWidth(65)
        self.zval.connect(self.xval, SIGNAL("textChanged(const QString&)"), self.zchanged)
        
        self.xlabel.setStyleSheet("QWidget {font-weight:bold;}")
        self.ylabel.setStyleSheet("QWidget {font-weight:bold;}")
        self.zlabel.setStyleSheet("QWidget {font-weight:bold;}")
        
        self.indexbutton = QPushButton("")
        self.indexbutton.setMaximumWidth(30)
        self.indexbutton.setStyleSheet("QWidget {font-weight:bold;background-color: rgb(79,148,205); color: rgb(248,248,255);}")
        
        self.gotobutton = QPushButton("Goto")
        self.gotobutton.setMaximumWidth(35)
        self.gotobutton.setStyleSheet("QWidget {font-weight:bold;background-color: rgb(79,148,205); color: rgb(248,248,255);}")     
        self.gotobutton.connect(self.gotobutton, SIGNAL("clicked()"), self.goto)        
        self.delbutton = QPushButton("X")
        self.delbutton.setMaximumWidth(15)
        self.delbutton.setStyleSheet("QWidget {font-weight:bold; background-color: rgb(220,20,60); color:rgb(248,248,255);}")
        self.delbutton.connect(self.delbutton, SIGNAL("clicked()"), self.delete) 
        self.layout.addWidget(self.indexbutton)         
        self.layout.addWidget(self.xlabel)
        self.layout.addWidget(self.xval)
        self.layout.addWidget(self.ylabel)
        self.layout.addWidget(self.yval)
        self.layout.addWidget(self.zlabel)
        self.layout.addWidget(self.zval)
        self.layout.addWidget(self.delbutton)
        self.layout.addWidget(self.gotobutton)
    
    def setIndex(self,indexin):
        self.currentindex = indexin
        self.indexbutton.setText("#"+str(indexin))
    
    def goto(self):
        self.parent.parent.interface.waitForReady(self.unit,self.manip)
        self.parent.parent.interface.moveTo(self.unit,self.manip,self.x,self.y,self.z)
        self.parent.parent.interface.waitForReady(self.unit,self.manip)
        self.parent.parent.interface.askCoords(self.unit,self.manip)
    def delete(self):
        self.parent.delItem(self)
    def toString(self):
        return "X: "+str(self.x)+" Y: "+str(self.y)+" Z: "+str(self.z)
    def xchanged(self):
        try:
            self.x = float(self.xval.text())
        except:
            print "BAD VALUE PLEASE ENTER A VALID FLOAT"
    def ychanged(self):
        try:
            self.y = float(self.yval.text())
        except:
            print "BAD VALUE PLEASE ENTER A VALID FLOAT"
    def zchanged(self):
        try:
            self.z = float(self.zval.text())
        except:
            print "BAD VALUE PLEASE ENTER A VALID FLOAT"
        
        
        