from django.http import HttpResponse,StreamingHttpResponse
from django.template import loader,Context
from django.shortcuts import render,render_to_response
from rest_framework.response import Response
from django import forms
import datetime
from datetime import date
from datetime import datetime
#import pymssql as sql
import pymysql,requests,json, base64
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, login
import urllib.parse
from django.core.files.base import ContentFile
#from reg.pet_face_verification_db import reg_outside_comparision,outside_inside_comparision
from reg.reg import registartion
from reg.facial_function import recognizer

from reg.clearing_id import clear_user_id
import reg.facenet2
import re,os,time, random,csv
from django.http import JsonResponse
from threading import Thread
from multiprocessing import Queue
from .models import *
from django.views.generic import View
from reg.render import render_to_pdf
#import boto3
#from boto3.s3.transfer import S3Transfer
import subprocess
#subprocess.Popen(["python","reg/tests.py"], close_fds=True)
import cv2,base64,io
import numpy as np
from PIL import Image
import datetime
import pytz
from reportlab.lib.pagesizes import letter,A3, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageTemplate, Spacer
from reportlab.lib import colors
from io import BytesIO
from reportlab.lib import pagesizes
def dbconnection():
     connection = pymysql.connect(host='127.0.0.1',database='ttipl_facial',user='root',password='Admin@123')
     return connection

#................................................
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

#...........................................................
def login1(request):
    try:
     if 'user' not in request.session:
      return render(request, "index.html")
     else:
      del  request.session['user']
      del  request.session['role']
      del  request.session['location']
      return render(request, "index.html")
    except:
     return render(request, "index.html")
#................................................................
def login2(request):
    return render(request, "index.html")

def logout(request):
    try:
     del  request.session['user']
     del  request.session['role']
     del  request.session['location']
     return render(request, "index.html")
    except:
     return render(request, "index.html")
#.................................................................
def login_details(request):
    try:
     browser=request.headers.get('User-Agent')
     connection = dbconnection()
     examdate=datetime.datetime.today().strftime('%Y-%m-%d')
     with connection.cursor() as cursor:
      stats=("select username,role,location from login where username='"+request.POST['username1']+"' and password='"+request.POST['pwd']+"'")
      stat_exe=cursor.execute(stats)
      row_stats=cursor.fetchall()
      
      if len(row_stats) == 1 : 
       client_ip = get_client_ip(request)
       operator_image=row_stats[0][0]
       request.session['user']=row_stats[0][0]
       request.session['role']=row_stats[0][1]
       request.session['location']=row_stats[0][2]
       now = datetime.datetime.now()
       sql_insert=("insert into login_details (username,login_time,ipaddress,role,location,browser) values ('"+row_stats[0][0]+"','"+str(now)+"','"+client_ip+"','"+row_stats[0][1]+"','"+row_stats[0][2]+"','"+browser+"')")
       cursor.execute(sql_insert)
       connection.commit()
       if row_stats[0][1] == 'admin_app':
        sql_update_query = ("SELECT r.id,r.employee_id,Name,photo_path,image_path,time_stamp FROM recognition r ,emp_details d where r.employee_id=d.id and date(time_stamp)='"+examdate+"' and verify_location='"+request.session['location']+"' and approve is null order by r.id desc,employee_id asc limit 1;")
        excute=cursor.execute(sql_update_query)
        row = cursor.fetchall()
        if(len(row)>0):
         sql_fetch = ("SELECT * FROM recognition  where  date(time_stamp)='"+examdate+"' and approve='1' and verify_location='"+request.session['location']+"' and employee_id='"+row[0][1]+"' order by id desc limit 1;")
         excute=cursor.execute(sql_fetch)
         rowfetch = cursor.fetchall() 
         if len(rowfetch)>0:
          diff=row[0][5]-rowfetch[0][3]
         
          hours = (diff.seconds) / 3600
          print(hours)
          #if hours >8:
           #hour=1
          #else:
          # hour=0
          cursor.close()
          connection.close()
          return render(request, "apporve.html",{"rollno": row,"click": 'alreadyverified',"dattime": rowfetch[0][3],"hour":hour,"entry":rowfetch[0][10] })
         else:
          cursor.close()
          connection.close()
          return render(request, "apporve.html",{"rollno": row ,"dattime": '--',"hour": 0})
        else:
         cursor.close()
         connection.close()
         notb='No More  Records Avaliable !!'
         return render(request, "apporve.html",{"message": notb })
       elif row_stats[0][1] == 'admin':
        sql_update_query = ("SELECT distinct CREW_TYPE FROM emp_details")
        excute=cursor.execute(sql_update_query)
        row = cursor.fetchall()
        sql_update_query1 = ("SELECT r.employee_id,Name,CREW_TYPE,photo_path,image_path,time_stamp as vdate FROM recognition r ,emp_details d where r.employee_id=d.id and date(time_stamp)='"+examdate+"' and  verify_location='"+request.session['location']+"' and approve='1' order by employee_id asc;")
        excute1=cursor.execute(sql_update_query1)
        row1 = cursor.fetchall()
        cursor.close()
        connection.close()
        if len(row1)>0:
           return render(request, "report.html",{"rollno": row,"data": row1 })
        else:
         notb='No Records Found !!'
         return render(request, "report.html",{"rollno": row })
       else:
        return render(request, "home.html")
      else :
       cursor.close()
       connection.close()
       return render(request, "index.html",{"msg": 'Username/password incorrect Try again !!'})
    except :
     cursor.close()
     connection.close()
     return render(request, "index.html",{"msg":'something went wrong please try again !!'})
#......................................................................................................
def index(request):
    return render(request, "home.html")


#..........................................................

def checking(request):
      connection = dbconnection()
      examdate=datetime.datetime.today().strftime('%d-%m-%Y')  
      with connection.cursor() as cursor:
        sql_update_query = ("select * from  emp_details where   id='"+request.POST['rollno']+"'")
        excute=cursor.execute(sql_update_query)
        row = cursor.fetchall()
        if len(row)>0:
           sql_update_check = ("select * from  emp_details where reg_time is not null and  id='"+request.POST['rollno']+"'")
           excute=cursor.execute(sql_update_check)
           row_fe = cursor.fetchall()
           cursor.close()
           connection.close()
           if len(row_fe)>0:
            notb='Empoylee Already Registred !!'
            return render(request, "home.html",{"rollno": notb })
           else:
            return render(request, "employeeDetails.html",{"rollno": row })
        else:
          sql_insert_check= ("insert into emp_details (id,Name,organisation) values ('"+request.POST['rollno']+"','"+request.POST['emp_name']+"','"+request.POST['Organisation']+"')")
          excute=cursor.execute(sql_insert_check)
          row = cursor.fetchall()
          connection.commit()          
      
          sql_update_query = ("select * from  emp_details where   id ='"+request.POST['rollno']+"'")
          excute=cursor.execute(sql_update_query)
          row = cursor.fetchall()
          cursor.close()
          connection.close()
          
          return render(request, "employeeDetails.html",{"rollno": row })
           
