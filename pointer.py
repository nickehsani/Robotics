# Import libraries used for PiCamera
import picamera
import picamera.array
import time
import cv2
import numpy as np
# Import libraries used for send_an_email() function
import smtplib
from email.mime.multipart import MIMEMultipart  
from email.mime.base import MIMEBase  
from email.mime.text import MIMEText  
from email.utils import formatdate  
from email import encoders 

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
        
        
        
def send_an_email():
    ''' Sends email with attachment from my email address to another'''
    recipient = input("Please enter your email: ")
    toaddr = recipient       # To id 
    me = 'chris.velasquez511@gmail.com'          # your id
    subject = "SPIS 2019!"              # Subject
    print("part1")
                
    msg = MIMEMultipart()  
    msg['Subject'] = subject  
    msg['From'] = me  
    msg['To'] = toaddr  
    msg.preamble = "test "   
    #msg.attach(MIMEText(text))
    print("part2")
                
    part = MIMEBase('application', "octet-stream")  
    part.set_payload(open("Spis2019.jpg", "rb").read())  
    encoders.encode_base64(part)  
    part.add_header('Content-Disposition', 'attachment; filename="Spis2019.jpg"')   # File name and format name
    msg.attach(part)  
    print("part3")
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
        print("pleasework")
    except SMTPException as error:  
        print ("Error")                # Exception

time.sleep(1)

# State 0
reddetected = 0

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
                if absolutemax > 50000:
                    # Only perform this function if the largest contour has just now entered the frame (if reddetected == 0:)
                    # Send an email once a big enough contour has been draw with that image as an attachment
                    # Change the state value to 1 so that this code doesn't run again even if the contour remains in the image
                    if reddetected == 0:
                        time.sleep(2)
                        camera.capture( 'Spis2019.jpg')
                        send_an_email()
                        print("its golden hour")
                        reddetected = 1
                else:
                    # Once the contour shrinks below the threshold and you are in state 1 default back to state 0 
                    if absolutemax < 50000:
                        if reddetected == 1:
                            print("it ain't golden hour no more :(")
                            reddetected = 0
                            
            cv2.waitKey(1)
            
    # Ctrl+C to end program 
    except KeyboardInterrupt:
        print("Program stopped by User")
        cv2.destroyAllWindows()
        camera.close()
