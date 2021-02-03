from __future__ import division, print_function

import os
from zipfile import ZipFile 
from twilio.rest import Client
import shutil
from os import path
import numpy as np
import base64
import cv2
from  imutils.object_detection import non_max_suppression
import csv
import imutils
from flask import request,Flask,flash,url_for,render_template,Response
import requests
import sys
import random
from geopy.geocoders import Nominatim
#from goto import goto, label
#import smtplib
from flask_mail import Mail, Message


#from twilio.rest import Client
#from sendgrid import SendGridAPIClient
#from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)
#import smtplib
app=Flask(__name__)
mail=Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'mansi22ag@gmail.com'
app.config['MAIL_PASSWORD'] = 'Mansiag22'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

ls=[]
loc=[]
count=[]
hog=cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
geolocator=Nominatim(user_agent="People Count")

print("[INFO] accessing video stream..")
video_capture=cv2.VideoCapture('video3.mp4')

z=0

def detect(image):
        try:
                image=imutils.resize(image,width=min(400,image.shape[1]))
        except:
                print("Video over")
                '''account_sid = "AC7e9349d6774b81ec0a1f66fb53ddaab7"
                # Your Auth Token from twilio.com/console
                auth_token  = "8373d2e77ed2e996efece1c87c4812a2"

                client = Client(account_sid, auth_token)

                message = client.messages \
                .create(
                     body='Images of people and the location of people during a disaster'+'output/',
                     #media_url='D:\MANSI\smartbridge\Detection of people in a disaster\output',
                     from_='+12157178767',
                     to='+918106772300'
                 )
                
                print(message.sid)'''
               
        orig=image.copy()
        (rects, weights) = hog.detectMultiScale(image, winStride=(4, 4),padding=(8, 8), scale=1.05)
        for(x,y,w,h) in rects:
            cv2.rectangle(orig,(x,y),(x+w,y+h),(0,0,255),2)
        rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
        pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)
        ls.append(len(pick))
        
        for(xA,yA,xB,yB) in pick:
            da=cv2.rectangle(image,(xA,yA),(xB,yB),(0,255,0),2)
            location=geolocator.geocode("Hyderabad")
            print(location.latitude,location.longitude)
            loc.append(location.latitude)
            loc.append(location.longitude)
            cv2.imwrite('Output/image'+str(random.randint(1,100))+'.jpg',da)
            with open('Output/location.csv',mode='a',newline="") as csv_file:
                writer=csv.writer(csv_file,delimiter=',')
                writer.writerow(loc)
                loc.clear()
        return image

def get_all_file_paths(directory): 

	# initializing empty file paths list 
	file_paths = [] 

	# crawling through directory and subdirectories 
	for root, directories, files in os.walk(directory): 
		for filename in files: 
			# join the two strings in order to form the full filepath. 
			filepath = os.path.join(root, filename) 
			file_paths.append(filepath) 

	# returning all file paths 
	return file_paths

@app.route('/')
def index():
        return render_template('index.html')

@app.route('/message123')
def message123():
        '''if(path.exists("output")):
           src=path.realpath("output");
        root_dir,tail=path.split(src)
        shutil.make_archive("outputarchive","zip",root_dir)'''
        directory = './output'

	# calling function to get all file paths in the directory 
        file_paths = get_all_file_paths(directory) 

	# printing the list of all files to be zipped 
        print('Following files will be zipped:') 
        for file_name in file_paths: 
                print(file_name)
        
        with ZipFile('images_locations.zip','w') as zip:
                for file in file_paths:
                        zip.write(file)
	#print('All files zipped successfully!')
        msg = Message('Alert!||Disaster Management Department', sender = 'mansi22ag@gmail.com', recipients = ['mansi22ag@gmail.com'])
        msg.body = "Images and locations of the victims in the disaster."
        with app.open_resource("images_locations.zip") as fp:  
                msg.attach("images_locations.zip","file/zip",fp.read())  
        mail.send(msg)
        return "Mail Sent."

def gen():
    while True:
        _,frame = video_capture.read()
        image=detect(frame)
        (flag,encodedImage)=cv2.imencode(".jpg",image)
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage)+ b'\r\n')


@app.route('/video_feed')
def video_feed():
        return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame')

if(__name__=='__main__'):
    app.run(host='0.0.0.0',debug=True)