#..................................................................................        

def goback(request):
    return render(request, "home.html")

def candidate_photo(request):
#try:
      connection = dbconnection()
      examdate=datetime.datetime.today().strftime('%d-%m-%Y')
      examdate1=datetime.datetime.today().strftime('%Y-%m-%d')
      with connection.cursor() as cursor:
         image_data = re.sub("^data:image/png;base64,", "", request.POST['image_src'])
         print(type(image_data))
         dir = 'reg/static/candidate_photos'
         #input_image = 'static/'
         file_directory = dir+"/"+request.POST['rollno']+".jpg"
         #print(file_directory)
         data_bytes = image_data.encode("utf-8")
         
         decoded = base64.b64decode(data_bytes)  
         output = open(file_directory, 'wb')
         output.write(decoded)
         output.close()
         now = datetime.datetime.now()
         results=registartion(request.POST['rollno'],request.POST['name'],request.POST['image_src'])
         #print("results........................",results)
         if results == 'Empoylee Face is Not Detected Please try again':
           return render(request, "home.html",{"rollno": results })
         elif results == 'Image quality is not clear. Please try again':
           cursor.close()
           connection.close()
           return render(request, "home.html",{"rollno": results })
         else:
           sql_update_query = ("update  emp_details   set reg_time='"+str(now)+"',reg_user='"+request.session['user']+"',location='"+request.session['location']+"',photo_path='"+image_data+"',attendanceDate='"+examdate1+"' where id='"+request.POST['rollno']+"'")
           cursor.execute(sql_update_query)
           connection.commit()
           cursor.close()
           connection.close()
           return render(request, "home.html",{"rollno1": results })
        
		  
'''except :
 cursor.close()
 return render(request, "home.html",{"rollno": 'Someting went wrong please try again!!' })'''



#......................................................................................................   
def facial_submit(request):
     list_1 = []
   
     result,result1=recognizer(request.POST['image_detct'])
     
     for  index,name  in enumerate(result):
       if  name =='Unknown':
         today = str(date.today())
         if not os.path.exists('reg/static/results'):
             os.mkdir('reg/static/results')
         if not os.path.exists('reg/static/results'+'/'+today):
            os.mkdir('reg/static/results'+'/'+today)
         dt_string = datetime.datetime.today().strftime('%Y_%m_%d %H_%M_%S')
        
         if not os.path.exists('reg/static/results'+'/'+today+'/'+name):
            os.mkdir('reg/static/results'+'/'+today+'/'+name)
         verifydate = datetime.datetime.today().strftime('%d-%m-%Y')
         verifytime = datetime.datetime.today().strftime('%H:%M:%S')
         result='NOT REGISTERED'
         unknown_img=result1[index]
         
         cv2.imwrite('reg/static/results'+'/'+today+'/'+name+'/'+name+'_'+today+'_'+str(index)+'.jpg',unknown_img)
         #cv2.imshow('reg/static/results'+'/'+today+'/'+name+'/'+name+'_'+today+'_'+str(index)+'.jpg',unknown_img)
         
         #print(unknown_img)
         #file_directory = 'reg/static/results'+'/'+today+'/'+name+'/'+unknown_img+'_'+dt_string+'.jpg'
         #output = open(file_directory, 'wb')
         #cv2.imwrite(file_directory,unknown_img)
         id_1='N/A'
         name1='N/A'
         main_dict1 = {"id":id_1,"name":name1,"date":verifydate,"time":verifytime,"photo":'/static/results'+'/'+today+'/'+name+'/'+name+'_'+today+'_'+str(index)+'.jpg',"result": result}
         list_1.append(main_dict1) 
       else:         
         today = str(date.today())
          #print(today)
         if not os.path.exists('reg/static/results'):
            os.mkdir('reg/static/results')
         if not os.path.exists('reg/static/results'+'/'+today):
          os.mkdir('reg/static/results'+'/'+today)
         dt_string = datetime.datetime.today().strftime('%Y_%m_%d %H_%M_%S')
          #print(result)
         if not os.path.exists('reg/static/results'+'/'+today+'/'+name):
           os.mkdir('reg/static/results'+'/'+today+'/'+name)
         dt_string = datetime.datetime.today().strftime('%Y_%m_%d %H_%M_%S')
         dt_string1 = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
         image_data = re.sub("^data:image/png;base64,", "", request.POST['image_detct'])
         #print("image_data...........................",image_data)
         file_directory = 'reg/static/results'+'/'+today+'/'+name+'/'+name+'_'+dt_string+'.jpg'
         file_save_path  = today+'/'+name+'/'+name+'_'+dt_string+'.jpg'
         data_bytes = image_data.encode("utf-8")
         decoded = base64.b64decode(data_bytes)  
         output = open(file_directory, 'wb')
         output.write(decoded)
         verifydate = datetime.datetime.today().strftime('%d-%m-%Y')
         verifytime = datetime.datetime.today().strftime('%H:%M:%S')
         current_date =datetime.datetime.now().strftime('%Y-%m-%d 00:00:00')         
         current_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
         #print('The name is++++++++++++++++++++++++========================================??????????????????????????????????????>',name)
         connection = dbconnection()
         with connection.cursor() as cursor:
          db_data=cursor.execute("select employee_id from recognition where employee_id ='"+name+"' and  time_stamp >= '"+current_date+"'")
          db_data=cursor.fetchone()
         cursor.close()
         #connection.close()
         print('...........................................',db_data)
         if db_data is None:
          with connection.cursor() as cursor:
            sql = "INSERT INTO recognition (employee_id,image_path,time_stamp) VALUES ('"+name+"','"+file_save_path+"','"+current_time+"')"
            cursor.execute(sql)
            connection.commit() 
            sql_update_query = ("SELECT r.id,r.employee_id,Name,photo_path,image_path,time_stamp FROM recognition r ,emp_details d where r.employee_id=d.id and date(time_stamp)='"+current_date
            +"' and approve is null order by r.id desc,employee_id asc limit 1;")      
            cursor.execute(sql_update_query)
            row = cursor.fetchall()   
            #print(row)
          cursor.close()
          #connection.close()         
          #print('the row is-------------->',row)
          result='VERIFIED'
          main_dict = {"id":row[0][1],"name":row[0][2],"date":verifydate,"time":verifytime,"photo":'/static/candidate_photos/'+str(row[0][1])+'.jpg',"result": result}
            
          list_1.append(main_dict)            
            
         elif db_data is  not None:
          with connection.cursor() as cursor: 
            sql_logout ="UPDATE recognition set time_stamp1 ='"+current_time+"' where employee_id ='"+name+"' AND time_stamp >='"+current_date+"'"
            cursor.execute(sql_logout)
            connection.commit() 
            
            sql_update_query = ("SELECT r.id,r.employee_id,Name,photo_path,image_path,time_stamp1 FROM recognition r ,emp_details d where r.employee_id=d.id and date(time_stamp)='"+current_date+"' and employee_id='"+name+"' and approve is null")    
            #print('.......................',sql_update_query) 
            cursor.execute(sql_update_query)
            row = cursor.fetchall()   
           #print('...................',row[0][1],row[0][2])
            #print('.........................',row[0][0],row[0][1],row[0][2],row[0][5]) 
          cursor.close()
          connection.close()         
            #print('the row is-------------->',row)
          result='VERIFIED'
          main_dict = {"id":row[0][1],"name":row[0][2],"date":verifydate,"time":verifytime,"photo":'/static/candidate_photos/'+str(row[0][1])+'.jpg',"result": result}
          list_1.append(main_dict)
         else:
             pass
           
     main_data=json.dumps(list_1)
     return HttpResponse(main_data)


