import cv2
import numpy as np
import win32api

class detection():
    def __init__(self):
        self.cap = cv2.VideoCapture(0)#Camera
        self.cap.set(3,640)#sets the resolution
        self.cap.set(4,480)
        self.imageBGR = []#Colour image
        self.imageGRAY = None#Grayscale image
        self.imageHSV = None#HSV image
        self.faceCoords = None#Coordinates of face
        self.eyeCoords = None#Coordinates of eyes
        self.handCoords = None#Coordinates of hand
        self.rawSamples = []#samples corrected with the tolerance
        self.samples = []#Samples corrected with tolerance
        self.tolerance = [30,30,30]#Tolerance of upper and lower sample bounds
        self.mask = None#Mask of pixels that are within range of the samples
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')#Face cascade file
        self.eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')#Eye cascade file
        self.xSF = 1.1#x and y scale factors that adjust the speed of curser
        self.ySF = 1.1
        self.cameraHeight = 480.0
        self.cameraWidth = 640.0
        self.screenHeight = win32api.GetSystemMetrics(1)
        self.screenWidth = win32api.GetSystemMetrics(0)
        self.lowMode = 0
    
    def faceDetect(self, frame):#input: grayscale frame
        faces = self.face_cascade.detectMultiScale(frame, 1, 3, 5)
        if len(faces) > 0:#if face found
            largest = 0
            index = []
            for i in faces:
                if i[2] * i[3] > largest:
                    largest = i[2] * i[3]
                    index = i
            self.faceCoords = index#output: assigns self.facecoords to cordinates [x, y, w, h] of largest face in frame
        else:
            self.faceCoords = []

    def featureDetect(self, frame):#input: grayscale frame
        eyes = self.eye_cascade.detectMultiScale(frame)
        self.eyeCoords = eyes#output: assigns self.eyeCoords to eye coordinates in the form [x,y,w,h]

    def calibrateFaceDetection(self):#Take as image and returns with face/ eyes highlighted
        _, self.imageBGR = self.cap.read()
        self.imageGRAY = cv2.cvtColor(self.imageBGR, cv2.COLOR_BGR2GRAY)
        self.imageHSV = cv2.cvtColor(self.imageBGR, cv2.COLOR_BGR2HSV)
        self.imageHSV = cv2.blur(self.imageHSV, (5,5))
        self.faceDetect(self.imageGRAY)
        if len(self.faceCoords) > 0:
            [x, y, w, h] = self.faceCoords
            cv2.rectangle(self.imageBGR, (x,y), (x+w, y+h), (255,0,0), 2)#draws rectangle around face
            self.featureDetect(self.imageGRAY[y:y+h, x:x+w])#Calls featureDetection for eye detection
            for [ex, ey, ew, eh] in self.eyeCoords:
                cv2.rectangle(self.imageBGR, (ex + x, ey + y), (ex + x + ew, ey + y + eh), (0, 255, 0), 2)#Draws rectangle around eyes
            if len(self.eyeCoords) != 2:#If there are not 2 eyes print error message
                pass#print "Eye count error"
        return self.imageBGR#Return the image
    
    def calibrateSamples(self):
        [x, y, w, h] = self.faceCoords
        imageFace = self.imageHSV[y:y + h, x:x + w]
        by = 0#Biggest ey
        sx = 10000#Smallest ex
        bx = 0#Biggest ex
        for [ex, ey, ew, eh] in self.eyeCoords:
            if ey + eh > by:
                by = ey + eh 
            if ex < sx:
                sx = ex
            if ex + ew > bx:
                bx = ex + ew
        for i in range(i, (bx - sx)// 10+1):
            self.rawSamples.append(imageFace[by][sx+i*10])
            upper, lower = [], []
            for x in range (len(self.tolerance)):
                upper.append(imageFace[by][sx + i * 10][x]+ self.tolerance[x])
                lower.append(imageFace[by][sx + i * 10][x]- self.tolerance[x])

            for y in range (len(upper)):
                if upper[y] < 0:
                    upper[y] = 0
                if upper [y] > 255:
                    upper[y] = 255
            for y in range (len(lower)):
                if lower[y] < 0:
                    lower[y] = 0
                if lower [y] > 255:
                    lower[y] = 255
            lower = np.array(lower, dtype=np.uint8)
            upper = np.array(upper, dtype=np.uint8)
            self.samples.append([lower, upper])
    
    def createMask(self):
        self.mask = cv2.inRange(self.imageHSV, self.samples[0][0], self.samples[0][1])#create mask of correct size
        for i in self.samples: 
            tempMask = cv2.inRange(self.imageHSV, i[0], i[1])
            self.mask = cv2.bitwise_or(self.mask, tempMask)
    
    def findContours(self):
        self.imageGRAY = cv2.cvtColor(self.imageBGR, cv2.COLOR_BGR2GRAY)
        if self.lowMode == 0:
            self.faceDetect(self.imageGRAY)
            if len(self.faceCoords) != 0:
                [fx, fy, fw, fh] = self.faceCoords
                cv2.rectangle(self.mask, (fx, fy), (fx+fw, fy+int(fh*1.5)), (0,0,0), -1)
                _, contours, _ = cv2.findContours(self.mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) != 0:
                largest = 0
                contour = None
                for cnt in contour:
                    x, y, w, h = cv2.boundingRect(cnt)
                    if w*h > largest:
                        largest = w*h
                        contour = cnt
        cv2.drawContours(self.imageBGR, [contour], 0, (0, 255, 0), 2)
        hx, hy, hw, hh = cv2.boundingRect(contour)
        self.handCoords = [hx + hw//2, hy + hh//2, hw*hh]
        cv2.circle(self.imageBGR, (self.handCoords[0], self.handCoords[1]), 4, (255, 0, 0), -1)

    def temploop(self):
        _, self.imageBGR = self.cap.read()
        self.imageHSV = cv2.cvtColor(self.imageBGR, cv2.COLOR_BGR2HSV)
        self.imageHSV = cv2.blur(self.imageHSV, (5,5))
        self.createMask()
        self.findContours()
        x1 = int((self.cameraWidth - self.cameraWidth/self.xSF)/2)
        x2 = int(self.cameraWidth - x1)
        y1 = int((self.cameraHeight - self.cameraHeight/self.ySF)/2)
        y2 = int(self.cameraHeight - y1)
        cv2.rectangle(self.imageBGR, (x1, y1), (x2, y2), (0, 0, 255))
        cv2.putText(self.imageBGR, "Active Region", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
    
    def changeTolerance(self, value):
        self.tolerance = [value, value, value]
        self.samples = []
        for i in self.rawSamples:
            upper, lower = [],[]
            upper.append(i[0] + self.tolerance[0])
            upper.append(i[1] + self.tolerance[1])
            upper.append(i[2] + self.tolerance[2])

            lower.append(i[0] - self.tolerance[0])  
            lower.append(i[1] - self.tolerance[1])   
            lower.append(i[2] - self.tolerance[2])

            for y in range (len(upper)):
                if upper[y] < 0:
                    upper[y] = 0
                if upper [y] > 255:
                    upper[y] = 255
            for y in range (len(lower)):
                if lower[y] < 0:
                    lower[y] = 0
                if lower [y] > 255:
                    lower[y] = 255
            lower = np.array(lower, dtype = np.uint8)
            upper = np.array(upper, dtype = np.uint8)
            self.samples.append([lower, upper])
        
    def newMouse(self):
        x = self.handCoords[0]/640.0
        y = self.handCoords[1]/480.0
        x = 1920 - int(x*1920)
        y = int(y*1200)
        print(self.handCoords)
        win32api.SetCursorPos((x,y))

    def newMoveMouse(self):
        screenHeight = 1200.0
        screenWidth = 1920.0
        x = self.handCoords[0]#Camera frame x
        y = self.handCoords[1]#Camera frame y
        x = (x/self.cameraWidth)*self.screenWidth
        y = (y/self.cameraHeight)*self.screenHeight
        x = x - (self.screenWidth/2)#Moves the origin (point at coordinates (0,0) to the middle of the frame
        y = y - (self.screenHeight/2)
        x = x * self.xSF#Applies the stretch
        y = y * self.ySF
        x = -x #Flips the x axis 
        x = x + (self.screenWidth/2)#Replaces the origin to the corner
        y = y + (self.screenHeight/2)
        x = int(x)#Puts into interger form 
        y = int(y)

        if x > self.screenWidth:#Checks the coordinates are on the screen 
            x = int(self.screenWidth)
        elif x < 0:
            x = 0
        
        if y > self.screenHeight:
            y = int(self.screenHeight)
        elif y < 0:
            y = 0

        win32api.SetCursorPos((x,y))#Moves the cursor

        """
        test = detection()
        for i in range (100):
            cv2.imshow("Testing", test.calibrateFaceDetection())
            k = cv2.waitKey(30) & 0xff
            if k == 27:
                break
        if len(test.faceCoords) != 0:
            test.calibrateSamples()
        
        while True:
            test.temploop()
            cv2.imshow("Image", test.imageBGR)
            if k == 27:
                break
        cv2.destroyAllWindows()
        test.cap.release()
        """
        
