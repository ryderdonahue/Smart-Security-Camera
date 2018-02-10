import cv2
from imutils.video.pivideostream import PiVideoStream
import imutils
import time
import numpy as np
import pprint
class VideoCamera(object):
    def __init__(self, flip = True):
        self.vs = PiVideoStream((640,480)).start()
        self.vs.camera.vflip = True
#        self.vs.camera.framerate = 30
        #self.vs.camera.exposure_mode = 'night'
        #self.vs.camera.vflip = True
        self.flip = flip
        self.vs.camera.start_preview()
        
        time.sleep(2.0)

    def __del__(self):
        self.vs.stop()

    def flip_if_needed(self, frame):
#	return frame
        if not self.flip:
            return np.flip(frame, 0)
        return frame

    def get_frame(self):
        frame = self.flip_if_needed(self.vs.read())
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tostring().tobytes()

    def get_object(self, classifiers):
        found_objects = False
        xLocation = 0
        yLocation = 0
        frame = self.flip_if_needed(self.vs.read()).copy() 
#	print(frame[1].size
	height, width = frame.shape[:2]
        #print width
	#print height
#	small = cv2.resize(frame, (width/2, height/2), interpolation = cv2.INTER_AREA)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	classifier_used = -1
        for i in range(len(classifiers)):     
            objects = classifiers[i].detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(64, 64),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            if len(objects) > 0:
                found_objects = True
                print 'found with %s' % i
                classifier_used = i
                break
    
        

        # Draw a rectangle around the objects
        for (x, y, w, h) in objects:
            cv2.circle(frame, (x + w / 2, y + h / 2), 10, (0, 255, 0), 2)
            xLocation = x
            yLocation = y
        
        ret, jpeg = cv2.imencode('.jpg', frame)
        return (jpeg.tobytes(), found_objects, xLocation, yLocation, classifier_used, width, height)