def  show_details(request):
    emp_name=request.GET['name']
    return render(request, "test.html",{"data":emp_name})
   
#...............................................................................	
def facial(request):
    return render(request, "det_frame_allfaces.html")


#..................................................................................................
#attendence report with verified time sheet and reg and verified photos

def Attendence_report(request):
    emp_report = []  # Initialize emp_report as an empty list

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id', '')      
        From_Date = request.POST.get('From_Date', '') 
        To_Date = request.POST.get('To_Date', '') 
        from_date = From_Date + ' 00:00:00'
        to_date = To_Date + ' 23:59:59'
        
        connection = dbconnection()
        with connection.cursor() as cursor:
            if not employee_id:
                sql_report = """
                SELECT r.employee_id, Name, r.time_stamp1, Organisation, photo_path, CONCAT('/static/results/', r.image_path) AS image_path
                FROM recognition r
                JOIN emp_details d ON r.employee_id = d.id
                WHERE r.time_stamp1 BETWEEN %s AND %s
                """
                cursor.execute(sql_report, (from_date, to_date))
                emp_report = cursor.fetchall()
            else:  
                sql_report = """
                SELECT r.employee_id, Name, r.time_stamp1, Organisation, photo_path, CONCAT('/static/results/', r.image_path) AS image_path
                FROM recognition r
                JOIN emp_details d ON r.employee_id = d.id
                WHERE employee_id=%s AND r.time_stamp1 BETWEEN %s AND %s
                """
                cursor.execute(sql_report, (employee_id, from_date, to_date))
                emp_report = cursor.fetchall()
                if not emp_report:
                    return render(request, "norecord.html", {'emp_report': 'no_more_records'})
            
        if 'download-pdf' in request.POST:
            """# Create a PDF response
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="attendance_report.pdf"'

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer,leftMargin=150,rightMargin=150)
            elements = []

            # Create a table for the report
            data = []
            # Add table headers
            #data.append(["ID", "Name", "Verified Time", "Organisation", "Registration Photo", "Verified Photo"])
            for row in emp_report:
                data.append(row)  # Append the entire row to the table
            table_width = 400  # Adjust the width as needed

            table = Table(data)
            #table = Table(data,colWidths=[50, 100, 80, 80, 80, 80])
            
            #]))
            elements.append(Spacer(1, 20))


            elements.append(table)
            doc.build(elements)

            # Get the PDF content from the buffer and add it to the response
            pdf = buffer.getvalue()
            buffer.close()
            response.write(pdf)
            return response"""

        return render(request, "attend_report.html", {'emp_report': emp_report})
    else:
        return render(request, "attend_report.html")


#.........................................................................
#..Attendance report... with  login logout time and reg and verified photos         
'''def Attendence_report(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id', '')      
        From_Date = request.POST.get('From_Date', '') 
        To_Date = request.POST.get('To_Date', '') 
        from_date = From_Date + ' 00:00:00'
        to_date = To_Date + ' 23:59:59'
        
        connection = dbconnection()
        with connection.cursor() as cursor:
            sql_report = """
            SELECT r.employee_id, Name, reg_time, r.time_stamp, r.time_stamp1, Organisation,  photo_path, CONCAT('/static/results/', r.image_path) AS image_path
            FROM recognition r
            JOIN emp_details d ON r.employee_id = d.id
            WHERE employee_id = %s
            AND r.time_stamp BETWEEN %s AND %s
            """
            cursor.execute(sql_report, (employee_id, from_date, to_date))
            emp_report = cursor.fetchall()
            
            if not emp_report:
                return render(request, "norecord.html", {'emp_report': 'no_more_records'})
            
        return render(request, "attend_report.html", {'emp_report': emp_report})
    else:
        return render(request, "attend_report.html")'''

#............................................................................
def users_list(request):
    connection = dbconnection()
    with connection.cursor() as cursor:
        sql_user = "SELECT id, Name, reg_time, photo_path FROM emp_details"
        cursor.execute(sql_user)
        user_list = cursor.fetchall()
        #print('......................',user_list)
    return render(request, 'user_list_zoom.html', {'user_list': user_list})

    


def img_to_base64(image):
  retval, buffer = cv2.imencode('.jpg', image)
  jpg_as_text = base64.b64encode(buffer)
  return jpg_as_text



#................................
def clear(request):
    return render(request, "clear_home.html")



#.........................................................................

