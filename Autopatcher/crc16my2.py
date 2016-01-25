# -*- coding: utf-8 -*-
"""
crc16(data) - function - converted from Rodrigo Perin's CRC function
Created on Mon Oct 31 15:18:26 2011

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
__version__="version 1.0"
__date__="Mon Oct 31 15:18:26 2011"
__copyright__="Copyright (c) 2011 Alex Chubykin"
__license__="Python"

import numpy as np

# to convert a string a='123456789' into a list of uint8:
# b=[uint8(e) for e in a]
def crc16p(data_str): # crc function confirmed correct, coincides with Rodrigo Perin's crc16 function in Matlab 
    data_int=[np.uint8(ord(e)) for e in data_str]
    crc=0
    len_=len(data_int)
    #print len_
    for dcount in data_int:
        crc=np.uint16(np.bitwise_xor(  crc,np.left_shift(np.uint16(dcount),8)  )) # fixed by using dcount and pythonic for-loop
        #print bin(crc)
        #print '______'        
        for i in range(0,8):
            if np.bitwise_and(crc,np.uint16(0x8000)):
                crc=np.uint16(np.bitwise_and(np.bitwise_xor(np.left_shift(crc,1),np.uint16(0x1021)),np.uint16(0xffff)))
            else:
                crc=np.uint16(np.left_shift(crc,1))
            #print bin(crc)
        #print '======'
    
    return crc
    

def crc16(data_str): # data_str is a list of uint8 
    data_int=[np.uint8(ord(e)) for e in data_str]
   
    #print data_int
    checksum=np.uint16(0x3030) # uint16 checksum

    
    if data_int==0:
        return checksum
    #result=np.uint8(data_int[len(data_int)-1])
    result=data_int[len(data_int)-1]
    #for i in range(0,len(data_int)):
        #result=np.bitwise_xor(result,data_int[i])
    #for dcount in data_int:
    #    result=np.uint8(np.bitwise_xor(result, dcount))
    dcount=0
    while data_int[dcount]:
        if dcount==len(data_int)-1:
            break
        result=np.bitwise_xor(result,data_int[dcount])
        dcount=dcount+1
        
        
        

    checksum=np.uint16(result)
    checksum=np.left_shift(checksum,4)
    checksum=np.bitwise_and(checksum, 0xff00)
    checksum+=0x3000
    
    result=np.bitwise_and(result, 0x0f)
    result+=0x30
    checksum+=result

        
    return checksum                     
                
def main():
    #a=[0b11010011101100]
    #a=[13,17]
    #a=[87]
    #a=[1,2,3,4,5,6,7,8,9]
    a='#3?P'
    print 'Perin\'s a:',a,' checksum: ',hex(crc16p(a)) # works - corresponds to Rodrigo Perin's Matlab program, for '#1?P' - 4441 
    # at least the imported module crc16 (CRC-CCITT (XModem)) gives 12739 checksum
    print 'a:',a,' checksum: ',crc16(a), 'in hex:', hex(crc16(a))
  
if __name__ == "__main__":
    main()
