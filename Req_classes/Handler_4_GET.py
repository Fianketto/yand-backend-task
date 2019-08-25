from flask import request
from flask_restful import Resource
import json
import sqlite3
import Req_classes.Functions as Func




class GetBirthdays(Resource):
	def get(self, import_id):

		#	---	0.	Some preparations
		Func.Recording(1,request)
		error_exists=False
		error_description=""

		#	---	1.	Check if import_id exists
		conn1=sqlite3.connect(Func.DB_name)
		cursor=conn1.cursor()
		sql_req="SELECT table_id FROM "+Func.InfoTable_name+" WHERE table_id="+import_id
		cursor.execute(sql_req)
		rows=cursor.fetchall()
		try:
			this_id=rows[0][0]
		except:
			error_description="Invalid import_id"
			error_exists=True
			return Func.MakeResponse(error_description,400)
		if int(import_id)<1:
			error_description="Invalid import_id"
			error_exists=True
			return Func.MakeResponse(error_description,400)

		#	---	2.	Delete existing temp table
		sql_req="DROP TABLE IF EXISTS TEMP_TABLE"
		cursor.execute(sql_req)
		conn1.commit()

		#	---	3.	Get data from needed table (fields: cit_id,birth_dt,relatives)
		table_name=Func.CitTable_prefix+str(import_id)
		sql_req="SELECT citizen_id,birth_date,relatives FROM "+table_name
		cursor.execute(sql_req)
		rows=cursor.fetchall()

		#	---	4.	Make new table with separate rows for each relative
		rel={}
		birth_dt={}

		for i in range(len(rows)):
			print("row: ",rows[i])
			cit_id=rows[i][0]					#0 - "citizen_id" column
			birth_dt[cit_id]=rows[i][1]			#1 - "birth_dt" column
			rel[cit_id]=rows[i][2].split()		#2 - "relatives" column
		cursor.execute("CREATE TABLE TEMP_TABLE (citizen_id int, birth_date text, rel_id int, rel_birth_date text)")
		conn1.commit()

		for cit_id in rel.keys():
			for rel_id in rel[cit_id]:
				values_string=str(cit_id)+",'"+birth_dt[cit_id]+"',"+str(rel_id)+",'"+birth_dt[int(rel_id)]+"'"
				sql_req="INSERT INTO TEMP_TABLE VALUES ("+values_string+")"
				cursor.execute(sql_req)
		conn1.commit()

		#	---	5.	Group by month and citizens
		sql_req="SELECT citizen_id,substr(rel_birth_date,4,2) as M,COUNT(*) as cnt FROM TEMP_TABLE GROUP BY citizen_id,M ORDER BY M,citizen_id"
		cursor.execute(sql_req)
		rows=cursor.fetchall()

		sql_req="DROP TABLE IF EXISTS TEMP_TABLE"
		cursor.execute(sql_req)
		conn1.commit()

		#	---	6.	Response
		RESP_DICT={}
		for i in range(12):
			RESP_DICT[i+1]=[]
		for row in rows:
			d={"citizen_id":row[0],"presents":row[2]}
			RESP_DICT[int(row[1])].append(d)
		
		return Func.MakeResponse(RESP_DICT,200)

		#JS=json.dumps(RESP_DICT,sort_keys=True)
		#print("\nJS: ",JS)