def clear_data(request):
     connection = dbconnection()
     examdate=datetime.datetime.today().strftime('%d-%m-%Y')
     now = datetime.datetime.now()
     with connection.cursor() as cursor:
       sql_update_query = ("select id,photo_path,reg_time,reg_user,location from  emp_details where   id='"+request.POST['rollno']+"'")
       excute=cursor.execute(sql_update_query)
       row = cursor.fetchall()
       dt_string = datetime.datetime.today().strftime('%Y_%m_%d %H_%M_%S')
       if len(row)>0:
          #if not os.path.exists('reg/static/candidate_photos/reg_cleared_photos'):
          #os.mkdir('reg/static/candidate_photos/reg_cleared_photos')
          #source='reg/static/candidate_photos/'+row[0][0]+'.jpg'
          #dir='reg/static/candidate_photos/reg_cleared_photos/'+row[0][0]+'_'+dt_string+'.jpg'
          #os.rename(source,dir)
          sql_clear = ("insert into clear_log (emp_id, photo_path,reg_time, reg_user, reg_location, clear_time, clear_location) values ('"+row[0][0]+"','"+row[0][1]+"','"+str(row[0][2])+"','"+row[0][3]+"','"+row[0][4]+"','"+str(now)+"','"+request.session['location']+"')")
          #print(sql_clear)
          excute=cursor.execute(sql_clear)
          connection.commit()

          sql_update_check = ("update emp_details set reg_time=null,photo_path=null where  id='"+request.POST['rollno']+"'")
          excute=cursor.execute(sql_update_check)
          connection.commit()
          result=clear_user_id(request.POST['rollno'])
          cursor.close()
          connection.close()
          notb='Succssfully Empoylee registartion cleared'
          return render(request, "clear_home.html",{"rollno1": result })
       else:
        cursor.close()
        connection.close()
        notb='No Records Found !!'
        return render(request, "clear_home.html",{"rollno": notb })






def approve(request):
     connection = dbconnection()
     examdate=datetime.datetime.today().strftime('%Y-%m-%d')
     with connection.cursor() as cursor:
       sql_update_query = ("SELECT r.id,r.employee_id,Name,photo_path,image_path,time_stamp,entry_point,grievance_flag_user,attendanceDate,attendanceDate_imgpath FROM recognition r ,emp_details d where r.employee_id=d.id and date(time_stamp)='"+examdate+"' and verify_location='"+request.session['location']+"' and approve is null order by r.id desc,employee_id asc limit 1;")
      
       excute=cursor.execute(sql_update_query)
       row = cursor.fetchall()
       if(len(row)>0):
        sql_fetch = ("SELECT * FROM recognition  where   approve='1' and employee_id='"+row[0][1]+"' order by id desc limit 1;")
        excute=cursor.execute(sql_fetch)
        rowfetch = cursor.fetchall() 
        if len(rowfetch)>0:
         diff=row[0][5]-rowfetch[0][3]
         #print(diff)
         hours = (diff.seconds) / 3600
         if hours >8:
          hour=1
         else:
          hour=0
     
         cursor.close()
         connection.close()
         return render(request, "apporve.html",{"rollno": row,"click": 'alreadyverified',"dattime": rowfetch[0][3],"hour":hour,"entry":rowfetch[0][10],"gri_user":rowfetch[0][14],"apporve_image":approve_image,"reg_photo":registre_image })
        else:
         cursor.close()
         connection.close()
         return render(request, "apporve.html",{"rollno": row ,"dattime": '--',"hour": 0,"entry":'no',"gri_user": 0,"apporve_image":approve_image,"reg_photo":registre_image})
       else:
        cursor.close()
        connection.close()
        notb='No More  Records Avaliable !!'
        return render(request, "apporve.html",{"message": notb })





def app_submit(request):
     try:
      connection = dbconnection()
      examdate=datetime.datetime.today().strftime('%Y-%m-%d')
      with connection.cursor() as cursor:
        if request.method == "POST":
         now = datetime.datetime.now()
         if request.POST['remark'] == '1' :
          Sql_update=("update recognition set approve='"+request.POST['remark']+"',approve_date='"+str(now)+"',apporve_user='"+request.session['user']+"',approve_location='"+request.session['location']+"',entry_point='"+request.POST['time']+"' where id='"+request.POST['f_id']+"' and employee_id='"+request.POST['empid']+"' and verify_location='"+request.session['location']+"'")
          sql_entry=("insert into enrty_point(emp_id, entry_point, entry_location, enrty_time, images_path, remark_approve) values ('"+request.POST['empid']+"','"+request.POST['time']+"','"+request.session['location']+"','"+str(now)+"','"+request.POST['photopath']+"','"+request.POST['remarktext']+"') ")
          exede=cursor.execute(sql_entry)
          connection.commit()
         if request.POST['remark'] == '0' :
          Sql_update=("update recognition set approve='"+request.POST['remark']+"',approve_date='"+str(now)+"',apporve_user='"+request.session['user']+"',approve_location='"+request.session['location']+"' where id='"+request.POST['f_id']+"' and employee_id='"+request.POST['empid']+"' and verify_location='"+request.session['location']+"'")
         exe=cursor.execute(Sql_update)
         connection.commit()
         Sql_update1=("update recognition set approve='0',apporve_user='"+request.session['user']+"',approve_location='"+request.session['location']+"' where approve is null  and employee_id='"+request.POST['empid']+"' and date(time_stamp)='"+examdate+"' and verify_location='"+request.session['location']+"'")
         exe1=cursor.execute(Sql_update1)
         connection.commit()
         sql_update_query = ("SELECT r.id,r.employee_id,Name,photo_path,image_path,time_stamp FROM recognition r ,emp_details d where r.employee_id=d.id and date(time_stamp)='"+examdate+"' and verify_location='"+request.session['location']+"' and approve is null order by r.id desc,employee_id asc limit 1;")
         excute=cursor.execute(sql_update_query)
         row = cursor.fetchall()
         if(len(row)>0):
          sql_fetch = ("SELECT * FROM recognition  where  date(time_stamp)='"+examdate+"' and approve='1' and employee_id='"+row[0][1]+"'  order by id desc limit 1;")
          excute=cursor.execute(sql_fetch)
          rowfetch = cursor.fetchall() 
          if len(rowfetch)>0:
           diff=row[0][5]-rowfetch[0][3]
           hours = (diff.seconds) / 3600
           #print('----------------------',rowfetch[0][10])
           if hours >8:
            hour=1
           else:
            hour=0
           return render(request, "apporve.html",{"rollno": row,"click": 'alreadyverified',"dattime": rowfetch[0][3],"hour":hour,"entry":rowfetch[0][10] })
          else:
           return render(request, "apporve.html",{"rollno": row ,"dattime": '--',"hour": 0})
         else:
          notb='No More  Records Avaliable !!'
          return render(request, "apporve.html",{"message": notb })
        else:
         sql_update_query = ("SELECT r.id,r.employee_id,Name,photo_path,image_path,time_stamp FROM recognition r ,emp_details d where r.employee_id=d.id and date(time_stamp)='"+examdate+"' and approve is null and verify_location='"+request.session['location']+"' order by r.id desc,employee_id asc limit 1;")
         excute=cursor.execute(sql_update_query)
         row = cursor.fetchall()
         if(len(row)>0):
          sql_fetch = ("SELECT * FROM recognition  where  date(time_stamp)='"+examdate+"' and approve='1' and verify_location='"+request.session['location']+"' and employee_id='"+row[0][1]+"' order by id desc limit 1;")
          excute=cursor.execute(sql_fetch)
          rowfetch = cursor.fetchall() 
          if len(rowfetch)>0:
           diff=row[0][5]-rowfetch[0][3]
           hours = (diff.seconds) / 3600
           if hours >8:
            hour=1
           else:
            hour=0
           cursor.close()
           connection.close()
           return render(request, "apporve.html",{"rollno": row,"click": 'alreadyverified',"dattime": rowfetch[0][3],"hour":hour,"entry":rowfetch[0][10] })
          else:
           cursor.close()
           connection.close()
           return render(request, "apporve.html",{"rollno": row ,"dattime": '--',"hour": 0})
         else:
          cursor.close()
          connection.close()
          notb='No More  Records Avaliable !!'
          return render(request, "apporve.html",{"message": notb })
     except :
      return render(request, "index.html",{"msg":'something went wrong please login again !!'})



