import re
from datetime import datetime
import inspect as ins
from sys import stdout,stdin
from time import sleep
from ctypes import *
from time import sleep
import time
#import inspect as ins
import os
import threading
from mcc import mccControl
from IPython import embed
import signal
import sys

"""
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

class MCCThread(threading.Thread):

	def __init__(self):
		super(MCCThread, self).__init__()

		#Constants
		self.IC_Mode = 1;
		self.VC_Mode = 0;
		self.MCC_DLLPATH = "./DLL/"


		#  Variables
		self.HoldingPotential = 0.07;
		self.HoldingEnable = False
		# self.PulseEnable = False
		# self.PulseAmplitude = 0.05 
		# self.PulseInterval = 20 						#in milli seconds
		# self.PulseFrequency = 1000/self.PulseInterval 	#in  Hz
		self.TestSignalEnable = False
		self.TestSignalAmplitude = 0.05           #in mV
		self.TestSignalFrequency = 60              #in Hz

		self.Mode = self.VC_Mode
		self.HoldingEnable = False;									


		#initialize handle
		self.mcc = (mccControl(dllPath = "./DLL"))



		self.lastPulseTime = None;
		self.accumulateCycle = 0;
		self.stopBoolean = False;


	def run(self):
		while self.stopBoolean is False:
			self.accumulateCycle = self.accumulateCycle + 1;
			if((self.accumulateCycle*10) >= self.PulseInterval and self.PulseEnable):
				# Clear Accumulate Count
				self.accumulateCycle = 0;
				# Perform Pulse
				self.mcc.Pulse();


		time.sleep(0.005);	#sleep thread for 10 milli seconds

	def setHoldingPotential(self, hP):
		self.HoldingPotential = hP;
		self.mcc.SetHolding(hP);

	def setHoldingEnable(self, hE):
		self.HoldingEnable = hE;
		self.mcc.SetHoldingEnable(hE);

	# def setPulseEnable(self, pE):
	# 	self.PulseEnable = pE;

	# def setPulseAmplitude(self, pA):
	# 	self.PulseAmplitude = pA;
	# 	self.mcc.SetPulseAmplitude(pA);
		
	# def setPulseInterval(self, pI):
	# 	self.PulseInterval = pI;
	# 	self.PulseFrequency = 1000/self.PulseInterval; 

	# def setPulseFrequency(self, pF):
	# 	self.PulseFrequency = pF;
	# 	self.PulseInterval = 1000/pF;

	def setTestSignalEnable(self, TS):
		self.TestSignalEnable = TS;
		

	def setTestSignalAmplitude(self, TSA):
		self.TestSignalAmplitude = TSA;
		self.mcc.SetTestSignalAmplitude(TSA);

	def setTestSignalFrequency(self, TSF):
		self.TestSignalFrequency = TSF;
		self.mcc.SetTestSignalFrequency(TSF);

	def setTimeOut(self):
		self.mcc.SetTimeOut();

	def zap(self):
		self.mcc.Zap();

	def AutoPipetteOffsetEnbale(self, aPOE):
		self.mcc.AutoPipetteOffset();
		
	def setMode(self, m):
		self.Mode = m;
		self.HoldingEnable = True
		self.mcc.SetMode(m);

def setMode(self, m):
		self.Mode = m;
		self.HoldingEnable = True
		self.mcc.SetMode(m);

setMode(self,1)	




# print "main"
# t = MCCThread();

# try:
# 	t.start();
# except KeyboardInterrupt:
# 	t.stopBoolean = True;
# 	t.join();
# 	exit();
# tt = 0;
# t.setPulseEnable(True)
# t.setPulseInterval(20)
# t.setPulseAmplitude(0.010)

# while True:
# 	print "Pulse"
# 	print t.PulseEnable


# 	tt = tt + 1;
# 	if ((tt%2) == 0):
# 		t.setPulseEnable(True);
# 	else:
# 		t.setPulseEnable(False);

# 	if(tt > 30):
# 		t.stopBoolean = True;
# 		break;
# 	if tt == 29:
# 		t.zap()

# 	time.sleep(2);



