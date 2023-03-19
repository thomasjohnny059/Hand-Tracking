import Tkinter as tk
from PIL import Image, ImageTk
import cv2
import Main
import win32api
import win32con

calibrated = 0

class mainClass:
    def __init__(self,master):
        self.master = master
        self.master.title("Real-time Hand Tracking Accessibility Tool")

        self.running = 0

        self.img = ImageTk.PhotoImage(Image.open("CalibrationNeeded.png"))#The calibration image
        self.imageLabel = tk.Label(master, image = self.img)#sets the frame to show the calibration image by default
        self.imageLabel.grid(row = 0, column = 0, rowspan = 5)#Location of the image
        self.imageLoop()
        self.calibrateButton = tk.Button(master, text = "Calibrate", command = self.calibrateWindow, height = 5, width = 50, bg = "LIGHT BLUE")
        self.calibrateButton.grid(row = 0, column = 1, columnspan = 2)
        self.infoButton = tk.Button(master, text = "Info", command = self.infoButton, height = 5, width = 25, bg = "LIGHT BLUE")
        self.infoButton.grid(row = 1, column = 1)
        self.stopButton = tk.Button(master, text = "Start", height = 5, width = 24, bg = "GREEN", command = self.startStop)
        self.stopButton.grid( row = 1, column = 2)
        self.stopLabel = tk.Label(master, text = "Push to stop key:", font=("Helvetica",16))
        self.stopLabel.grid(row = 2, column = 1)
        self.settingButton = tk.Button(master, text = "Settings", command = self.settingsWindow, height = 5, width = 50, bg = "LIGHT BLUE")
        self.settingButton.grid(row = 3, column = 1, columnspan = 2)
        self.runningLabel = tk.Label(master, text = "Not Running", font = ("Helvetica", 16),bg = "RED")
        self.runningLabel.grid(row = 3, column = 1, columnspan = 2)
        self.stopKeyTextUpdate()

    def stopKeyTextUpdate(self):
        try:
            self.stopKeyLabel = tk.Label(self.master, text = self.app.stopKeyVar.upper(), font = ("Helvetica", 16))
            self.stopKeyLabel.grid(row = 2, column = 2)
            stopKeys = {
                "F1":win32con.VK_F1,
                "F2":win32con.VK_F2,
                "F3":win32con.VK_F3,
                "F4":win32con.VK_F4,
                "F5":win32con.VK_F5,
                "F6":win32con.VK_F6,
                "F7":win32con.VK_F7,
                "F8":win32con.VK_F8,
                "F9":win32con.VK_F9,
                }

            self.stopKeys(self.stopKeyVar.upper())
            print(self.stopKey)
        except AttributeError:
            self.stopKeyLabel = tk.Label(self.master, text= "F2", font = ("Helvetica", 16))
            self.stopKeyLabel.grid(row = 2, column = 2)
            self.stopKey = win32con.VK_F2

    def calibrateWindow(self):
        self.newWindow = tk.Toplevel(self.master)
        self.app = calibration(self.newWindow)

    def infoWindow(self):
        self.newWindow = tk.Toplevel(self.master)
        self.app = info(self.newWindow)

    def settingsWindow(self):
        self.newWindow = tk.Toplevel(self.master)
        self.app = settings(self.newWindow)

    def imageLoop(self):
        global calibrated
        if calibrated: #Checks the calibrated variable 
            cameraFeed.temploop()#If calibrated, it shows the camera image
            image = cameraFeed.imageBGR
            cv2image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.imageLabel.imgtk = imgtk
            self.imageLabel.configure(image = imgtk)
            if self.running:
                cameraFeed.newMoveMouse()
                if win32api.GetAsyncKeyState(self.stopKey) != 0:
                    self.startStop()
        else:
            self.imageLabel.configure(image = self.img)#Else shows the calibration needed image
        self.imageLabel.after(10, self.imageLoop)#Loops

    def startStop(self):
        if calibrated:
            self.running = not(self.running)
            if self.running:
                self.stopButton.configure (bg = "RED", text = "Stop")
                self.runningLabel.configure (bg = "GREEN", text = "Running")
            else:
                self.stopButton.configure (bg = "GREEN", text = "Start")
                self.runningLabel.configure (bg = "RED", text = "Not Running")
