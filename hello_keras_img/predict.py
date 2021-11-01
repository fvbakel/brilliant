from keras.models import load_model
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.applications.vgg16 import preprocess_input
from keras.applications.vgg16 import decode_predictions
from keras.applications.vgg16 import VGG16
import numpy as np
import os
import sys

from keras.models import load_model
 
#model = load_model('model_saved.h5')

pb  = './model_1/saved_model.pb'

model = load_model('model_1.h5')
img_width, img_height = 10, 20

def predict(filename):
    image = load_img(filename, target_size=(img_height,img_width),color_mode="grayscale")
    img = np.array(image)
    # todo, check if below makes a difference at all
    img = img / 255.0
    img = img.reshape(1,img_height,img_width,1)
    label_distribution = model.predict(img)
    label_index = label_distribution.argmax()

    print("Predicted Class index:", label_index)

predict_num = sys.argv[1]
print("Predicting for: " + predict_num)
directory='/data/digits-data/Validation/' + str(predict_num)
#directory='/data/tmp/train'
for filename in os.listdir(directory):
    if filename.endswith(".png"):
        predict(os.path.join(directory, filename))


