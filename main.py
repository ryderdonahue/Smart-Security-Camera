import cv2
import sys
import os
from mail import sendEmail
from flask import Flask, render_template, Response
from camera import VideoCamera
import time
import threading
import pantilthat
import random

se_interval = 8 # sound effect inteval
last_se = 0

report_interval = 15
last_report = 0


update_interval = .25
last_epoch = 0
video_camera = VideoCamera(flip=True) # creates a camera object, flip vertically
# object_classifier = cv2.CascadeClassifier("models/upperbody_recognition_model.xml") # an opencv classifier

object_classifier4 = cv2.CascadeClassifier("models/h_upperbody.xml") 
tilt_offset_2 = 55

object_classifier5 = cv2.CascadeClassifier("models/haarcascade_fullbody.xml") 
object_classifier6 = cv2.CascadeClassifier("models/haarcascade_lowerbody.xml") 

object_classifier = cv2.CascadeClassifier("models/haarcascade_profileface.xml")
object_classifier2 = cv2.CascadeClassifier("models/haarcascade_frontalface_alt2.xml") 
object_classifier3 = cv2.CascadeClassifier("models/facial_recognition_model.xml") 
tilt_offset = 90

classifiers = [cv2.CascadeClassifier("models/haarcascade_profileface.xml"),
cv2.CascadeClassifier("models/haarcascade_frontalface_alt2.xml"),
cv2.CascadeClassifier("models/facial_recognition_model.xml"),
#cv2.CascadeClassifier("models/h_upperbody.xml"),
cv2.CascadeClassifier("models/haarcascade_fullbody.xml"),
cv2.CascadeClassifier("models/haarcascade_lowerbody.xml")]

classifiers_usage = [0,0,0,0,0,0]
# App Globals (do not edit)
app = Flask(__name__)


lost = True
lastKnownTime = 0
searchTime = 10
lastKnownPan = 0
lastKnownTilt = 0

sweepTime = 30
lastRandomSweep = 0

pan = -45
tilt = -30
pantilthat.pan(pan)
pantilthat.tilt(tilt)
soundDir = '~/Desktop/foley/'

overwatchDir = 'overwatch/radiovoice/'

mineDir = 'roller/mine/'
mineSounds = ['rmine_tossed1']

scannerDir = 'scanner/'
scannerSounds = ['scanner_talk1']

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

def playOverwatch():
        path = soundDir + overwatchDir + overwatchVoices[random.randint(0,len(overwatchVoices) - 1)] + '.wav'
        print path
        os.system('aplay ' + path)

def playSoundEffect():
        path = soundDir + scannerDir + scannerSounds[random.randint(0,len(scannerSounds) - 1)] + '.wav'
        print path
        os.system('aplay ' + path)
        
def playMineEffect():
        path = soundDir + mineDir + mineSounds[random.randint(0,len(mineSounds) - 1)] + '.wav'
        print path
        os.system('aplay ' + path)

def playConfirmSound():
        os.system('aplay ~/Desktop/foley/buttons/button9.wav')

def playStartSound():
        os.system('aplay ~/Desktop/foley/buttons/combine_button5.wav')

def playOverwatchSound():
        os.system('aplay ~/Desktop/foley/overwatch/radiovoice/reinforcementteamscode3.wav')

def clamp(n, smallest, largest): return max(smallest, min(n, largest))
def check_for_objects():
	global pan
	global tilt
	global tilt_offset
        playStartSound()
        global last_epoch
        global last_se
        global last_report
        global lastKnownPan
        global lastKnownTilt
        global lastKnownTime
        global lost
        global lastRandomSweep
        print 'searching for objects'
        
        while True:
                time.sleep(update_interval)
                frame, found_obj, xLocation, yLocation, classifier_used, height, width = video_camera.get_object(classifiers) 

                if not found_obj and (time.time() - lastKnownTime) < searchTime and (time.time() - lastKnownTime) > 1:
                        offset = 30
                        pan = lastKnownPan + random.randint(-30,30)
                        tilt = lastKnownTilt + random.randint(-30,30)
                        pantilthat.tilt(clamp(tilt, -70,70))
                        pantilthat.pan(clamp(pan, -90, 90))
                        if not lost:
                                soundThread3 = threading.Thread(target = playMineEffect, args = ())
                                soundThread3.start()
                                lost = True
                elif not found_obj and (time.time() - lastKnownTime) > 1 and  (time.time() - lastRandomSweep) > sweepTime:
                        lastRandomSweep = time.time()
                        pan = random.randint(-90,90)
                        tilt = random.randint(-70,70)
                        pantilthat.tilt(clamp(tilt, -30,30))
                        pantilthat.pan(clamp(pan, -90, 90))
                                        
                        
                if found_obj and (time.time() - last_epoch) > update_interval:
                        classifiers_usage[classifier_used] += 1
                        last_epoch = time.time()
                        pan -= (xLocation / (width / -60)) + 30
                        tilt -= ((yLocation+tilt_offset) / (height / -60)) + 30

                        lastKnownPan = pan
                        lastKnownTilt = tilt
			pantilthat.pan(clamp(pan, -90, 90))
			pantilthat.tilt(clamp(tilt, -70,70))
			#print used_secondary
                        #print 'x: %s' % (xLocation)
                        #print 'y: %s' % (yLocation)
                        #print "Sending email..."
                        sendEmail(frame)
			lastKnownTime = time.time()
			if lost and (time.time() - last_report) > report_interval:
                                lost = False
                                soundThread = threading.Thread(target = playOverwatch, args = ())
                                soundThread.start()
                                last_report = time.time()

                        if (time.time() - last_se) > se_interval:
                                soundThread2 = threading.Thread(target = playSoundEffect, args = ())
                                soundThread2.start()
                                last_se = time.time()
                        
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
