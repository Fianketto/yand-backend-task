from flask import request
from flask_restful import Resource
import json
import sqlite3
import Req_classes.Functions as Func




class PatchCitizenData(Resource):
	def patch(self, import_id,citizen_id):

		#	---	0.	Some preparations
		Func.Recording(1,request)
		needed_keys=["citizen_id","town","street","building","apartment","name","birth_date","gender","relatives"]
		possible_keys=["town","street","building","apartment","name","birth_date","gender","relatives"]
		possible_keys_str_values=["town","street","building","name","birth_date","gender"]
		possible_keys_int_values=["apartment"]
		genders=["male","female"]
		error_exists=False
		error_description=""


		#	---	1.	Check request
		#	---		1.1.	Check if import_id exists
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

		#	---		1.2.	Check if citizen_id exists
		table_name=Func.CitTable_prefix+str(import_id)
		sql_req="SELECT count(citizen_id) as cnt FROM "+table_name+" WHERE citizen_id="+str(citizen_id)
		cursor.execute(sql_req)
		rows=cursor.fetchall()
		cnt=rows[0][0]
		if int(cnt)!=1:
			error_description="Invalid citizen_id"
			error_exists=True
			return Func.MakeResponse(error_description,400)	

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

		#	---		2.3.	At least one field exists and no extra field
		citizen=req_data
		key_found=False
		for k in citizen.keys():
			if k not in possible_keys:
				error_description="One or more extra fields in import data - key "+str(k)
				error_exists=True
				return Func.MakeResponse(error_description,400)
			else:
				key_found=True

		if key_found==False:
			error_description="No valid key in import data"
			error_exists=True
			return Func.MakeResponse(error_description,400)

		#	---		2.4.	All fields are correct type
		e_d_part=""
		for k in citizen.keys():
			if k in possible_keys_str_values:
				if type(citizen[k])!=str:
					error_exists=True
					e_d_part=" - key "+k
			elif k in possible_keys_int_values:
				if type(citizen[k])!=int:
					error_exists=True
					e_d_part=" - key "+k
			elif k=="relatives":
				if type(citizen[k])!=list:
					error_exists=True
					e_d_part=" - key "+k
				else:
					for j in citizen[k]:
						if type(j)!=int:
							error_exists=True	
							e_d_part=" - key "+k										
		if error_exists:
			error_description="One or more fields in import data have incorrect type"+e_d_part
			return Func.MakeResponse(error_description,400)

		#	---		2.5.	All values are non-null or non-negative
		for k in citizen.keys():
			if k in possible_keys_str_values:
				if len(citizen[k])==0 or len(citizen[k])>256 or citizen[k].lower()=="null":
					error_exists=True
					e_d_part=" - key "+k
			elif k in possible_keys_int_values:
				if citizen[k]<0 or citizen[k]>100000000000:
					error_exists=True
					e_d_part=" - key "+k
			elif k=="relatives":
				for j in citizen[k]:
					if j<0 or j>100000000000:
						error_exists=True	
						e_d_part=" - key "+k								
		if error_exists:
			error_description="One or more values in import data are invalid"+e_d_part
			return Func.MakeResponse(error_description,400)

		#	---		2.6.	Valid birth date
		if "birth_date" in citizen.keys():	
			if Func.IsValidDate(citizen["birth_date"])==False:
				error_exists=True
				error_description="birth_date is invaild or has incorrect format, must be dd.mm.yyyy"
				return Func.MakeResponse(error_description,400)				
			if Func.IsFromFuture(citizen["birth_date"])==True:
				error_exists=True
				error_description="Newborn citizens and time travelers are not supported. Check birth_date"
				return Func.MakeResponse(error_description,400)		

		#	---		2.7.	Valid gender
		if "gender" in citizen.keys():
			if citizen["gender"] not in genders:
				error_exists=True
				error_description="Invalid gender"
				return Func.MakeResponse(error_description,400)	

		#	---		2.8.	Valid relaltives list	
		if "relatives" in citizen.keys():
		#	---					---	No duplicate citizen_id in list of relatives
			rel_list=citizen["relatives"]
			print("rel_list: ",type(rel_list),rel_list)
			unique_rel_list=list(set(rel_list))
			if len(rel_list)>len(unique_rel_list):
				error_description="Duplicate citizen_id in relatives list"
				error_exists=True
				return Func.MakeResponse(error_description,400)					
		#	---					---	No invalid (nonexistent) citizen_id in list of relatives
			sql_req="SELECT citizen_id FROM "+table_name
			cursor.execute(sql_req)
			rows=cursor.fetchall()			
			cit_ids=list(rows[i][0] for i in range(len(rows)))
			for i in citizen["relatives"]:
				if i not in cit_ids:
					error_exists=True
					error_description="Nonexistent citizen_id "+str(i)+" in the list of relatives"
					return Func.MakeResponse(error_description,400)						

		#	---	3.	Keep previous list of relatives		
			sql_req="SELECT relatives FROM "+table_name+" WHERE citizen_id="+str(citizen_id)
			cursor.execute(sql_req)
			rows=cursor.fetchall()
			rel_old=rows[0][0].split()
			rel_new=list(map(str,citizen["relatives"]))

		#	---	4.	Update values
		#	---		4.1.	Update citizen's data
		for k in citizen.keys():
			if k in possible_keys_str_values:
				sql_req="UPDATE "+table_name+" SET "+k+"='"+citizen[k]+"' WHERE citizen_id="+str(citizen_id)
				cursor.execute(sql_req)
			elif k in possible_keys_int_values:
				sql_req="UPDATE "+table_name+" SET "+k+"="+str(citizen[k])+" WHERE citizen_id="+str(citizen_id)
				cursor.execute(sql_req)
			elif k=="relatives":
				rel_new_string=" ".join(list(map(str,citizen[k])))
				sql_req="UPDATE "+table_name+" SET "+k+"='"+rel_new_string+"' WHERE citizen_id="+str(citizen_id)
				cursor.execute(sql_req)
		conn1.commit()

		#	---		4.2.	Update citizen's relatives' data
		#	---					---	Remove given citizen from his old relatives' lists
		if "relatives" in citizen.keys():
			for i in rel_old:
				if i!=citizen_id:
					sql_req="SELECT relatives FROM "+table_name+" WHERE citizen_id="+str(i)
					cursor.execute(sql_req)
					rows=cursor.fetchall()
					print("rel old are: ",rel_old,"\nnow on: ",i,"\nrel of old rel are: ",rows)
					rel_of_old_rel=rows[0][0].split()
					rel_of_old_rel.remove(citizen_id)
					rel_of_old_rel_string=" ".join(rel_of_old_rel)
					sql_req="UPDATE "+table_name+" SET relatives='"+rel_of_old_rel_string+"' WHERE citizen_id="+str(i)
					cursor.execute(sql_req)
		#	---					---	Add given citizen to his new relatives' lists
		#							note: some or all new relatives may be the same as old ones
			for i in rel_new:
				if i!=citizen_id:
					sql_req="SELECT relatives FROM "+table_name+" WHERE citizen_id="+str(i)
					cursor.execute(sql_req)
					rows=cursor.fetchall()
					rel_of_new_rel=rows[0][0].split()
					rel_of_new_rel.append(citizen_id)
					rel_of_new_rel_string=" ".join(rel_of_new_rel)
					sql_req="UPDATE "+table_name+" SET relatives='"+rel_of_new_rel_string+"' WHERE citizen_id="+str(i)
					cursor.execute(sql_req)			
			conn1.commit()

		#	---	5.	Get the updated data
		sql_req="SELECT * FROM "+table_name+" WHERE citizen_id="+str(citizen_id)
		cursor.execute(sql_req)
		rows=cursor.fetchall()

		#	---	6.	Response
		citizen={}
		for j in range(len(needed_keys)-1):
			citizen[needed_keys[j]]=rows[0][j]
		citizen["relatives"]=list(map(int,rows[0][8].split()))

		return Func.MakeResponse(citizen,200)




