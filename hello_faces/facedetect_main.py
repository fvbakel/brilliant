import PySimpleGUIQt as sg
import numpy as np
import os
import cv2
from datetime import datetime
from PIL import Image

class Configuration:

    def __init__(self):
        self.default_model_file = "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"
        self.data_dir = "/home/fvbakel/Documenten/faces"
        self.raw_dir = self.data_dir + "/raw"
        self.train_dir = self.data_dir + "/train_data"
        self.model_dir = self.data_dir + "/models"
        self.model_name = "gezin"
        self.model_file = self.model_dir + os.sep + self.model_name + ".yml"
        self.label_file = self.model_dir + os.sep + self.model_name + ".txt"

class FaceDetector:
    def __init__(self, configuration):
        self.configuration = configuration
        self.face_cascade = cv2.CascadeClassifier(self.configuration.default_model_file)
        self.id_vs_name = dict()
        self.name_vs_id = dict()
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.recognizer.read(self.configuration.model_file)
        self.read_label_file(self.configuration.label_file)
        self.current_image = None
        self.current_gray_image = None

    def read_label_file(self,filename):
        self.id_vs_name = dict()
        with open(filename) as f:
            for line in f:
                fields = line.split('|')
                name = fields[1].rstrip()
                id = int(fields[0])
                self.id_vs_name[id] = name
                self.name_vs_id[name] = id

    def get_first_face(self,out_w,out_h):
        faces = self.get_faces_rectangles()
        for (x,y,w,h) in faces:
            delta_w = (out_w - w) // 2
            delta_h = (out_h - h) // 2
            x_out = x - delta_w
            y_out = y - delta_h 
            if x_out < 0:
                x_out = 0
            if y_out < 0:
                y_out = 0    
            face_img = self.current_image[y_out:y_out+out_h, x_out:x_out+out_w].copy()
            return face_img
        return None

    def make_train_image(self,person_name,img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in faces:
            face_img = gray[y:y+h, x:x+w]
            cv2.imshow('Captured face',face_img)
            cv2.waitKey(1000)
            cv2.destroyAllWindows()
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            cv2.imwrite(self.configuration.train_dir + "/User."+person_name+ "." +timestamp+ ".jpg", gray[y:y+h, x:x+w])
        
    def getImagesWithID(self,path):
        imagePaths = [os.path.join(path, f) for f in os.listdir(path)]   
        faces = []
        IDs = []
        self.id_vs_name = dict()
        self.name_vs_id = dict()
        next_id = 0
        for imagePath in imagePaths:      
            # Read the image and convert to grayscale
            facesImg = Image.open(imagePath).convert('L')
            faceNP = np.array(facesImg, 'uint8')
            # Get the label of the image
            person_name = os.path.split(imagePath)[-1].split(".")[1]
            if person_name in self.name_vs_id:
                ID = self.name_vs_id[person_name]
                self.id_vs_name[ID] = person_name
            else:
                ID = next_id
                self.name_vs_id[person_name] = ID
                next_id += 1

            faces.append(faceNP)
            IDs.append(ID)
        return np.array(IDs), faces

    def save_labels(self,filename):
        label_file = open(filename, "w")

        for key,value in self.name_vs_id.items():
            label_file.write(str(value)+"|"+key+"\n")
        label_file.close()

    def run_training(self):
        Ids,faces  = self.getImagesWithID(self.configuration.train_dir)
        self.recognizer.train(faces,Ids)
        self.recognizer.save(self.configuration.model_file)
        self.save_labels(self.configuration.label_file)

    def set_image(self,image):
        self.current_image = image
        self.current_gray_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
    
    def get_faces_rectangles(self):
        self.faces = self.face_cascade.detectMultiScale(self.current_gray_image, 1.5, 5)
        return self.faces
    
    def get_person_names(self):
        person_names = []
        for (x,y,w,h) in self.faces:
            id,conf=self.recognizer.predict(self.current_gray_image[y:y+h,x:x+w])
            person_name = "Unknown"
            if id in self.id_vs_name:
                person_name = self.id_vs_name[id]
                person_names.append(person_name)
        return person_names

class FaceDetectDialog:
    def __init__(self,face_detector):
        self.face_detect = face_detector
        left_frame = [[sg.Image(filename='', key='_IMAGE_')]]
        right_frame = [ [sg.Image(filename='', key='_PERSON_')],
                        [sg.Text("Who is it?")],
                        [sg.Input()],
                        [sg.Button('Capture')],
                        [sg.Button('Train model')],
                        [sg.Button('Quit')]
                    ]
        layout = [  [sg.Frame("", left_frame),sg.Frame("", right_frame)]]
        self.window = sg.Window('Face recognition training centre', layout)

        self.cap = cv2.VideoCapture(0)
        ret, self.frame = self.cap.read()
        self.mirror = cv2.flip(self.frame, 1)
        self.person_img = None
        self.colors = []
        self.update_colors()

    def update_colors(self):
        self.colors = np.random.uniform(0, 255, size=(len(self.face_detect.name_vs_id), 3))

    def get_color(self,person_name):
        return self.colors[self.face_detect.name_vs_id[person_name]]

    def update_current_images(self):
        ret, self.frame = self.cap.read()
        self.mirror = cv2.flip(self.frame, 1)

        self.face_detect.set_image(self.mirror)
        self.person_img = self.face_detect.get_first_face(200,200)
        faces = self.face_detect.get_faces_rectangles()
        person_names = self.face_detect.get_person_names()
        index = 0
        for (x,y,w,h) in faces:
            cv2.rectangle(self.mirror,(x,y),(x+w,y+h),(255,0,0),2)
            label = person_names[index]
            color = self.get_color(person_names[index])
            cv2.putText(self.mirror, label, (int(x), int(y)),cv2.FONT_HERSHEY_SIMPLEX, .75, color, 2)
            index +=1

    def update_dialog(self):
        self.update_current_images()
        imgbytes=cv2.imencode('.png', self.mirror)[1].tobytes()
        self.window.FindElement('_IMAGE_').Update(data=imgbytes)
        
        if self.person_img is not None:
            imgbytes=cv2.imencode('.png', self.person_img)[1].tobytes()
            self.window.FindElement('_PERSON_').Update(data=imgbytes)

    def run(self):
        while True:
            event, values = self.window.Read(timeout=20, timeout_key='timeout')
            if event is None or event == 'Quit':
                break
            if event == 'Capture':
                person_name = values[0]
                if person_name is not None and person_name != "":
                    self.face_detect.make_train_image(person_name,self.frame)
            if event == 'Train model':
                self.face_detect.run_training()
                self.update_colors()
            
            self.update_dialog()

        self.window.close()
        self.cap.release()

def main():
    config = Configuration()
    detector = FaceDetector(config)
    dialog = FaceDetectDialog(detector)
    dialog.run()
    cv2.destroyAllWindows()

main()
