from flask import request
from flask_restful import Resource
import json
import sqlite3
import Req_classes.Functions as Func




class PostNewTable(Resource):	
	def post(self):

		#	---	0.	Some preparations
		Func.Recording(1,request)
		needed_keys=["citizen_id","town","street","building","apartment","name","birth_date","gender","relatives"]
		needed_keys_str_values=["town","street","building","name","birth_date","gender"]
		needed_keys_int_values=["citizen_id","apartment"]
		genders=["male","female"]
		error_exists=False
		error_description=""

		#	---	1.	First we want to get new id for import
		conn1=sqlite3.connect(Func.DB_name)
		cursor=conn1.cursor()
		sql_req="SELECT max(table_id) FROM "+Func.ReserveTable_name
		cursor.execute(sql_req)
		rows=cursor.fetchall()
		next_id=rows[0][0]+1
		cursor.execute("INSERT INTO "+Func.ReserveTable_name+" VALUES (?)",(next_id,))
		conn1.commit()
		next_table_name=Func.CitTable_prefix+str(next_id)
		print("next table is ", next_table_name)

		#	---	2.	Now check import data
		#	---		2.1.	Import data is in JSON format
		if Func.IsJSON(request)==False:
			error_description="Import data is not in JSON format"
			error_exists=True
			return Func.MakeResponse(error_description,400)			
		#req_data=request.json
		req_data=request.get_json(force=True)		
		dump_data=json.dumps(req_data,ensure_ascii=False)

		#	---		2.2.	Import data has no duplicate keys
		if Func.HasDuplicateKeys(request)==True:
			error_description="Import data has duplicate keys"
			error_exists=True
			return Func.MakeResponse(error_description,400)				

		#	---		2.3.	Only "citizens" key exists
		key_count=len(req_data.keys())
		print(key_count)
		if key_count==0:
			error_description="Import data has no keys"
			error_exists=True
		elif key_count>1:
			error_description="Import data has more than 1 key (should be only \"citizens\")"
			error_exists=True
		elif key_count==1:
			if "citizens" not in req_data.keys():
				error_description="Import data has no \"citizens\" key"
				error_exists=True
		if error_exists:
			return Func.MakeResponse(error_description,400)
						
		#	---		2.4.	The "citizens" value is list
		citizens=req_data["citizens"]
		if type(citizens)!=list:
			error_description="The \"citizens\" value must be a list"
			error_exists=True
			return Func.MakeResponse(error_description,400)				

		#	---		2.5.	List of citizens is not empty			
		if len(citizens)==0:
			error_description="No citizens in import data. Should be at least one"
			error_exists=True
			return Func.MakeResponse(error_description,400)	

		#	---		2.6.	List of citizens consists of only dicts
		for cit in citizens:
			if type(cit)!=dict:
				error_description="Invalid data format. All citizens must be in dict format"
				error_exists=True
				return Func.MakeResponse(error_description,400)										

		#	---		2.7.	All fields exist and no extra field
		for i in range(len(citizens)):
			for k in needed_keys:
				if k not in citizens[i].keys():
					error_description="One or more fields are missing in import data - key "+k+" (citizen "+str(i)+")"
					error_exists=True
					return Func.MakeResponse(error_description,400)
			for k in citizens[i].keys():
				if k not in needed_keys:
					error_description="One or more extra fields in import data - key "+k+" (citizen "+str(i)+")"
					error_exists=True
					return Func.MakeResponse(error_description,400)

		#	---		2.8.	All fields are correct type
		e_d_part=""
		for i in range(len(citizens)):
			for k in citizens[i].keys():
				if k in needed_keys_str_values:
					if type(citizens[i][k])!=str:	
						error_exists=True	
						e_d_part=" - key "+k+" (citizen "+str(i)+")"
				elif k in needed_keys_int_values:
					if type(citizens[i][k])!=int:	
						error_exists=True	
						e_d_part=" - key "+k+" (citizen "+str(i)+")"
				elif k=="relatives":
					if type(citizens[i][k])!=list:	
						error_exists=True	
						e_d_part=" - key "+k+" (citizen "+str(i)+")"
					else:
						for j in citizens[i][k]:
							if type(j)!=int:
								error_exists=True
								e_d_part=" - key "+k+" (citizen "+str(i)+")"						
		if error_exists:
			error_description="One or more fields in import data have incorrect type"+e_d_part
			return Func.MakeResponse(error_description,400)

		#	---		2.9.	All values are non-null or non-negative
		for i in range(len(citizens)):
			for k in citizens[i].keys():
				if k in needed_keys_str_values:
					if len(citizens[i][k])==0 or len(citizens[i][k])>256 or citizens[i][k].lower()=="null":
						error_exists=True
						e_d_part=" - key "+k+" (citizen "+str(i)+")"
				elif k in needed_keys_int_values:
					if citizens[i][k]<0 or citizens[i][k]>100000000000:
						error_exists=True	
						e_d_part=" - key "+k+" (citizen "+str(i)+")"
				elif k=="relatives":
					for j in citizens[i]["relatives"]:
						if j<0 or j>100000000000:
							error_exists=True
							e_d_part=" - key "+k+" (citizen "+str(i)+")"
		if error_exists:
			error_description="One or more values in import data are invalid"+e_d_part
			return Func.MakeResponse(error_description,400)

		#	---		2.10.	No duplicate citizen_id
		id_list=[]
		for i in range(len(citizens)):
			id_list.append(citizens[i]["citizen_id"])
		unique_id_list=list(set(id_list))
		if len(id_list)>len(unique_id_list):
			error_description="Duplicate citizen_id in import data"
			error_exists=True
			return Func.MakeResponse(error_description,400)			


		#	---		2.10.	Valid birth date	
		for i in range(len(citizens)):
			if Func.IsValidDate(citizens[i]["birth_date"])==False:
				error_exists=True
				error_description="birth_date is invaild or has incorrect format, must be dd.mm.yyyy (citizen "+str(i)+")"
				return Func.MakeResponse(error_description,400)	
			if Func.IsFromFuture(citizens[i]["birth_date"])==True:
				error_exists=True
				error_description="Newborn citizens and time travelers are not supported. Check birth_date (citizen "+str(i)+")"
				return Func.MakeResponse(error_description,400)					

		#	---		2.11.	Valid gender
		for i in range(len(citizens)):
			if citizens[i]["gender"] not in genders:
				error_exists=True
				error_description="Invalid gender (citizen "+str(i)+")"
				return Func.MakeResponse(error_description,400)					

		#	---		2.12.	Valid relaltives list
		q=[0 for i in range(len(citizens))]
		d={}
		for i in range(len(citizens)):
			q[i]=citizens[i]["citizen_id"]
			d[q[i]]=i
							
		for i in range(len(citizens)):
		#	---					---	No duplicate citizen_id in list of relatives
			rel_list=citizens[i]["relatives"]
			unique_rel_list=list(set(rel_list))
			if len(rel_list)>len(unique_rel_list):
				error_description="Duplicate citizen_id in relatives list (citizen "+str(i)+")"
				error_exists=True
				return Func.MakeResponse(error_description,400)				
			for j in citizens[i]["relatives"]:
		#	---					---	No invalid (nonexistent) citizen_id in list of relatives
				try:
					rel_i=d[j]
				except:
					error_exists=True
					error_description="Nonexistent citizen_id "+str(j)+" in the list of relatives (citizen "+str(i)+")"
					return Func.MakeResponse(error_description,400)
		#	---					---	No relatives inconsistency						
				if citizens[i]["citizen_id"] not in citizens[rel_i]["relatives"]:
					error_exists=True
					error_description="Relatives inconsistency: citizen_id="+str(citizens[i]["citizen_id"])+" is not in the list of citizen_id="+str(citizens[rel_i]["citizen_id"])
					return Func.MakeResponse(error_description,400)								

		#	---	3.	Add new table_id to tables_info
		cursor.execute("INSERT INTO "+Func.InfoTable_name+" VALUES (?)",(next_id,))
		conn1.commit()

		#	---	4.	Create new table and add recieved data to it
		cursor.execute("CREATE TABLE "+next_table_name+" (citizen_id int,town text, street text, building text, apartment int, name text,birth_date text, gender text, relatives text)")
		conn1.commit()
		list_of_values_to_add=[]
		values_to_add=()

		row_count=len(req_data["citizens"])
		for row in req_data["citizens"]:
			rel=" ".join(map(str,row["relatives"]))
			values_to_add=(row["citizen_id"],row["town"],row["street"],row["building"],row["apartment"],row["name"],row["birth_date"],row["gender"],rel)
			list_of_values_to_add.append(values_to_add)
		print("\n")
		#print("list values to add: ",list_of_values_to_add)		
		cursor.executemany("INSERT INTO "+next_table_name+" VALUES (?,?,?,?,?,?,?,?,?)",list_of_values_to_add)
		conn1.commit()

		#	---	5.	Return import_id
		import_id_dict={"import_id":next_id}
		return Func.MakeResponse(import_id_dict,201)
	
