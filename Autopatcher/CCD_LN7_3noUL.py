# -*- coding: utf-8 -*-
"""
idea - to incorporate OpenCV acquisition and online image processing:
    move the state all the way up, start lowering till you see a slice (which should coincide with detecting any contours (particular size also) vs nothing before that)
CCD_LN6.py
This program is combining image acquisition through a CCD camera using videocapture library with controlling the L&N manipulators using the MssUnitChr.py class import
ver.3 - adding mouse click functionality and sequence stage move
ver.4 - adding pyUniversal library acquisition from the external daq board - usb-1208fs in this case
ver.5 - changing the individiaul K_LEFT_UP processing into sending stop commands
ver.6 - using MssUnitChr2.py version with the coordinates in um, not x,y camera coordinates

ver.7 the idea is to receive the TTL signal from the Clampex and initiate the move to the next position 4 seconds later (one can use the El Stim TTL pulse)
ver.7 reads the TTL signal from the A1 digital port (pin 21) and moves only when the key 'm' was pressed and the TTL signal is received
I can also use the pygame.time.set_timer(USEREVENT+1, time_in_ms) to generate a timer event
also importing a less talkative version of MssUnit.py vs MssUnitChr2

ver.7_2 - incorporating my new ideas (absolute um coordinates), after I sent Brendan the latest CCD_LN7.py
ver.7_3 - adding positions to remember (Ctr-1,...), goto those positions  1,...
Created on Wed Oct 12 12:48:14 2011

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
__version__="version 7.3"
__date__="Wed Oct 12 12:48:14 2011"
__copyright__="Copyright (c) 2011 Alex Chubykin"
__license__="Python"

from VideoCapture import Device
import ImageDraw, sys, pygame, time
from pygame.locals import *
from PIL import ImageEnhance
#import MssUnitChr2 as ms
import MssUnit2 as ms # less talkative version of the MssUnit

#import UniversalLibrary as UL
import numpy as np

# camera parameters
res = (1344,1024)
#res = (640,480)
pixel_4x=[1.532,1.532] # one pixel in um at 4x, resolution 1344x1024
FRAMERATE = 25 # 25
pygame.init()
cam = Device()
cam.displayCapturePinProperties()
cam.setResolution(res[0],res[1])
screen = pygame.display.set_mode(res)
pygame.display.set_caption('CRACM Now')
pygame.font.init()
font = pygame.font.SysFont("Courier",11)      
    
brightness = 1.0
contrast = 1.0
shots = 0

# pygame control initial settings
moveLeft = False
moveRight = False
moveUp = False
moveDown = False
moveZUp= False
moveZDown = False
DelayInterval = 0.3 # delay interval between commands, s
Speed = 'F'
M_LEFT=1 # left mouse button
M_MIDDLE=2 # Middle mouse button (scrolling wheel)
M_RIGHT=3 # Right mouse button

mouse_seq=[] # mouse_seq is a list of tuples [(x1,y1),(x2,y2)]
scan_seq=[]
motor_coord=np.zeros(8)
seq_coord=[] # seq_coord is a list of lists ([[x1,y1,z1],[x2,y2,z2]])
remembered_position_index=[] # stores the indeces of remembered positions
"""
# Universal library acquisition
BoardNum = 0
Gain = UL.BIP5VOLTS
Chan = 0
tstart = time.time()
data = []
times = []
# digital input for the TTL signal - external synchronization (could also be done through the SYNC and TRIG inputs)
PortNum = UL.FIRSTPORTA
Direction = UL.DIGITALIN
BitNum = 0
#UL.cbDConfigPort(BoardNum, PortNum, Direction)
DataValue = 0
DataValue2 = 0
TTL_input = 0
TTL_switch=0
"""
command_exec=0
Move_seq_marker=1 #originally 0 with UL

def disp(phrase,loc):
    s = font.render(phrase, True, (200,200,200))
    sh = font.render(phrase, True, (50,50,50))
    screen.blit(sh, (loc[0]+1,loc[1]+1))
    screen.blit(s, loc)

def get_screen_coord(Device_number=0):
    """
    get the current coordinates of the microscope stage-Device_number=0 (always 
    center of the screen) or the manipulators (Device_number>0)
    """
    if Device_number==0:
        return res/2 # global variable!!! - correct
    else:
        return NaN  # to determine the coordinates of the manipulators (more precisely tip of the pipette - need to use object recognition in opencv)
    
def send_TTL(channel=0, time=1): # time in ms
    pass

def calibrate(MyUnit,x,y):
    """ 
    Determines the relationship between the screen and stage motors coordinates
    MyUnit is the MssUnitChr.MssUnit instance, x,y - screen coordinates
    """
    coord=[]
    if MyUnit.isOpen():
        coord=MyUnit.get_motors_coord()
    return coord
    
# L&N Manipulators part
BAUD = 19200 # 19200 for the Rig, 9600 for arduino
# Port the Arduino\lolshield is on:
PORT = 'COM3' # 'COM4'- Gateway # COM6 - Tanya's PC # COM1 - Rig PC
MyUnit = ms.MssUnit(port=PORT, baudrate=BAUD,timeout=0.1)
print MyUnit.isOpen()
time.sleep(1.5)
MyUnit.set_camera_resolution(res[0],res[1]) # also updates the scale

# assaying the status and position of the motors
print 'What is the status of the motors?'
for i in range(0,7):
    a='#'+str(i)+'?Z'
    motor_message=MyUnit.talk(a)
    time.sleep(0.5)
    if 'P' in motor_message:
        print motor_message
        index_P=motor_message.index('P')
        if motor_message[index_P+1]=='+':
            motor_coord[i]=float(motor_message[index_P+2:-3])
        else:
            motor_coord[i]=float(motor_message[index_P+1:-3])
    else: # the message didn't get in the first time, repeating
        motor_message=MyUnit.talk(a)
        print motor_message
        index_P=motor_message.index('P')
        if motor_message[index_P+1]=='+':
            motor_coord[i]=float(motor_message[index_P+2:-3])
        else:
            motor_coord[i]=float(motor_message[index_P+1:-3])

# starting the clock for the pygame loop
my_clock = pygame.time.Clock()

# main loop, pygame
while 1:
    # Maintain our framerate:
    my_clock.tick(FRAMERATE)
    # pyUniversal library - acquiring data from external DAQ board
    """
    pyUniversal library block:
    """
    """
    DataValue = UL.cbAIn(BoardNum, Chan, Gain)
    data.append( DataValue )
    times.append( time.time()-tstart )
    if times[-1] > 10.0:
        tstart = time.time()
        data=[]
        times=[]
    #print DataValue
    # get TTL input from Clampex    
    TTL_input = UL.cbDBitIn(BoardNum, PortNum, BitNum, DataValue2)
    if TTL_input == 1:  # move only if a TTL signal received
        if TTL_switch==0: # Incoming TTL signal only switches the switch once (could be long TTL signal, assayed twice)
            Move_seq_marker=1 # good to move
            print "TTL signal received"
            TTL_switch=1
    else:
        TTL_switch=0 # as soon as the TTL signal is gone, the TTL_switch is switched off
    
    # end of pyUniversal library block
    """
    """
    Move Sequence block
    """
    # version CCD_LN7_2.py uses absolute coordinates of the microscope stage in um as a reference in seq_coord
    if Move_seq_marker==1 and command_exec==1:  # move only when the TTL signal marks command marker, and the 'm' key was pressed to mark the Move_seq_marker
        if len(seq_coord)>0:
            print 'Moving sequence initiated...'
            # seq_coord already has the sequence of the absolute coordinates to move to (in the microscope stage coordinate system)
            x,y,z=seq_coord.pop(0)            
            MyUnit.move_to_um(x,y,z) 
            mouse_seq.pop(0)
        Move_seq_marker=1#originally 0 w/ UL
        
            
            
    #camera 
    camshot = ImageEnhance.Brightness(cam.getImage()).enhance(brightness)
    camshot = ImageEnhance.Contrast(camshot).enhance(contrast)
    for event in pygame.event.get():
        
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
                
        keyinput = pygame.key.get_pressed() # returns the status of every key pressed - tuple
        if keyinput[K_b]: brightness -= .1
        if keyinput[K_n]: brightness += .1
        if keyinput[K_c]: contrast -= .1
        if keyinput[K_v]: contrast += .1
        if keyinput[K_q]: cam.displayCapturePinProperties()
        if keyinput[K_e]: cam.displayCaptureFilterProperties()
        if keyinput[K_t]:
            filename = str(time.time()) + ".jpg"
            cam.saveSnapshot(filename, quality=80, timestamp=0)
            shots += 1
        
        
        

        
        if event.type == KEYDOWN:
            # memorizing/recalling positions            
            for i in range(0,10):
                if event.key == ord(str(i)):
                    if pygame.key.get_mods() & KMOD_CTRL: # CTRL+X remmebers position
                        print 'CTRL+',str(i),' pressed, microscope positioned remembered'
                        MyUnit.remembered_positions[i,:]=MyUnit.get_motors_coord_um()
                        remembered_position_index.append(i)
                        remembered_position_index.sort()
                    elif pygame.key.get_mods() & KMOD_SHIFT: # SHIFT+X deletes position
                        MyUnit.remembered_positions[i,:]=[0,0,0]
                        del remembered_position_index[remembered_position_index.index(i)]
                        print 'SHIFT+',str(i),' pressed, positioned deleted'
                    else:
                        if np.all(MyUnit.remembered_positions[i,:]==0): # if the coordinates are zeros, no moving
                            pass
                        else:
                            print str(i),' pressed, microscope position recalled'
                            x,y,z=MyUnit.remembered_positions[i,:]
                            MyUnit.move_to_um(x,y,z)        
            
            # controlling the manipulator with arrows
            if event.key == K_LEFT or event.key == ord('a'):
                moveRight = False
                moveLeft = True
            if event.key == K_RIGHT or event.key == ord('d'):
                moveLeft = False
                moveRight = True
            if event.key == K_UP or event.key == ord('w'):
                moveDown = False
                moveUp = True
            if event.key == K_DOWN or event.key == ord('s'):
                moveUp = False
                moveDown = True
            # Z axis movement
            if event.key == ord('r'):
                moveZDown = False
                moveZUp = True
            if event.key == ord('f'):
                moveZUp = False
                moveZDown = True
            if event.key == ord('z'): # speed fast
                Speed = 'F'
                DelayInterval = 0.3
            if event.key == ord('x'): # speed slow
                Speed = 'S'
                DelayInterval = 0.05
                
            # initiating the sequence of stage movements                
            if event.key == ord('m'): # every 'm'-keypress switches the status of the move marker
                if command_exec==0:
                    command_exec=1
                else:
                    command_exec=0
                
            if event.key == ord('i'): # input the current coordinates to remember
                MyUnit.remembered_coord_um=MyUnit.get_motors_coord_um()
                print MyUnit.remembered_coord_um
                
            if event.key == ord('o'): # goes to the remembered coordinate position
                if len(MyUnit.remembered_coord_um)>0:
                    x,y,z=MyUnit.remembered_coord_um
                    print MyUnit.remembered_coord_um
                    MyUnit.move_to_um(x,y,z)
                
                
        if event.type == KEYUP:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == K_p: # stops the movement along all axes
                MyUnit.talk('#1!A')
                MyUnit.talk('#2!A')
                MyUnit.talk('#3!A') 
            if event.key == K_LEFT or event.key == ord('a'):
                moveLeft = False
                MyUnit.talk('#1!A')
            if event.key == K_RIGHT or event.key == ord('d'):
                moveRight = False
                MyUnit.talk('#1!A')
            if event.key == K_UP or event.key == ord('w'):
                moveUp = False
                MyUnit.talk('#2!A')
            if event.key == K_DOWN or event.key == ord('s'):
                moveDown = False
                MyUnit.talk('#2!A')
            # Z axis movement
            if event.key == ord('r'):
                moveZUp = False
                MyUnit.talk('#3!A')
            if event.key == ord('f'):
                moveZDown = False
                MyUnit.talk('#3!A')
        # mouseclick processing
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == M_LEFT: # left mouse clicked (M_LEFT=1)
            posn_of_click = event.dict['pos']    # get the coordinates
            print(posn_of_click)
            #pygame.draw.circle(screen, Color('red'), posn_of_click, 64)
            #scan_seq.append(stage_message)
            mouse_seq.append(posn_of_click)
            temp_coord=MyUnit.get_motors_coord_um()
            x_a=-1*round((posn_of_click[0]-res[0]/2)/pixel_4x[0],4) # correct polarity
            temp_coord[0]=temp_coord[0]+x_a
            x_b=-1*round((posn_of_click[1]-res[1]/2)/pixel_4x[1],4) # correct polarity
            temp_coord[1]=temp_coord[1]+x_b
            seq_coord.append(temp_coord) # sequence of absolute coordinates in um (microscope coordinates) to go to
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == M_RIGHT: # left mouse clicked (M_RIGHT=3)          
            if len(mouse_seq)>0:
                mouse_seq.pop()
                seq_coord.pop() # seq_coord is a list of lists ([[x1,y1,z1],[x2,y2,z2]])
            
    # move the stage
    if moveDown:
        a='#2!'+Speed+'-'
        MyUnit.talk(a)
        time.sleep(DelayInterval)
    if moveUp:
        Py_BEGIN_ALLOW_THREADS
        a='#2!'+Speed+'+'
        MyUnit.talk(a)
        time.sleep(DelayInterval)
        Py_END_ALLOW_THREADS
    if moveLeft:
        a='#1!'+Speed+'+'
        MyUnit.talk(a)
        time.sleep(DelayInterval)
    if moveRight:
        a='#1!'+Speed+'-'
        MyUnit.talk(a) 
        time.sleep(DelayInterval)
    if moveZUp:
        a='#3!'+Speed+'+'
        MyUnit.talk(a) 
        time.sleep(DelayInterval)
    if moveZDown:
        a='#3!'+Speed+'-'
        MyUnit.talk(a) 
        time.sleep(DelayInterval)
        
        
        
        
            
    camshot = pygame.image.frombuffer(camshot.tostring(), res, "RGB")
    screen.blit(camshot, (0,0))
    disp("S:" + str(shots), (10,4))
    disp("B:" + str(brightness), (10,16))
    disp("C:" + str(contrast), (10,28))
    disp("Speed: Fast" if Speed=='F' else "Speed: Slow",(50,4))
    disp("Pos:"+str(remembered_position_index),(100,16))
    disp("+",(res[0]/2,res[1]/2)) # drawing the cross in the center 
    # drawing the marks for the mouse clicks sequence   
    if len(mouse_seq)>0:
        for x,y in mouse_seq:
            disp("<",(x,y)) 
            
    pygame.display.flip()