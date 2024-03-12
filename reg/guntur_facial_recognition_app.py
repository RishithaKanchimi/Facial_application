import pymysql
import face_recognition,cv2,sys,io,base64,os,pickle,json,ast
from flask import Flask,request,Response,jsonify
from flask import request
from PIL import Image
from collections import defaultdict
import operator
from datetime import datetime
from django.http import HttpResponse
from keras.preprocessing.image import img_to_array
from keras.models import load_model
from keras import backend as K
import tensorflow as tf
import numpy as np


global keys
keys = {}
separator = "="
keys = {}
with open('config.properties') as f:
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
  #print(face_bounding_boxes)

app = Flask(__name__)
@app.route( "/api/registartion", methods=['POST'])
def registartion():
	#a = dt['name']
	data = request.json
	try:
		id = data['id']
		name = data['name']
		base64_image = data['image']
	except:
		result = {"code":201,"message":"please check the dictonaries keys which you have sent"}
		result['required_keys'] = {'id','name','image'}
		return jsonify(result)
	base64_image=base64_image.split(',')[-1]
	base64_image=base64_image.replace(" ", "+")
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
			encodings = face_recognition.face_encodings(image, face_locations)
			for encoding in encodings:
				knownEncodings.append(encoding)
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
			result = {"code":200,"message":"Empoylee Registration Successful"}
			return jsonify(result)
		else:
			if not os.path.exists(keys['not_detected']):
				os.mkdir(keys['not_detected'])
			else:
				pass
			cv2.imwrite(keys['not_detected']+str(id)+'_'+dt_string+".jpg",image)
			result = {"code":201,"message":"Empoylee Face is Not Detected Please try again"}
			return jsonify(result)
	else:
		if not os.path.exists(keys['not_detected']):
			os.mkdir(keys['not_detected'])
		else:
			pass
		cv2.imwrite(keys['not_detected']+str(id)+'_'+dt_string+".jpg",image)
		#result = "Image quality is not clear. Please try again"
		#print(result)
		result = {"code":201,"message":"Image quality is not clear"}
		return jsonify(result)


@app.route('/api/recognizer', methods=['POST'])
def recognizer():
	graph = tf.get_default_graph()
	request_data = request.json
	try:
		base64_image = request_data['image']
	except:
		result = {"code":201,"message":"please check the dictonaries keys which you have sent"}
		result['required_keys'] = {'image'}
		return jsonify(result)
	#time.sleep(0.02)
	model = load_model(keys["liveness_model"])
	#print(model)
	le = pickle.loads(open(keys["liveness_pickel"], "rb").read())
	data = pickle.loads(open(keys['encodings'], "rb").read())
	base64_image=base64_image.split(',')[-1]
	base64_image=base64_image.replace(" ", "+")
	image = cv2.cvtColor(np.array(Image.open(io.BytesIO(base64.b64decode(base64_image)))), cv2.COLOR_BGR2RGB)
	#print(base64_image)
	face_locations = face_recognition.face_locations(image)
	#print(face_locations)
	empty_list = []
	if len(face_locations) != 0:
		for b in face_locations:
			list1 = []
			length = int(b[2])-int(b[0])
			breadth = int(b[3])-int(b[1])
			area = length * breadth
			#print(area)
			list1.append(area)
		max_index = list1.index(max(list1))
		face_locations = face_locations[max_index]
		#print(face_locations)
		empty_list.append(face_locations)
		top = empty_list[0][0]
		right = empty_list[0][1]
		bottom = empty_list[0][2]
		left = empty_list[0][3]
		face = image[top:bottom,left:right]
		face = cv2.resize(face, (32, 32))
		#print(face.shape)
		face = face.astype("float") / 255.0
		face = img_to_array(face)
		face = np.expand_dims(face, axis=0)
		#print(face)
		# pass the face ROI through the trained liveness detector
		# model to determine if the face is "real" or "fake"
		#keras.backend.clear_session()
		with graph.as_default():
			#y = model.predict(X)
			preds = model.predict(face)[0]
		j = np.argmax(preds)
		label = le.classes_[j]
		K.clear_session()
		# draw the label and bounding box on the frame
		label = "{}: {:.4f}".format(label, preds[j])
		#print('------------',label)
		if label.split(':')[0] != "fake":
			face_encoding = face_recognition.face_encodings(image, empty_list)
			distances = face_recognition.face_distance(data["encodings"], face_encoding[0])
			#print('the distances are ----------------------------------------------------------------->',distances)
			matches = face_recognition.compare_faces(data["encodings"], face_encoding[0],tolerance=0.4)
			#print(matches)
			name = "Unknown"
			if True in matches:
				first_match_index = matches.index(True)
				name = data["names"][first_match_index]
				#print('---------------',name)
				#username=data5["usernames"][first_match_index]
			if name != "Unknown":
				result = {"code":200,"status":"success"}
				result['message'] = {}
				result['message']['id'] = name
				result['message']['result'] = 'matched'
				return jsonify(result)
			
			elif name == "Unknown":
				result = {"code":201,"status":"fail","message":"Unknown"}
				return jsonify(result)
			else:
				result = {"code":201,"status":"fail","message":"User id doen't exist"}
				return jsonify(result)
		else:
			result = {"code":201,"status":"fail","message":"unknown"}
			return jsonify(result)
	else:
		result = {"code":201,"status":"fail","message":"Face is not detected in image"}
		return jsonify(result)

@app.route('/api/clear_user_id', methods=['POST'])
def clear_user_id():
	request_data = request.json
	#print(request_data)
	try:
		user_id = str(request_data['userid'])
	except:
		result = {"code":201,"message":"please check the dictonaries keys which you have sent"}
		result['required_keys'] = {'userid'}
		return jsonify(result)
	encodings_data = pickle.loads(open(keys['encodings'], "rb").read())
	encodings_names = pickle.loads(open(keys['encodings_name'], "rb").read())
	#print(encodings_data)
	#print(encodings_names['names'])
	if user_id in encodings_data['names'] and encodings_names['names']:
		value_1 = encodings_data['names'].index(user_id)
		encodings_data['names'].remove(user_id)
		encodings_data['encodings'].pop(value_1)
		#print(encodings_data['names'],encodings_data['encodings'])
		#print(encodings_data)
		value_2 = encodings_names['names'].index(user_id)
		encodings_names['names'].remove(user_id)
		encodings_names['usernames'].pop(value_2)
		#print(encodings_data['names'],encodings_data['encodings'])
		#print(encodings_names)
		f = open(keys['encodings'], "wb")
		f.write(pickle.dumps(encodings_data))
		f.close()
		
		f2 = open(keys['encodings_name'], "wb")
		f2.write(pickle.dumps(encodings_names))
		f2.close()
		result = {"code":200,"message":"successfully cleared"}
		return jsonify(result)
	else:
		result = {"code":201,"message":"user_id is not registered in pickle file"}
		return jsonify(result)

if __name__ == '__main__':
       app.run(host="0.0.0.0", port=5000, debug=True)