def report(request):
     connection = dbconnection()
     examdate=datetime.datetime.today().strftime('%Y-%m-%d')
     with connection.cursor() as cursor:
       sql_update_query = ("SELECT distinct CREW_TYPE FROM emp_details")
       excute=cursor.execute(sql_update_query)
       row = cursor.fetchall()
       sql_update_query1 = ("SELECT r.employee_id,Name,CREW_TYPE,photo_path,image_path,time_stamp as vdate FROM recognition r ,emp_details d where r.employee_id=d.id and date(time_stamp)='"+examdate+"' and verify_location='"+request.session['location']+"' and approve='1' order by employee_id asc;")
       excute1=cursor.execute(sql_update_query1)
       row1 = cursor.fetchall()
       cursor.close()
       connection.close()
       if len(row1)>0:
          return render(request, "report.html",{"rollno": row,"data": row1 })
       else:
        notb='No Records Found !!'
        return render(request, "report.html",{"rollno": row })



def report1(request):
     connection = dbconnection()
     examdate=datetime.datetime.today().strftime('%Y-%m-%d')
     with connection.cursor() as cursor:
       sql_update_query = ("SELECT distinct CREW_TYPE FROM emp_details")
       excute=cursor.execute(sql_update_query)
       row = cursor.fetchall()
       if request.POST['atta'] == '':
        if request.POST['crew'] == '':
         crew=''
        else:
         crew="and  CREW_TYPE='"+request.POST['crew']+"'"
        sql_update_query1 = ("SELECT r.employee_id,Name,CREW_TYPE,photo_path,image_path,time_stamp as vdate FROM recognition r ,emp_details d where r.employee_id=d.id and date(time_stamp)='"+request.POST['att_date']+"' and  verify_location='"+request.session['location']+"' and approve='1'  "+crew+" order by employee_id asc;")
        #print(sql_update_query1)
        excute1=cursor.execute(sql_update_query1)
        row1 = cursor.fetchall()
        cursor.close()
        connection.close()
        if len(row1)>0:
           return render(request, "report.html",{"rollno": row,"data": row1 })
        else:
         notb='No Records Found !!'
         return render(request, "report.html",{"rollno": row })
       elif request.POST['atta'] == 'Absent':
        if request.POST['crew'] == '':
         crew=''
        else:
         crew="and  CREW_TYPE='"+request.POST['crew']+"'"
        sql_update_query1 = ("SELECT id,Name,CREW_TYPE,photo_path from emp_details where  id not in (select employee_id from recognition where date(time_stamp)='"+request.POST['att_date']+"') "+crew+" order by id asc;")
        #print(sql_update_query1)
        excute1=cursor.execute(sql_update_query1)
        row1 = cursor.fetchall()
        cursor.close()
        connection.close()
        if len(row1)>0:
           return render(request, "report.html",{"rollno": row,"data": row1 })
        else:
         notb='No Records Found !!'
         return render(request, "report.html",{"rollno": row })




def GeneratePDF(request):
     connection = dbconnection()
     examdate=datetime.datetime.today().strftime('%Y-%m-%d')
     examdate1=datetime.datetime.today().strftime('%d-%m-%Y')
     with connection.cursor() as cursor:
       if request.POST['crew'] == '':
        crew=''
       else:
        crew="and  CREW_TYPE='"+request.POST['crew']+"'"
       sql_update_query = ("SELECT r.employee_id,Name,CREW_TYPE,photo_path,image_path,time_stamp as vdate FROM recognition r ,emp_details d where r.employee_id=d.id and date(time_stamp)='"+request.POST['att_date']+"' and  verify_location='"+request.session['location']+"' and approve='1'  "+crew+" order by employee_id asc;")
       excute=cursor.execute(sql_update_query)
       row = cursor.fetchall()
       #print(sql_update_query)
       cursor.close()
       connection.close()
       data = {
          "invoice_id":   row,
          "date":   examdate1,
       }
       pdf = render_to_pdf('pdf.html', data)
       return HttpResponse(pdf, content_type='application/pdf')




def GeneratePDFh(request):
     connection = dbconnection()
     examdate=datetime.datetime.today().strftime('%Y-%m-%d')
     with connection.cursor() as cursor:
       sql_update_query = ("SELECT distinct CREW_TYPE FROM emp_details")
       excute=cursor.execute(sql_update_query)
       row = cursor.fetchall()
       cursor.close()
       connection.close()
       if len(row)>0:
          return render(request, "pdf_home.html",{"rollno": row })
       else:
        notb='No Records Found !!'
        return render(request, "pdf_home.html",{"rollno": row })



