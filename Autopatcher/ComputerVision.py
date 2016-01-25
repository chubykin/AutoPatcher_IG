import cv2
import numpy as np
from matplotlib import pyplot as plt
import os
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

@Author: Zhaolun Su

"""
	


class ComputerVision:

	def __init__(self):

		#Templates Import
		self.templates = []
		self.matchingCoefficientThreshold = 1700
		for file in os.listdir("./configuration/PipetteTemplates/"):
			if file.endswith(".png") or file.endswith(".PNG"):
				img = self.equalize(cv2.imread(file,0))
				templates.add(img);




	"""
	40x Pipette Tip Detection
	"""

	def genericFourtyXPipetteDetection(img, frame):
		height, width = img.shape
		edges = cv2.Canny(img,30,100)
		minimum_length = 15;

		while 1:
			linecount = 0;
			lines_unsorted = cv2.HoughLines(edges,1,np.pi/180,minimum_length)[0]

			#count lines
			for rho,theta in lines_unsorted:
				linecount = linecount + 1;
				#print rho, theta

			if linecount > 10:
				minimum_length = minimum_length + 1;
				continue

			#create cartesian matrix for each line
			#ax + by + c = 0    b is set to 1 and not being recorded
			cartesian_line = copy.deepcopy(lines_unsorted)
			for index,[rho,theta] in enumerate(lines_unsorted):
				a = np.cos(theta)
				b = np.sin(theta)
				x0 = a*rho
				y0 = b*rho
				x1 = int(x0 + 1000*(-b))
				y1 = int(y0 + 1000*(a))
				x2 = int(x0 - 1000*(-b))
				y2 = int(y0 - 1000*(a))
				a = y1 - y2;
				b = x2 - x1;
				c = x1*y2 - x2*y1;
				a = a/b;
				c = c/b;
				cartesian_line[index] = [a,c]

			print "fitting line length is ", minimum_length

			print lines_unsorted
			cv2.imshow('edges', edges)
			cv2.waitKey(0)
			cv2.destroyAllWindows()

			lines = lines_unsorted
			
			black_board = np.zeros((img.shape[0], img.shape[1]), np.uint8)
			for index,[rho,theta] in enumerate(lines):

					  
					
				a = np.cos(theta)
				b = np.sin(theta)
				x0 = a*rho
				y0 = b*rho
				x1 = int(x0 + 1000*(-b))
				y1 = int(y0 + 1000*(a))
				x2 = int(x0 - 1000*(-b))
				y2 = int(y0 - 1000*(a))
				cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)
				temp = np.zeros((img.shape[0], img.shape[1]), np.uint8)
				cv2.line(temp,(x1,y1),(x2,y2),(50,50,50),2)
				black_board = black_board + temp;
				#aftermath = aftermath + 1
				
			cv2.imshow('black_board with lines', black_board)
			cv2.waitKey(0)
			cv2.destroyAllWindows()

			tip_x = 0;
			tip_y = 0;
			minimum_distance = 999999;	#has to be big
			current_distance = 0;
			cumulative_distance = 0;

			
			#calculate the distance to each line
			for x, col in enumerate(edges):
				for y, val in enumerate(col):
					cumulative_distance = 0
					if val != 0:
						for index,[a,c] in enumerate(cartesian_line):
							distance = abs(a*y + x + c)/(math.sqrt(a*a + 1))
							cumulative_distance = cumulative_distance + distance
						if cumulative_distance < minimum_distance:
							tip_x = x;
							tip_y = y;
							minimum_distance = cumulative_distance;
				print "the minimum distance is ", minimum_distance
				coordinate = (tip_y, tip_x);
			cv2.circle(edges, coordinate, 2, (255, 255, 255), 2)

			cv2.imshow('edges', edges)
			cv2.waitKey(0)
			cv2.destroyAllWindows()

			return [tip_y, tip_x, minimum_distance]
			break

		pass

	def fourtyXPipetteDetectionDistance(self, frame, equalizedBool):

		# Returns the minimum distance from detected tip to detected lines

		if not equalizedBool:
			frame = self.equalize(frame);
		return self.genericFourtyXPipetteDetection(frame)[2];

		pass

	def fourtyXPipetteDetectionCorrdinate(self, frame, equalizedBool):

		# Returns detected pipette tip coordinates in pixel 

		if not equalizedBool:
			frame = self.equalize(frame);
		result = self.genericFourtyXPipetteDetection(frame)
		return [result[0], result[1]]

		pass



	"""
	Template matching
	"""

	def getTemplateMatchingCoefficient(self, frame, matchingTemplate):
		method = eval('cv2.TM_CCOEFF')
		res = cv2.matchTemplate(frame, matchingTemplate, method);
		min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
		
		# In case you want to plot the matching result
		# top_left = max_loc
		# bottom_right = (top_left[0] + w, top_left[1] + h)
		# cv2.rectangle(frame,top_left, bottom_right, 255, 2)
		# plt.subplot(131),plt.imshow(res,cmap = 'gray')
		# plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
		# plt.subplot(132),plt.imshow(frame,cmap = 'gray')
		# plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
		# plt.subplot(133),plt.imshow(matchingTemplate,cmap = 'gray')
		# plt.title("coefficient is %d" % alltimemax), plt.xticks([]), plt.yticks([])
		# plt.suptitle(method)
		# plt.show()

		return max_val

	def getTemplateMatchResult(self, frame, equalizedBool):
		# frame is from the microscope
		# equalizedBool is true is frame is already equalized
		# return trun is coefficient surpasses threshold
	
		if not equalizedBool:
			frame = self.equalize(frame);

		for index, matchingTemplates in enumerate(self.templates):
			matchingCoefficient = self.getTemplateMatchingCoefficient(frame, matchingTemplates)
			if matchingCoefficient >= self.matchingCoefficientThreshold:
				return true

		return False

	def equalize(self, frame_1):
		clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
		cl1 = clahe.apply(frame_1)
		return t
















