import sys
import os,cv2
import dlib
import pickle
#from random import randrange
import tensorflow as tf
from keras.preprocessing.image import *
from numpy import expand_dims
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot  as plt
import cv2
import random
from random import randrange
import face_recognition
datagen = ImageDataGenerator(
    horizontal_flip=True,
    brightness_range=[0.2,1.0],
    featurewise_center=True,
    featurewise_std_normalization=True)

def show_jittered_images(window, jittered_images):
  
      
    
    for img in jittered_images:
        window.set_image(img)
        

face_locations='/home/tgt/Documents/pst_cropped/sampl_crop/221000806_99.939883_1.jpg'

predictor_path ='/home/tgt/Documents/Rishitha/Timing_facial/ttipl_facial/reg/data'
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(predictor_path)
img = dlib.load_rgb_image(face_locations)
dets = detector(img)
num_faces = len(dets)
faces = dlib.full_object_detections()
for detection in dets:
    faces.append(sp(img, detection))
image = dlib.get_face_chip(img, faces[0], size=320)
window = dlib.image_window()
window.set_image(image)
random_number = randrange(2,5)
print(random_number)
#jittered_images = dlib.jitter_image(image, num_jitters=random_number)
#show_jittered_images(window, jittered_images)
jittered_images = dlib.jitter_image(image, num_jitters=random_number, disturb_colors=True)
samples = expand_dims(image, 0)
it = datagen.flow(samples,batch_size=1)
image_data_images = [it.next()[0].astype('uint8') for i in range(random_number)]
for img in image_data_images:
   jittered_images.append(img)
jittered_images.append(image)
   
#image_data_images = [batch) for batch in image_data_images
#print(len(image_data_images))
#imagedata_images = 
#show_jittered_images(window, jittered_images)

knownEncodings = []
knownNames = []
count = 0
for a in jittered_images:
    count+=1
    print('the count is------->',count)
    #print(a)
    #print(random.randrange(a(1,5))
    im = cv2.cvtColor(a, cv2.COLOR_RGB2BGR)
    boxes = face_recognition.face_locations(im,model='hog')
    #name =  jittered_images.split(os.path.sep)[-1]
    #cv2.imshow('image',im)
    #cv2.waitKey(0)
    if len(im) != 0:
       encodings = face_recognition.face_encodings(im ,boxes )
       print(encodings)
       #for encoding in encodings:
           #print(encodings)  
          
       '''if not os.path.exists('/home/tgt/Documents/Rishitha/Timing_facial/ttipl_facial/encoded_data.pickle'):
               f = open('/home/tgt/Documents/Rishitha/Timing_facial/ttipl_facial/encoded_data.pickle',"wb")
                      
                 
          else:
                knownEncodings.append(encoding)
                knownNames.append(name)
                new_data = {"encodings":knownEncodings, "names":knownNames}
                f = open('/home/tgt/Documents/Rishitha/Timing_facial/ttipl_facial/encoded_data.pickle',"wb")
                f.write(pickle.dumps(new_data))
                f.close()'''
#new_file = pickle.loads(open('/home/tgt/Documents/Rishitha/Timing_facial/ttipl_facial/encoded_data.pickle', "rb").read())
#print(new_file)                
                                
                              
                               
                            
