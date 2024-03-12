import os
from os import path 
import pymysql 
  
connection = pymysql.connect(host='bpsscrds.cof0fc3mnt2s.ap-southeast-1.rds.amazonaws.com',database='bpssc_si_jail_2019',user='bpssc_ttl',password='bpssc_ttil_1234')
cursor = connection.cursor()
src_path='xyz/'
dst_path='xyz/'

def main(): 
  
    for count, filename in enumerate(os.listdir(src_path)):
     imagename=filename.split(".")
     print(imagename[0])
     sql_update_query = ("SELECT transactionid,werollno FROM applicants where werollno is not null and transactionid='"+imagename[0]+"' ")
     excute=cursor.execute(sql_update_query)
     row = cursor.fetchall()

     if len(row) >=1:
      dst = row[0][1]+ ".jpg"
      src =src_path+ filename 
      dst =dst_path+ dst 
      path1=os.path.abspath(dst)
      os.rename(src, dst)
      sql_update_query1 = ("insert into datalabel (reg_no,reg_path) values ('"+imagename[0]+"','"+path1+"') ")
      excute=cursor.execute(sql_update_query1)
      connection.commit()
     else:
      pass	 
  
# Driver Code 
if __name__ == '__main__': 
      
    # Calling main() function 
    main() 