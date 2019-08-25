import random
import json

main_list=[]
list_of_dicts=[]

f=open("/home/khr/Dropbox/Python_serv/Testing/Other_files/All_fields/All_fields1000.txt","r",encoding="utf-8-sig")
lines=f.readlines()

for line in lines:
	cols=line.split("\t")
	inner_list=[]
	for col in cols:
		print(col)
		inner_list.append(col)
	main_list.append(inner_list)

needed_keys=["citizen_id","town","street","building","apartment","name","birth_date","gender","relatives"]
for i in range(len(main_list)):
	main_list[i][0]=int(main_list[i][0])								#id
	main_list[i][4]=int(main_list[i][4])								#apartment
	main_list[i][8]=main_list[i][8][1:-2].split(", ")					#relatives
	try:
		print("now i=",i,", we are in try, main_list[8]=",main_list[i][8])
		main_list[i][8]=list(map(int,main_list[i][8]))
	except:
		main_list[i][8]=[]
		print("now i=",i,", we are in except")
		
	list_of_dicts.append(dict(zip(needed_keys,main_list[i])))

fnl={"citizens":list_of_dicts}
fnl_json=json.dumps(fnl,ensure_ascii=False)
print(main_list[9])
with open("/home/khr/Dropbox/Python_serv/Testing/Data_to_import/POST/cit1000.json", "w") as f2:
	print(fnl_json,file=f2)


