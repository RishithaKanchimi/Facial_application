import cv2,pickle,face_recognition,base64,io,time,datetime
import numpy as np
from PIL import Image
import tensorflow as tf
from keras.preprocessing.image import img_to_array
from keras.models import load_model
graph = tf.get_default_graph()


global keys
keys = {}
separator = "="
keys = {}


with open('reg/config.properties') as f:
	for line in f:
		if separator in line:
			name, value = line.split(separator, 1)
			keys[name.strip()] = value.strip()
			
model = load_model(keys["liveness_model"])
print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',model)
le = pickle.loads(open(keys["liveness_pickel"], "rb").read())

def recognizer(base64_image):
	
	#time.sleep(0.02)
	data = pickle.loads(open(keys['encodings'], "rb").read())
	base64_image=base64_image.split(',')[-1]
	base64_image=base64_image.replace(" ", "+")
	image = cv2.cvtColor(np.array(Image.open(io.BytesIO(base64.b64decode(base64_image)))), cv2.COLOR_BGR2RGB)
	#print("...............................",base64_image)
	start_time = datetime.datetime.now()
	face_locations = face_recognition.face_locations(image)
	print('the duration is----------------------------->',(datetime.datetime.now()-start_time))
	#print(face_locations)
	
	face_encodings = face_recognition.face_encodings(image,face_locations)
	usernames=[]
	usernames_unknown=[]
	for (top,right,bottom,left),face_encoding in zip(face_locations,face_encodings):
		distances = face_recognition.face_distance(data["encodings"], face_encoding)
				#print('the distances are ----------------------------------------------------------------->',distances)
		matches = face_recognition.compare_faces(data["encodings"], face_encoding,tolerance=0.4)
		#print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",matches)
		
		name = "Unknown"
		if True in matches:
			matchedIdxs = [i for (i, b) in enumerate(matches) if b]
			counts = {}
			for i in matchedIdxs:
				name = data["names"][i]
				counts[name] = counts.get(name, 0) + 1

			name = max(counts, key=counts.get)
			usernames.append(name)
			#crop_img = image[top+10: bottom+10, left+10:right+10]
			#usernames_unknown.append(crop_img)
	
			usernames_unknown.append(None)
		
		else:
			#print(top,bottom,right,left)
			
			crop_img = image[top-30: bottom+30,left-30:right+30]
			#cv2.imshow('crop_img',crop_img)
			#cv2.waitKey(0)
			#crop_img=image[y1:y2,x1:x2]
			#cv2.imshow('crop_img',crop_img)
			#cv2.waitKey(0)
			
			usernames_unknown.append(crop_img)
			usernames.append(name)
			#return crop_img
	#print('the name is--------------------------------------->',name)
	#print(".............................................",usernames)
	return usernames,usernames_unknown
		
	
	           
'''
#.....works for only matched condition 
def recognizer(base64_image):
	#time.sleep(0.02)
	data = pickle.loads(open(keys['encodings'], "rb").read())
	base64_image=base64_image.split(',')[-1]
	base64_image=base64_image.replace(" ", "+")
	image = cv2.cvtColor(np.array(Image.open(io.BytesIO(base64.b64decode(base64_image)))), cv2.COLOR_BGR2RGB)
	#print("...............................",base64_image)
	face_locations = face_recognition.face_locations(image)
	
	#print(face_locations)
	
	face_encodings = face_recognition.face_encodings(image,face_locations)
	usernames=[]
	for (top,right,bottom,left),face_encoding in zip(face_locations,face_encodings):
		distances = face_recognition.face_distance(data["encodings"], face_encoding)
		#print('the distances are ----------------------------------------------------------------->',distances)
		matches = face_recognition.compare_faces(data["encodings"], face_encoding,tolerance=0.4)
		#print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",matches)
		
		name = "Unknown"
		if True  in matches:
			matchedIdxs = [i for (i, b) in enumerate(matches) if b]
			counts = {}
			for i in matchedIdxs:
				name = data["names"][i]
				counts[name] = counts.get(name, 0) + 1

			name = max(counts, key=counts.get)
			usernames.append(name)
	#print('the name is--------------------------------------->',name)
	print(".............................................",usernames)
	return usernames'''
		
		  
		  
		  
		  
		  	
            	
