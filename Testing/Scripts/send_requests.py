import os
import time


comm_1='curl -X POST -d "@../Data_to_import/POST/d'
comm_2='.json" 0.0.0.0:8080/imports'
for i in range(7,64):
	print("sending ",i)
	comm=comm_1+str(i)+comm_2
	os.system(comm)
	time.sleep(1.5)


comm_1='curl -X PATCH -d "@../Data_to_import/PATCH/d'
comm_2='.json" 0.0.0.0:8080/imports/2/citizens/1'
for i in range(1,21):
	print("sending ",i,"\n")
	comm=comm_1+str(i)+comm_2
	os.system(comm)
	time.sleep(1.5)
