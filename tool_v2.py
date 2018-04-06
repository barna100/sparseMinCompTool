import re
import sys
import bisect

arrayList = []
nodeList = []
computationList = []
accessGraph = []
dfaList = []
codeList = []

def prepare_data(dataFile):
  array = ''
  rowDecl = ''
  dataList = []
  for df in dataFile:
    indxList = []
    f1 = open(df,'r')
    array = f1.readline().strip()
    dim = get_dimension(array)	
    if dim == 2:
      for indx,line in enumerate(f1):      
        if indx >= 1:
          entry = line.split()
          row = int(entry[0])
          col = int(entry[1])            
          indxList = update_indxList(row,col,indxList)
    if dim == 1:
      for indx,line in enumerate(f1):      
        if indx >= 1:
          entry = line.split()
          indx = int(entry[0])
	  bisect.insort(indxList,indx)
    f1.close()
    if array == '':
      print "error!!! annotate the data file with the name of accessing array"
    else:
      sparseEntry = []
      sparseEntry.append(array)
      sparseEntry.append(indxList)
      dataList.append(sparseEntry)
  return dataList
    
def update_indxList(row,col,tmpList):
  flag = 0
  for indx in tmpList:
    if row == indx[0]:
      bisect.insort(indx[1],col)
      indx[1] = list(set(indx[1]))
      flag = 1
      break
  if flag == 0:
    item = []
    colList = []
    item.append(row)
    colList.append(col)
    item.append(colList)
    bisect.insort(tmpList,item)
  return tmpList

def post_process(dataList):
  for array in arrayList:
    post_process1(array[0])

def post_process1(array):    
    dim = get_dimension(array)
    for indx,data in enumerate(dataList):
      if data[0] == array:
        length = 0
        if dim == 2:
          for i,d in enumerate(dataList[indx][1]):
            if len(dataList[indx][1][i]) == 2:                
              dataList[indx][1][i].append(length)
            else:
              dataList[indx][1][i][2] = length
            length = length + len(d[1])
          if len(dataList[indx]) == 2:
            dataList[indx].append(length)
          else:
            dataList[indx][2] = length
        if dim == 1:
          dataList[indx].append(len(dataList[indx][1]))
    return dataList
 
def prepare_bitVector(entry):
  flag = 0
  for data in dataList:
    if data[0] == get_array(entry):
      flag = 1
      return [1]*data[2]
  if flag == 0:
    print 'error!!!data entry for array '+ get_array(entry)+ ' not found.'

def prepare_graph(iFile):
  lines  = [line.strip() for line in open(iFile,'r')]
  length = len(lines)
  i = 0
  while i!= length:
    if lines[i] == 'array':
      name = lines[i+1].strip().split(':')[1].strip()
      dim = lines[i+2].strip().split(':')[1].strip()
      array = (name,int(dim))
      arrayList.append(array)
      i = i+3
    elif lines[i] == 'node':
      name = lines[i+1].strip().split(':')[1].strip()
      access = lines[i+2].strip().split(':')[1].strip()
      index = lines[i+3].strip().split(':')[1].strip().split(',')
      lb = [int(j) for j in lines[i+4].strip().split(':')[1].strip().split(',')]
      ub = [int(j) for j in lines[i+5].strip().split(':')[1].strip().split(',')]
      array = lines[i+6].strip().split(':')[1].strip()
      offset = [int(j) for j in lines[i+7].strip().split(':')[1].strip().split(',')]
      node = (name,access,index,lb,ub,array,offset)
      nodeList.append(node)
      i = i+8
    elif lines[i] == 'computation':
      comp = lines[i+1].strip().split("=")
      computationList.append((comp[0].strip(),comp[1]))
      i = i+2
    elif lines[i] == 'accessGraph':
      strt_indx = i+1
      indx = strt_indx
      while indx != length:
        nodes = lines[indx].strip().split(':')
        node = nodes[0].strip()
        succList = nodes[1].strip().split(',')
        predList = nodes[2].strip().split(',')
        entry = (node,succList,predList)
        accessGraph.append(entry)
        indx = indx+1;      
      break
    else:
      i = i+1	    

def prepare_dfaList():
  for node in nodeList:
    item = []
    item.append(node[0])
    item.append([])
    item.append([])
    dfaList.append(item)

def analysis_mayNZ(dataList):
  workList = []
  for node in nodeList:
    workList.append(node[0])
  cnt = 0
  while (cnt <= 1):
