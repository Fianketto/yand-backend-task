from flask import request, Response
from flask_jsonpify import jsonify
import sqlite3
import json
import datetime


path_to_serv="/home/entrant/Orkhan/Python_serv/"
#DB_name=path_to_serv+"SQL_DB/TEST_BASE_CITIZENS.db"
DB_name=path_to_serv+"SQL_DB/CITIZENS.db"
CitTable_prefix="CIT_DATA_"
InfoTable_name="TABLES_INFO"
ReserveTable_name="TABLES_RESERVE"



def Recording(x,req="",resp_st=0,resp_txt=""):
	global starting_time,ending_time,run_duration,logfile,filename
	if x==1:
		try:
			tst1=filename
		except:
			filename=path_to_serv+"Testing/Response_log/log_"+datetime.datetime.now().strftime("D%Y_%m_%d_T%H_%M_%S")
			logfile=open(filename,"w+")
			print("starting_time\trequest\tending_time\tduration\tresponse_status\tresponse_text",file=logfile)

		starting_time=datetime.datetime.now()
		#print("start: ",starting_time,"\t",req,req.data.decode("utf-8"),file=logfile, end="\t")
		print(starting_time,"\t",req,file=logfile, end="\t")
	elif x==0:
		ending_time=datetime.datetime.now()
		run_duration=ending_time-starting_time
		print("\nstarting at: ",starting_time)
		print("ending at: ",ending_time)
		print("duration: ",run_duration)
		if len(str(resp_txt))>300:
			resp_txt="longer than 300 symbols"
		print(ending_time,"\t",run_duration,"\t",resp_st,"\t",resp_txt,file=logfile)

def CreateInfoTable():
	conn1=sqlite3.connect(DB_name)
	cursor=conn1.cursor()
	sql_req="CREATE TABLE IF NOT EXISTS "+InfoTable_name+" (table_id int)"
	cursor.execute(sql_req)
	sql_req="SELECT MIN(table_id) FROM "+InfoTable_name
	cursor.execute(sql_req)
	rows=cursor.fetchall()
	min_id=rows[0][0]
	print("min_id in InfoTable=",min_id,type(min_id))
	if min_id!=0:
		sql_req="INSERT INTO "+InfoTable_name+" VALUES (0)"
		cursor.execute(sql_req)
		conn1.commit()
		print("inserted 0 in InfoTable")

	sql_req="CREATE TABLE IF NOT EXISTS "+ReserveTable_name+" (table_id int)"
	cursor.execute(sql_req)
	sql_req="SELECT MIN(table_id) FROM "+ReserveTable_name
	cursor.execute(sql_req)
	rows=cursor.fetchall()
	min_id=rows[0][0]
	print("min_id in ReserveTable=",min_id,type(min_id))
	if min_id!=0:
		sql_req="INSERT INTO "+ReserveTable_name+" VALUES (0)"
		cursor.execute(sql_req)
		conn1.commit()
		print("inserted 0 in ReserveTable")



def dict_raise_on_duplicates(ordered_pairs):
    """Reject duplicate keys."""
    d = {}
    for k, v in ordered_pairs:
        if k in d:
           raise ValueError("duplicate key: %r" % (k,))
        else:
           d[k] = v
    return d



def IsJSON(a):
	try:
		b=a.get_json(force=True)
		#c=a.json
	except:
		return False
	return True



def HasDuplicateKeys(a):
	try:
		f=a.data.decode("utf-8")
		j=json.loads(f,object_pairs_hook=dict_raise_on_duplicates)
	except:
		return True
	return False

		

def MakeResponse(resp_text,st):
	return_data={"data":resp_text}
	resp=jsonify(return_data)
	resp.status_code=st
	Recording(0, "", st,resp_text)
	return resp

def IsValidDate(date_text):
	try:
		datetime.datetime.strptime(date_text,'%d.%m.%Y')
		return True
	except ValueError:
		return False	

def IsFromFuture(date_text):
	dt_curr = datetime.date.today()
	dt_cit=datetime.datetime.strptime(date_text,'%d.%m.%Y')
	return dt_cit.date()>=dt_curr
	

def FullYears(dt):
	dt_curr = datetime.date.today()
	y=dt_curr.year-dt.year
	if dt_curr.month<dt.month or (dt_curr.month==dt.month and dt_curr.day<dt.day):
		y-=1
	return y
