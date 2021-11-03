import numpy as np
import cv2
import os

default_model_file = "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"
data_dir = "/home/fvbakel/Documenten/faces/"
model_dir = data_dir + "/models"
model_name = "gezin"


def read_label_file(filename):
    names = dict()
    with open(filename) as f:
        for line in f:
            fields = line.split('|')
            names[int(fields[0])] = fields[1].rstrip()
    return names


face_cascade = cv2.CascadeClassifier(default_model_file)
cap = cv2.VideoCapture(0)
rec = cv2.face.LBPHFaceRecognizer_create()
rec.read(model_dir + os.sep + model_name + ".yml")
names = read_label_file(model_dir + os.sep + model_name + ".txt")
print(names)
# Colors we will use for the object labels
colors = np.random.uniform(0, 255, size=(len(names), 3))

id=0
while True:
    ret, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.5, 5)
    for (x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        id,conf=rec.predict(gray[y:y+h,x:x+w])
        person_name = "Unknown"
        if id in names:
            person_name = names[id]

        if conf > 255:
            conf = 255
        percentage = ((255- conf) / 255) * 100
        label = "{} ({:.0f} % sure)".format(person_name,percentage )
        #
        cv2.putText(img, label, (int(x), int(y)),cv2.FONT_HERSHEY_SIMPLEX, .75, colors[id], 2)
        
    cv2.imshow("Webcam",img)
    
    # Press ESC to quit
    if cv2.waitKey(1) == 27: 
        break 

cap.release()

cv2.destroyAllWindows()