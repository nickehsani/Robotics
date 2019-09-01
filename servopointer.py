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

ServoPinx = 7 #servo 1
ServoPiny = 11 #servo 2

GPIO.setup(ServoPinx, GPIO.OUT)
GPIO.setup(ServoPiny, GPIO.OUT)


rawframe = picamera.array.PiRGBArray(camera, size = (640,480))

#PWM stuff is here
pwm_frequency = 50
duty_min = 2.5 * float(pwm_frequency) / 50.0
duty_max =12.5 * float(pwm_frequency) / 50.0

def set_duty_cycle(angle):
    return ((duty_max - duty_min) * float(angle) / 180.0 + duty_min)

pwm_servox = GPIO.PWM(ServoPinx, pwm_frequency)
pwm_servoy = GPIO.PWM(ServoPiny, pwm_frequency) 

#no more pwm stuff


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

            if 

            cv2.imshow("Masked image", image_masked)

            cv2.waitKey(1)

            angle = 0
            pwm_servox.start(set_duty_cycle(angle))
            print ("Moving to angle 0")
	    time.sleep(1)            
            
            angle = 359
            pwm_servoy.start 

        cv2.destroyAllWindows()
        camera.close()

    except KeyboardInterrupt:
        print("Program stopped by User")
        cv2.destroyAllWindows()
        camera.close()

