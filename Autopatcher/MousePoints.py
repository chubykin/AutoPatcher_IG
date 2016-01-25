# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 19:32:54 2012

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

#from PyQt4.QtCore import *
#from PyQt4.QtGui import *
import math
import copy

pixelsperum = 6.0

#REMEMBERS MOUSE POINTS THAT THE USER CAN CLICK.  NOT REALLY COMPLETED

#I don't think that this class is used, it's from way back when only the grid was completed

class MousePoints():
    def __init__(self):
        self.mousepoints = []
    def getPoints(self):
        return self.mousepoints
    
    def addPoint(self,mousepoint):
        print("*********************ADDING MOUSE POINT")
        self.mousepoints.append([mousepoint.x(),mousepoint.y()])
        
    def removePoint(self,pointtoremove):
        for x in self.mousepoints:
            if x == pointtoremove:
                self.mousepoints.remove(x)
    
    def getMousePointsum(self):
        mousepointsum = copy.deepcopy(self.mousepoints)
        xcounter = 0 
        ycounter = 0
        for x in mousepointsum:
            ycounter = 0
            for y in x:
                mousepointsum[xcounter][ycounter] = y/pixelsperum
                ycounter +=1
            xcounter += 1
        return mousepointsum