# -*- coding: utf-8 -*-
"""
autopatcher
ver 7_1 - mock
ver 7_1w - working
ver 7.2w - working, applicationWindow __init__ is changed to be callable from QTtest
trying to implement pyqwt for plotting instead of the slower matplotlib
ver 7_3 - 12/02/12 - To Do: add the buttons to maintain the set pressure:
12/06/12 - to make sure the singleShot slots are not generated consistently, i do a crude conditional wait till they are over by changing the global variable ok_to_go=0/1 - changed to 0 after the conditional call, changed back to 1 by the slot.    
Created on Mon Jul 09 22:03:02 2012
ver 7_4 - 12/07/12 - 2-pump configuration
ver 7_4_PosPressure
ver 8_1 - 01/27/13 - adding threshold_coefficients, default pump1, pump2 pulse times (also pulse times can now be passed as arguments to the pump_burst functions)
ver 8_2 - 02/02/13 - separated positive pressure step at step 1 from the movement down - moved now to step 1.5
                     also, introduced the python threads here (as the main QTtest program also uses python threads)
ver 8_3 - 02/04/13 - added two widgets with the current updated step-value
ver 8_4mock - 02/06/13 - added easily changeable mock part (Data_Control) plus MssUnit import
                    re-arranged the widgets better
                    also, added clickable buttons as the current status of the pumps, valves
ver 9_0 - 06/07/13
ver 10_0 - 05/16/14 - patching in vivo, axial approach, changing the motors controlled to #1
ver 10_2 - 06/07/15 - expanding how much of the history of recordings is shown (not 2 s, not informative, possibly add Current and resistance)
                     
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

@Author: Zhaolun Su, Qiuyu Wu, Alexander A. Chubykin

"""
import sys, os
__progname__ =  os.path.basename(sys.argv[0])
__author__="Alex Chubykin"
__version__="10_2mock"
__date__="Mon Jul 09 22:03:02 2012"
__copyright__="Copyright (c) 2012 Alex Chubykin"
__license__="Python"

from PyQt4 import QtGui, QtCore
from PyQt4 import Qt
import PyQt4.Qwt5 as Qwt
#from PyQt4.Qwt5.anynumpy import *

#from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.figure import Figure

import UniversalLibrary as UL
import numpy as np
import time
import h5py
import scipy.io
from threading import Thread
import csv
import datetime
import MultiClampDriver

history_shown=40000 # in units, 400 is about 2 sec.
Icurrent_injected=5 # injected current in mV
Manipulator_coords=[]
Patch_threshold=0.3
move_limit=150 # limit on the down movement, in um
step_size=1# step size (0.2)
move_counter=0
marker_patch=0

ok_to_go = 1
ok_to_go2 = 1
file_save_bool = 0
zap_bool = False
zap_hold = 0
csvDictionary = {'InitialResistance': 0, 'StartTime':0, 'GigasealResistance':0, 'GigasealTime':0, 'BrokenInResistance':0, 'EndTime':0}

# stages:
# 0 - before patching
# 1 - positive pressure, started movement down
# 2 - once the current command decreased enough, switch to atmosphere
# 3 - apply short suction
# 4 - wait till the current command is decreased to about zero
# 5 - break-in
# 6 - broken in
 
#thresholds: 0: unused. 1:positive threshold 2:negative threshold

# thresholds=np.array([[20,45,55,0,0,0,0], # thresholds for DataControl.data1 (pressure)
#                     [100.0,80.0,30.0,15.0,10.0,30.0,0.0]]) # thresholds for DataControl.data2 (Vm difference), they will be assigned at the marker_step=0.5 by multiplying delta_data2*threshold_coefficients
# threshold_coefficients=np.array([1,0.8,0.3,0.15,0.1,0.3,0.0]) # should be the same number as the number of columns in thresholds
initialResistance = 5
#pump default pulses
#pump_pulse=10 # for L5 cells, in ms
pump_pulse=10 # for L3 cells - 5-7 ms, in ms short burst default
pump_long_pulse=50 #long burst default
pump2_pulse=250 # in ms
MSSInterface = None

"""
configuration:
            pin_outs={'valve1':1,'valve2':2,'pump':3,'pump2':4,'power':7+8}
            valve1: 0 - positive pressure,  1 - negative pressure
            valve2: 0 - atmosphere,         1 - inside
            pump - stronger 12V pump
            pump2 - weaker 5V pump
                
"""

#import MockUnit as ms
import MssUnit2 as ms

class DataControl2(Thread):
    data1 = []
    data2 = []
    #def __init__(self,BoardNum=0, Gain=UL.BIP5VOLTS):
    def __init__(self,BoardNum=0, Gain=UL.BIP10VOLTS): # single-ended mode - configered in InstaCal
        # initialize the thread first
        Thread.__init__(self)        
        # Universal library acquisition
        self.BoardNum=BoardNum
        self.Gain=Gain        
        self.Chan = 0
        #self.Chan2 = 1
        self.Chan2 = 1 # single-ended mode
        self.data = []
        self.times = []
        #self.data1 = []
        #self.data2 = []
        # digital input for the TTL signal - external synchronization (could also be done through the SYNC and TRIG inputs)
        self.PortNum = UL.FIRSTPORTA
        self.Direction = UL.DIGITALOUT
        self.PortNum2 = UL.FIRSTPORTB
        self.Direction2 = UL.DIGITALIN 
        self.BitNum2 = 0

        #DataValue = 0
        #DataValue2 = 0
        self.TTL_input = 0
        self.TTL_switch=0
        
        # part for the UL.cbAInScan
        self.LowChan = 0
        self.HighChan = 0
       
        self.Count = 5 # how many samples to acquire per scan. with the GUI update every 5 ms, 10 samples/ms seems good (max rate/channel is 50kS/s)
        self.Rate = 500 # Samples/s
        
        self.Options = UL.CONVERTDATA
        self.ADData = np.zeros((self.Count,), np.int16)
        
        """
        mock_autopatcher3.py

        #initialize the Universal Library Board
        UL.cbDConfigPort(self.BoardNum, self.PortNum, self.Direction)
        #UL.cbDOut(self.BoardNum, self.PortNum, 0b0000)

        # Power switch at Port B7 out
        UL.cbDConfigPort(self.BoardNum, self.PortNum2, self.Direction)        
        """
        
        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.AcquireAll)
        self.timer.start(5) # timer has 5 ms counter interval (maximum acquisition rate of USB-1208FS is 50 kS/s per all used channels), Patching Current Step Pulse 5 ms
        # arduino clock speed 16 MHz, maybe can also acquire digital input at high enough rate, not sure how precise it is.        
        
        


    def AcquireAll(self):
        self.AIn(Chan=0)
        self.AIn(Chan=1)
        
    def AIn(self,Chan=0):
        """
        DataValue = UL.cbAIn(self.BoardNum, Chan, self.Gain)
        EngUnits = UL.cbToEngUnits(self.BoardNum, self.Gain, DataValue)
        #self.data.append( EngUnits )
        # storing data in the global data1 variable
        if Chan==0:
            # Chan==0 - pressure input:
            #self.data1.append(EngUnits)
            self.data1.append((EngUnits/5-0.5)/0.018*7.5) # Traself.data1.append(EngUnits)nsfer function of the MPX7025 pressure sensor, in mmHr (Torr))
        else:
            self.data2.append(EngUnits)
        #times.append( time.time()-tstart )
        return EngUnits
        """
        self.data1.append(np.random.random()*100)
        self.data2.append(np.random.random()*100)
        return np.random.random()*100
        
    def DOut(self, PortNum=UL.FIRSTPORTA, digitalpattern=0b000):
        """
        return UL.cbDOut(self.BoardNum, PortNum, digitalpattern)
        """
        
    def DBitOut(self,PortNum=UL.FIRSTPORTA, BitNum=0, BitValue=0):
        """
        return UL.cbDBitOut(self.BoardNum, PortNum, BitNum, BitValue)
        """
        
