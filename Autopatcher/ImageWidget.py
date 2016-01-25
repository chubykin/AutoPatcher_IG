# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 17:14:24 2011

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

import cv

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import cv2

import sys
sys.path.append('../2-Photon/')
import opencv_LoadImage4_1 as loadImage2P
sys.path.append("C:\Program Files\Micro-Manager-1.4")
import MMCorePy


#SEE _ONNEWFRAME FUNCTION FOR THE MAIN LOOP THAT UPDATES THE CAMERA.


#This class is used by the 2 Photon microscope code in order to display images that
#have been transferred from a remote location.  It's very similar to CameraWidget
#in operation; nearly the same thing.

class CameraDevice(QObject):

    _DEFAULT_FPS = 30

    newFrame = pyqtSignal(cv.iplimage)
    
    #this and the following short functions mostly initialize the camera
    def __init__(self, cameraId=-1, mirrored=False, parent=None):
        super(CameraDevice, self).__init__(parent)
        
        self.mirrored = mirrored
        #self._cameraDevice = cv.CaptureFromCAM(cameraId)
        
        self.defaultImageSize = (512,512)
        self.imageSize = self.defaultImageSize
        #this counts how often to grab a frame based on the above FPS value.
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._queryFrame)
        self._timer.setInterval(1000/30)
        
        self.brightness = 0
        self.contrast = 1
        self.videoDisplay = None
        
        #mmc = MMCorePy.CMMCore()  # Instance micromanager core
        #mmc.loadDevice('Camera', 'QCam', 'QCamera')
        #mmc.initializeAllDevices()
        #mmc.setCameraDevice('Camera')

        self.paused = False

    #send out the new frame to be picked up by the CameraScene
    @pyqtSlot()
    
    def setParent(self,parentin):
        self.parent = parentin
        self.parent.getGrid().setScreenSize(self.imageSize[0],self.imageSize[1])
    
    def _queryFrame(self):
        
#        frame = cv.QueryFrame(self._cameraDevice)
#        if self.mirrored:
#            mirroredFrame = cv.CreateImage(cv.GetSize(frame), 12, \
#                frame.nChannels)
#            cv.Flip(frame, mirroredFrame, 1)
#            frame = mirroredFrame
#            
#        if self.brightness != 0:
#            cv.AddS(frame, cv.Scalar(self.brightness,self.brightness,self.brightness), frame);
#        
#        if self.contrast != 1:
#            cv.Scale(frame,frame, self.contrast);
#        
#        self.newFrame.emit(frame)



        source = cv2.imread(loadImage2P.getLatestImage())
        frame = cv.CreateImageHeader((source.shape[1], source.shape[0]), cv.IPL_DEPTH_8U, 3)
        cv.SetData(frame, source.tostring(), source.dtype.itemsize * 3 * source.shape[1])
        # Now let opencv decompress your image
        #frame = cv.DecodeImage(pi, cv.CV_LOAD_IMAGE_COLOR)
        
        #frame = cv.GetImage(preframe, cv.IPL_DEPTH_8U, 3)
        
        if self.mirrored:
            mirroredFrame = cv.CreateImage(cv.GetSize(frame), 12, \
                frame.nChannels)
            cv.Flip(frame, mirroredFrame, 1)
            frame = mirroredFrame
            
        if self.brightness != 0:
            cv.AddS(frame, cv.Scalar(self.brightness,self.brightness,self.brightness), frame);
        
        if self.contrast != 1:
            cv.Scale(frame,frame, self.contrast);
            
        (w, h) = cv.GetSize(frame)
        if (w,h) != self.imageSize:
            self.imageSize = (w,h)
            self.parent.setGeometry(3,20,w,h)
            self.parent.display.setFixedSize(w,h)
            self.parent.getGrid().setScreenSize(w,h)

        self.newFrame.emit(frame)
    @property
    def paused(self):
        return not self._timer.isActive()

    @paused.setter
    def paused(self, p):
        if p:
            self._timer.stop()
        else:
            self._timer.start()

    @property
    def frameSize(self):
        w = cv.GetCaptureProperty(self._cameraDevice, \
            cv.CV_CAP_PROP_FRAME_WIDTH)
        h = cv.GetCaptureProperty(self._cameraDevice, \
            cv.CV_CAP_PROP_FRAME_HEIGHT)
        return int(w), int(h)

    @property
    def fps(self):
        fps = int(cv.GetCaptureProperty(self._cameraDevice, cv.CV_CAP_PROP_FPS))
        if not fps > 0:
            fps = self._DEFAULT_FPS
        return fps