#  while (len(workList) > 0):
    cnt = cnt+1
    rmList = []
    for entry in workList:
      compute_inInfo(entry)	    
      localInfoVec = compute_localInfoVec(entry)
      outInfoVec = compute_outInfoVec(entry,localInfoVec)
      if get_bitVector(get_outInfo(entry)) == []:
  	outInfo = []
  	outInfo.append(entry)
   	outInfo.append(get_array(entry))
  	outInfo.append(outInfoVec)
	set_outInfo(outInfo, entry)
      elif is_equal(get_bitVector(get_outInfo(entry)),outInfoVec) == 0:
  	outInfo = []
  	outInfo.append(entry)
   	outInfo.append(get_array(entry))
  	outInfo.append(outInfoVec)
	set_outInfo(outInfo, entry)
#      else:
#	rmList.append(entry)
#        workList = remove_entry(rmList,workList)

def remove_entry(rmList, workList):
  for entry in rmList:
    for indx,item in enumerate(workList):
      if item == entry:
        del workList[indx]
  return workList

def compute_localInfoVec(entry):
  bv = []
  if get_access(entry) == 'read':
    return bv
  else:
    localInfoList = compute_localInfo(entry)
    if len(localInfoList) != 0:
      array = get_array(entry)
      relIndxList = update_data(localInfoList,array)
      post_process1(array)
      length = get_dataLength(get_array(entry))
      indxList = compute_indxList(relIndxList,array)
      bv = compute_localInfoVec1(indxList,length)
      if len(indxList) != 0:
        update_bitVector(indxList,get_array(entry))
    return bv

def compute_indxList(relIndxList,array):
  indxList = []
  for data in dataList:
    if data[0] == array:
      for relIndx in relIndxList:
        indxList.append(data[1][relIndx[0]][2] + relIndx[1])
  return indxList

def compute_localInfoVec1(indxList, length):
  bv = [0]*length
  for indx in indxList:
    bv[indx] = 1
  return bv

def compute_localInfo(entry):
    localEntryList = []
    expr = re.sub('\s+','',get_expression(entry))
    exprCompList =  expr.strip().split('+')
    for comp in exprCompList:
      if re.search('\*',comp):
        proCompList = comp.strip().split('*')	      
        baseEntry = compute_baseEntry(proCompList)
	baseEntryNZList = get_nzEntries(baseEntry)
        baseIndex = get_index(baseEntry)
	baseRelOffset = compute_zeroMinus(get_offset(baseEntry))
        lhsRelIndex = compute_relIndex(get_index(entry),baseIndex)
	lhsRelOffset = compute_relOffset(get_offset(entry),baseRelOffset,lhsRelIndex,baseIndex)
	andEntryList = []
        for pcomp in proCompList:
          andEntry = []
	  andEntry.append(pcomp)
          relIndex = compute_relIndex(get_index(pcomp),baseIndex)
	  andEntry.append(relIndex)
          relOffset = compute_relOffset(get_offset(pcomp),baseRelOffset,relIndex,baseIndex)
	  andEntry.append(relOffset)
	  andEntry.append(get_nzEntries(pcomp))
	  andEntryList.append(andEntry)
        for lhsIdx in lhsRelIndex:
          if re.search('INV',lhsIdx):
            flag = 0
            for indx,andEntry in enumerate(andEntryList):
              if (lhsIdx in andEntry[1]) & (flag == 0):
                relDiff = 0 - andEntry[2][andEntry[1].index(lhsIdx)]
                andEntryList[indx][2][andEntry[1].index(lhsIdx)] = 0
                lhsRelOffset[lhsRelIndex.index(lhsIdx)] = lhsRelOffset[lhsRelIndex.index(lhsIdx)] + relDiff
                flag = 1
              elif (lhsIdx in andEntry[1]) & (flag == 1):
                offset = andEntryList[indx][2][andEntry[1].index(lhsIdx)] 
                andEntryList[indx][2][andEntry[1].index(lhsIdx)] = offset + relDiff
	for baseEntryNZ in baseEntryNZList:
	  andOprdList = []
   	  for andEntry in andEntryList:
	    if andEntry[0] != baseEntry:
	      nzEntryList = compute_nzEntry(baseIndex,baseEntryNZ,andEntry)
	      if nzEntryList != []:
		andOprdList.append(nzEntryList)
	      else:
		andOprdList = []
		break
            else:
              tmpList = []
              tmpList.append(baseEntryNZ)
	      andOprdList.append(tmpList)
	  if len(andOprdList) != 0:
            localEntry = []
            for indx,lhsIndex in enumerate(lhsRelIndex):
              if not re.search('INV',lhsIndex):
                localIndices = []
                localIndices.append(lhsRelOffset[indx] + baseEntryNZ[baseIndex.index(lhsIndex)])
                localEntry = cartesian_product(localEntry, localIndices)
              else:
                for indx1,andEntry in enumerate(andEntryList):
                  if lhsIndex in andEntry[1]: 
                    if andEntry[2][andEntry[1].index(lhsIndex)] == 0:
                      localIndices = compute_localEntry(andOprdList[indx1],andEntry[1].index(lhsIndex),lhsRelOffset[indx])
                      localEntry = cartesian_product(localEntry,localIndices)
            localEntry = check_limit(get_lb(entry),get_ub(entry),localEntry)
            for l1 in localEntry:
              localEntryList.append(l1)
            flattenList = []
            flattenList = flatten(andOprdList)       
