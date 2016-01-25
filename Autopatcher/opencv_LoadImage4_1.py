# -*- coding: utf-8 -*-
"""
Created on Sun Nov 11 15:46:11 2012


opencv_LoadImage.py
ver 0_2 - 11/13/12 opens the newest image in the target folder
ver 0_3 - 11/13/12 - adapting for the 2-photon approach - identifying the newest folder and then the newest file in that folder, as 2-photon creates individual folder for each single scan
                     also added xml-parsing of the X,Y,Z stage coordinates
ver 0_4 - 11/14/12 - simplifying the filename return (now full name including the path)

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

@Author: Alexander A. Chubykin

"""

__author__="Alex Chubykin"
__version__="ver0_4"
__date__="Sun Nov 11 15:46:11 2012"
__copyright__="Copyright (c) 2012 Alex Chubykin"
__license__="Python"

import cv #Import functions from OpenCV
import cv2
import os
import time
import operator
import xml.etree.cElementTree as et
    
#os.system("subst P: \"F:\\My Dropbox\"")
#os.system("subst P: \"F:\\Dropbox\"")
os.system("subst P: \"C:\\Documents and Settings\\Bear Lab\\Desktop\\Dropbox\"")

#report_dirName='p:/python_projects/OpenCV_work/2-photon/'
report_dirName='p:\\Code\\2-photon\\'
#report_dirName='p:\\Code (2)\\2-photon\\'
#report_dirName='p:\\Dropbox-2photon-2\\SingleImage-11132012-1130-192\\' # 2-photon folder
#report_dirName='p:\\Dropbox-2photon-2\\'
#report_dirName='p:\\python_projects\\OpenCV_work\\2-photon\\ZSeries-10012012-1715-090\\'

x = 20
y = 100

def latest_file(path=report_dirName, name_start='ZSeries', name_end='.tif'):
    path
    # Open a file
    #dirs = os.listdir( path )
    dirs=[ f for f in os.listdir(path) if f.startswith(name_start) and f.endswith(name_end) ]
    file_times=[]
    # This would print all the files and directories
    for file1 in dirs:
        file1_time=time.ctime(os.path.getmtime(path+file1))
        file_times.append(file1_time)

    files_and_times=dict(zip(dirs,file_times))
    #print files_and_times

    sorted_file_times = sorted(files_and_times.iteritems(), key=operator.itemgetter(1))
    #print sorted_file_times

    timestamps=[]
    for file2 in dirs:
        #if os.path.isdir(file2):
        timestamp=os.path.getmtime(path+file2)
#        print timestamp
        timestamps.append(timestamp)
    # sort the timestamp 
    sorted_timestamps=sorted(timestamps)
    #print timestamps
    #print sorted_timestamps

#    print 'The newest file is:',sorted_file_times[-1][0],' time:',sorted_file_times[-1][1]
    return sorted_file_times[-1][0]
    
    
def getLatestImage():
    latest_folder=report_dirName+latest_file(name_start='Z',name_end='')+'\\'
    return latest_folder+latest_file(path=latest_folder, name_start='Z', name_end='.tif')

def return_xyz_coordinates(xml_filename=None):
    
    latest_folder=report_dirName+latest_file(name_start='Z',name_end='')+'\\' 
    
    if xml_filename == None:
        xml_filename = latest_folder+latest_file(path=latest_folder, name_start='', name_end='.xml')    
    
    tree = et.parse(xml_filename)

    root = tree.getroot()
    #for child in root:
        #print child.tag, child.attrib

#    print root[1][0][2][12].attrib    
    root[1][0][2][12].attrib['value'],root[1][0][2][13].attrib['value'],root[1][0][2][14].attrib['value']
    return ([root[1][0][2][12].attrib['value'],root[1][0][2][13].attrib['value'],root[1][0][2][14].attrib['value']])

def main():
    while True:
        cv.NamedWindow('a_window', cv.CV_WINDOW_AUTOSIZE)
        #logfiles = sorted([ f for f in os.listdir(report_dirName) if f.startswith('image')])
        #logfiles=GetLatestArchive('image*.jpg')       
        latest_folder=report_dirName+latest_file(name_start='Z',name_end='')+'\\'
        image=cv.LoadImage(latest_folder+latest_file(path=latest_folder, name_start='Z', name_end='.tif'), cv.CV_LOAD_IMAGE_COLOR) # .jpg images are 4x times smaller
            #img = cv2.imread(latest_folder+latest_file(path=latest_folder, name_start='', name_end='.tif'))        
            #gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)        
            #img2=cv2.equalizeHist(gray)
            #cvmat_img2=cv.fromarray(img2)
        font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 1, 1, 0, 3, 8)
        newFrameImage8U = cv.CreateImage((image.width, image.height), cv.IPL_DEPTH_8U, 3)   # optional convert to 8U
        cv.ConvertScale(image,newFrameImage8U)                                              # optional 
        image=newFrameImage8U                                                               # optional
        cv.PutText(image,"Counter:", (x,y),font, 255) #Draw the text
            #cv.PutText(cvmat_img2,"Counter:", (x,y),font, 255)
        cv.ShowImage('a_window', image) #Show the image
        #cv.Waitkey(10000)
        # open the latest xml-file in this folder and get the stage coordinates (x,y,z)
        (stage_x,stage_y,stage_z)=return_xyz_coordinates(latest_folder+latest_file(path=latest_folder, name_start='', name_end='.xml'))
        print 'stage coordinates x,y,z:',stage_x,stage_y,stage_z
        if cv.WaitKey(10) == 27:
            break
    cv.DestroyWindow("a_window")    
           
    
    
    
if __name__ == "__main__":
    main()
