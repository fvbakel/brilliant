import PySimpleGUIQt as sg                        # Part 1 - The import
import numpy as np
import os
import cv2

default_model_file = "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"

data_dir = "/home/fvbakel/Documenten/faces/"
raw_dir = data_dir + "/raw"
train_dir = data_dir + "/train_data"

face_cascade = cv2.CascadeClassifier(default_model_file)
sampleN = 70

def get_first_face(img,out_w,out_h):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:
        delta_w = (out_w - w) // 2
        delta_h = (out_h - h) // 2
        x_out = x - delta_w
        y_out = y - delta_h 
        if x_out < 0:
            x_out = 0
        if y_out < 0:
            y_out = 0    
        ##face_img = img[y:y+h, x:x+w]
        face_img = img[y_out:y_out+out_h, x_out:x_out+out_w]
        return face_img
    return None

def process_image(person_name,img):
    global sampleN
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x,y,w,h) in faces:

        sampleN=sampleN+1
        face_img = gray[y:y+h, x:x+w]
        cv2.imshow('Captured face',face_img)
        cv2.waitKey(1000)
        cv2.destroyAllWindows()
        cv2.imwrite(train_dir + "/User."+person_name+ "." +str(sampleN)+ ".jpg", gray[y:y+h, x:x+w])

def start_dialog():
    left_frame = [[sg.Image(filename='', key='_IMAGE_')]]
    right_frame = [ [sg.Image(filename='', key='_PERSON_')],
                    [sg.Text("Who is it?")],
                    [sg.Input()],
                    [sg.Button('Capture')],
                    [sg.Button('Quit')] 
                ]

    layout = [  [sg.Frame("", left_frame),sg.Frame("", right_frame)]]

    window = sg.Window('Window Title', layout)
                                                    
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    while True:
        event, values = window.Read(timeout=20, timeout_key='timeout')
        if event is None or event == 'Quit':
            break
        if event == 'Capture':
            person_name = values[0]
            if person_name is not None and person_name != "":
                process_image(person_name,frame)
        ret, frame = cap.read()

        imgbytes=cv2.imencode('.png', frame)[1].tobytes()
        window.FindElement('_IMAGE_').Update(data=imgbytes)
        person_img = get_first_face(frame,200,200)
        if person_img is not None:
            imgbytes=cv2.imencode('.png', person_img)[1].tobytes()
            window.FindElement('_PERSON_').Update(data=imgbytes)

    window.close()
    cap.release()

cv2.destroyAllWindows()

start_dialog()