import numpy as np
import cv2
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import imutils
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"

#first we would ask the user to select the desired image and would display it.
Tk().withdraw()
file = askopenfilename()
image = cv2.imread(file)
image = imutils.resize(image, width=500)
cv2.imshow("Original Image", image)
cv2.waitKey(0)
#Now we would have to do some image processing
gray_scaled = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)#this will convert the image to grayscale
gray_scaled = cv2.bilateralFilter(gray_scaled, 11, 17, 17)#this will apply the bilateral filter over the images for noise remov
edged = cv2.Canny(gray, 170, 200) #This will remove the noise in the image and preserve the edges
cv2.imshow("Edged", edged)
cv2.waitKey(0)

# Find contours based on Edges
contours, heirarchy  = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)#this would help in finding the contours and heirarchy

# Create copy of original image to draw all contours
image_1 = image.copy()# Now we would make a copy of the original image so that whatever changes we make,it doesn't affect the original image
cv2.drawContours(img1, cnts, -1, (0,255,0), 3) #this would draw the contours over the image copy


#We would reverse sort all the contours in terms of area, and take the top 30 contours so that the smaller ones can be neglected
contours=sorted(contours, key = cv2.contourArea, reverse = True)[:30]
Number_Plate_Contour = 0 #This would be our number plate contour,and currently we don't have any


for current_contour in contours:
        perimeter = cv2.arcLength(current_contour, True)#this will help in setting up a parameter for the cv2.approxPolyDP()
        approx = cv2.approxPolyDP(c, 0.02 * perimeter, True) #this will approximate the polygon curve
        if len(approx) == 4:  # find the contour with 4 corners as number plates are in rectangular shape
            Number_Plate_Contour = approx #This is will be the approx Number Plate Contour
            break

mask = np.zeros(gray_scaled.shape,np.uint8)
new_image1 = cv2.drawContours(mask,[Number_Plate_Contour ],0,255,-1,)
new_image1 = cv2.bitwise_and(image,image,mask=mask)
cv2.imshow("Number Plate",new_image1)
cv2.waitKey(0)
gray_scaled1 = cv2.cvtColor(new_image1, cv2.COLOR_BGR2GRAY)
ret,processed_img = cv2.threshold(np.array(gray_scaled1), 125, 255, cv2.THRESH_BINARY)
cv2.imshow("Number Plate",processed_img)
cv2.waitKey(0)
# Use tesseract to covert image into string
text = pytesseract.image_to_string(processed_img)
print("Number is :", text)

cv2.waitKey(0) #Wait for user input before closing the images displayed
