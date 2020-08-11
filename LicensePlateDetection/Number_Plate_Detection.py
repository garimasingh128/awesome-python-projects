import numpy as np
import cv2
import imutils
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import cv2
import imutils
import pytesseract
pytesseract.pytesseract.tesseract_cmd =r"c:\Program Files(x86)\Tesseract-OCR\tesseract.exe"
#first we would ask the user to select the desired image and would display it.
Tk().withdraw()
file = askopenfilename()
image = cv2.imread(file)
image = imutils.resize(image, width=500)
cv2.imshow("Original Image", image)
cv2.waitKey(0)




#Now we would have to do some image processing
gray_scaled = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #this will convert the image to grayscale
gray_scaled = cv2.bilateralFilter(gray_scaled, 11, 17, 17) #this will apply the bilateral filter over the images for noise removal
edged = cv2.Canny(gray_scaled, 170, 200)




contours,heirarchy = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)#this would help in finding the contours and heirarchy
image_1 = image.copy() # Now we would make a copy of the original image so that whatever changes we make,it doesn't affect the original image
cv2.drawContours(image_1, contours, -1, (0,255,0), 3) #this would draw the contours over the image copy
cv2.imshow("Contoured Image", image_1)
cv2.waitKey(0)



#We would reverse sort all the contours in terms of area, and take the top 10 contours so that the smaller ones can be neglected
contours =sorted(contours, key = cv2.contourArea, reverse = True)[:10]
Number_Plate_Contour = None #This would be our number plate contour,and currently we don't have any



index =1
for current_contour in contours:
        perimeter = cv2.arcLength(c, True) #this will help in setting up a parameter for the cv2.approxPolyDP()
        approx = cv2.approxPolyDP(c, 0.001 *perimeter, True) #this will approximate the polygon curve
        if len(approx) == 4:  # find the contour with 4 corners as number plates are in rectangular shape
            Number_Plate_Contour = approx #This is will be the approx Number Plate Contour
            break


mask = np.zeros(gray_scaled.shape,np.uint8)
new_image1 = cv2.drawContours(mask,[Number_Plate_Contour],0,255,-1,)
new_image1 = cv2.bitwise_and(image,image, mask=mask)
cv2.imshow("Number Plate",new_image1)
cv2.waitKey(0)





number_on_the_plate = pytesseract.image_to_string(new_image1) #Convert the image to text
print ("Number on the car is :", number_on_the_plate)