class calibration:
    def __init__ (self, master):
        global calibrated
        calibrated = 0

        self.master = master
        self.master.title("Calibration")

        self.imageLabel = tk.Label (self.master)
        self.imageLabel.grid(row=0, column=0, columnspan=2)
        self.showFrame()

        self.quitButton = tk.Button(self.master, text = "Quit", width = 25, command = self.close_windows)
        self.quitButton.grid(row = 3, column = 0)

        self.nextButton = tk.Button(self.master, text = "Next", command = self.stage2, width = 25)
        self.nextButton.grid(row = 3, column = 1)
        self.instructions = tk.Label(master, text = "Make sure your image has a clear background and")
        self.instructions2 = tk.Label(master, text = "do not wear short sleeves. ")
        self.instructions.grid(row = 1, column = 0, columnspan = 2)
        self.instructions2.grid(row = 2, column = 0, columnspan = 2)

    def showFrame(self):
        image = cameraFeed.cap.read()#Captures an image
        cv2image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)#converts format of the image
        img = Image.fromarray(cv2image)#Converts again into a format that tkinter accepts 
        imgtk = ImageTk.PhotoImage(image=img)
        self.imageLabel.imgtk = imgtk
        self.imageLabel.configure(image=imgtk)
        self.imageLabel.after(10, self.showFrame)

    def showFace(self):
        image = cameraFeed.calibrateFaceDetection()
        cv2image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.imageLabel.imgtk = imgtk
        self.imageLabel.configure(image=imgtk)
        self.imageLabel.after(10, self.showFace)

    def showMask(self):
        cameraFeed.changeTolerance(self.toleranceSlider.get())
        _, cameraFeed.imageBGR = cameraFeed.cap.read()
        cameraFeed.imageHSV = cv2.cvtColor(cameraFeed.imageBGR, cv2.COLOR_BGR2HSV)
        cameraFeed.imageHSV = cv2.blur(cameraFeed.imageHSV, (5,5))
        cameraFeed.createMask()

        image = cameraFeed.mask
        img = Image.fromarray(image)
        imgtk = ImageTk.PhotoImage(image = img)
        self.imageLabel.imgtk = imgtk
        self.imageLabel.configure(image = imgtk)
        self.imageLabel.after(10, self.showMask)

    def close_windows(self):
        self.master.destroy()

    def stage2(self):
        self.instructions.destroy
        self.instructions2.destroy()
        self.nextButton.destory()
        self.quitButton.destroy()
        self.imageLabel.destroy()

        self.imageLabel = tk.Label(self.master)
        self.imageLabel.grid(row = 0, column = 0, columnspan = 2)
        self.showFace()

        self.instructions = tk.Label(self.master, text = "Ensure your face is within the blue box, and there is a green box around each eye.")
        self.instruction2 = tk.Label(self.master, text = "When there is, click 'Next'")
        self.instructions.grid(row = 1, column = 0, columnspan = 2)
        self.instruction2.grid(row = 2, column = 0, columnspan = 2)

        self.quitButton = tk.Button(self.master, text = 'Quit', width = 25, command = self.close_windows)
        self.quitButton.grid(row = 3, column = 0)
        
        self.nextButton = tk.Button(self.master, text = 'Next', width = 25, command = self.stage3)
        self.nextButton.grid(row = 3, column = 1)

    def gotostage2(self):
        self.yesButton.destroy()
        self.noButton.destroy()
        self.stage2()

    def stage3(self):
        self.instructions.destroy()
        self.instructions2.destroy()
        self.nextButton.destroy()
        self.quitButton.destroy()
        self.imageLabel.destroy()

        self.imageLabel = tk.Label(self.master)
        self.imageLabel.grid(row = 0, column = 0, columnspan = 3)

        image = cameraFeed.imageBGR
        cv2image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image = img)
        self.imageLabel.imgtk = imgtk
        self.imageLabel.configure(image = imgtk)

        self.instructions = tk.Label(self.master, text = "Is the blue box around your face, and green boxes areound your eyes?")
        self.instructions.grid(row = 1, column = 0, columnspan = 3)

        self.yesButton = tk.Button(self.master, text = 'Yes', width = 25, command = self.gotostage4)
        self.noButton = tk.Button(self.master, text = 'No', width = 25, command = self.gotostage2)
        self.yesButton.grid(row = 2, column = 2)
        self.noButton.grid(row = 2, column = 1)

        self.quitButton = tk.Button(self.master, text = 'Quit', width = 25, command = self.close_windows)
        self.quitButton.grid(row = 2, column = 0)

    def gotostage4(self):
        try:
            self.stage4()
        except ValueError:
            self.crash()

    def stage4(self):
        self.instructions.destroy()
        self.yesButton.destroy()
        self.noButton.destroy()
        self.quitButton.destroy()
        self.imageLabel.destroy()

        self.imageLabel = tk.Label(self.master)
        self.imageLabel.grid(row = 0, column = 0, columnspan = 3)

        self.instructions = tk.label(self.master, text = "Adjust the slider so that your face and hands are clear")
        self.instructions2 = tk.Label(self.master, text = "and so that there is a minimum amount of background white spots. ")
        self.instructions.grid(row = 1, column = 0, columnspan = 3)
        self.instructions2.grid(row = 2, column = 0, columnspan = 3)

        self.toleranceSlider = tk.Scale(self.master, from_ = 0, to = 50, orient = tk.HORIZONTAL, length = 400)
        self.toleranceSlider.grid(row = 3, column = 0, columnspan = 3)

        self.finishButton = tk.Button(self.master, text = "Finish", width = 25, command = self.finish)
        self.finishButton.grid(row = 4, column = 0, columnspan = 3)

        cameraFeed.calibrateSamples()
        self.showMask()

    def finish(self):
        global calibrated 
        calibrated = 1
        self.close_windows()

    def crash(self):
                mainApp.calibrateWindow()
                self.close_windows()

