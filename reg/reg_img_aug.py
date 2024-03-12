


import tensorflow as tf
from keras.preprocessing.image import *
from numpy import expand_dims
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot  as plt
import cv2
import random
import pickle
from random import randrange


'''datagen = ImageDataGenerator(
    horizontal_flip=True,
    brightness_range=[0.2,1.0],
    featurewise_center=True,
    featurewise_std_normalization=True)
tf.keras.preprocessing.image.ImageDataGenerator(
    featurewise_center=False,
    samplewise_center=False,
    featurewise_std_normalization=False,
    samplewise_std_normalization=False,
    zca_whitening=False,
    zca_epsilon=1e-06,
    rotation_range=0,
    width_shift_range=0.0,
    height_shift_range=0.0,
    brightness_range=None,
    shear_range=0.0,
    zoom_range=0.0,
    channel_shift_range=0.0,
    fill_mode="nearest",
    cval=0.0,
    horizontal_flip=False,
    vertical_flip=False,
    rescale=None,
    preprocessing_function=None,
    data_format=None,
    validation_split=0.0,
    dtype=None,
)
face_locations='/home/tgt/Documents/pst_cropped/sampl_crop/221000806_99.939883_1.jpg'
img = load_img(face_locations)


plt.figure(figsize=(45,30))


data = img_to_array(img)
#print(data,type(data),data.shape)

samples = expand_dims(data, 0)

datagen = ImageDataGenerator(
    #width_shift_range=0.2,
    #height_shift_range=0.2,
    horizontal_flip=True,
    brightness_range=[0.2,1.0],
    #zoom_range=[0.2,0.2],
    featurewise_center=True,
    #rescale=1,
    #zca_whitening=True,
    #zca_epsilon=1e-06,
    preprocessing_function=None,
    featurewise_std_normalization=True)

it = datagen.flow(samples, batch_size=1)
#
print(randrange(1,10))
# generate samples and plot
for i in randrange(1,6):
    print(i)
    plt.subplot(330 + 1 + i)
    batch = it.next()
    image = batch[0].astype('uint8')
    cv2.imshow('image',image)
    cv2.waitKey(0)
# show the figure
#plt.show()'''


		
'''def recognizer(base64_image):
	#time.sleep(0.02)
	data = pickle.loads(open(keys['encodings'], "rb").read())
	base64_image=base64_image.split(',')[-1]
	base64_image=base64_image.replace(" ", "+")
	image = cv2.cvtColor(np.array(Image.open(io.BytesIO(base64.b64decode(base64_image)))), cv2.COLOR_BGR2RGB)
	#print(base64_image)
	face_locations = face_recognition.face_locations(image)
	encodings=face_recognition.face_encodings(rgb,boxes)
	names=[]
	for encoding in encodings:
	  matches=face_recognition.compare_faces(data["encodings"],encoding)
	  name="unknown"
	  if True in matches:
	     matchedIdxs =[i for (i,b) in enumerate(matches) if b ]
	     counts={}
	     
	     for i in matchedIdxs:
	         name=data["names"][i]
	         counts[name]=counts.get(name,0)+1
	     name=max(counts,key=counts.get)
	  names.append(name)
	  for  ((top,right,bottom,left),name) in zip(boxes,names):
	     cv2.rectangle(image,(left,top),(right,bottom),(0,255,0),2)
	     y=top-15 if top -15>15 elsetop+15
	     cv2.putText(image,name,(left,y),cv2.FONT_HERSHEY_SIMPLEX,0.75,(0.255,0),2)'''
	     

new_file = pickle.loads(open('/home/rishitha/Documents/ttipl_facial/reg/static/pickle/encoding_name.pickle', "rb").read())


#new_file = pickle.loads(open('/home/tgt/encoding.pickle', "rb").read())

print(new_file.keys())

#new_file = pickle.loads(open('/home/tgt/Documents/Rishitha/Timing_facial/ttipl_facial/reg/static/pickle/encoding_name.pickle', "rb").read())
#print(new_file)






