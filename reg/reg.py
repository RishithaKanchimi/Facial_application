import pymysql
import sys
import dlib
import face_recognition,cv2,sys,io,base64,os,pickle,json,ast
#from flask import Flask,request,Response,jsonify
#from flask import request
import numpy as np
import pymysql
import random
from random import randrange
import tensorflow as tf
from keras.preprocessing.image import *
from numpy import expand_dims
from keras.preprocessing.image import load_img,img_to_array,ImageDataGenerator
from PIL import Image
from collections import defaultdict
import operator
from datetime import datetime
from django.http import HttpResponse


datagen = ImageDataGenerator(
    horizontal_flip=True,
    brightness_range=[0.2,1.0],
    featurewise_center=True,
    featurewise_std_normalization=True)

now = datetime.now()
dt_string = now.strftime('%d_%m_%Y_%H_%M_%S')
global keys
keys = {}
separator = "="
keys = {}
with open('reg/config.properties') as f:
    for line in f:
        if separator in line:
            name, value = line.split(separator, 1)
            keys[name.strip()] = value.strip()

def face_detection(img):
    im = img
    rgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb,
        model = "hog")
    #print(boxes)
    return boxes



def color_analysis(img):
    # obtain the color palatte of the image 
    palatte = defaultdict(int)
    for pixel in img.getdata():
        palatte[pixel] += 1
    
    # sort the colors present in the image 
    sorted_x = sorted(palatte.items(), key=operator.itemgetter(1), reverse = True)
    light_shade, dark_shade, shade_count, pixel_limit = 0, 0, 0, 25
    for i, x in enumerate(sorted_x[:pixel_limit]):
        if all(xx <= 20 for xx in x[0][:3]): ## dull : too much darkness 
            dark_shade += x[1]
        if all(xx >= 240 for xx in x[0][:3]): ## bright : too much whiteness 
            light_shade += x[1]
        shade_count += x[1]
        
    light_percent = round((float(light_shade)/shade_count)*100, 2)
    dark_percent = round((float(dark_shade)/shade_count)*100, 2)
    return light_percent, dark_percent
    