class info():
    def __init__(self, master):
        self.master = master

        self.calibrationInstructionsButton = tk.Button(self.master, text = "Calibration Instructions", height = 3, width = 40, bg = 'LIGHT BLUE', command = self.instructionWindow)
        self.calibrationInstructionsButton.grid(row = 0, column = 0)

        self.infoText = tk.Label(self.master, text = "About this software:", font = ("Helvetica", 16))
        self.infoText.grid(row = 1, column = 0)
        aboutThisSoftware = """This software is hand detection software that is used to move the mouse.\nClick 'Calibrate' to teach it how to recognise you, and then you can see how it detects your hand./nThe green outline of your hand, abd thge blue dot is the centre of your hand.\nThis is the point that is used to move the mouse.\n The red box is the area that the blue dot can move in that moves the mouse.\nThe smaller the box, the faster the mouse moves. This 'Active Region' can be adjusted in the settings"""
        self.aboutThisSoftwareLabel = tk.Label(self.master, text = aboutThisSoftware, justify = tk.LEFT, wraplength = 500)
        self.aboutThisSoftwareLabel.grid(row = 2, column = 0)
        self.infoText2 = tk.label(self.master, text = "How to use this software:", font = ("Helvetica", 16))
        self.infoText2.grid(row = 3, column = 0)
        howToUse = """Click Calibrate and follow the calibration instructions to start using this software (click on calibration instructions above if you're not sure what to do).\nWhen this is done you will see that it can track your hand. To start moving the mouse with your hands click 'Start'.\nTo stop the mouse from moving, either click 'Stop' or press the push to stop button (this is shown on the main windows , by default it is F2). To change the button that stops the program, click on settings and type in a new F-key (e.g. 'F1', 'f3', can go from F1 to F9)\nTo adjust the speed that the mouse moves adjust the sliders in the settings menu.\nIf the program is running slowly, tick the 'Low processing mode' tick box in settings."""
        self.howToUseLabel = tk.Label(self.master, text = howToUse, justify = tk.LEFT, wraplength = 500)
        self.howToUseLabel.grid (row = 4, column = 0)
        self.exitButton = tk.Button(master, text = "Exit", command = self.close_windows, width = 40, bg = 'LIGHT BLUE')
        self.exitButton.grid(row = 5, column = 0)

    def close_windows(self):
        self.master.destroy()
    
    def instructionsWindow(self):
        self.instrWindow = tk.Toplevel(self.master)
        self.app = instructions(self.instrWindow)

