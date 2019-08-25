import random

N=1000
cit=[[] for i in range(N)]
cit2=[[] for i in range(N)]
a=[]

for i in range(int(N/5)):
	r=max(0,int(random.normalvariate(10,8)))
	a.append(r)

a.sort()
print("a=",a)

#random rel for first 200 citizens
for i in range(len(a)):
	for j in range(a[i]):
		k=int(N*random.random())
		cit[i].append(k)

#now make it consistent
for cit_id in range(len(a)):
	for rel_id in cit[cit_id]:
		cit2[rel_id].append(cit_id)
		print(cit_id,rel_id)

for cit_id in range(N):
	cit[cit_id]+=cit2[cit_id]

for cit_id in range(N):
	cit[cit_id]=list(set(cit[cit_id]))
	print("cit_id=",cit_id,cit[cit_id])

with open('out1.txt', 'w') as f:
	for cit_id in range(N):
		print(cit_id,cit[cit_id],file=f)




