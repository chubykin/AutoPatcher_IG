import cv2
import cv
import copy
import numpy as np


img = cv2.imread('template0.png', 0)
img1 = copy.deepcopy(img)
img2 = img
method = eval('cv2.TM_CCOEFF')
print cv2.TM_CCOEFF
try:
	a = cv2.matchTemplate(img1, img, method)
except Exception as e:
	print(e)
print a