#            pseudoCode_gen2(localEntry,flattenList,comp)
      else:
        baseEntry = comp
	baseEntryNZList = get_nzEntries(baseEntry)
        baseIndex = get_index(baseEntry)
	baseRelOffset = compute_zeroMinus(get_offset(baseEntry))
        lhsRelIndex = compute_relIndex(get_index(entry),baseIndex)
	lhsRelOffset = compute_relOffset(get_offset(entry),baseRelOffset,lhsRelIndex,baseIndex)
	for baseEntryNZ in baseEntryNZList:
          localEntry = []
          for indx,lhsIndex in enumerate(lhsRelIndex):
            if not re.search('INV',lhsIndex):
              localIndices = []
              localIndices.append(lhsRelOffset[indx] + baseEntryNZ[baseIndex.index(lhsIndex)])
              localEntry = cartesian_product(localEntry, localIndices)              
            else:
              localEntry = expand_rangeIndex(get_lbIndex(entry,indx),get_ubIndex(entry,indx),localEntry)           
          localEntry = check_limit(get_lb(entry),get_ub(entry),localEntry)
          for l1 in localEntry:            
            localEntryList.append(l1)  
          pseudoCode_gen1(localEntry,baseEntryNZ,comp)
    localEntryList = rmDup_sort(localEntryList,get_dimension(get_array(entry)))
    return localEntryList

def pseudoCode_gen1(localEntry,baseEntry,comp):
  print localEntry
  if len(codeList) == 0:
    codeLine = []
    codeLine.append(comp)
    for le in localEntry:    
      codeEntry = []
      codeEntry.append(baseEntry)
      codeEntry.append(le)
      codeLine.append(codeEntry)
    codeList.append(codeLine)
  else:
    indx = -1
    for indx,lst in enumerate(codeList):
      if lst[0] == comp:
        break
    if indx == -1:
      codeLine = []
      codeLine.append(comp)
      for le in localEntry:
        codeEntry = []
        codeEntry.append(baseEntry)
        codeEntry.append(le)
        codeLine.append(codeEntry)
      codeList.append(codeLine)
    else:
      for le in localEntry:
        codeEntry = []
        codeEntry.append(baseEntry)
        codeEntry.append(le)
        if codeEntry not in codeList[indx][1]:
          codeList[indx].append(codeEntry)
        
      
      
 
def flatten(list1):
  retList = []
  for l in list1:    
    retList = cartesian_product(retList,l)
  return retList

def update_bitVector(indxList,array):
  for dfa in dfaList:
    inInfoList = get_inInfo(dfa[0])
    for indx,inInfo in enumerate(inInfoList):
      if inInfo[1] == array:
        tmpList = []
        for indx1, t1 in enumerate(inInfo[2]):
          if indx1 in indxList:
            tmpList.append(0)
          tmpList.append(inInfo[2][indx1])
        inInfoList[indx][2] = tmpList
    outInfo = get_outInfo(dfa[0])
    if outInfo != [] :
      if outInfo[1] == array:
        tmpList = []
        for indx1, t1 in enumerate(outInfo[2]):
          if indx1 in indxList:
            tmpList.append(0)
          tmpList.append(inInfo[2][indx1])
        outInfo[2] = tmpList

def rmDup_sort(tmpList,dim):
  if dim == 2:
    tmpList = [list(tup) for tup in {tuple(item) for item in tmpList}]
    return sortList2D(tmpList)

def convert_toNestedLists(tmpList):
  resList = []
  rowList = []
  for item in tmpList:
    row = item[0]
    col = item[1]
    if row not in rowList:
      rowList.append(row)
      entry = []
      entry.append(row)
      colEntry = []
      bisect.insort(colEntry,col)
      entry.append(colEntry)
      resList.append(entry)
    else:
      for i in resList:
        if i[0] == row:
          bisect.insort(i[1],col)
  resList = sortListNested(resList)
  return resList

def sortListNested(list1):
    return sorted(list1, key=lambda x: int(x[0]))