def GeneratePDF_not(request):
     connection = dbconnection()
     examdate=datetime.datetime.today().strftime('%Y-%m-%d')
     examdate1=datetime.datetime.today().strftime('%d-%m-%Y')
     with connection.cursor() as cursor:
       if request.POST['crew'] == '':
        crew=''
       else:
        crew="and  CREW_TYPE='"+request.POST['crew']+"'"
       sql_update_query = ("SELECT r.employee_id,Name,CREW_TYPE,photo_path,image_path,time_stamp as vdate FROM recognition r ,emp_details d where r.employee_id=d.id and date(time_stamp)='"+request.POST['att_date']+"' and  verify_location='"+request.session['location']+"' and approve='0' and approve_date is not null  "+crew+" order by employee_id asc;")
       #sql_update_query = ("SELECT r.employee_id,Name,CREW_TYPE,photo_path,image_path,time_stamp as vdate FROM recognition r ,emp_details d where r.employee_id=d.id and date(time_stamp)='"+examdate+"' and approve='Approve' order by employee_id asc;")
       excute=cursor.execute(sql_update_query)
       row = cursor.fetchall()
       #print(sql_update_query)
       cursor.close()
       connection.close()
       data = {
          "invoice_id":   row,
          "date":   examdate1,
       }
       pdf = render_to_pdf('pdf_not.html', data)
       return HttpResponse(pdf, content_type='application/pdf')





def notapporve(request):
     connection = dbconnection()
     examdate=datetime.datetime.today().strftime('%Y-%m-%d')
     with connection.cursor() as cursor:
       sql_update_query = ("SELECT distinct CREW_TYPE FROM emp_details")
       excute=cursor.execute(sql_update_query)
       row = cursor.fetchall()
       cursor.close()
       connection.close()
       if len(row)>0:
          return render(request, "notapp_home.html",{"rollno": row })
       else:
        notb='No Records Found !!'
        return render(request, "notapp_home.html",{"rollno": row })
        
        
        
        


def sync_home(request):
    connection = dbconnection()
    with connection.cursor() as cursor:
     Sync_stats=("select Date(time_stamp),sum(case when sync_data=1 then 1 else 0 end) as synced, sum(case when sync_data is null then 1 else 0 end) as notsynced  from recognition where  approve='1'  group by Date(time_stamp)")
     excute=cursor.execute(Sync_stats)
     row = cursor.fetchall()
     cursor.close()
     connection.close()
    return render(request, "sync_home.html",{'stats': row})





def sync_server(request):
     connection = dbconnection()
     with connection.cursor() as cursor:
      sql_update1=("SELECT  id,employee_id, image_path, time_stamp, approve, approve_date,apporve_user,approve_location FROM recognition where sync_data is null and approve='1' and  Date(time_stamp)='"+request.POST['examdate']+"'")
      #print(sql_update1)
      excute=cursor.execute(sql_update1)
      row = cursor.fetchall()
      if len(row)>0:
       i=0
       for data_out in row:	 
        try:
         conn = pymysql.connect(host='67.20.76.214',database='timingin_gun_frs',user='timingin_ssr',password='SSC_GUNTUR')
         with conn.cursor() as cursor_up:
          sql_update_query = ("insert into recognition (id,employee_id, image_path, time_stamp, approve, approve_date,apporve_user,approve_location) values ('"+str(data_out[0])+"','"+str(data_out[1])+"','"+str(data_out[2])+"','"+str(data_out[3])+"','"+data_out[4]+"','"+str(data_out[5])+"','"+str(data_out[6])+"','"+str(data_out[7])+"') ")
          #print(sql_update_query)
          cursor_up.execute(sql_update_query)
          conn.commit()
          i=i+1
          #cursor_up.close()
          sql_update_in = ("update  recognition   set sync_data='1' where id='"+str(data_out[0])+"'")
          cursor.execute(sql_update_in)
          connection.commit()
        except pymysql.Error as err:
         #print(err)
         return render(request, "sync_home.html",{"count": 'Please check your internet connection' })
       return render(request, "sync_home.html",{"count":'Succssfully '+str(i)+' Record Synced' })
      else:
       notb='No Records  Available to Synced'
       return render(request, "sync_home.html",{"count": notb })



def approve_user(request):
     connection = dbconnection()
     examdate=datetime.datetime.today().strftime('%Y-%m-%d')
     dataapp = []
     with connection.cursor() as cursor:
       sql_update_query = ("SELECT distinct CREW_TYPE FROM emp_details")
       excute=cursor.execute(sql_update_query)
       row = cursor.fetchall()
       sql_update_query1 = ("SELECT r.employee_id,Name,CREW_TYPE,photo_path,image_path,time_stamp as vdate,attendanceDate_imgpath,attendanceDate FROM recognition r ,emp_details d where r.employee_id=d.id and date(time_stamp)='"+examdate+"' and approve='1' and apporve_user='"+request.session['user']+"' order by employee_id asc;")
       excute1=cursor.execute(sql_update_query1)
       row1 = cursor.fetchall()
       for data in row1:
        datasetbb = []
        javadecrty_approve=requests.post('http://localhost:8082/FRSAPI/decryptPhoto?encryptedImageName='+data[3]+'&attendanceDate='+data[7])
        javadecrty_reg=requests.post('http://localhost:8082/FRSAPI/decryptPhoto?encryptedImageName='+data[4]+'&attendanceDate='+data[6])
        approve_image=javadecrty_approve.text
        registre_image=javadecrty_reg.text
        datasetbb.append(data[0])
        datasetbb.append(data[1])
        datasetbb.append(data[2])
        datasetbb.append(data[5])
        datasetbb.append(approve_image)
        datasetbb.append(registre_image)
        dataapp.append(datasetbb)
       #print(dataapp)
       cursor.close()
       connection.close()
       if len(row1)>0:
          return render(request, "report_user.html",{"rollno": row,"data": dataapp  })
       else:
        notb='No Records Found !!'
        return render(request, "report_user.html",{"rollno": row })