class instructions():
    def __init__(self, master):
        self.master = master 
        self.img = ImageTk.PhotoImage(Image.open("infoImg1.png"))
        self.imgLabel = tk.label(self.master, image = self.img)
        self.imgLabel.grid(row = 0, column = 0)
        text = """Set up your camera so that it is pointer at you. This program uses colour to detect your hands, so wear long sleeves so that it does not detect your arms instead of your hands. Try not to be in a location with a clear background so that it does not detect background objects."""
        self.textLabel = tk.Label(self.master, text = text, justify = tk.LEFT, wraplength = 600, font = ("Helvetica", 10))
        self.textLabel.grid (row = 1, column = 0)
        
        self.nextButton = tk.Button(self.master, text = "Next Step", command = self.step2, width = 40, bg = 'LIGHT BLUE')
        self.nextButton.grid(row = 2, column = 0)

    def step2(self):
        self.imgLabel.destroy()
        self.textLabel.destroy()
        self.nextButton.destroy()

        self.img = ImageTk.PhotoImage(Image.open("infoImg2.png"))
        self.imgLabel = tk.label(self.master, image = self.img)
        self.imgLabel.grid(row = 0, column = 0)
        text = """The program then will try to find your face and eyes. When the blue box is around your face and there is a green box over each eye (and no where else), click next"""
        self.textLabel = tk.Label(self.master, text = text, justify = tk.LEFT, wraplength = 600, font = ("Helvetica", 10))
        self.textLabel.grid(row = 1, column = 0)

        self.nextButton = tk.Button(self.master, text = "Next step", command = self.step3, width = 40, bg = 'LIGHT BLUE')
        self.nextButton.grid(row = 2, column = 0)

    def step3(self):
        self.imgLabel.destroy()
        self.textLabel.destroy()
        self.nextButton.destroy()

        self.img = ImageTk.PhotoImage(Image.open("infoImg3.png"))
        self.imgLabel = tk.label(self.master, image = self.img)
        self.imgLabel.grid(row = 0, column = 0)
        text = """You have the option to confirm the image, or if the boxes have moved you can re-take it."""
        self.textLabel = tk.Label(self.master, text = text, justify = tk.LEFT, wraplength = 600, font = ("Helvetica", 10))
        self.textLabel.grid(row = 1, column = 0)

        self.nextButton = tk.Button(self.master, text = "Next step", command = self.step4, width = 40, bg = 'LIGHT BLUE')
        self.nextButton.grid(row = 2, column = 0)

    def step4(self):
        self.imgLabel.destroy()
        self.textLabel.destroy()
        self.nextButton.destroy()

        self.img = ImageTk.PhotoImage(Image.open("infoImg4.png"))
        self.imgLabel = tk.label(self.master, image = self.img)
        self.imgLabel.grid(row = 0, column = 0)
        text = """This is what the program sees. Adjust the slider so that it can see your face clearly. Hold up a hand and make sure that there is as little background noise as possible (as shown in the top right in this image). Click finish, and the program is calibrated!"""
        self.textLabel = tk.Label(self.master, text = text, justify = tk.LEFT, wraplength = 600, font = ("Helvetica", 10))
        self.textLabel.grid(row = 1, column = 0)
        
        self.nextButton = tk.Button(self.master, text = "Finish", command = self.close_windows, width = 40, bg = 'LIGHT BLUE')
        self.nextButton.grid(row = 2, column = 0)

    def close_windows(self):
        self.master.destroy()

