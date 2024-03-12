import csv
import face_recognition
import argparse
import numpy as np
import pickle,pymysql
import cv2,imutils
import os,sys
from imutils import paths
from datetime import datetime,time
import timeit
import time
from imutils.video import VideoStream



global keys
keys = {}
separator = "="
keys = {}

with open('config.properties') as f:
	for line in f:
		if separator in line:
			name, value = line.split(separator, 1)
			keys[name.strip()] = value.strip()
#video_capture = VideoStream(src='rtsp://root:admin@123@192.168.1.202:554/').start()
#video_capture = VideoStream(src='http://root:admin@123@192.168.1.202:80/axis-cgi/mjpg/video.cgi').start()
#video_capture = VideoStream(src='rtsp://admin:timing@123@192.168.1.164:554/Streaming/Channels/1').start()

def file_saving(frame,name,dt_string,today):
	#print('the name and dt_string are-------------->',(name,dt_string))
	if not os.path.exists(keys['results']+'/'+today+'/'+name):
		os.mkdir(keys['results']+'/'+today+'/'+name)
		cv2.imwrite(keys['results']+'/'+today+'/'+name+'/'+name+'_'+dt_string+'.jpg',frame)
		path = today+'/'+name+'/'+name+'_'+dt_string+'.jpg'
		return path
	else:
		cv2.imwrite(keys['results']+'/'+today+'/'+name+'/'+name+'_'+dt_string+'.jpg',frame)
		path = today+'/'+name+'/'+name+'_'+dt_string+'.jpg'
		return path

def drawing(frame,name,top,right,bottom,left,today,username):
	h,w,c = frame.shape
	#current_time = datetime.now().time()
	#current_time = current_time.split('.')[0]
	day = today
	current_time = time.strftime("%a, %Y %b %b %H:%M:%S")
	dt_string = now.strftime('%d-%m-%Y')
	dt_stringt = now.strftime('%H:%M:%S')
	if name != "Unknown":
		#cv2.rectangle(frame, (left, top), (right, bottom),(0, 255, 0), 2)
		#y = top - 15 if top - 15 > 15 else top + 15
		#cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,1.0, (0, 255, 0), 2)
		frame2 = cv2.imread('index.jpg')
		#print('-----------frame2',frame2)
		frame2 = cv2.resize(frame2,(w,h))
		cv2.putText(frame2, 'Id :- '+name, (45, 30), cv2.FONT_HERSHEY_TRIPLEX,1.0, (255,0,255), 2)
		cv2.putText(frame2, 'Name :- '+username, (45, 90), cv2.FONT_HERSHEY_TRIPLEX,1.0, (255,0,255), 2)
		#cv2.putText(frame2, 'date'+':'+day, (54, 60), cv2.FONT_HERSHEY_SIMPLEX,1.0, (0, 255, 0), 2)
		cv2.putText(frame2, 'Date :- '+dt_string, (45, 150), cv2.FONT_HERSHEY_TRIPLEX,1.0, (255,0,255), 2)
		cv2.putText(frame2, 'Time :- '+dt_stringt, (45, 210), cv2.FONT_HERSHEY_TRIPLEX,1.0, (255,0,255), 2)
		res = np.hstack((frame,frame2))
		return res
	else:
		#cv2.rectangle(frame, (left, top), (right, bottom),(0, 0, 255), 2)
		#y = top - 15 if top - 15 > 15 else top + 15
		#cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,1.0, (0, 0, 255), 2)
		frame2 = cv2.imread('wrong.jpg')
		frame2 = cv2.resize(frame2,(w,h))
		cv2.putText(frame2, 'Id :- '+name, (54,22), cv2.FONT_HERSHEY_SIMPLEX,1.0, (0, 0, 255), 2)
		#cv2.putText(frame2,'date'+':'+day , (187, 60), cv2.FONT_HERSHEY_SIMPLEX,1.0, (0,0,255), 2)
		cv2.putText(frame2,'Time :- '+dt_string, (54, 90), cv2.FONT_HERSHEY_SIMPLEX,1.0, (0,0,255), 2)
		cv2.putText(frame2, 'Time :- '+dt_stringt, (45, 150), cv2.FONT_HERSHEY_SIMPLEX,1.0, (0,0,255), 2)
		res = np.hstack((frame,frame2))
		return res

def db_inserting(name,path,dt_string):
	#print(name)
	#print(type(name),type(path),type(dt_string))
	db = pymysql.connect("127.0.0.1","root","root","rrc_gun")
	cursor = db.cursor()
	sql = 'INSERT INTO recognition (employee_id,image_path,time_stamp) VALUES (%s, %s, %s)'
	val = (name,path,dt_string)
	cursor.execute(sql,val)
	db.commit()
	#print(cursor.rowcount, "record inserted.")

from datetime import date
today = str(date.today())
print(today)
if not os.path.exists(keys['results']):
	os.mkdir(keys['results'])
if not os.path.exists(keys['results']+'/'+today):
	os.mkdir(keys['results']+'/'+today)
video_capture = VideoStream(src=0).start()
frame_number = 0
while True:
		empty_list = []
		now = datetime.now()
		dt_string = now.strftime('%Y_%m_%d_%H_%M_%S')
		frame = video_capture.read()
		#print('the frame is------------>',frame.shape)
	
		time.sleep(0.02)
		data = pickle.loads(open(keys['encodings1'], "rb").read())
		data5 = pickle.loads(open(keys['encodings2'], "rb").read())
		#print(data)
		#if frame_number%5 == 0:
		rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
		#rgb_frame = imutils.resize(frame, width=450)
		#print(rgb_frame.shape)
		#r = frame.shape[1] / float(rgb_frame.shape[1])
		r = 1
		face_locations = face_recognition.face_locations(rgb_frame)
        print(face_locations)
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
			face_encoding = face_recognition.face_encodings(rgb_frame, empty_list)
			distances = face_recognition.face_distance(data["encodings"], face_encoding[0])
			#print('the distances are ----------------------------------------------------------------->',distances)
			matches = face_recognition.compare_faces(data["encodings"], face_encoding[0],tolerance=0.44)
			#print(matches)
			name = "Unknown"
			if True in matches:
				first_match_index = matches.index(True)
				name = data["names"][first_match_index]
				username=data5["usernames"][first_match_index]
				#print(name,'- ',data5["names"])
				if name in data5["names"]:
					username=data5["usernames"][first_match_index]
				else:
					username=' '
				#name = data["names"]
				#print('the name and corresponding distances are-------------------------------->',(name,distances[first_match_index]))
			res = drawing(frame,name,top,right,bottom,left,today,username)
			path = file_saving(frame,name,dt_string,today)
			db_inserting(name,path,dt_string)
		else:
			h,w,c = frame.shape
			frame2 = cv2.imread('white.jpg')
			frame2 = cv2.resize(frame2,(w,h))
			res = np.hstack((frame,frame2))
		
		'''else:
		h,w,c = frame.shape
		frame2 = cv2.imread('/home/hp/Downloads/white.jpg')
		frame2 = cv2.resize(frame2,(w,h))
		res = np.hstack((frame,frame2))'''
		frame_number = frame_number+1
		#else:
		#continue
		#Display the resulting image
		#cv2.namedWindow('Recognition', cv2.WINDOW_NORMAL)
		#resize the window according to the screen resolution
		#cv2.resizeWindow('Recognition', 1080,1920)
		res = cv2.resize(res,(1400,700))
		cv2.imshow('Recognition', res)	

		# Hit 'q' on the keyboard to quit!
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
         

