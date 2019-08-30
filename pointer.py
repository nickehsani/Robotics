import picamera
import picamera.array
import time
import cv2
import numpy as np
import RPi.GPIO as GPIO


camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.framerate = 60
camera.vflip = False
camera.hflip = True

GPIO.setmode(GPIO.BOARD)

ServoPinx = 7
ServoPiny = 11

GPIO.setup(ServoPinx, GPIO.OUT)
GPIO.setup(ServoPiny, GPIO.OUT)


rawframe = picamera.array.PiRGBArray(camera, size = (640,480))

def nothing(x):
    pass

time.sleep(1)


# Main Program

if __name__ == '__main__':
    try:

        # Video stream that will only display red objects
        for frame in camera.capture_continuous(rawframe, format = "bgr", use_video_port = True):

            rawframe.truncate(0)

            image = frame.array

            image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            lowerColorThreshold = np.array([0, 153, 41])
            upperColorThreshold = np.array([255, 255, 255])

            ourmask = cv2.inRange(image_hsv, lowerColorThreshold, upperColorThreshold)

            image_masked = cv2.bitwise_and(image, image, mask = ourmask)

            cv2.imshow("Masked image", image_masked)

            cv2.waitKey(1)
            
             

        cv2.destroyAllWindows()
        camera.close()

    except KeyboardInterrupt:
        print("Program stopped by User")
        cv2.destroyAllWindows()
        camera.close()
