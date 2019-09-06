# Import libraries used for PiCamera
import picamera
import picamera.array
import time
import cv2
import numpy as np
from PIL import Image
# Import libraries used for send_an_email() function
import smtplib
from email.mime.multipart import MIMEMultipart  
from email.mime.base import MIMEBase  
from email.mime.text import MIMEText  
from email.utils import formatdate  
from email import encoders 
# Import for matrix
from PIL import ImageDraw

#from Adafruit_LED_Backpack import Matrix8x8
# Camera Settings
camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.framerate = 60
camera.vflip = False
camera.hflip = True

# Creates an array of frames that represents the image feed
rawframe = picamera.array.PiRGBArray(camera, size = (640,480))

def nothing(x):
    pass

def largest_area(contours):
    ''' Find largest contour in the current feed '''
    absolutemax = 0
    for contour in contours:
        maximum = cv2.contourArea(contour)
        if maximum > absolutemax:
            absolutemax = maximum
    return absolutemax

'''display = Matrix8x8.Matrix8x8()
display.begin()

def display1():
    display.clear()
    display.begin()
    image = Image.new('1', (8,8))
    draw = ImageDraw.Draw(image)
    draw.line((3,0,6,0), fill = 255)
    draw.line((0,2,0,5), fill = 255)
    draw.line((1,2,1,5), fill = 255)
    draw.line((3,7,6,7), fill = 255)
    draw.point((2,1), fill = 255)
    draw.point((2,6), fill = 255)
    draw.point((7,1), fill = 255)
    draw.point((7,6), fill = 255)
    draw.point((3,2), fill = 255)
    draw.point((3,5), fill = 255)
    draw.point((5,2), fill = 255)
    draw.point((5,5), fill = 255)
    draw.point((6,3), fill = 255)
    draw.point((6,4), fill = 255)
    display.set_image(image)
    display.write_display()'''

def flipHoriz(im):
    (width, height) = im.size
    editim = Image.new('RGB', (width,height))
    for x in range (width):
        for y in range(height):
            (red, green, blue) = im.getpixel((x, y))
            editim.putpixel( (width-1-x,y) , (red, green, blue))
    return editim
        
def send_an_email():
    ''' Sends email with attachment from my email address to another'''
    recipient = input("Please enter your email: ")
    toaddr = recipient       # To id 
    me = 'chris.velasquez511@gmail.com'          # your id
    subject = "SPIS 2019!"              # Subject
                
    msg = MIMEMultipart()  
    msg['Subject'] = subject  
    msg['From'] = me  
    msg['To'] = toaddr  
    msg.preamble = "Pictures!"   
    #msg.attach(MIMEText(text))
                
    part = MIMEBase('application', "octet-stream")  
    part.set_payload(open("Spis19.jpg", "rb").read())  
    encoders.encode_base64(part)  
    part.add_header('Content-Disposition', 'attachment; filename="Spis19.jpg"')   # File name and format name
    msg.attach(part)  
    try:  
        s = smtplib.SMTP('smtp.gmail.com', 587)  # Protocol
        s.ehlo()  
        s.starttls()  
        s.ehlo()  
        s.login(user = 'chris.velasquez511@gmail.com', password = 'chris1135952840')  # User id & password
        #s.send_message(msg)  
        s.sendmail(me, toaddr, msg.as_string())  
        s.quit()  
        #except:  
        #   print ("Error: unable to send email")
    except SMTPException as error:  
        print ("Error")                # Exception

#display = Matrix8x8,Matrix8x8()
#display.begin()
#def display_1():
#    display.clear()
#    image = Image.new('1', 
time.sleep(1)

# State 0
reddetected = 0
timestate = 0
FSM1NextState = 0
FSM1LastTime = 0

# Main Program
if __name__ == '__main__':
    try:
        ''' Video feed that will capture images and email once a large enough red object is detected'''
        for frame in camera.capture_continuous(rawframe, format = "bgr", use_video_port = True):

            rawframe.truncate(0)
            # Unaltered image feed 
            image = frame.array
               
            # apply a gaussian blur to image feed to identify and draw contours with less noise
            blurred_masked = cv2.GaussianBlur(image, (7,7), 0) 

            # convert the blurred_masked to HSV colorspace from BGR colorspace
            image_hsv = cv2.cvtColor(blurred_masked, cv2.COLOR_BGR2HSV)

            # Create ourmask1 using reds found at the beginning of the HSV colorspace
            lower_red = np.array([0, 120, 255])
            upper_red = np.array([10, 255, 255])
            ourmask1 = cv2.inRange(image_hsv, lower_red, upper_red)
            
            # Create ourmask2 using reds found at the end of the HSV colorspace
            lower_red = np.array([170,50,50])
            upper_red = np.array([180,255,255])
            ourmask2 = cv2.inRange(image_hsv, lower_red, upper_red)

            # Combine both masks to detect all reds in HSV image
            ourmask = ourmask1 + ourmask2
            
            # Binarize the masked image
            image_masked = cv2.bitwise_and(image, image, mask = ourmask)

            # Find contours based on the binarized image 
            _, contours, _ = cv2.findContours(ourmask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

            # Draw contours onto the original image feed
            cv2.drawContours(image, contours, -1, (0,255,0), 3)

            cv2.imshow("image", image)

            # If contours are found, call largest_area function to find largest contour
            if len(contours) != 0:
                absolutemax = largest_area(contours)
                print(absolutemax)
                if absolutemax > 62000:
                    # Only perform this function if the largest contour has just now entered the frame (if reddetected == 0:)
                    # Send an email once a big enough contour has been draw with that image as an attachment
                    # Change the state value to 1 so that this code doesn't run again even if the contour remains in the image
                    if reddetected == 0:
                        if timestate == 0:
                            print("Smile for the camera!")
                            currentTime = time.time()
                            FSM1LastTime = currentTime
                            timestate = 1
                        if timestate == 1:
                            currentTime = time.time()
                            print(currentTime - FSM1LastTime)
                            if currentTime - FSM1LastTime >= 3:
                                camera.capture( 'Spis2019.jpg')
                                Spisimage = Image.open("Spis2019.jpg")
                                Spisimage = flipHoriz(Spisimage)
                                Spisimage.save("Spis19.jpg")
                                flipimage = Image.open("Spis19.jpg")
                                flipimage.show()
                                send_an_email()
                                flipimage.close()
                                print("Enjoy!")
                                timestate = 0
                                reddetected = 1
                        else:
                            pass

                else:
                    # Once the contour shrinks below the threshold and you are in state 1 default back to state 0 
                    if absolutemax < 62000:
                        if reddetected == 1:
                            print("Object no longer detected")
                            reddetected = 0
                            
            cv2.waitKey(1)
            
    # Ctrl+C to end program 
    except KeyboardInterrupt:
        print("Program stopped by User")
        cv2.destroyAllWindows()
        camera.close()