def report_user(request):
     connection = dbconnection()
     examdate=datetime.datetime.today().strftime('%Y-%m-%d')
     dataapp = []
     with connection.cursor() as cursor:
       dateinpost=datetime.datetime.strptime(request.POST['att_date'], "%d-%m-%Y").strftime("%Y-%m-%d")
       #print(dateinpost)
       sql_update_query = ("SELECT distinct CREW_TYPE FROM emp_details")
       excute=cursor.execute(sql_update_query)
       row = cursor.fetchall()
       sql_update_query1 = ("SELECT r.employee_id,Name,CREW_TYPE,photo_path,image_path,time_stamp as vdate,attendanceDate_imgpath,attendanceDate FROM recognition r ,emp_details d where r.employee_id=d.id and date(time_stamp)='"+dateinpost+"' and approve='1'  and apporve_user='"+request.session['user']+"' order by employee_id asc;")
       #print(sql_update_query1)
       excute1=cursor.execute(sql_update_query1)
       row1 = cursor.fetchall()
       for data in row1:
        datasetbb = []
        javadecrty_approve=requests.post('http://localhost:8082/FRSAPI/decryptPhoto?encryptedImageName='+data[3]+'&attendanceDate='+data[7])
        javadecrty_reg=requests.post('http://localhost:8082/FRSAPI/decryptPhoto?encryptedImageName='+data[4]+'&attendanceDate='+data[6])
        approve_image=javadecrty_approve.text
        registre_image=javadecrty_reg.text
        datasetbb.append(data[0])
        datasetbb.append(data[1])
        datasetbb.append(data[2])
        datasetbb.append(data[5])
        datasetbb.append(approve_image)
        datasetbb.append(registre_image)
        dataapp.append(datasetbb)
       #print(dataapp)
       cursor.close()
       connection.close()
       if len(row1)>0:
          return render(request, "report_user.html",{"rollno": row,"data": dataapp })
       else:
        notb='No Records Found !!'
        return render(request, "report_user.html",{"rollno": row })


def already_approved(request):
     print(request)
     connection = dbconnection()
     examdate=datetime.datetime.today().strftime('%Y-%m-%d')
     with connection.cursor() as cursor:
       sql_update_query = ("SELECT r.id,r.employee_id,Name,photo_path,image_path,time_stamp FROM recognition r ,emp_details d where r.employee_id=d.id and date(time_stamp)='"+examdate+"' and  approve='1' and r.employee_id='"+request.GET['id']+"' order by r.id desc,employee_id asc;")
       #print(sql_update_query)
       excute=cursor.execute(sql_update_query)
       row = cursor.fetchall()
       cursor.close()
       connection.close()
       if(len(row)>0):
         return render(request, "already_approved.html",{"rollno": row})
       else:
        notb='No More  Records Avaliable !!'
        return render(request, "already_approved.html",{"message": notb })

def sync_images(request):
    connection = dbconnection()
    with connection.cursor() as cursor:
     Sync_stats=("select Date(time_stamp),sum(case when sync_images=1 then 1 else 0 end) as synced, sum(case when sync_images is null then 1 else 0 end) as notsynced  from recognition where  approve='1'  group by Date(time_stamp)")
     excute=cursor.execute(Sync_stats)
     row = cursor.fetchall()
     cursor.close()
     connection.close()
     return render(request, "sync_images_home.html",{'stats': row})




def s3upload(request):
    connection = dbconnection()
    with connection.cursor() as cursor:
     sql_update1=("SELECT  id,employee_id, image_path, time_stamp, approve, approve_date,apporve_user,approve_location FROM recognition where sync_images is null and approve='1' and  Date(time_stamp)='"+request.POST['examdate']+"'")
     #print(sql_update1)
     excute=cursor.execute(sql_update1)
     row = cursor.fetchall()
     if len(row)>0:
      i=0
      for data_out in row:
       x = data_out[2].split("/")
       s3_path = x[-1]
       local_directory = 'reg/static/results/'+data_out[2]
       try:
        transfer  = S3Transfer(boto3.client('s3','ap-south-1', aws_access_key_id='AKIAJKBXJG4YG3OKKSDA', aws_secret_access_key='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'))
        bucket='rrcgunturattendance'
        #result=transfer.upload_file(local_directory, bucket, s3_path)
        result=transfer.upload_file(local_directory, bucket, s3_path,extra_args={'ACL': 'bucket-owner-full-control','ContentType': 'image/jpeg'})
        i=i+1
        #cursor_up.close()
        sql_update_in = ("update  recognition   set sync_images='1' where id='"+str(data_out[0])+"'")
        cursor.execute(sql_update_in)
        connection.commit()
       except :
        return render(request, "sync_images_home.html",{"count": 'Please check your internet connection' })
      return render(request, "sync_images_home.html",{"count":'Succssfully '+str(i)+' Record Synced' })
     else:
      notb='No Images are  Available to Synced'
      return render(request, "sync_images_home.html",{"count": notb })	  
    '''local_directory = 'reg/static/results/2020-04-21/GNT1019/'
    transfer  = S3Transfer(boto3.client('s3','ap-south-1', aws_access_key_id='AKIAJKBXJG4YG3OKKSDA', aws_secret_access_key='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'))
    bucket='rrcgunturattendance'
    for root, dirs, files in os.walk(local_directory):
     for filename in files:
      local_path = os.path.join(root, filename)
      relative_path = os.path.relpath(local_path, local_directory)
      #relative_path = 'GNT1019_2020_04_21_13_48_25.jpg'
      s3_path = filename
      s3_path1 = 'hh.pdf'
      #print('---------------------------------',client)
      if filename.endswith('.pdf'):
       #print('-----------------------------hi')
       transfer.upload_file(local_path, bucket, s3_path1,extra_args={'ACL': 'public-read'})
      else:
       #print('-----------------------------hello')
       transfer.upload_file(local_path, bucket, s3_path,extra_args={'ACL': 'bucket-owner-full-control'})'''




def ghome(request):
    return render(request,"ghome.html")
