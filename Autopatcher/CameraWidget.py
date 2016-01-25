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

@Author: Zhaolun Su, Brendan Callahan, Alexander A. Chubykin

Date 7/2/2015

"""

import numpy as np
import cv2
import sys
sys.path.append("C:\Program Files\Micro-Manager-1.4")
import MMCorePy
import matplotlib.pyplot as plt
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import copy


#SEE _ONNEWFRAME FUNCTION FOR THE MAIN LOOP THAT UPDATES THE CAMERA.

#CameraDevice is the only class that uses OpenCV so far.  This class's purpose is image acquisition 
#from a standard Windows camera (would probably be portable to other OSes), as well as 
#conversion to the QPixmap format, used by Qt.  It extends QObject so that it can use 
#signals & slots; it emits new frames, which are then caught by the CameraScene class.

#The class CameraScene is the QGraphicsScene of the VideoDisplay viewport, found in QTTest right now.
#CameraScene manages drawing each new pixmap in the viewport, while the viewport itself manages
#drawing the grid, points, fps readout, etc on top of the camera frames.

#So, this class is just a mini pipeline for getting the frames from the camera and displaying
#them.

#Modification:
#Switched to use MicroManipulaotr with QImaging Rolera bolt camera. 
#Changed algorithm for converting image to iplimage

DEVICE = ['Camera', 'QCam', 'QCamera']
class CameraDevice(QObject):

    _DEFAULT_FPS = 30

    newFrame = pyqtSignal(cv2.cv.iplimage)

        

    def __init__(self, cameraId=-1, mirrored=False, parent=None):
        super(CameraDevice, self).__init__(parent)
        self.mmc = MMCorePy.CMMCore()  # Instance micromanager core
        self.mmc.getVersionInfo()
        self.mmc.getAPIVersionInfo()
        self.mmc.loadDevice(*DEVICE)
        self.mmc.initializeAllDevices()
        self.mmc.setCameraDevice('Camera')
        print "Camera Exposure Property Modifiable: ", self.mmc.hasProperty(DEVICE[0], 'Exposure') 

        #self.mmc.setProperty(DEVICE[0], 'Exposure', int(10))
        self.mmc.startContinuousSequenceAcquisition(1)



        temp = self.mmc.getLastImage();
        self.framesize = (temp.shape[1], temp.shape[0])
        self.npFrame = None;
        self.rawFrame = None;
        #self.mmc.setExposure(50);

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._queryFrame)
        self._timer.setInterval(1000/self.fps)

        self.equalizationOn = False

        self.paused = False

        self.brightness = 0
        self.contrast = 1

        self.BrightnessOffset = 0

    def setEqualization(self, equalization):
        self.equalizationOn = equalization;
    
    def setBrightnessOffset(self, BrightnessOffset):
        self.BrightnessOffset = BrightnessOffset
        print "BrightnessOffset is ", self.BrightnessOffset

    def setExposure(self, exposure_time):
        self.mmc.setProperty(DEVICE[0], 'Exposure', int(exposure_time))
        print "New Exposure Time ", exposure_time 

    #send out the new frame to be picked up by the CameraScene
    @pyqtSlot()
    
    #called every time the queryframe timer is triggered.
    #also accounts for user-set brightness and contrast.
    def _queryFrame(self):
        
        frame_1 = self.mmc.getLastImage()
        #self.npFrame = copy.deepcopy(frame_1);

        self.rawFrame = copy.deepcopy(frame_1)
        if self.equalizationOn:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            cl1 = clahe.apply(frame_1)
            frame_1 = cl1
        else:
            brightness_temp = np.array(frame_1, dtype = np.int32)
            brightness_temp = brightness_temp + self.BrightnessOffset
            clipped = np.clip(brightness_temp, 0, 255)
            frame_1 = np.array(clipped, dtype = np.uint8)

        frame_flip = cv2.flip(frame_1, 0)
        
        frame_1 = frame_flip
        self.npFrame = frame_1;
        #frame = [frame_1, frame_1, frame_1]
        #print np.var(frame_1)
        frame = cv2.cvtColor(frame_1, cv2.COLOR_GRAY2RGB)
        #self.npFrame = frame
        bitmap = cv2.cv.CreateImageHeader((frame.shape[1], frame.shape[0]), cv2.cv.IPL_DEPTH_8U, 3)
        cv2.cv.SetData(bitmap, frame.tostring(), frame.dtype.itemsize * 3 * frame.shape[1])
        #frame = OpenCVQImage(frame_3)
        self.newFrame.emit(bitmap)


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
        return self.framesize

    @property
    def fps(self):
        return 30


    def start(self):
        
        while True:
            if self.mmc.getRemainingImageCount() > 0:
                frame = self.mmc.getLastImage()
                cv2.imshow('QImage',frame)
                key = cv2.waitKey(10)   #HIT ESCAPE KEY TO TERMINATE
                if key == 27:
                    break

#convert a frame into the correct image format
class OpenCVQImage(QImage):
    def __init__(self, opencvBgrImg):
        
        depth, nChannels = opencvBgrImg.depth, opencvBgrImg.nChannels
        if depth != cv2.cv.IPL_DEPTH_8U or nChannels != 3:
            raise ValueError("the input image must be 8-bit, 3-channel")
        w, h = cv2.cv.GetSize(opencvBgrImg)
        opencvRgbImg = cv2.cv.CreateImage((w, h), depth, nChannels)
        # it's assumed the image is in BGR format
        cv2.cv.CvtColor(opencvBgrImg, opencvRgbImg, cv2.cv.CV_BGR2RGB)
        self._imgData = opencvRgbImg.tostring()
        
        super(OpenCVQImage, self).__init__(self._imgData, w, h, \
          QImage.Format_RGB888)
        
