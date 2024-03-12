import face_recognition,cv2,sys,io,base64,os,pickle,json,ast

global keys
keys = {}
separator = "="
keys = {}
with open('reg/config.properties') as f:
	for line in f:
		if separator in line:
			name, value = line.split(separator, 1)
			keys[name.strip()] = value.strip()



def clear_user_id(user_id):
	user_id = str(user_id)
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
		return 'successfully cleared'
	else:
		return 'user_id is not registered in pickle file'

if __name__ == "__main__":
	user_id = 'TGT-0040'
	result = clear_user_id(user_id)
	print(result)
if __name__ == "__main__":
	registartion(user_id)
	






	