def grievance(request):
    connection = dbconnection()
    examdate=datetime.datetime.today().strftime('%d-%m-%Y')
    examdate1=datetime.datetime.today().strftime('%Y-%m-%d')
    with connection.cursor() as cursor:
     sql_update_query = ("select * from  emp_details where   id='"+request.POST['empid']+"'")
     print(sql_update_query)
     excute=cursor.execute(sql_update_query)
     row = cursor.fetchall()
     if len(row)>0:
      today = str(date.today())
      if not os.path.exists('reg/static/results'):
       os.mkdir('reg/static/results')
      if not os.path.exists('reg/static/results'+'/'+today):
       os.mkdir('reg/static/results'+'/'+today)
      if not os.path.exists('reg/static/results'+'/'+today+'/'+row[0][0]):
       os.mkdir('reg/static/results'+'/'+today+'/'+request.POST['empid'])
      dt_string = datetime.datetime.today().strftime('%Y_%m_%d %H_%M_%S')
      dt_string1 = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
      image_data = re.sub("^data:image/png;base64,", "", request.POST['image_src'])
      file_directory = 'reg/static/results'+'/'+today+'/'+row[0][0]+'/'+row[0][0]+'_'+dt_string+'.jpg'
      file_save_path = today+'/'+row[0][0]+'/'+row[0][0]+'_'+dt_string+'.jpg'
      data_bytes = image_data.encode("utf-8")
      decoded = base64.b64decode(data_bytes)  
      output = open(file_directory, 'wb')
      output.write(decoded)
      time_submit=request.POST['att_date']+' '+request.POST['time']
      javacall=requests.post('http://localhost:8082/FRSAPI/encryptPhoto',data ={'base64Image':request.POST['image_src'],'attendanceDate':examdate1})
      if(javacall.status_code == 200):
       sql = "INSERT INTO grievance (emp_id, image_path, time_stamp,grievance_time, grievance_user, grievance_location, entry_point,attendanceDate) VALUES ('"+row[0][0]+"','"+javacall.text+"','"+time_submit+"','"+dt_string1+"','"+request.session['user']+"','"+request.session['location']+"','"+request.POST['entrypoint']+"','"+examdate1+"')"
       excute=cursor.execute(sql)
       connection.commit()
       cursor.close()
       connection.close()
       return render(request,"ghome.html",{"message1": 'Successfully Registred Empoylee grievance'})
      else:
       cursor.close()
       connection.close()
       return render(request, "ghome.html",{"rollno": 'Someting went wrong please try again!!' })
     else:
      cursor.close()
      connection.close()
      return render(request,"ghome.html",{"message": 'Empoylee id incorrect please try again'})
def ghome1(request):
    print(request.GET)
    return render(request,"ghome1.html",{"empid":request.GET['empid'],"check":request.GET['checkOut'],"id":request.GET['id']})
def grievance1(request):
    print(request.POST['empid'])
    connection = dbconnection()
    examdate=datetime.datetime.today().strftime('%d-%m-%Y')
    examdate1=datetime.datetime.today().strftime('%Y-%m-%d')
    with connection.cursor() as cursor:
     sql_update_query = ("select * from  emp_details where   id='"+request.POST['empid']+"'")
     print(sql_update_query)
     excute=cursor.execute(sql_update_query)
     row = cursor.fetchall()
     if len(row)>0:
      today = str(date.today())
      if not os.path.exists('reg/static/results'):
       os.mkdir('reg/static/results')
      if not os.path.exists('reg/static/results'+'/'+today):
       os.mkdir('reg/static/results'+'/'+today)
      if not os.path.exists('reg/static/results'+'/'+today+'/'+row[0][0]):
       os.mkdir('reg/static/results'+'/'+today+'/'+request.POST['empid'])
      dt_string = datetime.datetime.today().strftime('%Y_%m_%d %H_%M_%S')
      dt_string1 = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
      image_data = re.sub("^data:image/png;base64,", "", request.POST['image_src'])
      file_directory = 'reg/static/results'+'/'+today+'/'+row[0][0]+'/'+row[0][0]+'_'+dt_string+'.jpg'
      file_save_path = today+'/'+row[0][0]+'/'+row[0][0]+'_'+dt_string+'.jpg'
      data_bytes = image_data.encode("utf-8")
      decoded = base64.b64decode(data_bytes)  
      output = open(file_directory, 'wb')
      output.write(decoded)
      time_submit=request.POST['att_date']+' '+request.POST['time']
      javacall=requests.post('http://localhost:8082/FRSAPI/encryptPhoto',data ={'base64Image':request.POST['image_src'],'attendanceDate':examdate1})
      if(javacall.status_code == 200):
       sql = "INSERT INTO grievance (emp_id, image_path, time_stamp,grievance_time, grievance_user, grievance_location, entry_point,attendanceDate) VALUES ('"+row[0][0]+"','"+javacall.text+"','"+time_submit+"','"+dt_string1+"','"+request.session['user']+"','"+request.session['location']+"','"+request.POST['entrypoint']+"','"+examdate1+"')"
       excute=cursor.execute(sql)
       connection.commit()
       sql1 ="update recognition set grievance_flag_user=1 where id='"+request.POST['id']+"' and employee_id='"+request.POST['empid']+"'"
       excute=cursor.execute(sql1)
       connection.commit()
       cursor.close()
       connection.close()
       return render(request,"ghome.html",{"message1": 'Succssfully Registred Empoylee grievance'})
      else:
       cursor.close()
       connection.close()
       return render(request, "home.html",{"rollno": 'Someting went wrong please try again!!' })
     else:
      cursor.close()
      connection.close()
      return render(request,"ghome.html",{"message": 'Empoylee id incorrect please try again'})
      
'''def fetch_data(request):
     print(request.POST)
     connection = dbconnection()
     examdate=datetime.datetime.today().strftime('%d-%m-%Y')
     with connection.cursor() as cursor:
       sql_update_query = ("select * from  emp_details where   id='"+request.POST['rollno']+"'")
       excute=cursor.execute(sql_update_query)
       row = cursor.fetchall()
       print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",row)

       if len(row)>0:
          sql_insert_check = ("select * from  emp_details where Name is  null and  id='"+request.POST['rollno']+"'")
          excute=cursor.execute(sql_insert_check)
          row_fe = cursor.fetchall()
          cursor.close()
          connection.close()

          if len(row_fe)>0:
           notb='Empoylee Not  Registred !!'
           return render(request, "clear_home.html",{"rollno": notb })
          else:
           return render(request, "clear_home.html",{"datass": row })

       else:
        cursor.close()
        connection.close()
        notb='No Records Found !!'
        return render(request, "clear_home.html",{"rollno": notb })'''


'''def view_photos(request):
     try:
      connection = dbconnection()
      examdate=datetime.datetime.today().strftime('%d-%m-%Y')

      with connection.cursor() as cursor:
        sql_update_query = ("select * from  emp_details where   id='"+request.POST['rollno']+"'")
        excute=cursor.execute(sql_update_query)
        row = cursor.fetchall()
        if len(row)>0:
           sql_update_check = ("select * from  emp_details where reg_time is not null and  id='"+request.POST['rollno']+"'")

           excute=cursor.execute(sql_update_check)
           row_fe = cursor.fetchall()
           cursor.close()
           connection.close()
           if len(row_fe)>0:

            notb='Empoylee Already Registred !!'
            return render(request, "home.html",{"rollno": notb })
           else:
            return render(request, "employeeDetails.html",{"rollno": row })
        else:

         cursor.close()
         connection.close()
         notb='No Records Found !!'
         return render(request, "home.html",{"rollno": notb })
     except :
      cursor.close()

      connection.close()
      return render(request, "home.html",{"rollno": 'something went wrong try again !!' })'''
      
      
      


