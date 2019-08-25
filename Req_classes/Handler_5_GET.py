from flask import request
from flask_restful import Resource
import json
import sqlite3
import Req_classes.Functions as Func
import datetime
from numpy import percentile


class GetAgeStats(Resource):
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

		#	---	2.	Get data from needed table (fields: birth_dt,town)
		table_name=Func.CitTable_prefix+str(import_id)
		sql_req="SELECT birth_date,town FROM "+table_name
		cursor.execute(sql_req)
		rows=cursor.fetchall()

		#	---	3.	Make list of ages
		ages={}
		for row in rows:
			birth_dt=datetime.datetime.strptime(row[0],'%d.%m.%Y')
			town=row[1]
			age=Func.FullYears(birth_dt)
			ages[town]=ages.get(town,[])
			ages[town].append(age)

		#	---	4.	Calculate percentiles
		perc_list=[]
		for k in ages.keys():
			perc50='%.2f' % round(percentile(ages[k],50),2)
			perc75='%.2f' % round(percentile(ages[k],75),2)
			perc99='%.2f' % round(percentile(ages[k],99),2)

			perc50=float(perc50)
			perc75=float(perc75)
			perc99=float(perc99)
			perc_list.append({"town":k,"p50":perc50,"p75":perc75,"p99":perc99})
			print(type(perc99),perc99)

		#	---	5.	Response
		return Func.MakeResponse(perc_list,200)



