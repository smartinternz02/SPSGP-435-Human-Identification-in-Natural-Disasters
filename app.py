from __future__ import division, print_function

import os
from twilio.rest import Client
#import shutil
#from os import path
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
#from flask_mail import Mail, Message


#from twilio.rest import Client
#from sendgrid import SendGridAPIClient
#from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)
#import smtplib
app=Flask(__name__)
'''mail=Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'mansi22ag@gmail.com'
app.config['MAIL_PASSWORD'] = 'Mansiag22'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)'''

ls=[]
loc=[]
count=[]
hog=cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
geolocator=Nominatim(user_agent="People Count")

print("[INFO] accessing video stream..")
video_capture=cv2.VideoCapture('video2.mp4')

z=0

def detect(image):
        try:
                image=imutils.resize(image,width=min(400,image.shape[1]))
        except:
                account_sid = "AC7e9349d6774b81ec0a1f66fb53ddaab7"
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

                print(message.sid)
                '''sender = 'umakunuthuru@gmail.com'
                receivers = ['mansi22ag@gmail.com']
                message = """From: From Person <from@fromdomain.com>
                To: To Person <to@todomain.com>
                MIME-Version: 1.0
                Content-type: text/html
                Subject: SMTP HTML e-mail test

                This is an e-mail message to be sent in HTML format

                <b>This is HTML message.</b>
                <h1>This is headline.</h1>
                """

                try:
                   smtpObj = smtplib.SMTP('localhost')
                   smtpObj.sendmail(sender, receivers, message)         
                   print("Successfully sent email")
                except SMTPException:
                   print("Error: unable to send email")'''
                '''z=1
                print("Yes")
                msg = Message('Hello', sender = 'mansi22ag@gmail.com', recipients = ['mansi22ag@gmail.com'])
                print("Yes")
                msg.body = "Hello Flask message sent from Flask-Mail"
                print("Yes")
                mail.send(msg)            
                print(msg)
                return "Sent"'''
                #if(path.exits("output/location.csv")):
                #   src=path.realpath("output/location.csv");
                #root_dir,tail=path.split(src)
                #shutil.make_archive("outputarchive","csv",root_dir)
                '''message = Mail(
                    from_email='human@gmail.com',
                    to_emails='mansi22ag@gmail.com',
                    subject='Images and locations of humans in a disaster.',
                    html_content='<strong>and easy to do anywhere, even with Python</strong>'
                )

                with open('output/location.csv', 'rb') as f:
                    data = f.read()
                    f.close()
                encoded_file = base64.b64encode(data).decode()

                attachedFile = Attachment(
                    FileContent(encoded_file),
                    FileName('location.csv'),
                    FileType('location/csv'),
                    Disposition('attachment')
                )
                message.attachment = attachedFile

                sg = SendGridAPIClient(os.environ.get('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'))
                response = sg.send(message)
                print(response.status_code, response.body, response.headers)
                #flash('The images of people and the locations have been sent your mail')
                #sys.exit()'''
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

@app.route('/')
def index():
        return render_template('index.html')

def gen():
    while True:
        _,frame = video_capture.read()
        try:
                image=detect(frame)
        except:
                exit(0)
        (flag,encodedImage)=cv2.imencode(".jpg",image)
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage)+ b'\r\n')


@app.route('/video_feed')
def video_feed():
        return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame')

if(__name__=='__main__'):
    app.run(host='0.0.0.0',debug=True)
