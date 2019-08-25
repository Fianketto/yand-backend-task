from flask import request
from flask_restful import Resource
import json
import sqlite3
import Req_classes.Functions as Func




class GetCitizens(Resource):
	def get(self, import_id):

		#	---	0.	Some preparations
		Func.Recording(1,request)
		needed_keys=["citizen_id","town","street","building","apartment","name","birth_date","gender","relatives"]
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

		"""
		conn1=sqlite3.connect(Func.DB_name)
		cursor=conn1.cursor()
		sql_req="SELECT max(table_id) FROM "+Func.InfoTable_name
		cursor.execute(sql_req)
		rows=cursor.fetchall()
		max_id=rows[0][0]
		if int(import_id)>max_id or int(import_id)<1:
			error_description="Invalid import_id"
			error_exists=True
			return Func.MakeResponse(error_description,400)
		"""	
		#	---	2.	Get the data
		table_name=Func.CitTable_prefix+str(import_id)
		sql_req="SELECT * FROM "+table_name
		cursor.execute(sql_req)
		rows=cursor.fetchall()

		#	---	3.	Response
		citizens=[{} for i in range(len(rows))]
		for i in range(len(rows)):
			for j in range(len(needed_keys)-1):
				citizens[i][needed_keys[j]]=rows[i][j]
			citizens[i]["relatives"]=list(map(int,rows[i][8].split()))
			#print("Now i=",i,"\n")
			#print("citizens len=",len(citizens),", citizens=",citizens,"\n")

		return Func.MakeResponse(citizens,200)