class DataControl(Thread):
    data1 = []
    data2 = []
    #def __init__(self,BoardNum=0, Gain=UL.BIP5VOLTS):
    def __init__(self,BoardNum=0, Gain=UL.BIP10VOLTS): # single-ended mode - configered in InstaCal
        # initialize thread        
        Thread.__init__(self)
        # Universal library acquisition
        self.BoardNum=BoardNum
        self.Gain=Gain

        self.Chan = 0
        #self.Chan2 = 1
        self.Chan2 = 1 # single-ended mode
        self.data = []
        self.times = []
        #self.data1 = []
        #self.data2 = []
        # digital input for the TTL signal - external synchronization (could also be done through the SYNC and TRIG inputs)
        self.PortNum = UL.FIRSTPORTA
        self.Direction = UL.DIGITALOUT
        self.PortNum2 = UL.FIRSTPORTB
        self.Direction2 = UL.DIGITALIN 
        self.BitNum2 = 0

        #DataValue = 0
        #DataValue2 = 0
        self.TTL_input = 0
        self.TTL_switch=0
        
        # part for the UL.cbAInScan
        self.LowChan = 0
        self.HighChan = 0
        
        self.Count = 5 # how many samples to acquire per scan. with the GUI update every 5 ms, 10 samples/ms seems good (max rate/channel is 50kS/s)
        self.Rate = 500 # Samples/s
        
        self.Options = UL.CONVERTDATA
        self.ADData = np.zeros((self.Count,), np.int16)
        
        #initialize the Universal Library Board
        UL.cbDConfigPort(self.BoardNum, self.PortNum, self.Direction)
        #UL.cbDOut(self.BoardNum, self.PortNum, 0b0000)

        # Power switch at Port B7 out
        UL.cbDConfigPort(self.BoardNum, self.PortNum2, self.Direction)        
        
        
        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.AcquireAll)
        self.timer.start(5) # timer has 5 ms counter interval (maximum acquisition rate of USB-1208FS is 50 kS/s per all used channels), Patching Current Step Pulse 5 ms
        # arduino clock speed 16 MHz, maybe can also acquire digital input at high enough rate, not sure how precise it is.        
    
    def AcquireAll(self):
        self.AIn(Chan=0)
        self.AIn(Chan=1)
        
    def AIn(self,Chan=0):
        
        DataValue = UL.cbAIn(self.BoardNum, Chan, self.Gain)
        EngUnits = UL.cbToEngUnits(self.BoardNum, self.Gain, DataValue)
        #self.data.append( EngUnits )
        # storing data in the global data1 variable
        if Chan==0:
            # Chan==0 - pressure input:
            #self.data1.append(EngUnits)
            self.data1.append((EngUnits/5-0.5)/0.018*7.5) # Traself.data1.append(EngUnits)nsfer function of the MPX7025 pressure sensor, in mmHr (Torr))
        else:
            self.data2.append(EngUnits)
        #times.append( time.time()-tstart )
        return EngUnits
        
    def DOut(self, PortNum=UL.FIRSTPORTA, digitalpattern=0b000):        
        return UL.cbDOut(self.BoardNum, PortNum, digitalpattern)
        
        
    def DBitOut(self,PortNum=UL.FIRSTPORTA, BitNum=0, BitValue=0):        
        return UL.cbDBitOut(self.BoardNum, PortNum, BitNum, BitValue)
    
    def getData(self,board=0,chan=0,gain=UL.BIP10VOLTS):
        return UL.cbAIn(board, chan, gain)
               


class DataPlot(Qwt.QwtPlot):

    def __init__(self, *args):
        Qwt.QwtPlot.__init__(self, *args)

        self.setCanvasBackground(Qt.Qt.white)
        self.alignScales()

        # Initialize data
        self.x = arange(0.0, 100.1, 0.5)
        self.y = zeros(len(self.x), Float)
        self.z = zeros(len(self.x), Float)

        self.setTitle("A Moving QwtPlot Demonstration")
        self.insertLegend(Qwt.QwtLegend(), Qwt.QwtPlot.BottomLegend);

        self.curveR = Qwt.QwtPlotCurve("Data Moving Right")
        self.curveR.attach(self)
        self.curveR.setPen(Qt.QPen(Qt.Qt.red))

        mY = Qwt.QwtPlotMarker()
        mY.setLabelAlignment(Qt.Qt.AlignRight | Qt.Qt.AlignTop)
        mY.setLineStyle(Qwt.QwtPlotMarker.HLine)
        mY.setYValue(0.0)
        mY.attach(self)

        self.setAxisTitle(Qwt.QwtPlot.xBottom, "Time (ms)")
        self.setAxisTitle(Qwt.QwtPlot.yLeft, "Values")
    
        self.startTimer(50)
        self.phase = 0.0

    # __init__()

    def alignScales(self):
        self.canvas().setFrameStyle(Qt.QFrame.Box | Qt.QFrame.Plain)
        self.canvas().setLineWidth(1)
        for i in range(Qwt.QwtPlot.axisCnt):
            scaleWidget = self.axisWidget(i)
            if scaleWidget:
                scaleWidget.setMargin(0)
            scaleDraw = self.axisScaleDraw(i)
            if scaleDraw:
                scaleDraw.enableComponent(
                    Qwt.QwtAbstractScaleDraw.Backbone, False)

    # alignScales()
    
    def timerEvent(self, e):
        if self.phase > pi - 0.0001:
            self.phase = 0.0

        # y moves from left to right:
        # shift y array right and assign new value y[0]
        self.y = concatenate((self.y[:1], self.y[:-1]), 1)
        self.y[0] = sin(self.phase) * (-1.0 + 2.0*random.random())

        self.curveR.setData(self.x, self.y)
        self.replot()
        self.phase += pi*0.02

    # timerEvent()

# class DataPlot

def make():
    demo = DataPlot()
    demo.resize(500, 300)
    demo.show()
    return demo


class MyMinCanvas(Qwt.QwtPlot):
    """ Minimal MyMinCanvas from DataPlot"""
    def __init__(self, *args):
        Qwt.QwtPlot.__init__(self, *args)
        # self.setGeometry(0,0,320,100) # doesn't seem to do much in this context
        # self.size = (600, 400) # also does nothing
        self.enableAxis(Qwt.QwtPlot.xBottom, False) # hiding the axis
        self.enableAxis(Qwt.QwtPlot.yLeft, False)
        self.compute_initial_figure()


    def compute_initial_figure(self):
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(2*np.pi*t)
        curve = Qwt.QwtPlotCurve('y = sin(2*pi*t)',)

        curve.attach(self)
        
        #curve.setPen(Qt.QPen(Qt.Qt.green, 2))
        color1=QtGui.QColor()
        color1.setNamedColor(self.color)

        curve.setPen(Qt.QPen(color1,2))
        curve.setData(t, s)
        self.replot()

class MyDynamicCanvas(Qwt.QwtPlot):
    """ Dynamic MyDynamicCanvas from DataPlot"""
    def __init__(self, *args):
        self.timer_interval=5 # in ms
        self.canvas_data=[]
        self.times=[0]
        
        if 'color' in kwargs:
            self.color=kwargs['color']
            print kwargs['color']
        else:
            self.color='black'
        if 'title' in kwargs:
            self.title=kwargs['title']
        else:
            self.title=''
            
        Qwt.QwtPlot.__init__(self, *args)
        self.setCanvasBackground(Qt.Qt.white)
        color1=QtGui.QColor()
        color1.setNamedColor(self.color)
        title1=Qwt.QwtText(self.title)
        title1.setColor(color1)

        #self.setTitle(str(self.y[2]),color=color1)
        self.setTitle(title1)
        
        self.curveR = Qwt.QwtPlotCurve("Data Moving Right")
        self.curveR.attach(self)
        #self.curveR.setPen(Qt.QPen(Qt.Qt.red))
        self.curveR.setPen(QtGui.QColor().setNamedColor("lime")) # "mediumvioletred"
        
        self.setAxisTitle(Qwt.QwtPlot.xBottom, "Time (ms)")
        self.setAxisTitle(Qwt.QwtPlot.yLeft, "Values")
    
        self.timer = QtCore.QTimer(self)
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.update)
        self.timer.start(self.timer_interval)
        
    def timerEvent(self, e):
        if len(self.data)>history_shown: # prevents from the memory leak, creates a moving graph
            self.data.pop(0)

        self.curveR.setData(np.arange(0.0, len(self.data)), self.data)
        self.replot()

    def set_data(self,data):
        self.data=data

    def set_timer_interval(self,interval):
        self.timer.setInterval(interval)
        
    def update(self):
        if len(self.canvas_data)>history_shown: # prevents from the memory leak, creates a moving graph
            self.canvas_data.pop(0)
        #self.times.append(QtCore.QTime().currentTime().msec())
        self.times.append(self.times[-1]+self.timer_interval)
        self.curveR.setData(self.times, self.canvas_data)
        #self.curveR.setData(np.arange(0.0, len(self.canvas_data)), self.canvas_data)
        
        self.replot()       

