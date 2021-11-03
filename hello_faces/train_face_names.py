import numpy as np
import cv2
import os
from PIL import Image # For face recognition we will the the LBPH Face Recognizer 

#recognizer = cv2.createLBPHFaceRecognizer()
recognizer = cv2.face.LBPHFaceRecognizer_create()

data_dir = "/home/fvbakel/Documenten/faces/"
train_dir = data_dir + "/train_data"
model_dir = data_dir + "/models"
model_name = "gezin"

def getImagesWithID(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]   
    faces = []
    IDs = []
    names = dict()
    next_id = 0
    for imagePath in imagePaths:      
        # Read the image and convert to grayscale
        facesImg = Image.open(imagePath).convert('L')
        faceNP = np.array(facesImg, 'uint8')

        # Get the label of the image
        person_name = os.path.split(imagePath)[-1].split(".")[1]
         
        if person_name in names:
           ID = names[person_name]
        else:
           ID = next_id
           names[person_name] = ID
           next_id += 1

        # Detect the face in the image
        faces.append(faceNP)
        IDs.append(ID)
    return names, np.array(IDs), faces


def save_labels(filename,names):
    label_file = open(filename, "w")

    for key,value in names.items():
        label_file.write(str(value)+"|"+key+"\n")
    label_file.close()

names,Ids,faces  = getImagesWithID(train_dir)
recognizer.train(faces,Ids)
recognizer.save(model_dir + os.sep + model_name + ".yml")
save_labels(model_dir + os.sep + model_name + ".txt",names)

cv2.destroyAllWindows()