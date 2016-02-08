# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 15:17:33 2011

@author: Brendan Callahan

More development log in Will_Coding_Log file

"""



from PyQt4.QtCore import *
from PyQt4.QtGui import *
import math
import copy


#The data model for the grid points and the grid lines.  VideoDisplay uses this data to draw the grid
#when DrawForeground is called, and the center point data can be used by the binary command stuff, as well
#as the "traverse grid points" operation that can be called from the grid points window.
class Grid():
    def __init__(self):
        
        #These are the values for the proportions that each magnification corresponds to.
        #Can just as easily be calculated on the fly from the pixelsperum1x value where needed;
        #these values correspond to the radio buttons used in the interface to select the magnification.
        self.pixelsperum1x = [.1445,.1449] #self.pixelsperum1x = [.15461625,.15494375]
        
        #These are by no means accurate values, although they should be pretty close.
  
        
        #Default magnification is 4x, changed whenever the magnification is changed in the interface.
        self.currentmagnification = 4.0
        self.pixelsperum = [self.pixelsperum1x[0]*4.0,self.pixelsperum1x[1]*4.0]
        
        #Default row and column parameters for program start
        self.rows = 2
        self.cols = 2
        self.vdiv = 50.0
        self.hdiv = 50.0
        
        #Initializing the basic values which hold the point locations for the graphical elements,
        #and are the primary set of data for the graphical elements.
        self.rowlines = None    #Point values for the row lines.  Each index corresponds to a line segment
                                #in the form [x1,y1,x2,y2].
                                
        self.collines = None    #Same format as rowlines.
        self.center = None      #The point where the user-defined center (pivot) of the grid is currently located.

        self.centerpoints = None    #These are the points that are at the center of the grid boxes.
                                    #Regularly recalculated from the grid line values; should not need to 
                                    #be modified except in situations where it's economical to perform some 
                                    #operation on of these points individually rather then recalculating 
                                    #them all (e.g. a translation, but probably not rotation or anything
                                    #more complex)

        self.gridcontrolbox = None  #This object is passed from the main program; the box used to enter row/col values etc.
                                    #It also contains the table of center points.
        
        self.calcLines()    #Calculate the grid lines based on the in initial parameters
        self.reCalcCenter() #Place the pivot at the actual center of the grid
        
        #Get the screen center value.  Should not need to be changed unless we switch to a new resolution.
        self.screenCenter = [1280.0/2,1024.0/2] 
        #Convert this value to um
        self.screenCenterUM = [self.screenCenter[0]/self.pixelsperum[0],self.screenCenter[1]/self.pixelsperum[1]]
        
        #Will be updated  by the main class with the micrometer value from Unit 0 Device 0 on program start.__debug__
        self.startPoint = [0.0,0.0,0.0]
        #When the micrometer value of U0D0 changes, this is updated, so that we can tell where the
        #grid and its components are located in relation to where the screen is currently looking.
        self.currentPoint = [0.0,0.0,0.0]
        
        #Keeps track of how far from the start point that the grid is.  Actually does nothing and
        #should probably be deleted & excised
        self.offsetInUm = [0.0,0.0]
        
        print self.center
        #self.rotateGrid(math.pi)
        
        #Indent the grid a little bit from the edges of the screen
        self.translateGrid(100.0,100.0)
        
        print self.getPivotUM()
        print self.getRealCenterUM()
        
    def setScreenSize(self,width,height):
        print "width",width,"height",height
        self.screenCenter = [width/2,height/2]
        print "newcenter",self.screenCenter
    
    #This is used to change the magnification and to scale the grid accordingly.
    def setPixelsPerUM(self,magnification):

        if magnification == 40.0:
            magnification = 38.65        
        print "Magnification is adjusted for refraction as:", magnification
        #set the new pixelsperum based on the 1x value.
        self.pixelsperum = [self.pixelsperum1x[0] * magnification,self.pixelsperum1x[1]*magnification]

        #store the real center of the grid (not the pivot)
        (centerx, centery) = self.getRealCenter() 
        
        #move the grid to the point (0,0) such that it will be centered at this point.
        #This operation will later be reversed in order to move the grid back to its original location
        #after scaling.
        self.translateGrid(-centerx,-centery)
        
        #For each point, scale it to the new appropriate distance from point (0,0).
        #This could also be done in the grid's original location (not 0,0), but doing it at (0,0)
        #makes the code a little cleaner.
        for x in self.rowlines:
            counter = 0
            radius = 0
            currenttheta = 0
            #for each point in each line
            while counter < 4:
               radius = math.sqrt(x[counter+1]**2+x[counter]**2) #distance
               radius = radius*magnification/self.currentmagnification #scale the radius
               currenttheta = math.atan2(x[counter],x[counter+1]) #get theta
               x[counter+1] = radius*math.cos(currenttheta) #scale the y value
               x[counter] = radius*math.sin(currenttheta) #scale the x value
               #jump ahead to the second point in the list; we're scaling the x and y values for
               #each point in the previous two lines
               counter += 2
        
        for x in self.collines: #do the same for column lines and the center points
            counter = 0
            while counter < 4:
               radius = math.sqrt(x[counter+1]**2+x[counter]**2)
               radius = radius*magnification/self.currentmagnification
               currenttheta = math.atan2(x[counter],x[counter+1])
               x[counter+1] = radius*math.cos(currenttheta)
               x[counter] = radius*math.sin(currenttheta)
               counter += 2
        
        #move the grid back to its original location
        self.translateGrid(centerx,centery)
        
        #figure out how far the grid now needs to be offset from the screen center in order to
        #accomplish the "zoom" effect of scaling.
        centerdiff  = self.getDeltaToScreenCenter(centerx,centery) #initial x and y delta from screen center
        centerdist = math.sqrt(centerdiff[0]**2+centerdiff[1]**2) #calculate this as a distance
        thetatocenter = math.atan2(centerdiff[0],centerdiff[1]) #get the theta
        newcenterdist = centerdist*magnification/self.currentmagnification #scale said distance
        newcenterdiffy = newcenterdist*math.cos(thetatocenter) #turn the scaled radial distance back into 
        newcenterdiffx = newcenterdist*math.sin(thetatocenter) #a usable x and y delta
        
        #apply this new distance from the screen center as a translation to the grid.
        self.translateGrid(centerdiff[0]-newcenterdiffx,centerdiff[1]-newcenterdiffy)
        
        #scale the hdiv and vdiv values (in pixels) to reflect the new magnification.
        self.hdiv = self.hdiv*magnification/self.currentmagnification
        self.vdiv = self.vdiv*magnification/self.currentmagnification        
        
        #finally, update the current magnification value with the new magnification, as all operations
        #have now been performed
        self.currentmagnification = magnification
        
        #update the screen center value in micrometers to reflect the new magnification
        self.screenCenterUM = [self.screenCenterUM[0]*magnification/self.currentmagnification, self.screenCenterUM[1]*magnification/self.currentmagnification]
        
        #finally, recalculate the center points
        self.calcCenterPoints()
    
    #Used to calculate the difference (in pixels) from any point to the screen center.
    def getDeltaToScreenCenter(self,xin,yin):
        return [self.screenCenter[0]-xin,self.screenCenter[1]-yin]
        
    #Calculates the difference (in micrometers) of any point to the screen center.
    def getDeltaToScreenCenterUM(self,xin,yin):
        
        xin = xin/self.pixelsperum[0]
        yin = yin/self.pixelsperum[1]
        return [xin-self.screenCenterUM[0],yin-self.screenCenterUM[1]]
    
    #Given a value in pixels, return the difference to the screen center in micrometers.
    def getDeltaToScreenCenterPixToUM(self,xin,yin):
        self.screenCenterUM = [self.screenCenter[0]/self.pixelsperum[0],self.screenCenter[1]/self.pixelsperum[1]]
        xin = xin/self.pixelsperum[0]
        yin = yin/self.pixelsperum[1]
        return [xin-self.screenCenterUM[0],yin-self.screenCenterUM[1]]
        
    #Given the pixel coordinates of a mouse click on the screen, return the difference to the screen center.
    ############################ debug
    def getDeltaToScreenCenterMouseToUM(self,mouseclick):
        x = mouseclick.x()/self.pixelsperum[0]
        y = mouseclick.y()/self.pixelsperum[1]
        print self.screenCenterUM[0]-x
        print self.screenCenterUM[1]-y
        
        return [self.screenCenterUM[0]-x,self.screenCenterUM[1]-y]

    def getDeltaToScreenCenterMouseToUMFromCoords(self, xx, yy):
        x = xx/self.pixelsperum[0]
        y = yy/self.pixelsperum[1]
        print self.screenCenterUM[0]-x
        print self.screenCenterUM[1]-y
        
        return [self.screenCenterUM[0]-x,self.screenCenterUM[1]-y]
    def getDeltaToScreenCenterMouseToUMFromCoords40x(self, xx, yy):
        x = xx/(self.pixelsperum[0])
        y = yy/(self.pixelsperum[1])
        print (self.screenCenterUM[0]/10)-x
        print (self.screenCenterUM[1]/10)-y
        print "::", [(self.screenCenterUM[0])-x,(self.screenCenterUM[1])-y]
        return [(self.screenCenterUM[0])-x,(self.screenCenterUM[1])-y]
        
    def getPointUMtoPix(self,x,y):
        offset = [x-self.currentPoint[0]-self.screenCenterUM[0],y-self.currentPoint[1]-self.screenCenterUM[1]]
        offset = [-offset[0]*self.pixelsperum[0],-offset[1]*self.pixelsperum[1]]
        return offset
        
    #Return a copy of the center points coordinate array, converted to their micrometer values.
    def returnCenterPointsUMwithOffset(self):
        returnarray = self.getCenterPointsUM()
        
        print self.startPoint
        for x in returnarray:
            x[0] = self.startPoint[0]+self.screenCenterUM[0]-x[0]
            x[1] = self.startPoint[1]+self.screenCenterUM[1]-x[1]
        return returnarray
        
    #Translate the grid by a micrometer value, in x and y.
    def translateUm(self,deltax,deltay):
        self.offsetInUm[0] += deltax
        self.offsetInUm[1] += deltay
        self.translateGrid(deltax*self.pixelsperum[0],deltay*self.pixelsperum[1])
    
    #Update the values stored in the grid control box.
    def controlboxUpdate(self):
        if self.gridcontrolbox != None:
            self.gridcontrolbox.updateText()
            self.gridcontrolbox.updatetable()
    
    #recalculates the acutal center point of the grid, and makes that the pivot as well
    def reCalcCenter(self):
        self.center = ((self.rowlines[0][0]+self.rowlines[self.rows][2])/2,(self.rowlines[0][1]+self.rowlines[self.rows][3])/2)
    
    #receive the gridControlBox object from the main program, so it can be updated from
    #this class in case the values change due to internal operations.
    def setGridControlBox(self,gcb):
        self.gridcontrolbox = gcb
        self.controlboxUpdate()
    
    #Make the user center (pivot) the actual center of the grid, and update the control box.
    #Corresponds to a button on the control box.    
    def reCenterUserCenter(self):
        self.center = self.getRealCenter()
        self.controlboxUpdate()
        
    #Move the grid such that its actual center is now centered on the pivot.
    #Corresponds to a button on the control box.
    def centerGridonUserCenter(self):
        (rcx,rcy) = self.getRealCenter()
        self.translateGrid(self.center[0]-rcx,self.center[1]-rcy)
        self.center = self.getRealCenter()
        self.controlboxUpdate()
    
    #remember, the X and Y values are treated as switched in geometric operations
    #involving the grid (what?  maybe I meant the mouse points?)
    
    #Handles scaling the grid if a user drags one of the grid's four draggable scaling handles.
    def scaleGrid(self,handle,originalmousepoint,secondmousepoint):
        
        realcenterx,realcentery = self.getRealCenter() #remember the center
        originalrotation = self.getRealTheta() #Figure out how far the grid is rotated
        originalslope = math.tan(originalrotation) #Convert this value into a slope
        perporiginalslope = math.tan(originalrotation-math.pi/2) #also get the perpendicular since we'll be using it
        (originalusercenterx, originalusercentery) = self.center #store the pivot point

        #Find medge, or the slope of the edge that's being dragged, based on the handle thats being dragged.
        if handle == 0:
            medge = perporiginalslope
        elif handle == 2:
            medge = perporiginalslope
        elif handle == 1:
            medge = originalslope
        else: #handle == 3
            medge = originalslope
        
        #Find the y intercept of the line corresponding to the real center using the aforementioned slope
        centeryintercept = realcenterx-realcentery*medge
        
        #Now we use the point-line distance formula to find the distance of the two mouse points
        #to the line parallel to the edge being dragged, that intersects the pivot.
        #This way only dragging that is done perpendicular to this line will count as scaling.
        distrealcentertopoint1 = abs(medge*originalmousepoint.y()+(-1)*originalmousepoint.x()+centeryintercept)/math.sqrt(medge**2+(-1)**2)        
        distrealcentertopoint2 = abs(medge*secondmousepoint.y()+(-1)*secondmousepoint.x()+centeryintercept)/math.sqrt(medge**2+(-1)**2) 
        
        #The difference between these values is the distance the grid has been scaled.
        distancescaled = distrealcentertopoint2-distrealcentertopoint1
        
        #Now we're ready to resize the grid.  Move the grid so its top left corner is at (0,0)
        #(as when the grid was created); this way we can just rebuild it with the new parameters.
        self.translateGrid(-self.rowlines[0][0],-self.rowlines[0][1])
        #Also rotate the grid to theta equals zero.  This will also be restored later
        self.rotateGrid(-originalrotation,0.0,0.0)
        
        #This next part figures out what proportion of the grid's total length or width
        #(whichever dimension is being scaled) is "cut off" by the perpendicular line corresponding
        #to the pivot point, such that the grid is proportionally scaled "around" the pivot.
        #Note that this value can be greater than 1, if the pivot is outside of the grid area.
        
        usercenterperpdistance = None
        usercenterproportion = None
        
        if handle == 0 or handle == 2:
            usercenterperpdistance = self.center[0] #The distance from the handle edge to the pivot
            resizeddimension = self.rows*self.vdiv #The total length of the dimension being scaled
            usercenterproportion = self.center[1]/resizeddimension #The aforementioned proportion

        if handle == 1 or handle == 3:
            usercenterperpdistance = self.center[1]
            resizeddimension = self.cols*self.hdiv
            usercenterproportion = self.center[0]/resizeddimension
                
        #Now we solve for how big the grid needs to be, based on how big it already is and the
        #proportion its scaled by
        totalnewwidth = resizeddimension+distancescaled+distancescaled*usercenterproportion
        
        #Update the grid size parameters with these new values
        if handle == 0 or handle == 2:
            self.vdiv = totalnewwidth/self.rows
        if handle == 1 or handle == 3:
            self.hdiv = totalnewwidth/self.cols
        
        #And then rebuild the grid from scratch.
        self.calcLines()
        
        #Move the pivot to the point corresponding to its original location.
        if handle == 0 or handle == 2:
            self.center = (usercenterperpdistance,totalnewwidth*usercenterproportion)
        else:
            self.center = (totalnewwidth*usercenterproportion, usercenterperpdistance)

        #Rotate the grid to its original rotation, around point (0,0).
        self.rotateGrid(originalrotation,0.0,0.0)
        (centerx,centery) = self.center
        #Translate the grid so that it's offset by its current pivot (remember, the pivot is the
        #unchanging reference point for this whole process)
        self.translateGrid(-centerx,-centery)
        #Translate the grid (and along with it the user center/pivot) back to its original location.
        self.translateGrid(originalusercenterx,originalusercentery)
        #Re-calculate the center points
        self.calcCenterPoints
        #Update the values in the control box to reflect the new hdiv or vdiv value.
        self.controlboxUpdate()
                
    #Performs the resizing operation seen in the scaling function(moving back to point (0,0) and 
    #theta=0, changing the grid parameters, rebuilding the grid, and restoring the grid to its original 
    #location) but without scaling.
    def updateDimensions(self,newrows,newcols,newvdiv,newhdiv):
        (originalcenterx,originalcentery) = self.getRealCenter()
        (originalusercenterx,originalusercentery) = self.center
        originalrotation = self.getRealTheta()
        self.rows = newrows
        self.cols = newcols
        self.vdiv = newvdiv
        self.hdiv = newhdiv
        self.calcLines() #rebuild grid
        self.rotateGrid(originalrotation,0.0,0.0)
        (transx,transy) = self.getRealCenter()
        self.translateGrid(-transx+originalcenterx,-transy+originalcentery)
        self.center = (originalusercenterx,originalusercentery)
        self.controlboxUpdate()
        
    
    #returns the angle of what is originally the leftmost vertical grid line or the
    #graphical +y (-y?) axis, which is actually the +x axis with regard to rotation
    def getRealTheta(self):
        #atan2 keeps track of quadrants as its passed two values instead of a single value,
        #and is pretty much superior to atan() in every way.
        return math.atan2(self.collines[0][2]-self.collines[0][0],self.collines[0][3]-self.collines[0][1])
    
    #returns whether the rows or colums have the shortest width, for use in creating the clickable area
    #that allows you to drag the grid.  The area is a circle framed by the shortest dimension centered at
    #the actual center of the grid.
    def getSmallestDimension(self):
        rowlength = (self.cols)*self.hdiv
        colheight = (self.rows)*self.vdiv
        if (rowlength <= colheight):
            return rowlength
        else:
            return colheight
    
    #calculates and returns the actual center of the grid
    def getRealCenter(self):
        return ((self.rowlines[0][0]+self.rowlines[self.rows][2])/2,(self.rowlines[0][1]+self.rowlines[self.rows][3])/2)
    
    #returns the user-defined center, aka the pivot
    def getCenter(self):
        return self.center
    
    #returns a list containing the coordinate pairs of each of the corners.
    def getCorners(self):
        return [[self.rowlines[0][0],self.rowlines[0][1]],[self.rowlines[0][2],self.rowlines[0][3]],[self.collines[0][2],self.collines[0][3]],[self.collines[self.cols][2],self.collines[self.cols][3]]]

    #These are returned in the order of their assigned index, 0 = top, 1 = right, 2 = bottom, 3 = left
    def getScalingHandles(self):
        return [[(self.rowlines[0][0]+self.rowlines[0][2])/2,(self.rowlines[0][1]+self.rowlines[0][3])/2], \
                [(self.collines[self.cols][0]+self.collines[self.cols][2])/2,(self.collines[self.cols][1]+self.collines[self.cols][3])/2], \
                [(self.rowlines[self.rows][0]+self.rowlines[self.rows][2])/2,(self.rowlines[self.rows][1]+self.rowlines[self.rows][3])/2], \
                [(self.collines[0][0]+self.collines[0][2])/2,(self.collines[0][1]+self.collines[0][3])/2]]

    #recalculates the entire grid based on the vdiv, hdiv, rows, and cols.  The top left corner is at (0,0).
    def calcLines(self):
        
        self.returnrows = [] #these variables contains the variable pairs for each line.
        self.returncols = []
        
        #the line coordinates are stored as [x1, y1, x2, y2] for each line.
        for x in range (0,self.rows+1):
            self.returnrows.append([0.0,0.0,0.0,0.0])
        for x in range (0,self.cols+1):
            self.returncols.append([0.0,0.0,0.0,0.0])
        
        #figure out the coordinates
        counter = 0
        for x in self.returnrows:
            x[0] = 0.0
            x[1] = counter*self.vdiv
            x[2] = (self.cols)*self.hdiv
            x[3] = counter*self.vdiv
            counter+=1
            
        counter = 0
        for x in self.returncols:
            x[0] = counter*self.hdiv
            x[1] = 0.0
            x[2] = counter*self.hdiv
            x[3] = (self.rows)*self.vdiv
            counter +=1
    
        self.rowlines = self.returnrows
        self.collines = self.returncols
        self.calcCenterPoints()
        self.controlboxUpdate()
        
    #Recalculates the position of the center point of each grid box
    def calcCenterPoints(self):
        newcenterpointarray = []
        for x in range(0,self.rows):
            
            #Figures out which points correspond to which "box"
            startx = (self.rowlines[x][0]+self.rowlines[x+1][0])/2
            starty = (self.rowlines[x][1]+self.rowlines[x+1][1])/2
            
            #use the current grid theta to figure out what direction the center
            #points are in from the starting grid corner points
            workingtheta = self.getRealTheta()+math.pi/2
            
            #draw a line from the defined corner point to the box center
            for pointnum in range(0,self.cols):
                radius = .5*self.hdiv+pointnum*self.hdiv
                xoffset = radius*math.sin(workingtheta)
                yoffset = radius*math.cos(workingtheta)
                newcenterpointarray.append([startx+xoffset,starty+yoffset])
        self.centerpoints = newcenterpointarray
        self.controlboxUpdate()
        
    #adds xtrans and ytrans to all x and y values in the grid and other associated 
    #items (eg the user center, the centerpoints)
    def translateGrid(self,xtrans,ytrans):
        groupcounter = 0
        for x in self.rowlines:
            counter = 0
            while counter < 4:
                if counter == 0 or counter == 2:
                    x[counter] = x[counter]+xtrans
                else:
                    x[counter] = x[counter]+ytrans
                counter +=1
                
        for x in self.collines:
            counter = 0
            while counter < 4:
                if counter == 0 or counter == 2:
                    x[counter] = x[counter]+xtrans
                else:
                    x[counter] = x[counter]+ytrans
                counter +=1
        for x in self.centerpoints:
            x[0] += xtrans
            x[1] += ytrans
        
        self.center = (self.center[0] + xtrans, self.center[1] + ytrans)
        self.controlboxUpdate()
    
    #Moves the grid so its top right corner is back at (0,0), converts to polar coordinates, adds
    #the deltatheta parameter to the current theta value, converts back to cartesian coordinates, and 
    #translates back to the original location.  Now that i'm keeping better track of the grid "centers",
    #this can probably be rewritten to do the rotation in place.
    def rotateGrid(self,deltatheta, rotationpointx = None, rotationpointy = None):
        
        rotatecenter = True
        if rotationpointx == None:
            (rotationpointx, rotationpointy) = self.center
            rotatecenter = False
            
        self.translateGrid(-rotationpointx,-rotationpointy)
        
        #NOTE THAT IN THE ROTATION THE +X AXIS ON THE IMAGE GRAPHICS IS TREATED AS THE +Y AXIS
        #IN THE TRIG FUNCTIONS AND THE +Y AXIS IS USED AS THE +X AXIS.
        #THUS, THETA = 0 MEANS STRAIGHT DOWN WITH REGARD TO THE GRAPHICAL COORDINATE SYSTEM
        #(although this can probably be converted to a more reasonable value for the sake of the interface)
        for x in self.rowlines:
            counter = 0
            radius = 0
            currenttheta = 0
            #for each point in each line
            while counter < 4:
               radius = math.sqrt(x[counter+1]**2+x[counter]**2) #distance
               currenttheta = math.atan2(x[counter],x[counter+1]) #get theta
               x[counter+1] = radius*math.cos(currenttheta+deltatheta) #graphical y value
               x[counter] = radius*math.sin(currenttheta+deltatheta) #graphical x value
               #jump ahead to the second point in the list
               counter += 2
        for x in self.collines: #do the same for column lines and the center points
            counter = 0
            while counter < 4:
               radius = math.sqrt(x[counter+1]**2+x[counter]**2)
               currenttheta = math.atan2(x[counter],x[counter+1])
               x[counter+1] = radius*math.cos(currenttheta+deltatheta)
               x[counter] = radius*math.sin(currenttheta+deltatheta)
               counter += 2
        for x in self.centerpoints:
            radius = math.sqrt(x[0]**2+x[1]**2)
            currenttheta = math.atan2(x[0],x[1])
            x[1] = radius*math.cos(currenttheta+deltatheta)
            x[0] = radius*math.sin(currenttheta+deltatheta)
            
        (centerx, centery) = self.center
        if rotatecenter == True:
            currenttheta = math.atan2(centerx,centery)
            radius = math.sqrt(centerx**2+centery**2)
            centerx = radius*math.sin(currenttheta+deltatheta)
            centery = radius*math.cos(currenttheta+deltatheta)
            self.center = (centerx, centery)
        
        self.translateGrid(rotationpointx,rotationpointy)
        self.controlboxUpdate()
        
    #########################################################################
    #   These functions return the arrays and values in micrometers         #
    #########################################################################
        
    def getCenterPointsUM(self):
        centerpointsum = copy.deepcopy(self.centerpoints)
        xcounter = 0 
        ycounter = 0
        
        for x in centerpointsum:
            x[0] = self.currentPoint[0]-self.getDeltaToScreenCenterPixToUM(x[0],x[1])[0]#+self.screenCenterUM[0]
            x[1] = self.currentPoint[1]-self.getDeltaToScreenCenterPixToUM(x[0],x[1])[1]#+self.screenCenterUM[1]
        
        return centerpointsum
    
    def getGridLinesUM(self):
        rowlinesum = self.rowlines[:]
        collinesum = self.collines[:]
        
        xcounter = 0 
        ycounter = 0
        for x in rowlinesum:
            ycounter = 0
            for y in x:
                rowlinesum[xcounter][ycounter] = y/self.pixelsperum[0]
                ycounter +=1
            xcounter += 1
            
        xcounter = 0 
        ycounter = 0
        for x in collinesum:
            ycounter = 0
            for y in x:
                collinesum[xcounter][ycounter] = y/self.pixelsperum[1]
                ycounter +=1
            xcounter += 1
        
        return (rowlinesum,collinesum)
        
    def getPivotUM(self):
        return (self.center[0]/self.pixelsperum[0],self.center[1]/self.pixelsperum[1])
        
    def getRealCenterUM(self):
        return (self.getRealCenter()[0]/self.pixelsperum[0],self.getRealCenter()[1]/self.pixelsperum[1])
