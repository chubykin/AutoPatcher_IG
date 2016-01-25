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

import csv

myConfig = dict([('VoltageCommand', 100), ('VoltageDifference', 100), ('WaitingTimeSpontaneous', 100), ('WaitingTimeNegativePressure', 100), ('WaitingTimePatchFail', 100), ('WaitingTimeBreakIn', 100), ('InitialPipetteResistance', 100), ('ResistanceAtCellSurface', 100), ('GigaSealResistance', 100)])
writer = csv.writer(open('PatchControlConfiguration.csv', 'wb'))
for key, value in myConfig.items():
   writer.writerow([key, value])