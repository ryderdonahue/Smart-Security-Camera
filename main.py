import cv2
import sys
import os
from mail import sendEmail
from flask import Flask, render_template, Response
from camera import VideoCamera
import time
import threading
import pantilthat

update_interval = .25 # sends an email only once in this time interval
video_camera = VideoCamera(flip=True) # creates a camera object, flip vertically
# object_classifier = cv2.CascadeClassifier("models/upperbody_recognition_model.xml") # an opencv classifier

#object_classifier = cv2.CascadeClassifier("models/h_upperbody.xml") # an opencv classifier
#tilt_offset = 55

object_classifier2 = cv2.CascadeClassifier("models/haarcascade_frontalface_alt2.xml") # an opencv classifier
object_classifier = cv2.CascadeClassifier("models/haarcascade_profileface.xml") # an opencv classifier

object_classifier3 = cv2.CascadeClassifier("models/facial_recognition_model.xml") # an opencv classifier
tilt_offset = 30

# App Globals (do not edit)
app = Flask(__name__)
last_epoch = 0
pan = 0
tilt = 0
pantilthat.pan(pan)
pantilthat.tilt(tilt)
soundDir = '~/Desktop/foley/'

overwatchDir = 'overwatch/radiovoice/'

overwatchVoices = ['sociostabilizationrestored', 
'fugitive17f', 
'recievingconflictingdata', 
'airwatchcopiesnoactivity',
'allunitsverdictcodeonsuspect',
'restrictedincursioninprogress',
'lostbiosignalforunit',
'youarejudgedguilty',
'airwatchreportspossiblemiscount',
'statuson243suspect'
]

def playOverwatch(num):
        path = soundDir + overwatchDir + overwatchVoices[(num % len(overwatchVoices))] + '.wav'
        print path
        os.system('aplay ' + path)

def playConfirmSound():
        os.system('aplay ~/Desktop/foley/buttons/button9.wav')

def playStartSound():
        os.system('aplay ~/Desktop/foley/buttons/combine_button5.wav')

def playOverwatchSound():
        os.system('aplay ~/Desktop/foley/overwatch/radiovoice/reinforcementteamscode3.wav')


def check_for_objects():
	global pan
	global tilt
	global tilt_offset
        playStartSound()
        global last_epoch
        print 'searching for objects'
        while True:
                time.sleep(update_interval)
                frame, found_obj, xLocation, yLocation = video_camera.get_object(object_classifier) 
                used_secondary = False
                if not found_obj:
                        used_secondary = True
                        frame, found_obj, xLocation, yLocation = video_camera.get_object(object_classifier2)        
                if found_obj and (time.time() - last_epoch) > update_interval:
                        last_epoch = time.time()
                        pan -= (xLocation / -5.33333) + 30
                        pantilthat.pan(pan)
			tilt -= ((yLocation+tilt_offset) / (240 / -60)) + 30
			pantilthat.tilt(tilt)
			print used_secondary
                        #print 'x: %s' % (xLocation)
                        #print 'y: %s' % (yLocation)
                        #print "Sending email..."
 #                       sendEmail(frame)
                        #playOverwatch(xLocation)
                        #print "done!"
                        
check_for_objects()

@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(video_camera),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    t = threading.Thread(target=check_for_objects, args=())
    t.daemon = True
    t.start()
    app.run(host='0.0.0.0', debug=False)