class BarCanvas(Qwt.QwtPlot):

    def __init__(self, *args,**kwargs):
        Qwt.QwtPlot.__init__(self, *args)
        if 'color' in kwargs:
            self.color=kwargs['color']
            #print kwargs['color']
            print self.color
        else:
            self.color='black'
        if 'title' in kwargs:
            self.title=kwargs['title']
        else:
            self.title=''
        color1=QtGui.QColor()
        color1.setNamedColor(self.color)

        self.setCanvasBackground(Qt.Qt.white)
        #self.alignScales()

        # Initialize data
        self.x = [0,9,10,20,21,30] #arange(0, 100, 20)
        self.y = [0.0,0.0,5.0,5.0,0.0,0.0]
        #self.z = zeros(len(self.x), Float)
        #title1=Qwt.QwtText(str(self.y[2]))
        title1=Qwt.QwtText("{0:.2f}".format(self.y[2]))
        title1.setColor(color1)

        #self.setTitle(str(self.y[2]),color=color1)
        self.setTitle(title1)
        self.insertLegend(Qwt.QwtLegend(), Qwt.QwtPlot.BottomLegend);

        self.curveR = Qwt.QwtPlotCurve(self.title)
        self.curveR.attach(self)
        self.curveR.setPen(Qt.QPen(color1,2))

        mY = Qwt.QwtPlotMarker()
        mY.setLabelAlignment(Qt.Qt.AlignRight | Qt.Qt.AlignTop)
        mY.setLineStyle(Qwt.QwtPlotMarker.HLine)
        mY.setYValue(0.0)
        mY.attach(self)

        #self.setAxisTitle(Qwt.QwtPlot.xBottom, "Time (seconds)")
        #self.setAxisTitle(Qwt.QwtPlot.yLeft, "MOhm")
    
        self.startTimer(1000) # 50 - update period, ms
        self.phase = 0.0

    # __init__()
    def set_data(self,data1):
        self.y=[0.0,0.0,data1,data1,0.0,0.0]  
        
    def alignScales(self):
        self.canvas().setFrameStyle(Qt.QFrame.Box | Qt.QFrame.Plain)
        self.canvas().setLineWidth(1)
        for i in range(Qwt.QwtPlot.axisCnt):
            scaleWidget = self.axisWidget(i)
            if scaleWidget:
                scaleWidget.setMargin(0)
            scaleDraw = self.axisScaleDraw(i)
            if scaleDraw:
                scaleDraw.enableComponent(
                    Qwt.QwtAbstractScaleDraw.Backbone, False)

    # alignScales()
    
    def timerEvent(self,e):
        #if self.phase > pi - 0.0001:
        #    self.phase = 0.0

        # y moves from left to right:
        # shift y array right and assign new value y[0]
        #self.y = concatenate((self.y[:1], self.y[:-1]), 1)
        #self.y[0] = sin(self.phase) * (-1.0 + 2.0*random.random())
        #self.setTitle(str(self.y[2]))
        self.setTitle("{0:.2f}".format(self.y[2]))
        self.curveR.setData(self.x, self.y)
        self.replot()
        #self.phase += pi*0.02

    # timerEvent()


class MyDynamicMplCanvas(Qwt.QwtPlot, Thread):
    """A canvas that updates itself, Qwt."""
    def __init__(self, *args, **kwargs):
        # initialize thread        
        Thread.__init__(self)
        
        self.timer_interval=5        
        self.canvas_data=[]
        self.times=[0]
        if 'color' in kwargs:
            self.color=kwargs['color']
            print kwargs['color']
        else:
            self.color='black'
        if 'title' in kwargs:
            self.title=kwargs['title']
        else:
            self.title=''
            
        Qwt.QwtPlot.__init__(self, *args)
        self.setCanvasBackground(Qt.Qt.white)
        color1=QtGui.QColor()
        color1.setNamedColor(self.color)
        self.title1=Qwt.QwtText(self.title)
        self.title1.setColor(color1)

        #self.setTitle(str(self.y[2]),color=color1)
        self.setTitle(self.title1)
        
        self.curveR = Qwt.QwtPlotCurve("Data")
        self.curveR.attach(self)       
        self.curveR.setPen(Qt.QPen(color1))
        #self.curveR.setPen(Qt.QPen(Qt.Qt.red))
        #self.curveR.setPen(QtGui.QColor().setNamedColor("lime")) # "mediumvioletred"
        
        self.setAxisTitle(Qwt.QwtPlot.xBottom, "Time (ms)")
        #self.setAxisTitle(Qwt.QwtPlot.yLeft, "Values")
    
        #self.startTimer(50)
        self.timer = QtCore.QTimer(self)
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.update)
        self.timer.start(self.timer_interval)        
    """
    def timerEvent(self,e):
        if len(self.canvas_data)>history_shown: # prevents from the memory leak, creates a moving graph
            self.canvas_data.pop(0)

        self.curveR.setData(np.arange(0.0, len(self.canvas_data)), self.canvas_data)
        self.replot()
    """

    def update(self):
        if len(self.canvas_data)>history_shown: # prevents from the memory leak, creates a moving graph
            self.canvas_data.pop(0)
        #self.times.append(QtCore.QTime().currentTime().msec())
        self.times.append(self.times[-1]+self.timer_interval)
        #self.setTitle(self.title1)
        self.curveR.setData(self.times, self.canvas_data)
        #self.curveR.setData(np.arange(0.0, len(self.canvas_data)), self.canvas_data)
        
        self.replot()
    
        

    def compute_initial_figure(self):
        self.axes.set_title('DAQ Analog Channel')
        self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')
    """        
    def set_data(self,data1):
        self.canvas_data=data1
    """
    def set_data(self,data,**kwargs):
        self.canvas_data=data
        if 'times' in kwargs:
            self.times=times
        
    def append_data(self,data,**kwargs):
        self.canvas_data.append(data)
        if 'times' in kwargs:
            self.times.append(kwargs['times'])

    def set_timer_interval(self,interval):
        self.timer.setInterval(interval)
        
    def update_figure(self):
        if len(self.canvas_data)>history_shown: # prevents from the memory leak, creates a moving graph
            self.canvas_data.pop(0)
        self.axes.plot(self.canvas_data, self.color)
        #self.axes.set_title('DAQ Analog Channel')
        self.setTitle(self.title)
        if hasattr(self, 'my_ylabel'): # nice check for existence of variable my_ylabel within the instance of this class
            self.axes.set_ylabel(self.my_ylabel)
        self.draw()


class PatchCanvas(MyMinCanvas):
    """A canvas that updates itself every second with a new plot."""
    data=[]
    def __init__(self, *args, **kwargs):
        MyMinCanvas.__init__(self, *args, **kwargs)
        
        # QLabel with the marker_patch
        font1=QtGui.QFont("OCR A Extended",15)
        font1.setBold(True)

        self.label1=QtGui.QLabel( "<font color=\"cyan\">Patch_stage: %s </font>" % marker_patch,self)
        self.label1.setStyleSheet("background-color: navy")
        self.label1.setFont(font1)
        #self.label1.setGeometry(10, 10, 200, 30)

        timer = QtCore.QTimer(self)
        QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), self.update)
        timer.start(5)

    def compute_initial_figure(self):
        pass
        
    def set_data(self,data2):
        self.data=data2
    
    def update(self):
        self.label1.setText("<font color=\"cyan\">Patch_stage: %s </font>" % marker_patch)
        
        if marker_patch>0 and (self.data[-1]>Patch_threshold):
            self.emit(QtCore.SIGNAL("Signal_to_patch"))
            #print 'signal_to_patch emmited by patch canvas'                 
        
    def set_timer_interval(self,interval):
        self.timer.setInterval(interval)

class PatchLabel(QtGui.QLabel):
    """A canvas that updates itself every second with a new plot."""
    data=[]
    def __init__(self, *args, **kwargs):
        QtGui.QLabel.__init__(self, *args, **kwargs)
        
        # QLabel with the marker_patch
        font1=QtGui.QFont("OCR A Extended",15)
        font1.setBold(True)

        self.label1=QtGui.QLabel( "<font color=\"cyan\">Patch_stage: %s </font>" % marker_patch,self)
        self.label1.setStyleSheet("background-color: navy")
        self.label1.setFont(font1)
        #self.label1.setGeometry(10, 10, 200, 30)

        timer = QtCore.QTimer(self)
        QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), self.update)
        timer.start(5)

    def compute_initial_figure(self):
        pass
        
    def set_data(self,data2):
        self.data=data2
    
    def update(self):
        self.label1.setText("<font color=\"cyan\">Patch_stage: %s </font>" % marker_patch)
        
        if marker_patch>0 and (self.data[-1]>Patch_threshold):
            self.emit(QtCore.SIGNAL("Signal_to_patch"))
            #print 'signal_to_patch emmited by patch canvas'                 
        
    def set_timer_interval(self,interval):
        self.timer.setInterval(interval)
  
        
