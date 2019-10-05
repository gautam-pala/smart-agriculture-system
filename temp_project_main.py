import numpy as np           
import argparse, sys, os
from GUIdriver import *

def endprogram():
	print ("\nProgram terminated!")
	sys.exit()
    

text = str(ImageFile)
print ("\n*********************\nImage : " + ImageFile + "\n*********************")
img = cv2.imread(text)

img = cv2.resize(img ,((int)(img.shape[1]/5),(int)(img.shape[0]/5)))
original = img.copy()
neworiginal = img.copy() 
cv2.imshow('original',img)

p = 0 
for i in range(img.shape[0]):
	for j in range(img.shape[1]):
		B = img[i][j][0]
		G = img[i][j][1]
		R = img[i][j][2]
		if (B > 110 and G > 110 and R > 110):
			p += 1
            
            
totalpixels = img.shape[0]*img.shape[1]
per_white = 100 * p/totalpixels

if per_white > 10:
	img[i][j] = [200,200,200]
	cv2.imshow('color change', img)
    
blur1 = cv2.GaussianBlur(img,(3,3),1)

newimg = np.zeros((img.shape[0], img.shape[1],3),np.uint8)
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER , 10 ,1.0)

img = cv2.pyrMeanShiftFiltering(blur1, 20, 30, newimg, 0, criteria)
cv2.imshow('means shift image',img)

blur = cv2.GaussianBlur(img,(11,11),1)

canny = cv2.Canny(blur, 160, 290)
canny = cv2.cvtColor(canny,cv2.COLOR_GRAY2BGR)

bordered = cv2.cvtColor(canny,cv2.COLOR_BGR2GRAY)
ret,contours,hierarchy = cv2.findContours(bordered, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

maxC = 0
for x in range(len(contours)):													#if take max or one less than max then will not work in
	if len(contours[x]) > maxC:													# pictures with zoomed leaf images
		maxC = len(contours[x])
		maxid = x

perimeter = cv2.arcLength(contours[maxid],True)

Tarea = cv2.contourArea(contours[maxid])
cv2.drawContours(neworiginal,contours[maxid],-1,(0,0,255))
cv2.imshow('Contour',neworiginal)

height, width, _ = canny.shape
min_x, min_y = width, height
max_x = max_y = 0
frame = canny.copy()

for contour, hier in zip(contours, hierarchy):
	(x,y,w,h) = cv2.boundingRect(contours[maxid])
	min_x, max_x = min(x, min_x), max(x+w, max_x)
	min_y, max_y = min(y, min_y), max(y+h, max_y)
	if w > 80 and h > 80:
		roi = img[y:y+h , x:x+w]
		originalroi = original[y:y+h , x:x+w]
        
if (max_x - min_x > 0 and max_y - min_y > 0):
	roi = img[min_y:max_y , min_x:max_x]	
	originalroi = original[min_y:max_y , min_x:max_x]
    
cv2.imshow('ROI', frame)
cv2.imshow('rectangle ROI', roi)
img = roi

imghls = cv2.cvtColor(roi, cv2.COLOR_BGR2HLS)
cv2.imshow('HLS', imghls)
imghls[np.where((imghls==[30,200,2]).all(axis=2))] = [0,200,0]
cv2.imshow('new HLS', imghls)

huehls = imghls[:,:,0]
cv2.imshow('img_hue hls',huehls)

huehls[np.where(huehls==[0])] = [35]
cv2.imshow('img_hue with my mask',huehls)

ret, thresh = cv2.threshold(huehls,28,255,cv2.THRESH_BINARY_INV)
cv2.imshow('thresh', thresh)

mask = cv2.bitwise_and(originalroi,originalroi,mask = thresh)
cv2.imshow('masked out img',mask)

_,contours,heirarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

Infarea = 0
for x in range(len(contours)):
	cv2.drawContours(originalroi,contours[x],-1,(0,0,255))
	cv2.imshow('Contour masked',originalroi)
	Infarea += cv2.contourArea(contours[x])

if Infarea > Tarea:
	Tarea = img.shape[0]*img.shape[1]

print ('_________________________________________\n Perimeter: %.2f' %(perimeter) 
	   + '\n_________________________________________')

print ('_________________________________________\n Total area: %.2f' %(Tarea) 
	   + '\n_________________________________________')


print ('_________________________________________\n Infected area: %.2f' %(Infarea) 
	   + '\n_________________________________________')

try:
	per = 100 * Infarea/Tarea
except ZeroDivisionError:
	per = 0

print ('_________________________________________\n Percentage of infection region: %.2f' %(per) 
	   + '\n_________________________________________')


print("\n*To terminate press and hold (q)*")

cv2.imshow('orig',original)

print("\nDo you want to run the classifier(Y/N):")
n = cv2.waitKey(0) & 0xFF

if n == ord('q' or 'Q'):
	endprogram()
