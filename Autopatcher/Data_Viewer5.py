# -*- coding: utf-8 -*-
"""

Data_Viewer.py
ver 0.2 - loading both data and data2
ver 0.3 - added matplotlib NavigationToolbar to the canvases

ver 0.4_2 - trying to share axis X
ver 0.5 - import Open Ephys .continuous data format 12/25/12

Created on Sun Jan 08 16:48:30 2012
combines loading data, pyqt, matplotlib plotting

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

@Author:  Alexander A. Chubykin

"""

__author__="Alex Chubykin"
__version__="version 0.5"
__date__="Sun Jan 08 16:48:30 2012"
__copyright__="Copyright (c) 2012 Alex Chubykin"
__license__="Python"

import sys, os, random
from PyQt4 import QtGui, QtCore

ComputerName=os.getenv('COMPUTERNAME')
if ComputerName=='BEARLABAXON-VII':
    dropbox_folder='f:\\Dropbox\\'
    sys.path.append('f:\\Dropbox\\python_projects\\abf_analysis\\')
elif ComputerName=='Tanya-PC':
    dropbox_folder='c:\\Users\\Alex\\Documents\\My Dropbox\\'
    sys.path.append('c:\\Users\\Alex\\Documents\\My Dropbox\\python_projects\\abf_analysis\\')
elif ComputerName=='Gateway':
    dropbox_folder='f:\\My Dropbox\\'
    sys.path.append('f:\\My Dropbox\\python_projects\\abf_analysis\\')
elif ComputerName=='AC-Ubuntu':
    dropbox_folder='\\home\\alex\\Dropbox\\'
    sys.path.append('/home/alex/Dropbox/python_projects/abf_analysis/')
else:
    dropbox_folder='f:\\Dropbox\\'
    sys.path.append('f:\\Dropbox\\python_projects\\abf_analysis\\') 

print "We are running under:",os.name
print dropbox_folder

import read_OpenEphys as rOE

from numpy import arange, sin, pi
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure

#import UniversalLibrary as UL
import numpy as np
import time
import h5py
import scipy.io

progname = os.path.basename(sys.argv[0])
progversion = "0.5"

class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100, sharedx=None):
        fig = Figure(figsize=(width, height), dpi=dpi)
        if sharedx!=None:
            self.axes=fig.add_subplot(111,sharex=sharedx)
        else:
            self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)
        self.compute_initial_figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class MyStaticMplCanvas(MyMplCanvas):
    """Simple canvas with a sine plot."""
        #QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), self.update_figure)
    data=[]
    color='b'
    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t)
        self.axes.plot(t, s)
    
    def set_data(self,data):
        self.data=data

    def set_data(self,data,color='b'):
        self.data=data        
        self.color=color
    
    def update_figure(self):
        self.axes.plot(self.data,self.color)
        self.axes.set_title('data')
        self.draw()
        

class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self):
        
        #rest - PyQt part
        QtGui.QMainWindow.__init__(self)
        self.setWindowIcon(QtGui.QIcon('FluorNeuronIcon.jpg'))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Data Viewer")
        #self.create_status_bar()
        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Load', self.fileLoad,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_L)      
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)
        self.help_menu = QtGui.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)
        self.main_widget = QtGui.QWidget(self)
        self.l = QtGui.QVBoxLayout(self.main_widget)
        self.sc = MyStaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        self.mpl_toolbar = NavigationToolbar(self.sc, self.main_widget)
        #dc = MyDynamicMplCanvas2(self.main_widget, width=5, height=4, dpi=100)
        self.l.addWidget(self.sc)
        self.l.addWidget(self.mpl_toolbar)
        #l.addWidget(dc)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        
        self.statusBar().showMessage("Data Viewer", 2000)

    def fileLoad(self):
        global data1
        global data2
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Load file', 
        '','HDF5 (*.h5);; HDF5 (*.HDF5);; MAT (*.mat);; Open Ephys (*.continuous)')
        if fname[-3:]=='mat':
            fh = scipy.io.loadmat(str(fname))
        elif fname[-10:]=='continuous':
            header,TimeStamp,data=rOE.read_split_data(fname)
            fh={'header':header,'timestamp':TimeStamp,'data':data}
        else:
            fh = h5py.File(str(fname),'r')
            
        if 'data' in fh: # looking for the dataset 'data' - essentially a list or a numpy array
            self.sc.set_data(fh['data'])
            self.sc.update_figure()
        
        if 'data2' in fh:
            if not hasattr(self,'lc'):
                                   
                self.lc = MyStaticMplCanvas(self.main_widget, width=5, height=4, dpi=100,sharedx=self.sc.axes)
                self.mpl_toolbar2 = NavigationToolbar(self.lc, self.main_widget)
                self.l.addWidget(self.lc)
                self.l.addWidget(self.mpl_toolbar2)
            self.lc.set_data(fh['data2'],color='r')
            self.lc.update_figure()
            
        
        
        # Showing the filename in the windows title        
        FullName=str(fname)
        FullName=FullName.split('/')
        FileName=FullName[len(FullName)-1]
        self.setWindowTitle("Data Viewer: "+FileName)
        #if fname[-3:]!='mat' or fname[-10:]!='continuous':
        if fname[-2:]=='h5' or fname[-4:]=='HDF5':
            fh.close()
            
    def fileQuit(self):
        self.close()

    def closeEvent(self, ce): # ce is close_event, which can be processed (ce.accept() or ce.ignore() in response to a message box for example)
        self.fileQuit()

    def about(self):
        QtGui.QMessageBox.about(self, "About %s" % progname,
u"""%(prog)s version %(version)s
Copyright \N{COPYRIGHT SIGN} 2012 Alex Chubykin
Data Viewer

""" % {"prog": progname, "version": progversion})

def main():
    qApp = QtGui.QApplication(sys.argv)

    
    # Create and display the splash screen
    splash_pix = QtGui.QPixmap('FluorNeuron.jpg')
    #splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash = QtGui.QSplashScreen(splash_pix)
    #splash.setMask(splash_pix.mask())
    splash.show()
    splash.showMessage("Data Viewer Loading...", color = QtCore.Qt.white)
    qApp.processEvents()
    
    # Simulate something that takes time
    time.sleep(2)
    
    # main application window
    aw = ApplicationWindow()
    aw.setWindowTitle("%s" % progname)
    aw.show()
    # close the splashscreen
    splash.finish(aw)
    
    sys.exit(qApp.exec_())
    #qApp.exec_()

if __name__ == "__main__":
    main()
           