class ApplicationWindow(QtGui.QMainWindow,Thread): # possibly delete in the autopatcher.py called by the QTtest.py
    def __init__(self,interface=None,parent=None):

        # initialize multiclamp driver
        self.mcc = MultiClampDriver.MCCThread();
        

        QtGui.QMainWindow.__init__(self,parent)
        # initialize thread        
        Thread.__init__(self)
        self.owner = None
        if interface!=None:
            self.interface = interface     
        if parent!=None:
            self.setParent(parent)
        
        self.global_timer_interval=5 # ms - rate of graph and data update

        # important valve information
        self.valve_status1=0
        self.valve_status2=0
        self.pump_status=0
        self.pump2_status=0

        #Popup control
        self.pop_holding = 0
        self.pop_holding_zap = False
        
        # pins on a DAQ board
        self.pin_outs={'valve1':1,'valve2':2,'pump':3,'pump2':4,'power':7+8}
        
        self.resistance_list = []
        #initialize the Universal Library Board
        if interface == None:        
            self.DataVar=DataControl()
        else:
            self.DataVar = self.interface.dataControl

        #Load Coonfiuration File
        self.myConfig = None
        self.myThresholdCoefficient = None
        self.loadConfiguration()

        #Timer record for patching

        self.timer_fail = None
        
        
        #rest - PyQt part
        QtGui.QMainWindow.__init__(self)
        self.setWindowIcon(QtGui.QIcon('rsc\FluorNeuronIcon.jpg'))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("DAQ Input Plotting")
        
        # Menus
        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Save', self.fileSave,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_X)      
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)
        self.help_menu = QtGui.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)
        self.help_menu.addAction('&About', self.about)

        self.main_widget = QtGui.QWidget(self)

        # Buttons        
        self.btn_zero = QtGui.QPushButton(QtGui.QIcon('./rsc/power.png'), 'Zero Data', self)
        QtCore.QObject.connect(self.btn_zero, QtCore.SIGNAL("clicked()"),self.button_zero)
        
        """        
        self.btn_power = QtGui.QPushButton(QtGui.QIcon('./rsc/power.png'), 'Power On/Off', self)
        QtCore.QObject.connect(self.btn_power, QtCore.SIGNAL("clicked()"),self.button_power)
        
        self.btn1 = QtGui.QPushButton(QtGui.QIcon('./rsc/plus.png'), 'Polarity Burst', self)
        QtCore.QObject.connect(self.btn1, QtCore.SIGNAL("clicked()"),self.slot1_brief)
        self.btn2 = QtGui.QPushButton(QtGui.QIcon('./rsc/minus.png'),'Atmosphere Burst', self)
        QtCore.QObject.connect(self.btn2, QtCore.SIGNAL("clicked()"),self.slot2_brief)
        """
        self.btn3 = QtGui.QPushButton(QtGui.QIcon('./rsc/valve.png'), 'Pressure Plus/Minus', self)
        QtCore.QObject.connect(self.btn3, QtCore.SIGNAL("clicked()"),self.slot1)
        self.btn3.setCheckable(True)
        self.btn4 = QtGui.QPushButton(QtGui.QIcon('./rsc/valve.png'),'Atmosphere Open/Closed', self)
        self.btn4.setCheckable(True)
        QtCore.QObject.connect(self.btn4, QtCore.SIGNAL("clicked()"),self.slot2)
        
        self.btn_pump = QtGui.QPushButton(QtGui.QIcon('./rsc/pump.png'),'Pump Switch', self)
        self.btn_pump.setCheckable(True)
        QtCore.QObject.connect(self.btn_pump, QtCore.SIGNAL("clicked()"),self.pump_switch)
        
        self.btn_pump_burst = QtGui.QPushButton(QtGui.QIcon('./rsc/pump.png'),'Pump Burst', self)
        QtCore.QObject.connect(self.btn_pump_burst, QtCore.SIGNAL("clicked()"),self.pump_burst)
        
        # 06/08/15 remove the button for the pump2
        #self.btn_pump2 = QtGui.QPushButton(QtGui.QIcon('pump.jpg'),'Pump2 Switch', self)
        #self.btn_pump2.setCheckable(True)
        #QtCore.QObject.connect(self.btn_pump2, QtCore.SIGNAL("clicked()"),self.pump2_switch)
        
        #self.btn_pump2_burst = QtGui.QPushButton(QtGui.QIcon('pump.jpg'),'Pump2 Burst', self)
        #QtCore.QObject.connect(self.btn_pump2_burst, QtCore.SIGNAL("clicked()"),self.pump2_burst)

        # Patch Status QLabel:        
        font1=QtGui.QFont("OCR A Extended",12)
        font1.setBold(True)

        self.label1=QtGui.QLabel( "<font color=\"navy\">Patch step: %s </font>" % marker_patch,self)
        #self.label1.setStyleSheet("background-color: gray")
        self.label1.setFont(font1)
        
        self.btn_patch = QtGui.QPushButton(QtGui.QIcon('./rsc/play.png'), 'Patch', self)
        QtCore.QObject.connect(self.btn_patch, QtCore.SIGNAL("clicked()"),self.button_patch)

        self.btn_clear_tip = QtGui.QPushButton(QtGui.QIcon('./rsc/clean.png'), 'Clear Tip', self)
        QtCore.QObject.connect(self.btn_clear_tip, QtCore.SIGNAL("clicked()"),self.clear_tip)
        
        #RachelWu 150727
        self.btn_next_step = QtGui.QPushButton(QtGui.QIcon('./rsc/fast_forward.png'), 'Next Stage', self)
        QtCore.QObject.connect(self.btn_next_step, QtCore.SIGNAL("clicked()"),self.next_step)

        self.btn_move_up = QtGui.QPushButton(QtGui.QIcon('./rsc/Arrow_Up.png'), 'Up (R)', self)
        self.btn_move_up.setToolTip('<b>R</b> - Manipulator Z-Up')
        ##QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_R), self, self.button_move_up)
        #QtGui.QShortcut(QtGui.QKeySequence(tr("Ctrl+p"), self, self.button_move_up)

        #QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_R), self, self.button_move_up)  
        QtCore.QObject.connect(self.btn_move_up, QtCore.SIGNAL("clicked()"),self.button_move_up)
        
        self.btn_move_down = QtGui.QPushButton(QtGui.QIcon('./rsc/Arrow_Down.png'), 'Down (F)', self)
        self.btn_move_down.setToolTip('<b>F</b> - Manipulator Z-Down')
        #QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_D), self, None, self.button_move_down)
        ##QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F), self, self.button_move_down)  
        QtCore.QObject.connect(self.btn_move_down, QtCore.SIGNAL("clicked()"),self.button_move_down)
        

        # self.btn_manipulator_status = QtGui.QPushButton(QtGui.QIcon('rsc\\patch.jpg'), 'Status (S)', self)
        # self.btn_manipulator_status.setToolTip('<b>S</b> - Manipulator Status')
        #QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_D), self, None, self.button_move_down)
        ##QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_S), self, self.button_move_down)  
        # QtCore.QObject.connect(self.btn_manipulator_status, QtCore.SIGNAL("clicked()"),self.button_manipulator_status)
        
        
        self.updatespeed_knob = self.create_knob()
        self.connect(self.updatespeed_knob, QtCore.SIGNAL('valueChanged(double)'),
            self.on_knob_change)
        self.knob_l = QtGui.QLabel('Update interval = %s (ms)' % self.updatespeed_knob.value())
        self.knob_l.setAlignment(Qt.Qt.AlignTop | Qt.Qt.AlignHCenter)
        lk=QtGui.QVBoxLayout()
        lk.addStretch(1)
        lk.addWidget(self.knob_l)
        lk.addWidget(self.updatespeed_knob)        
        
        self.label_thresholds=QtGui.QLabel( "<font color=\"navy\">Thresholds: {0:.4f} </font>".format(initialResistance * self.myConfig['TouchCellCoefficient']),self)
        self.label_deltadata2=QtGui.QLabel( "<font color=\"navy\">delta_data2: %s </font>" % self.DataVar.data2,self)
        lv = QtGui.QHBoxLayout()
        #lv.addStretch(1)
        lv.addWidget(self.btn_zero)
        #lv.addWidget(self.btn_power)
        #lv.addWidget(self.btn1) # valve 1 burst, irrelevant
        #lv.addWidget(self.btn2) # valve 2 burst, irrelevant
        lv.addWidget(self.btn3)
        lv.addWidget(self.btn4)
        lv.addLayout(lk)

        lth=QtGui.QHBoxLayout()
        lth.addWidget(self.label_thresholds)
        lth.addWidget(self.label_deltadata2)
        
        lu = QtGui.QHBoxLayout()
        lu0=QtGui.QVBoxLayout()
        lu0.addStretch(1)
        lu0.addWidget(self.label1)
        lu0.addWidget(self.btn_clear_tip)
#Rachel Wu 150727
        lu0.addWidget(self.btn_patch)
        lu0.addWidget(self.btn_next_step)

        
        lu1=QtGui.QVBoxLayout()        
        lu1.addStretch(1)        
        lu1.addWidget(self.btn_pump)
        lu1.addWidget(self.btn_pump_burst)
        lu2=QtGui.QVBoxLayout()
        lu2.addStretch(1)
        # 06/08/15 remove the button for the pump2
        #lu2.addWidget(self.btn_pump2)
        #lu2.addWidget(self.btn_pump2_burst)
        lw = QtGui.QVBoxLayout()
        lw.addStretch(1)
        # buttons to control the manipulator movement
        #lw.addWidget(self.btn_manipulator_status)        
        lw.addWidget(self.btn_move_up)
        lw.addWidget(self.btn_move_down)
        lu.addLayout(lu0)
        lu.addLayout(lu1)
        lu.addLayout(lu2)
        lu.addLayout(lw)
        

        
              
        l = QtGui.QVBoxLayout(self.main_widget) 
        # patcher         - no need for a separate canvas with QLabel label1 updating the patcher status
        #self.patcher_a=PatchCanvas(self.main_widget)
        #QtCore.QObject.connect(self.patcher_a, QtCore.SIGNAL("Signal_to_patch"),self.patch) 
        
        # Canvases for plotting

        lb = QtGui.QHBoxLayout()        
        self.testc=BarCanvas(self.main_widget,color='mediumseagreen', title='Pressure (mmHg)') 
        self.testd=BarCanvas(self.main_widget,color='firebrick', title='Resistance (MOhm)') 
        lb.addWidget(self.testc)
        lb.addWidget(self.testd)

        #sc = MyStaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        self.sc = MyDynamicMplCanvas(self.main_widget,color="mediumseagreen", title='Pressure (mmHg)')
        self.dc = MyDynamicMplCanvas(self.main_widget,color="firebrick", title='Current (nA)') #  06/08/15
                
        l.addWidget(self.sc)
        l.addWidget(self.dc)
        l.addLayout(lv)
        l.addLayout(lth)
        l.addLayout(lu)
        l.addLayout(lb)
        #l.addWidget(self.patcher_a)
        #l.addLayout(lu)
        #l.addLayout(lw)
        

        
        
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage("DAQ input plotting", 2000)
        
        BAUD = 19200 # 19200 for the Rig, 9600 for arduino
        # Port the Arduino\lolshield is on:
        PORT = 'COM1' # 2-photon room setup ports COM1, COM7, COM8 are recognized, COM1 works #'COM6' # 'COM4'- Gateway # COM6 - Tanya's PC # COM1 - Rig PC
        self.Speed='S'
        self.DelayInterval=0.05
        self.DelayInterval_move=0.2
        
        # if interface == None:
        #     self.MyUnit = ms.MssUnit(port=PORT, baudrate=BAUD,timeout=0.1)
        # else:
        #     self.MyUnit = self.interface.MyUnit[1] # MyUnit[0]

        time.sleep(1.5)
        
        """
        self.timer = QtCore.QTimer(self)
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.update_figures)
        self.timer.start(5)
        """
        self.timer = QtCore.QTimer(self)
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.update_figures)
        self.timer.start(self.global_timer_interval)

    def clear_tip(self):
        self.pin_switch(self.pin_outs['valve1'],0) # valve 1 to +pressure
        self.btn3.setChecked(False) # indicate the status of the valve by pressing/releasing the button
        self.pin_switch(self.pin_outs['valve2'],1) # switch valve 2 to inside (not atmosphere)
        self.btn4.setChecked(True)
        self.DataVar.DBitOut(BitNum=self.pin_outs['pump'],BitValue=1)
        #QtCore.QTimer.singleShot(pulse_latency,self.stop_clearing_tip)
        time.sleep(0.04)
    #def stop_clearing_tip(self):
        self.DataVar.DBitOut(BitNum=self.pin_outs['pump'],BitValue=0)
        self.pin_switch(self.pin_outs['valve2'],0) # switch valve 2 to atmosphere)
        self.btn4.setChecked(False)