def sortList1D(list1):
    return list1.sort(key=int)

def sortList2D(list1):
    list1 = sorted(list1, key=lambda x: (x[0],x[1]))
    return list1

def update_data(list1,array):
  relIndxList = []
  for indx,data in enumerate(dataList):
    if data[0] == array:
      dim = get_dimension(array)
      break
  if dim == 2:     
    list1 = convert_toNestedLists(list1)
    for l1 in list1:
      flag = 0
      row = l1[0]
      colList = l1[1]
      relOffset = 0
      if len(dataList[indx][1]) != 0:
        for indx1,indices in enumerate(dataList[indx][1]):
          if indices[0] == row:
            flag = 1
            for col in colList:
              if col not in dataList[indx][1][indx1][1]:
                bisect.insort(dataList[indx][1][indx1][1],col)
                relIndxList.append((indx1,dataList[indx][1][indx1][1].index(col)))
        if flag == 0:
          bisect.insort(dataList[indx][1],l1)
          for cnt in range(len(colList)):
            relIndxList.append((dataList[indx][1].index(l1),cnt))
      else:
        dataList[indx][1].append(l1) 
        for cnt in range(len(colList)):
          relIndxList.append((0,cnt))
  return relIndxList
          
def check_limit(lb,ub,list1):
  retList = []
  for l1 in list1:
    limit = 0
    for indx in range(len(l1)):
      if (l1[indx] >= lb[indx])&(l1[indx] <= ub[indx]):
        limit = 1
      else:
        limit = 0
    if limit == 1:
      retList.append(l1)          
  return retList
      
def expand_rangeIndex(lb,ub,list1):
  retList = []
  if len(list1) != 0:
    for i in range(lb,ub+1):
      for l1 in list1:
        l1.append(i)
        retList.append(l1)
  else:
    for i in range(lb,ub+1):
      item = []
      item.append(i)
      retList.append(item)
  return retList      
    

def cartesian_product(list1,list2):
  retList = []
  if len(list1) != 0:
    for l1 in list1:
      for l2 in list2:
        l3 = []
        for l in l1:
          l3.append(l)
        l3.append(l2)
        retList.append(l3)
  else:
    for l2 in list2:
      item = []
      item.append(l2)          
      retList.append(item)
  return retList


def compute_localEntry(nzEntryList,indx,offset):
  retList = []
  for nzEntry in nzEntryList:
    retList.append(nzEntry[indx]+offset)
  return retList

def compute_nzEntry(baseIndex,baseEntry,andEntry):
  retList = compute_modifiedEntry(baseIndex,baseEntry,andEntry[1],andEntry[2])
  return compute_nzEntry1(retList,andEntry[3])

def compute_modifiedEntry(baseIndex,baseEntry,relIndex,relOffset):
  retList = []    
  for indx,val in enumerate(relIndex):
    if re.search('INV',val):
      retList.append('INV')        
    else:
      retList.append(relOffset[indx] + baseEntry[baseIndex.index(val)])
  return retList      

def compute_nzEntry1(modifiedEntry,nzList):
  for pos,val in enumerate(modifiedEntry):
    if not re.search('INV',str(val)):
      nzList = compute_relevantNzEntry(pos,val,nzList)                  
      modifiedEntry[pos] == 'INV'
  return nzList

def compute_relevantNzEntry(indx,val,nzList):
  return [nz for nz in nzList if nz[indx] == val]
	
def get_nzEntries(entry):
  return filter_nzEntries(get_bitVector(get_outInfo(entry)), get_array(entry))

def filter_nzEntries(list1, array):
  for data in dataList:
    if data[0] == array:
      tmpList = convert_toListofTuples(get_dimension(array),data[1])
      return [x[0] for x in zip(tmpList,list1) if x[1] == 1]
     
def convert_toListofTuples(dim,list1):
  retList = []
  if len(list1) == 0:
    return retList
  else:
    if dim == 2:
      for l1 in list1:
        for l2 in l1[1]:
	  item = []
 	  item.append(l1[0])
 	  item.append(l2)
          retList.append(item)
    if dim == 1:
      for l1 in list1:
	item = []
	item.append(l1)
        retList.append(item)
  return retList
 
def compute_relIndex(indexList, baseIndexList):
  retList = []
  for indx,val in enumerate(indexList):
    if val in baseIndexList:
      retList.append(val)       
    else:
      retList.append((val+'_INV'))
  return retList      

def compute_relOffset(offsetList,baseOffsetList,relIndexList, baseIndexList):
  retList = []    
  for indx,val in enumerate(relIndexList):
    if re.search('INV',val):
      retList.append(offsetList[indx])
    else:
      retList.append((offsetList[indx]+baseOffsetList[baseIndexList.index(val)]))
  return retList