class settings():
    def __init__(self,master):
        self.master = master
        self.master.title("Settings")

        self.topKeyText = tk.Label(self.master, text = """Push to stop Key: (F-Keys 1 to 9, enter in the form 'F1' or 'f7')""")
        self.topKeyText.grid(row = 0, column = 0, columnspan = 1)

        self.topKeyText2 = tk.Label(self.master, text="")
        self.topKeyText2.grid(row = 0, column = 3)

        self.stopKeyVar = tk.StringVar()
        self.stopKeyEntry = tk.Entry(self.master, textvariable = self.stopKeyVar)
        self.stopKeyEntry.grid(row = 0, column = 1)

        self.stopKeyButton = tk.Button(self.master, text = "Set", command = self.stopKeyGet)
        self.stopKeyButton.grid(row = 0, column = 2)

        self.xSpeedText = tk.Label(self.master, text = "Horizontal speed:")
        self.xSpeedText.grid(row = 1, column = 0)
        self.xSpeedSlider = tk.Scale(self.master, from_ = 1, to = 10, orient = tk.HORIZONTAL, length = 400)
        self.xSpeedSlider.set(cameraFeed.xSF*10 - 10)
        self.xSpeedSlider.grid(row = 1, column = 1)

        self.ySpeedText = tk.Label(self.master, text = "Vertical speed:")
        self.ySpeedText.grid(row = 2, column = 0)
        self.ySpeedSlider = tk.Scale(self.master, from_ = 1, to = 10, orient = tk.HORIZONTAL, length = 400)
        self.ySpeedSlider.set(cameraFeed.ySF*10 - 10)
        self.ySpeedSlider.grid(row = 2, column = 1)

        self.lowModeText = tk.Label(self.master, text = "Low Processing Mode:")
        self.lowModeVar = tk.IntVar()
        self.lowModeCheckbutton = tk.Checkbutton (self.master, variable = self.lowModeVar, onvalue = 1, offvalue = 0)
        self.lowModeText.grid(row = 3, column = 0)
        self.lowModeCheckbutton.grid(row = 3, column = 1)
        if cameraFeed.lowMode == 1:
            self.lowModeCheckbutton.toggle()

        self.exitButton = tk.Button(master, text = "Exit", command = self.close_windows, width = 40, bg = 'LIGHT BLUE')
        self.exitButton.grid(row = 4, column = 0, columnspan = 4)

    def stopKeyGet(self):
        if len(self.stopKeyEntry.get()) == 2:
            if self.stopKeyEntry.get()[0].upper() == "F" and int(self.stopKeyEntry.get()[1]) >= 1 and int(self.stopKeyEntry.get()[1]) <= 9:
                self.stopKeyVar = self.stopKeyEntry.get()
                print(self.stopKeyVar)
                mainApp.stopKeyTextUpdate()
                self.stopKeyButton.configure(bg = "WHITE")
                self.topKeyText.configure(fg = "BLACK")

            else:
                self.stopKeyInputError()
        else:
            self.stopKeyInputError()

    def stopKeyInputError(self):
        self.stopKeyButton.configure(bg = "RED")
        self.topKeyText.configure(fg = "DARK RED")

    def close_windows(self):
        cameraFeed.xSF = (self.xSpeedSlider.get()+10)/10.0
        cameraFeed.ySF = (self.ySpeedSlider.get()+10)/10.0
        cameraFeed.lowMode = self.lowModeVar.get()
        self.master.destroy()

cameraFeed = MainDevelopment.detection()

if __name__ == "__main__":
    root = tk.Tk()
    mainApp = mainClass(root)
    root.mainloop()





        