#Rachel 150727
    def next_step(self):
        global marker_patch
        if marker_patch==1 or marker_patch==2 or marker_patch==3 or marker_patch==4 or marker_patch==5:
            marker_patch=marker_patch+1 

    def loadConfiguration(self):

        reader = csv.reader(open('.\configuration\PatchControlConfiguration.csv', 'rb'))
        self.myConfig = dict(x for x in reader)

        for key in self.myConfig:
            self.myConfig[key] = float(self.myConfig[key])

        print "Configuration:"
        print self.myConfig
        
        global pump_pulse
        pump_pulse = self.myConfig['PumpShortPulseTime']
        global pump_long_pulse
        pump_long_pulse = self.myConfig['PumpLongPulseTime']

        print "pump long pulse", pump_long_pulse
        print "pump short pulse", pump_pulse

        # with open('PatchControlThresholdCoefficient.csv', 'rb') as f:
        #     reader = csv.reader(f)
        #     self.myThresholdCoefficient = list(reader)[0]
        # for i,num in enumerate(self.myThresholdCoefficient):
        #     self.myThresholdCoefficient[i] = float(num)
        # print "Threshold Coefficients:"
        # print self.myThresholdCoefficient

        # global threshold_coefficients
        # threshold_coefficients = self.myThresholdCoefficient

        # print "Global Threshold Coefficients:"
        # print threshold_coefficients
        
    def keyPressEvent(self, event):
        if type(event) ==  QtGui.QKeyEvent:
            if (int(event.modifiers()) == QtCore.Qt.ControlModifier):
                #Control_X for saving patch control data
                if event.key() == QtCore.Qt.Key_X:
                    return
                if event.key() == QtCore.Qt.Key_L:
                    self.loadConfiguration()
        if self.owner != None:
            print "passed"
            self.owner.keyPressEvent(event)

    def keyReleaseEvent(self,event):
        if self.owner != None:
            self.owner.keyReleaseEvent(event)
        
    def create_knob(self):
        knob = Qwt.QwtKnob(self)
        knob.setRange(0, 1000, 0, 10)
        knob.setScaleMaxMajor(10)
        knob.setKnobWidth(50)
        knob.setValue(10)
        return knob 
        
    def on_knob_change(self):
        """ When the knob is rotated, it sets the update interval
            of the timer.
        """
        update_interval = self.updatespeed_knob.value()
        self.knob_l.setText('Update interval = %s (ms)' % self.updatespeed_knob.value())

        if self.timer.isActive():
            #update_interval = max(0.01, update_interval)
            self.timer.setInterval(update_interval)
            self.sc.set_timer_interval(update_interval)
            self.dc.set_timer_interval(update_interval)
    
    def button_power(self):
        #global marker_patch
        #marker_patch=marker_patch+1
        #print marker_patch
        if not 'power_switch' in globals():
            global power_switch
            print 'power_switch is not determined'
            power_switch=0
            
        global power_switch
        if power_switch==0:
            power_switch=1
            print 'power_switch=',power_switch
            
                        
            #self.DataVar.DOut(PortNum=UL.FIRSTPORTA, digitalpattern=0b111111111111111111)
            #self.DataVar.DBitOut(PortNum=UL.FIRSTPORTB,BitNum=7,BitValue=1)
            self.DataVar.DBitOut(PortNum=UL.FIRSTPORTA,BitNum=self.pin_outs['power'],BitValue=1) # Somehow, Universal library doesn't have UL.FIRSTPORTB, instead it uses UL.FIRSTPORTA, Bit=BitNumber+8 (2nd byte for portB input)
        else:
            power_switch=0
            print 'power_switch=',power_switch
            
            #self.DataVar.DOut(PortNum=UL.FIRSTPORTA, digitalpattern=0b000000000000000000)
            #self.DataVar.DBitOut(PortNum=UL.FIRSTPORTB,BitNum=7,BitValue=0)
            self.DataVar.DBitOut(PortNum=UL.FIRSTPORTA,BitNum=self.pin_outs['power'],BitValue=0) # Somehow, Universal library doesn't have UL.FIRSTPORTB, instead it uses UL.FIRSTPORTA, Bit=BitNumber+8 (2nd byte for portB input)
        
        
    def update_figures(self):
        # GetMeterValue Parameter:
        # 3 is the IC on channel 2; 2 is VC on channel 2; 1 is IC on channel 1; 0 is DC on channel 1
        #membraneCurrent = self.mcc.getMeterValue(3)
        #print "MembraneCurrent is ", membraneCurrent

        if len(self.DataVar.data1)>history_shown:
            self.sc.set_data(self.DataVar.data1[-history_shown:])
            self.dc.set_data(self.DataVar.data2[-history_shown:])
        else:
            self.sc.set_data(self.DataVar.data1)
            self.dc.set_data(self.DataVar.data2)
        #self.patcher_a.set_data(self.DataVar.data2)

        if(len(self.DataVar.data1)>=1):
            self.testc.set_data(self.DataVar.data1[-1])
        
        # Resistance, 06/08/15
        #self.testd.set_data(np.max(self.DataVar.data2[-10:])-np.min(self.DataVar.data2[-10:]))
        #self.testd.set_data(2.6/(np.max(self.DataVar.data2[-40:])-np.min(self.DataVar.data2[-40:]) + 0.000000000001))
        #Rachel Wu 150718 trying to fit gigaseal resistance at 1000MOhm
        #invert_current=1/(np.max(self.DataVar.data2[-40:])-np.min(self.DataVar.data2[-40:]) + 0.000000000001)
        #current_resistance = 0.0744*invert_current*invert_current+2.1556*invert_current+0.6293
        current_resistance=self.calculateResistance()
        if current_resistance > 10000.0:
            current_resistance = 9999
        self.testd.set_data(current_resistance)
        # patch if/elseif patching decision        
        self.patch()

    def slot1(self):
        if self.valve_status1==0:
            self.valve_status1=1
            self.DataVar.DBitOut(BitNum=self.pin_outs['valve1'],BitValue=1) # Doesn't send zeros to other Bits (ports)          
            time.sleep(0.5)
            print 'valve 1 open'
        else:
            self.valve_status1=0
            self.DataVar.DBitOut(BitNum=self.pin_outs['valve1'],BitValue=0)  
            time.sleep(0.5)
            print 'valve 1 close'
    
    def slot1_brief(self):
        self.DataVar.DBitOut(BitNum=self.pin_outs['valve1'],BitValue=1) # Doesn't send zeros to other Bits (ports)         
        time.sleep(0.01)
        print 'valve 1 open'
        #self.DataVar.DOut(digitalpattern=0b000)
        self.DataVar.DBitOut(BitNum=self.pin_outs['valve1'],BitValue=0) 
        print 'valve 1 close'
            
        
    def slot2(self):
        if self.valve_status2==0:
            self.valve_status2=1
            self.DataVar.DBitOut(BitNum=self.pin_outs['valve2'],BitValue=1)            
            time.sleep(0.5)
            print 'valve 2 open'
        else:
            self.valve_status2=0
            self.DataVar.DBitOut(BitNum=self.pin_outs['valve2'],BitValue=0)  
            time.sleep(0.5)
            print 'valve 2 close'
            
    def slot2_brief(self):
        self.DataVar.DBitOut(BitNum=self.pin_outs['valve2'],BitValue=1)          
        time.sleep(0.01)
        print 'valve 2 open'
        self.DataVar.DBitOut(BitNum=self.pin_outs['valve2'],BitValue=0)  
        print 'valve 2 close'
            
    def pump_switch(self):
        if self.pump_status==0:
            self.pump_status=1
            self.DataVar.DBitOut(BitNum=self.pin_outs['pump'],BitValue=1)  
            print 'pump_on'
        else:
            self.pump_status=0
            self.DataVar.DBitOut(BitNum=self.pin_outs['pump'],BitValue=0)
            print 'pump_off'
    
    def pump_burst(self,pulse_latency=pump_pulse): 
        self.DataVar.DBitOut(BitNum=self.pin_outs['pump'],BitValue=1)
        QtCore.QTimer.singleShot(pulse_latency,self.singleShot_pump_off) # 25 ms pump for the new strong pump 01/14/13. This slot changes ok_to_go to 1
        if self.btn_pump.isChecked(): # if the btn_pump is checked - toggle it off
            self.btn_pump.toggle()
        #QtCore.QTimer.singleShot(100,self.singleShot_pump_off) # time.sleep(3) # time.sleep(0.05) # not a good solution - freezes the program, not updating the data, use Qtimer.singleShot instead
        #self.DataVar.DBitOut(BitNum=self.pin_outs['pump'],BitValue=0) # pump is switched off in the singleShot_pump_off slot
    def pump_long_burst(self,pulse_latency=pump_long_pulse): 
        self.DataVar.DBitOut(BitNum=self.pin_outs['pump'],BitValue=1)
        QtCore.QTimer.singleShot(pulse_latency,self.singleShot_pump_off) # 25 ms pump for the new strong pump 01/14/13. This slot changes ok_to_go to 1
        if self.btn_pump.isChecked(): # if the btn_pump is checked - toggle it off
            self.btn_pump.toggle()
        #QtCore.QTimer.singleShot(100,self.singleShot_pump_off) # time.sleep(3) # time.sleep(0.05) # not a good solution - freezes the program, not updating the data, use Qtimer.singleShot instead
        #self.DataVar.DBitOut(BitNum=self.pin_outs['pump'],BitValue=0) # pump is switched off in the singleShot_pump_off slot
    
    def pump2_switch(self):
        if self.pump2_status==0:
            self.pump2_status=1
            self.DataVar.DBitOut(BitNum=self.pin_outs['pump2'],BitValue=1)  
            print 'pump2_on'
        else:
            self.pump2_status=0
            self.DataVar.DBitOut(BitNum=self.pin_outs['pump2'],BitValue=0)
            print 'pump2_off'
    
    def pump2_burst(self,pulse_latency=pump2_pulse):
        self.DataVar.DBitOut(BitNum=self.pin_outs['pump2'],BitValue=1)
        QtCore.QTimer.singleShot(pulse_latency,self.singleShot_pump2_off) # this slot changes ok_to_go to 1
        if self.btn_pump2.isChecked(): # if the btn_pump is checked - toggle it off
            self.btn_pump2.toggle()
        #QtCore.QTimer.singleShot(100,self.singleShot_pump_off) # time.sleep(3) # time.sleep(0.05) # not a good solution - freezes the program, not updating the data, use Qtimer.singleShot instead
        #self.DataVar.DBitOut(BitNum=self.pin_outs['pump'],BitValue=0) # pump is switched off in the singleShot_pump_off slot
        
              
    def pin_switch(self,pin_number=0,value=0):
        return self.DataVar.DBitOut(BitNum=pin_number,BitValue=value)

    def calculateResistance(self):
        global delta_data2
        delta_data2 = np.max(self.DataVar.data2[-50:])-np.min(self.DataVar.data2[-50:])
        invert_current=1/(delta_data2 + 0.000000000001)
        if delta_data2>0.0684:
            temporary_resistance=-0.0119*(invert_current**3)+0.3025*(invert_current**2)+5.2925*invert_current-0.4507
        else:
            temporary_resistance=81.794*invert_current-1091.9
        return temporary_resistance

        # Example resistance = calculateResistance()
        
    def patch(self): 
        # need to update this on timer - calling from the update_figures function
        global marker_patch
        global ok_to_go,ok_to_go2
        global move_counter
        global initialResistance
        global zap_hold
        global csvDictionary
        self.label1.setText("<font color=\"navy\">Patch step: {0} </font>".format(marker_patch)) # update the QLabel with the marker_patch status
        self.label_thresholds.setText("<font color=\"firebrick\">Thresholds:<br/> Pipette Resistance:{0:.4f}<br /> Touch Cell:{1:.4f}<br/> Spontaneous Gigaseal:{2:.4f}<br/> Forming Gigaseal:{3:.4f}<br/>Gigaseal Formed:{4:.4f} </font>".format(initialResistance, initialResistance*self.myConfig['TouchCellCoefficient'], self.myConfig['SpontaneousGigaSealResistance'],  self.myConfig['FormingGigaSealResistance'], self.myConfig['GigaSealFormedResistance']))
        
        delta_data2 = 0.0

        
        if len(self.DataVar.data2)>50:
            #delta_data2=2.6/(np.max(self.DataVar.data2[-40:])-np.min(self.DataVar.data2[-40:]) + 0.000000000001) # difference between max and min Vm
            #Rachel Wu 150718 trying to fit gigaseal resistance at 1000MOhm
            #delta_data2 = np.max(self.DataVar.data2[-20:])-np.min(self.DataVar.data2[-20:])
            #invert_current=1/(delta_data2 + 0.000000000001)
            #current_resistance=(0.0744*invert_current*invert_current+2.1556*invert_current+0.6293)
            current_resistance=self.calculateResistance()
            self.resistance_list.append(current_resistance)
        elif len(self.DataVar.data2)<=1:
            current_resistance=self.DataVar.data2
        else:
            current_resistance=np.max(self.DataVar.data2)-np.min(self.DataVar.data2)

        self.label_deltadata2.setText( "<font color=\"firebrick\">current_difference: {0:.4f} </font>".format(delta_data2))
        
        if marker_patch==0: #not patching            
            move_counter=0
            
        elif marker_patch==0.5: # command to patch

            # #test
            # if ok_to_go==1:
            #     self.button_move_down() # moving a small step down, see again if the deltaVm is within the threshold on the next cycle (button_move_down uses time.sleep(DelayInterval), DelayInterval=0.050)
            #     ok_to_go=0
            # return
            # #test
            self.timer_fail = None
            self.pin_switch(self.pin_outs['valve1'],0) # valve 1 to +pressure
            self.btn3.setChecked(False) # indicate the status of the valve by pressing/releasing the button
            self.pin_switch(self.pin_outs['valve2'],1) # switch valve 2 to inside (not atmosphere)
            self.btn4.setChecked(True)
            if self.DataVar.data1[-1]<self.myConfig['MinimumPositivePressure']:
                self.pump_burst()
                

            if self.DataVar.data1[-1]>self.myConfig['MinimumPositivePressure']:
                
                if len(self.resistance_list) > 200:
                    #initialResistance=np.median((self.resistance_list[-10:-1]).append(self.resistance_list[-1]))
                    
                    if (np.max(self.resistance_list[-50:]) - np.min(self.resistance_list[-50:])) <= 1 :
                        initialResistance=np.median(self.resistance_list[-50:])        # assigning the delta_data2 thresholds based on the initial delta_data2 value and the threshold_coefficients
                        # initialResistance=self.calculateResistance()
                        csvDictionary['InitialResistance'] = initialResistance
                        timeString = str(datetime.datetime.now())
                        csvDictionary['StartTime'] = timeString

                        if initialResistance>self.myConfig['MaximumPipetteResistance']:
                            QtGui.QMessageBox.information(self,'', 'Pipette clogged. Please clear tip or change pipette and try again.')
                            self.mcc.setTestSignalEnable(False)
                            self.mcc.setHoldingEnable(False)            
                            self.mcc.setMode(2)
                            marker_patch=0                               #reject trial if the initial Rp is too big
                        else:                                            
                            move_counter=0
                            marker_patch=1
                            ok_to_go=1
        elif marker_patch==1: # stage 1 - positive pressure
            if ok_to_go==1:
                if self.DataVar.data1[-1]<self.myConfig['MinimumPositivePressure']:
                    print "pressure smaller than ", self.myConfig['MinimumPositivePressure']
                    self.pin_switch(self.pin_outs['valve1'],0) # valve 1 to +pressure
                    self.btn3.setChecked(False) # indicate the status of the valve by pressing/releasing the button
                    self.pin_switch(self.pin_outs['valve2'],1) # switch valve 2 to inside (not atmosphere)
                    self.btn4.setChecked(True)
                    self.pump_burst() # brief pulse of the pump2 - weaker pump, pump - 12V, pump2 - 5V
                    #QtCore.QTimer.singleShot(5000,self.singleShot_slot)
                    ok_to_go=0 # back to 1 after the end of pump_burst
                else:            
                    marker_patch=2
        elif marker_patch==2:
            if current_resistance>(initialResistance*self.myConfig['TouchCellCoefficient']): # checking for the corresponding matching deltaVm change, indicating cell touched
                marker_patch=2.5
            else:
                if ok_to_go==1:
                    if self.DataVar.data1[-1]<self.myConfig['MinimumPositivePressure']:
                        marker_patch=1
                    if move_counter<move_limit:
                        self.button_move_down() # moving a small step down, see again if the deltaVm is within the threshold on the next cycle (button_move_down uses time.sleep(DelayInterval), DelayInterval=0.050)
                        ok_to_go=0
                        move_counter=move_counter+1
                        print 'move_counter',move_counter # potentially indicate the current position in the GUI (Z in micrometers)
                    else:
                        print "Move limit exceeded. Patching failed."
                        marker_patch=7 # send to the last if - condition related to the unsuccessful patch
            """+
            else: # simplified continuation to the next step without the deltaVm data
                print "pressure threshold reached - moving to step 2"
                marker_patch=2
            """

            
                
        elif marker_patch==2.5: # stage 2 - atmosphere
            if ok_to_go==1:
                # valve 2 to atmosphere:
                self.pin_switch(self.pin_outs['valve2'],0)
                self.btn4.setChecked(False)
                # valve 1 to -pressure
                self.pin_switch(self.pin_outs['valve1'],1)
                self.btn3.setChecked(True)# SpontaneousPatchTime
                #QtCore.QTimer.singleShot(2000,self.singleShot_slot) # need to wait till it's done
                QtCore.QTimer.singleShot(self.myConfig['SpontaneousPatchTime'],self.singleShot_slot) # need to wait till it's done
                ok_to_go=0
                
                if current_resistance<self.myConfig['SpontaneousGigaSealResistance']: # if not tight enough patch (no giga-seal yet) go to stage 3, otherwise stage 4
                    #QtGui.QMessageBox.information(self, '2 to 3', "data is %d threshold is %d" %(delta_data2, thresholds[1,2]))
                    marker_patch=3
                else:
                    marker_patch=4
                
        elif marker_patch==3: # stage 3 - small suction
            # print "to go 1 :", ok_to_go
            # print "to go 2 :", ok_to_go2
            if self.timer_fail is None:
                self.timer_fail = datetime.datetime.now()
            else:
                elapsed = datetime.datetime.now() - self.timer_fail
                if elapsed > datetime.timedelta(minutes=4):
                    print "Time exceeded 4 mins. Patching failed."
                    print "start at time:", self.timer_fail
                    print "fail at time:", datetime.datetime.now()
                    marker_patch = 7
            
            #print "Current Resistance is ", current_resistance, " threshold is ", self.myConfig['FormingGigaSealResistance']
            #if (self.pop_holding == 0) & (current_resistance > 50):#90
            if (self.pop_holding == 0) & (np.min(self.resistance_list[-10:-1])>50):
                """
                mcc control set holding -30
                """
                #if self.mcc.Mode != 0 or self.mcc.HoldingEnable != True:
                self.mcc.setMode(0);
                self.mcc.setHoldingEnable(True);
                self.mcc.setHoldingPotential(-0.03)
                self.pop_holding = 1
                    
            #if (self.pop_holding == 1) & (current_resistance > 100):#90
            if (self.pop_holding == 1) & (np.min(self.resistance_list[-10:-1])>90):
 
                """
                mcc control set holding -70
                """
                #if self.mcc.Mode != 0 or self.mcc.HoldingEnable != True:
                self.mcc.setMode(0);
                self.mcc.setHoldingEnable(True);
                self.mcc.setHoldingPotential(-0.07)

                self.pop_holding = 2
                # QtGui.QMessageBox.information(self, '', 'Please, switch to V=-70 mV')
            if np.min(self.resistance_list[-10:-1])>self.myConfig['FormingGigaSealResistance']:    
                    marker_patch=4

            if (ok_to_go==1)&(ok_to_go2==1) & ((self.DataVar.data1[-1]) > self.myConfig['MinimumNegativePressure']):
                #if current_resistance>self.myConfig['FormingGigaSealResistance']:
                #if np.min(self.resistance_list[-10:-1])>self.myConfig['FormingGigaSealResistance']:    
                    #marker_patch=4                

                # valve 2 to inside:
                self.pin_switch(self.pin_outs['valve2'],1)
                self.btn4.setChecked(True)
                # valve 1 to -pressure
                self.pin_switch(self.pin_outs['valve1'],1)
                self.btn3.setChecked(True)
                # burst of suction
                #self.pump2_burst() # brief pulse of the weaker pump, repeated non-stop (can change to pump_burst with the following SingleShot)
                self.pump_burst() # stronger pump
                #QtCore.QTimer.singleShot(3000,self.singleShot_slot)#SmallSuctionTime
                QtCore.QTimer.singleShot(self.myConfig['SmallSuctionTime'],self.singleShot_slot)#SmallSuctionTime
                ok_to_go=0
                ok_to_go2=0
        elif marker_patch==4: # stage 4 - wait for giga-seal to form:
            # self.mcc.setMode(0);
            # self.mcc.setHoldingEnable(True);
            # self.mcc.setHoldingPotential(-0.07)            
            if ok_to_go==1:
                if np.min(self.resistance_list[-100:-1])>self.myConfig['GigaSealFormedResistance']:
                #if current_resistance>self.myConfig['GigaSealFormedResistance']:
                    csvDictionary['GigasealResistance'] = current_resistance;
                    csvDictionary['GigasealTime'] = str(datetime.datetime.now())
                    global zap_hold
                    zap_hold=0 #make sure it does not directly zap
                    marker_patch=5
                #elif current_resistance<=self.myConfig['FormingGigaSealResistance']:
                elif np.max(self.resistance_list[-10:-1])<=self.myConfig['FormingGigaSealResistance']: # seal worsened - go back to small suctions, stage 3
                    ok_to_go=1
                    ok_to_go2=1
                    marker_patch=3
                else: # wait for the giga seal to form
                    #QtCore.QTimer.singleShot(1000,self.singleShot_slot)#GigaSealChecktime
                    QtCore.QTimer.singleShot(self.myConfig['GigaSealCheckTime'],self.singleShot_slot)#GigaSealChecktime
                    ok_to_go=0

        
        elif marker_patch==5: # stage 5 - break-in
            global file_save_bool
            
            if ok_to_go==1:                
                #if current_resistance<self.myConfig['BrokenInResistance']: # jump in current command after break in
                if np.max(self.resistance_list[-20:-1])<self.myConfig['BrokenInResistance']:  # account for unstable resistance calculation
                    Ihold = self.mcc.getMeterValue(3)
                    if Ihold > (-200*0.0000000000001) # Ihold needs to be bigger than -200 pA when R dropped to indicate broke-in
                        global file_save_bool
                        file_save_bool = 0
                        marker_patch=6
                    else:
                        marker_patch = 7 # Ihold dropped to lower than -200 pA means that we lost the patch after gigasealup
                
                    """
                    self.pump_switch()
                    QtCore.QTimer.singleShot(1000,self.singleShot_pump_off)
                    ok_to_go=0                
                    """
                else:
                    # Apply Zap popup
                    """
                    mcc control choose to zap
                    """
                    global zap_bool
                    global zap_hold
                    if zap_bool is False:
                        zap_bool = True
                        msg = "Wanna Zap?"
                        reply = QtGui.QMessageBox.question(self, 'Message', msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                        if reply == QtGui.QMessageBox.Yes:
                            zap_hold=1


                    # if self.pop_holding_zap is False:
                    #     self.pop_holding_zap = True
                    #     QtGui.QMessageBox.information(self, '', 'Apply ZAP!')
                    if (ok_to_go2==1) & ((self.DataVar.data1[-1]) > self.myConfig['MinimumNegativePressure']):
                        # valve 2 to inside:
                        print "break in time ", self.myConfig['BreakInTime']
                        self.pin_switch(self.pin_outs['valve2'],1)
                        self.btn4.setChecked(True)
                        # valve 1 to -pressure
                        self.pin_switch(self.pin_outs['valve1'],1)
                        self.btn3.setChecked(True)
                        self.pump_burst() # burst of the stronger pump
                        if zap_hold==1:
                            self.mcc.zap()
                            print "zapped"
                        ok_to_go=0
                        ok_to_go2=0
                        #QtCore.QTimer.singleShot(2000,self.singleShot_slot) # BreakInTime need to wait a little, otherwise, non-stop pumping
                        QtCore.QTimer.singleShot(self.myConfig['BreakInTime'],self.singleShot_slot) # BreakInTime need to wait a little, otherwise, non-stop pumping
                        
                    
                                            
        elif marker_patch==6: # stage 6 - broke in
            """
            mcc holding enable clear
            mcc control stop pulsing
            mcc control switch to holding potential in vc -0.07v mode

            """
            #if self.mcc.Mode != 1 or self.mcc.HoldingEnable != True:
                # self.mcc.setPulseEnable(False);
            csvDictionary['BrokenInResistance'] = current_resistance
            timeString = str(datetime.datetime.now())
            csvDictionary['EndTime'] = timeString

            self.mcc.setTestSignalEnable(False);
            self.mcc.setMode(2);  # Mode vc is 0, mode ic is 1, mode ie0 is 2
                # self.mcc.setHoldingPotential(-0.07);
            self.mcc.setHoldingEnable(False);
            
                       

            global file_save_bool
            # if current_resistance > 300:
            #     marker_patch = 5
            print "At Step 6 file save boolean is ",  file_save_bool
            print "At Step 6 ok to go is ", ok_to_go
            if (ok_to_go==1) & (file_save_bool==0):
                name = "./Experiment_Data/Resistance_auto_save/" + timeString + "RT"
                f = open(name.replace(":", "_"), 'w');
                f.write(str(csvDictionary))
                f.close(); 
                file_save_bool = 1
                ok_to_go=0
                QtGui.QMessageBox.information(self,'','Patch established. Please save patchlog')                
                self.fileSave()

            elif file_save_bool==1:
                marker_patch = 0
                #marker_patch=0
                #self.fileQuit()
                
            
                
        elif marker_patch==7: # marker_patch==7 - patching unsuccessful
            QtGui.QMessageBox.information(self,'', 'Patch unsuccessful. Please save patchlog, change pipette, and restart')
            self.fileSave()
            self.mcc.setTestSignalEnable(False)
            self.mcc.setHoldingEnable(False)            
            self.mcc.setMode(2)
            marker_patch=0
            #self.fileQuit()
           


    def singleShot_slot(self):
        global ok_to_go, ok_to_go2
        print "singleShot slot invoked"
        ok_to_go=1        
        ok_to_go2=1 # second flag for waiting specifically, to separate from the pump
        
    def singleShot_pump_off(self): # singleShot_pump_off evoked by the pump_burst to switch the pump off after a delay
        global ok_to_go
        print "singleShot evoked by the pump"        
        self.DataVar.DBitOut(BitNum=self.pin_outs['pump'],BitValue=0)
        ok_to_go=1

    def singleShot_pump2_off(self): # singleShot_pump_off evoked by the pump_burst to switch the pump off after a delay
        global ok_to_go
        print "singleShot evoked by the pump2"        
        self.DataVar.DBitOut(BitNum=self.pin_outs['pump2'],BitValue=0)
        ok_to_go=1
    
    
    def button_patch(self):
        
        global zap_bool
        zap_bool = False
        
        global marker_patch
        self.pop_holding = 0
        self.pop_holding_zap = False
        
        global zap_hold

        #initialize multiclamp driver Rachel 01202016
    
        if marker_patch==0:
            """
            MCC control start test signal
             MCCcontrol pipette auto offset
             MCC control test signal, amplitude and frequency

            """
            #self.clear_tip()
            self.mcc.setMode(0)
            #self.mcc.setMode(2)
            self.mcc.setHoldingEnable(False)
            self.mcc.setMode(0)            
            #self.mcc.setPulseInterval(20)
            #self.mcc.setPulseAmplitude(0.005)
            #self.mcc.setPulseEnable(True)
            self.mcc.AutoPipetteOffsetEnbale(True)
            self.mcc.setMode(0)
            QtCore.QTimer.singleShot(1500, self.membraneTest)
            #self.mcc.setTimeOut(3)                       #wait 3s for pipette offset to finish
            # self.mcc.AutoPipetteOffsetEnbale(True);
            # self.mcc.AutoPipetteOffsetEnbale(True);
            #QtGui.QMessageBox.information(self, '', 'Please Switch to Voltage Clamp and Initiate Membrane Test')            
            # self.mcc.getTestSignalFrequency()
            # self.mcc.getTestSignalAmplitude()
            # print "frequency is", self.mcc.getTestSignalFrequency(),"amplitude is", self.mcc.getTestSignalAmplitude
            #print "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD"
        else:           
            self.mcc.setTestSignalEnable(False)
            self.mcc.setHoldingEnable(False)            
            self.mcc.setMode(2)
            marker_patch=0
            # self.mcc.setPulseEnable(False)
            
    def membraneTest(self):
        global marker_patch
        self.mcc.setTestSignalEnable(True)
        self.mcc.setHoldingEnable(False)
        self.mcc.setTestSignalFrequency(0.02)           #0.1=10Hz 0.06=20Hz 0.01=100Hz 0.02=50Hz
        self.mcc.setTestSignalAmplitude(0.005)         #Coorespond to resistance calculation. Default as 5mV.

        self.button_zero()

        marker_patch=0.5

    # """
    # def button_move_down(self,step=step_size):
    #     a='#3!DS%+011.4f' %step        
    #     #a='#3!'+self.Speed+'+'
    #     #a='#3!E+'
        
    #     #for i in range(20):
        
        
    #     self.MyUnit.talk(a) 
    #     #time.sleep(self.DelayInterval_move)
    #     QtCore.QTimer.singleShot(1000,self.singleShot_move_stop)
    #     #a='#3!A'
    #     #self.MyUnit.talk(a) 

    # def button_move_up(self,step=step_size):       
    #     a='#3!DS%+011.4f' %-step      
    #     #a='#3!'+self.Speed+'-'
    #     #a='#3!E-'
        
    #     #for i in range(20):
        
    #     self.MyUnit.talk(a) 
    #     #time.sleep(self.DelayInterval_move)
    #     QtCore.QTimer.singleShot(1000,self.singleShot_move_stop)
    #     #a='#3!A'
    #     #self.MyUnit.talk(a)
    #     """
    def button_manipulator_status(self):
        # the motors are numbered 1-6, 1-3 for only one manipulator        
        for i in range(1,2): # important! - running this cycle results in a positive response code 0x10 for the 7th device - don't know why
            a='#'+str(i)+'?Z' # only #7?Z works, not #7?P
            response=self.MyUnit.talk(a)
            time.sleep(0.1)
            Manipulator_coords.append(response)
        
    def button_move_down(self,step=step_size):
        # #a='#1!DS%+011.4f' %step        
        # #a='#1!'+self.Speed+'+'
        # a='#2!E+'
        # #self.MyUnit.talk(a)
        # #for i in range(20):
        print "moving down, step size",  step_size
        MSSInterface.moveToRelWithoutWaiting(2,0,0,0, abs(step_size))
        #time.sleep(self.DelayInterval_move)
        QtCore.QTimer.singleShot(1500,self.singleShot_move_stop)
        #a='#3!A'
        #self.MyUnit.talk(a)
        
    def button_move_up(self,step=step_size):       
        #a='#1!DS%-011.4f' %-step      
        #a='#1!'+self.Speed+'-'
        # #a='#1!E-'
        
        #for i in range(20):
        
        # #self.MyUnit.talk(a) 
        #time.sleep(self.DelayInterval_move)
        print "moving down, step size",  step_size

        MSSInterface.moveToRelWithoutWaiting(2,0,0,0, -abs(step_size))

        QtCore.QTimer.singleShot(1000,self.singleShot_move_stop)
        #a='#3!A'
        #self.MyUnit.talk(a)
        
    def button_zero(self):
        self.DataVar.data1=[]
        self.DataVar.data2=[]
        self.DataVar.times=[0]
        Manipulator_coords=[]
        
   
    def singleShot_move_stop(self):
        global ok_to_go
        print "manipulator has moved"
        ok_to_go=1
        
       
    def fileSave(self):
        
        fname = QtGui.QFileDialog.getSaveFileName(self, 'Save file', 
        './Experiment_Data/Patch_log/','HDF5 (*.h5);; MAT (*.mat)')
        if fname[-3:]=='mat':
            fh=scipy.io.savemat(str(fname), mdict={'data':self.DataVar.data1,'data2':self.DataVar.data2,'coord':Manipulator_coords})
        else:
            fh=h5py.File(str(fname))
            if 'data' in fh: # looking for the dataset 'data' - essentially a list or a numpy array
                del fh['data'] # if exists, deleting the dataset, otherwise 
            # saves the global variable data1 (doesn't need to declare global data1 if not altering the value)
            if 'data2' in fh:
                del fh['data2']
            dset=fh.create_dataset('data',data=self.DataVar.data1) # creating it and saving my data into this dataset
            dset2=fh.create_dataset('data2',data=self.DataVar.data2)  
            dset3=fh.create_dataset('coord',coord=Manipulator_coords)
            fh.close()
        
    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtGui.QMessageBox.about(self, "About %s" % __progname__,
u"""%(prog)s version %(version)s
Copyright \N{COPYRIGHT SIGN} 2012 Alex Chubykin
Integration of matplotlib plotting in PyQt of the Digitally acquired input in the Measurement Computing USB-1208FS DAQ Board

""" % {"prog": __progname__, "version": __version__})



def main():
    qApp = QtGui.QApplication(sys.argv)

    
    # Create and display the splash screen
    splash_pix = QtGui.QPixmap('./rsc/FluorNeuron.jpg')
    splash = QtGui.QSplashScreen(splash_pix)
    splash.show()
    splash.showMessage("Autopatcher Loading...", color = QtCore.Qt.white)
    qApp.processEvents()
    
    # Simulate something that takes time
    time.sleep(2)
    
    # main application window
    aw = ApplicationWindow()
    aw.setWindowTitle("%s" % __progname__)
    #aw.resize(750, 550)
    aw.show()
    # close the splashscreen
    splash.finish(aw)
    
    sys.exit(qApp.exec_())
    #qApp.exec_()

if __name__ == "__main__":
    main()
