#/usr/bin/python

import sys
import random

def create_data(row, col, nnz, sd):
  random.seed(sd)
  entryList = []
  i = 0
  while i<nnz:
    entry = (random.randint(0,row-1), random.randint(0,col-1))
    if entry not in entryList:
      entryList.append(entry)
      i = i+1
  return entryList        	

def sort_list(list1):
  return sorted(list1, key = lambda x:(x[0],x[1]))

def write_file(f1,list1):
  for l in list1:
    f1.write(str(l[0])+' '+str(l[1])+' '+str(random.randint(1,10))+'\n') 
  return f1

if __name__ == "__main__":
  seed = int(sys.argv[len(sys.argv)-1])
  nnz = int(sys.argv[len(sys.argv)-2])
  col = int(sys.argv[len(sys.argv)-3])
  row = int(sys.argv[len(sys.argv)-4])
  inpList = create_data(row, col, nnz, seed)
  inpList = sort_list(inpList)
  f1 = open(str(row)+'_'+str(col)+'_'+str(nnz)+'_'+str(seed)+'.ip','w')
  write_file(f1,inpList)
  f1.close()

