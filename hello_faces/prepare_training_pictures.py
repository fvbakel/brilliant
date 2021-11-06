#
# Given a directory with pictures, extract the face and 
# make files that are suitable for training
#
# based on https://www.instructables.com/Face-Detectionrecognition/

import numpy as np
import os
import cv2

default_model_file = "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"

data_dir = "/home/fvbakel/Documenten/faces/"
raw_dir = data_dir + "/raw"
train_dir = data_dir + "/train_data"

face_cascade = cv2.CascadeClassifier(default_model_file)
sampleN = 67

def process_image(img):
    global sampleN
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x,y,w,h) in faces:

        sampleN=sampleN+1
        face_img = gray[y:y+h, x:x+w]
        cv2.imshow('img',face_img)
        cv2.waitKey(100)
        id = input("Who is it: \n")
        cv2.imwrite(train_dir + "/User."+str(id)+ "." +str(sampleN)+ ".jpg", gray[y:y+h, x:x+w])

        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)


def process_file(filename):
    img = cv2.imread(filename)
    process_image(img)


def process_dir(input_dir):
    for filename in os.listdir(input_dir):
        if filename.endswith(".jpg"):
            process_file(os.path.join(input_dir, filename))

def process_web_cam():
    cap = cv2.VideoCapture(0)
    while True:
        ret, img = cap.read()
        cv2.imshow('WebCam',img)
        if cv2.waitKey(1) == 27:
            process_image(img)
            choice = input("Again? (Y/n) \n")
            if choice == "n":
                break
    cap.release()

#process_dir(raw_dir)

process_web_cam()


cv2.destroyAllWindows()