def perform_color_analysis(img, flag):
    im = img
    im = Image.fromarray(im.astype('uint8'), 'RGB')
    # cut the images into two halves as complete average may give bias results
    size = im.size
    #print(size)
    halves = (size[0]//2, size[1]//2)
    #print(halves)
    im1 = im.crop((0, 0, size[0], halves[1]))
    im2 = im.crop((0, halves[1], size[0], size[1]))
    try:
      light_percent1, dark_percent1 = color_analysis(im1)
      light_percent2, dark_percent2 = color_analysis(im2)
    except Exception as e:
      return None
    light_percent = (light_percent1 + light_percent2)/2 
    dark_percent = (dark_percent1 + dark_percent2)/2 
    if flag == 'black':
        return dark_percent
    elif flag == 'white':
        return light_percent
    else:
        return None

def get_blurrness_score(image):
    path = image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    fm = cv2.Laplacian(image, cv2.CV_64F).var()
    return fm


def quality_check(base64_image):
  
  image = cv2.cvtColor(np.array(Image.open(io.BytesIO(base64.b64decode(base64_image)))), cv2.COLOR_BGR2RGB)
  #print(image)
  image_dullness_score = perform_color_analysis(image, 'black')
  #print(image_dullness_score)
  image_blurness_score = get_blurrness_score(image)
  #print(image_blurness_score)
  image_whiteness_score = perform_color_analysis(image, 'white')
  face_locations = face_detection(image)
  

def show_jittered_images(window, jittered_images):
  
      
    
    for img in jittered_images:
        window.set_image(img)
  
 

def registartion(id,name,base64_image):
    #a = dt['name']
    b = id
    b1 = name
    base64_image=base64_image.split(',')[-1]
    base64_image=base64_image.replace(" ", "+")
    #print(base64_image)
    image = cv2.cvtColor(np.array(Image.open(io.BytesIO(base64.b64decode(base64_image)))), cv2.COLOR_BGR2RGB)
   #print(image)

    image_dullness_score = perform_color_analysis(image, 'black')
    #print(image_dullness_score)
    image_blurness_score = get_blurrness_score(image)
    #print(image_blurness_score)
    image_whiteness_score = perform_color_analysis(image, 'white')
    face_locations = face_detection(image)
    #print(face_locations)
    knownEncodings = []
    knownNames = []
    knownusernames = []
    if image_dullness_score<=50 and image_blurness_score>=5:
        if len(face_locations) != 0:
            predictor_path ='reg/data'
            detector = dlib.get_frontal_face_detector()
            sp = dlib.shape_predictor(predictor_path)
            #img = dlib.load_rgb_image(face_locations)
            img = image
            dets = detector(img)
            num_faces = len(dets)
            faces = dlib.full_object_detections()
            for detection in dets:
               faces.append(sp(img, detection))
            
            #print(len(faces))
            image = dlib.get_face_chip(img, faces[0], size=320)
            #window = dlib.image_window()
            #window.set_image(image)
            random_number = randrange(2,5)
            #print(random_number)
            jittered_images = dlib.jitter_image(image, num_jitters=random_number, disturb_colors=True)
            samples = expand_dims(image, 0)
            it = datagen.flow(samples,batch_size=1)
            image_data_images = [it.next()[0].astype('uint8') for i in range(random_number)]
            for img in image_data_images:
               jittered_images.append(img)
            jittered_images.append(image)
            '''for a in jittered_images:
               #count+=1
               #print('the count is------->',count)
               im = cv2.cvtColor(a, cv2.COLOR_RGB2BGR)'''
            
            encodings = [face_recognition.face_encodings(image) for image in jittered_images]
            #print("encodings<<<<<<<<<<<<<<<<<<",encodings)
            for encoding in encodings:
                knownEncodings.append(encoding[0])
                knownNames.append(id)
                knownusernames.append(name)
            #print("[INFO] serializing encodings...")
            encoding_file_path = keys['encodings']
            if os.path.exists(encoding_file_path):
                encoding_file_data = pickle.loads(open(keys['encodings'], "rb").read())
                #print('the prevoius data is---------------------------------------------->',encoding_file_data)
                for new_encodings,new_user_id in zip(knownEncodings,knownNames):
                    encoding_file_data["encodings"].append(new_encodings)
                    encoding_file_data["names"].append(new_user_id)
                    #print('the updated data is--------------------->',encoding_file_data)
                    f = open(keys['encodings'], "wb")
                    f.write(pickle.dumps(encoding_file_data))
                    f.close()
            else:
                encoding_file_data = {"encodings": knownEncodings, "names": knownNames}
                #print(encoding_file_data)
                f = open(keys['encodings'], "wb")
                f.write(pickle.dumps(encoding_file_data))
                f.close()
            encoding_name_path = keys['encodings_name']
            if os.path.exists(encoding_name_path):
                encoding_name_data = pickle.loads(open(keys['encodings_name'], "rb").read())
                #print('the prevoius data is---------------------------------------------->',encoding_file_data)
                for new_usernames,new_user_id in zip(knownusernames,knownNames):
                    encoding_name_data["usernames"].append(new_usernames)
                    encoding_name_data["names"].append(new_user_id)
                    #print('the updated data is--------------------->',encoding_file_data)
                    f = open(keys['encodings_name'], "wb")
                    f.write(pickle.dumps(encoding_name_data))
                    f.close()
            else:
                encoding_name_data = {"usernames": knownusernames, "names": knownNames}
                #print(encoding_file_data)
                f = open(keys['encodings_name'], "wb")
                f.write(pickle.dumps(encoding_name_data))
                f.close()
            
            result ="Empoylee Registration Successful"
            #print(result)
            return result
        else:
            if not os.path.exists(keys['not_detected']):
                os.mkdir(keys['not_detected'])
            else:
                pass
            cv2.imwrite(keys['not_detected']+str(id)+'_'+dt_string+".jpg",image)
            result = "Empoylee Face is Not Detected Please try again"
            #print(result)
            return result
    else:
        if not os.path.exists(keys['not_detected']):
            os.mkdir(keys['not_detected'])
        else:
            pass
        cv2.imwrite(keys['not_detected']+str(id)+'_'+dt_string+".jpg",image)
        result = "Image quality is not clear. Please try again"
        #print(result)
        #result = {"code":201,"message":"Image quality is not clear"}
        return result
    
if __name__ == "__main__":
    registartion(dct)
    