#This is the backdrop for the video scene, which contains a pixmap of the current
#frame from the camera and is displayed after removing the previous frame.
class CameraScene(QGraphicsScene):

    newFrame = pyqtSignal(cv.iplimage)

    def __init__(self, cameraDevice, parent=None):
        
        QGraphicsScene.__init__(self)
        self.parentView = parent
        self._frame = None
        self.dispPixmap = None #the pixmap of the frame's data, that is displayed
        self.pixmappointer = None #remembers the previous frame's pointer
        
        self.frames = 0 #counts how many frames have passed since the last FPS calculation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.calcFPS)
        self.timer.start(1000) #calculate the FPS every second

        self._cameraDevice = cameraDevice
        self._cameraDevice.newFrame.connect(self._onNewFrame) #run the _onNewFrame method every time we get a frame

        self.w, self.h = self._cameraDevice.imageSize
        self.FPSout = 0

    def calcFPS(self):
        self.FPSout = self.frames
        self.frames = 0
        
    def resize(self):
        pass
    
    #THIS FUNCTION CORRESPONDS TO THE MAIN CAMERA LOOP
   
    #This creates the pixmap and puts it on scene, it also removes the pixmap
    #from the previous scene so it doesn't eat memory.
    @pyqtSlot(cv.iplimage)
    def _onNewFrame(self, frame):
        
        #if it's not the first frame, remove the previous pixmap
        if self.pixmappointer != None:
            self.removeItem(self.pixmappointer)
        #display the current frame
        self.dispPixmap = QPixmap.fromImage(OpenCVQImage(frame))
        
        self.frames +=1
        #if self.firstpixmap == True:
        self.pixmappointer = self.addPixmap(self.dispPixmap)
        
        if self._cameraDevice.imageSize != (self.w,self.h):
            (w,h) = self._cameraDevice.imageSize
            self.resize()
        

#    def changeEvent(self, e):
#        print("CHANGEEVENT") 
#        if e.type() == QEvent.EnabledChange:
#            if self.isEnabled():
#                self._cameraDevice.newFrame.connect(self._onNewFrame)
#            else:
#                self._cameraDevice.newFrame.disconnect(self._onNewFrame)
#
#    def paintEvent(self, e):
#        
#        print("PAINTEVENT")
#        if self._frame is None:
#            return
#        trace(paintEvent)
#        painter = QPainter(self)
#        painter.drawImage(QPoint(0, 0),OpenCVQImage(self._frame))

#convert a frame into the correct image format
class OpenCVQImage(QImage):
    def __init__(self, opencvBgrImg):
        
        depth, nChannels = opencvBgrImg.depth, opencvBgrImg.nChannels
        if depth != cv.IPL_DEPTH_8U or nChannels != 3:
            raise ValueError("the input image must be 8-bit, 3-channel")
        w, h = cv.GetSize(opencvBgrImg)
        
        
        opencvRgbImg = cv.CreateImage((w, h), depth, nChannels)
        # it's assumed the image is in BGR format
        cv.CvtColor(opencvBgrImg, opencvRgbImg, cv.CV_BGR2RGB)
        self._imgData = opencvRgbImg.tostring()
        
        super(OpenCVQImage, self).__init__(self._imgData, w, h, \
          QImage.Format_RGB888)
        

#@pyqtSlot(cv.iplimage)
#def onNewFrame(frame):
#    print("NEWFRAME2")
#    cv.CvtColor(frame, frame, cv.CV_RGB2BGR)
#    msg = "processed frame"
#    font = cv.InitFont(cv.CV_FONT_HERSHEY_DUPLEX, 1.0, 1.0)
#    tsize, baseline = cv.GetTextSize(msg, font)
#    w, h = cv.GetSize(frame)
#    tpt = (w - tsize[0]) / 2, (h - tsize[1]) / 2
#    cv.PutText(frame, msg, tpt, font, cv.RGB(255, 0, 0))
#import sys
#
#app = QtGui.QApplication(sys.argv)
#
#cameraDevice = CameraDevice(mirrored=True)
#
#cameraWidget1 = CameraWidget(cameraDevice)
#cameraWidget1.newFrame.connect(onNewFrame)
#cameraWidget1.show()
#
#cameraWidget2 = CameraWidget(cameraDevice)
#cameraWidget2.show()
#
#sys.exit(app.exec_())