def compute_zeroMinus(list1):
  retList = []
  for l in list1:
    retList.append(0-l)
  return retList

def compute_baseEntry(list1):
  length = len(get_outInfo(list1[0]))
  item = list1[0]
  for l in list1:
    length1 = len(get_outInfo(list1[0]))
    if length1 < length:
      length = length1
      item = l
  return item     
  	
def compute_outInfoVec(entry,localInfo):
  inInfoList = get_inInfo(entry)
  outInfo = []
  resInfo = []
  array = get_array(entry)
  outInfo.append(entry)
  outInfo.append(array)
  for inInfo in inInfoList:
    if inInfo[1] == array:
      resInfo = or_op(resInfo,inInfo[2]) 	    
  if get_access(entry) == 'write':
    resInfo = or_op(resInfo,localInfo)
  return resInfo

def is_equal(list1,list2):
  if (list1 == []) & (list2 == []):
    return 1
  if (list1 == []) | (list2 == []):
    return 0  
  flag = 0
  if (len(list1) == len(list2)):
    flag = 1
    for x in zip(list1,list2):
      if x[0] != x[1]:
	flag = 0
	break
  return flag


def or_op(list1, list2):
  return list1 or list2

def compute_inInfo(entry):
  if (get_access(entry) == 'read') & (get_inInfo(entry) == []):
    initialize(entry)
  else:
    inInfoList = []	  
    predList = get_predList(entry) 	 
    if (predList[0] != '') & (len(predList) >= 1):
      for pred in predList:
        outInfo = get_outInfo(pred)
        inInfoList.append(outInfo)
      set_inInfo(inInfoList,entry)
  	
def initialize(entry):
  inInfo = []
  inInfoList = []
  inInfo.append('init')
  array = get_array(entry)
  inInfo.append(array)
  inInfo.append(prepare_bitVector(entry))
  inInfoList.append(inInfo)
  set_inInfo(inInfoList,entry)

def reset_inInfo(entry):
  for indx,val in enumerate(dfaList):
    if val[0] == entry:
      dfaList[indx][1] = []

def set_inInfo(inInfoList,entry):
  for indx,val in enumerate(dfaList):
    if val[0] == entry:
      dfaList[indx][1] = []
      for i in inInfoList:	    
        dfaList[indx][1].append(i)

def set_outInfo(outInfo,entry):
  for indx,val in enumerate(dfaList):
    if val[0] == entry:
      dfaList[indx][2] = outInfo

def get_bitVector(term):
  if term != []:
    return term[2]
  else:
    return term

def get_predList(item):
  for entry in accessGraph:
    if entry[0] == item:
      return entry[2]

def get_access(item):
  for node in nodeList:
    if node[0] == item:
      return node[1]

def get_index(item):
  for node in nodeList:
    if node[0] == item:
      return node[2]
        
def get_lb(item):
  for node in nodeList:
    if node[0] == item:
      return node[3]

def get_lbIndex(item, indx):
  return get_lb(item)[indx]

def get_ub(item):
  for node in nodeList:
    if node[0] == item:
      return node[4]

def get_ubIndex(item, indx):
  return get_ub(item)[indx]
        
def get_array(item):
  for node in nodeList:
    if node[0] == item:
      return node[5]

def get_offset(item):
  for node in nodeList:
    if node[0] == item:
      return node[6]  

def get_expression(item):
  for comp in computationList:
    if comp[0] == item:
      return comp[1]	    

def get_inInfo(item):
  for entry in dfaList:
    if entry[0] == item:
      return entry[1]
  
def get_outInfo(item):
  for entry in dfaList:
    if entry[0] == item:
      return entry[2]

def get_dimension(array):
  for ar in arrayList:
    if ar[0] == array:
      return ar[1]

def get_dataLength(array):
  for data in dataList:
    if data[0] == array:
      return data[2]

def substitute(item):
  return item.strip().split(",")

def dump_dfaEntry(entry):
  for dfa in dfaList:
    if dfa[0] == entry:
      print dfa

def dump_dfaList():
  for dfa in dfaList:
    print dfa

if __name__ == "__main__":
  dataFile = []
  graphFile = sys.argv[1]
  prepare_graph(graphFile)
  dataFile.append(sys.argv[2])
  dataFile.append(sys.argv[3])
  dataFile.append(sys.argv[4])
  dataList = prepare_data(dataFile)
  post_process(dataList)
  prepare_dfaList()
  analysis_mayNZ(dataList)
  dump_dfaList()
