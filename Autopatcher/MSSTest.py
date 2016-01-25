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

@Author: Brendan Callahan, Alexander A. Chubykin
"""


import MSSInterface
import time
MSSInterface = MSSInterface.MSSInterface()
time.sleep(5)
# while True:
# 	print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n",MSSInterface.getCoords(2,0)
# 	print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n",MSSInterface.getCoords(2,0)

# 	MSSInterface.moveToRel(2,0, 100, 100, 100)
# 	MSSInterface.waitForReady(2,0)
# 	MSSInterface.askCoords(2,0)
# 	print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n",MSSInterface.getCoords(2,0)
# 	print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n",MSSInterface.getCoords(2,0)

# 	print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n",MSSInterface.getCoords(2,0)
# 	print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n",MSSInterface.getCoords(2,0)

# 	MSSInterface.moveToRel(2,0, -100, -100, -100)
# 	MSSInterface.waitForReady(2,0)
# 	MSSInterface.askCoords(2,0)
# 	print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n",MSSInterface.getCoords(2,0)
# 	print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n",MSSInterface.getCoords(2,0)

while True:
	print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n",MSSInterface.getCoords(2,0)
	print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n",MSSInterface.getCoords(2,0)

	currentCoord = MSSInterface.getCoords(2,0);
	MSSInterface.moveTo(2,0, currentCoord[0]+100, currentCoord[1]+100, currentCoord[2]+100)
	MSSInterface.waitForReady(2,0)
	MSSInterface.askCoords(2,0)
	print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n",MSSInterface.getCoords(2,0)
	print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n",MSSInterface.getCoords(2,0)

	print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n",MSSInterface.getCoords(2,0)
	print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n",MSSInterface.getCoords(2,0)

	currentCoord = MSSInterface.getCoords(2,0);
	MSSInterface.moveTo(2,0, currentCoord[0]-100, currentCoord[1]-100, currentCoord[2]-100)
	MSSInterface.waitForReady(2,0)
	MSSInterface.askCoords(2,0)
	print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n",MSSInterface.getCoords(2,0)
	print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n",MSSInterface.getCoords(2,0)