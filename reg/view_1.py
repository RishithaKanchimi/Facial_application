def facial_submit(request):
    list_1 = []
    connection = dbconnection()
    with connection.cursor() as cursor:
     result=recognizer(request.POST['image_detct'])
     
     #print("result............................",result)
     
     for  name  in result:
       if  name !='Unknown':
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
         sql = "INSERT INTO recognition (employee_id,image_path,time_stamp) VALUES ('"+name+"','"+file_save_path+"','"+dt_string1+"')"
         excute=cursor.execute(sql)
         connection.commit()
         examdate=datetime.datetime.today().strftime('%Y-%m-%d')
         #print('the examdate s---------------->',examdate)
         sql_update_query = ("SELECT r.id,r.employee_id,Name,photo_path,image_path,time_stamp FROM recognition r ,emp_details d where r.employee_id=d.id and date(time_stamp)='"+examdate+"' and approve is null order by r.id desc,employee_id asc limit 1;")
      #print('the sql_update_query  is------------>',sql_update_query)
         excute=cursor.execute(sql_update_query)

         row = cursor.fetchall()
         #print('the row is-------------->',row)
         #print("the................",row[0][1])

         #print("the.......",row[0][2])
         if(len(row)>0):
           sql_fetch = ("SELECT * FROM recognition  where  date(time_stamp)='"+examdate+"' and employee_id='"+row[0][1]+"' order by id asc limit 1;")
           #print('the sql_fetch is------------>',sql_fetch)
           excute=cursor.execute(sql_fetch)
           rowfetch = cursor.fetchall()
           
           if len(rowfetch)>0:
             diff=row[0][5]-rowfetch[0][3]
             print("diff....................",diff)
             hours = (diff.seconds) / 3600
             print(hours)
              #if hours >1:
                # hour=1
              #else:
                #hour=0
               #print(hours)
             result='matched'
             main_dict = {"id":row[0][1],"name":row[0][2],"date":verifydate,"time":verifytime,"photo":'/static/candidate_photos/'+str(row[0][1])+'.jpg',"result": result}
             list_1.append(main_dict)
             main_data=json.dumps(list_1)
             print(main_data)
             #print(main_data)
             #return JsonResponse({"id":row[0][1],"name":row[0][2],"date":verifydate,"time":verifytime,"photo":'/static/candidate_photos/'+str(row[0][1])+'.jpg',"result": result})
             #dict_2 = {"data":list_1}
             #print(dict_2)
             #return JsonResponse(main_data,safe=False)
             return HttpResponse(main_data)
          
        
         else:
           #print("enter into else block line-753")
           notb='No More  Records Avaliable !!'
           return render(request, "verified.html",{"message": notb })
       elif result == 'notmatched':
          message='UnKnown Please Try again !!'
          #file_directory = 'reg/static/results'+'/'+today+'/'+name+'/'+name+'_'+dt_string+'.jpg'
          #data_bytes = image_data.encode("utf-8")
          #decoded = base64.b64decode(data_bytes)  
          #output = open(file_directory, 'wb')
          #output.write(decoded)
          return JsonResponse({"result": "notmatched"})
       else:
          image_data = re.sub("^data:image/png;base64,", "", request.POST['image_detct'])

          #file_directory = 'reg/static/results'+'/'+today+'_'+dt_string+'_face.jpg'
          #file_save_path = today+'/'+name+'/'+name+'_'+dt_string+'.jpg'
          data_bytes = image_data.encode("utf-8")
          decoded = base64.b64decode(data_bytes)  
          #output = open(file_directory, 'wb')
          #output.write(decoded)
          message='Face Not Detected try again !!'
          return render(request, "det.html",{"rollno": message })
     # return JsonResponse({"result": "notmatched"})
     
     
     
     
def  show_details(request):
   print (",,,,,,,,,,,,,,,,,,,,,,main_data>>>>>>>>>>>>>")
   emp_name=request.GET['name']
   print (emp_name)
   '''print(request.POST.getlist('name'))
   print(",,,,,,,,,,,,,,,,,,,,,,,,,")
   print(request.POST.getlist('e_id'))
   emp_name=request.GET['name']
       emp_id= request.GET['e_id']
       connection = dbconnection()
       with connection.cursor() as cursor:
        sql_fetch_query=("SELECT * FROM emp_details where id="+emp_id+"")
        print("==================================================>",emp_name,emp_id)
        excute=cursor.execute(sql_fetch_query)
        row=cursor.fetchall()
        im=row[0][12]
        connection.commit()
        return render(request, "verified.html",{"data":data})'''
   return render(request, "verified.html",{"data":emp_name})
