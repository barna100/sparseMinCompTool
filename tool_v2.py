import re
import sys
import bisect

arrayList = []
loopIters = []
nodeList = []
computationList = []
accessGraph = []
dfaList = []
entryList  = []
codeList = []
sparseArrayList = []
#directory = '/home/barnali/Documents/IITB/PHD/parallel_sparse/semiautomatic-tool/source/'
def prepare_data(dataFile):
  array = ''
  rowDecl = ''
  dataList = []
  for df in dataFile:
    indxList = []
    valList = []
    f1 = open(df,'r')
    array = f1.readline().strip()
    dim = get_dimension(array)	
    if dim == 2:
      for indx,line in enumerate(f1):      
        if indx >= 1:
          entry = line.split()
          row = int(entry[0])
          col = int(entry[1])            
          val = int(entry[2])
          indxList = update_indxList(row,col,indxList)
          valList.append(val)
    if dim == 1:
      for indx,line in enumerate(f1):      
        if indx >= 1:
          entry = line.split()
          indx = int(entry[0])
          val = int(entry[1])
	  bisect.insort(indxList,indx)
          valList.append(val)

    f1.close()
    if array == '':
      print "error!!! annotate the data file with the name of accessing array"
    else:
      sparseEntry = []
      sparseEntry.append(array)
      sparseEntry.append(indxList)
      sparseEntry.append(valList)
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

def postProcess_dataList(dataList):
  for array in arrayList:
    post_process1(array[0])

def post_process1(array):    
    dim = get_dimension(array)
    for indx,data in enumerate(dataList):
      if data[0] == array:
        totalLength = 0
        if dim == 2:
          for i,d in enumerate(dataList[indx][1]):
            length = len(d[1])
            if len(dataList[indx][1][i]) == 2:                
              dataList[indx][1][i].append(length)
            else:
              dataList[indx][1][i][2] = length
            totalLength = totalLength + length
          if len(dataList[indx]) == 4:
            dataList[indx][3] = totalLength
          else:
            dataList[indx].append(totalLength)
        if dim == 1:
	  if len(dataList[indx]) == 4:
            dataList[indx][3] = len(dataList[indx][1])
	  else: 
            dataList[indx].append(len(dataList[indx][1]))
    return dataList

def compute_sparseIndex(array,indx):
  if len(indx) == 2:
    row = int(indx[0])
    col = int(indx[1])
    for data in dataList:
      if data[0] == array:
        return get_sparseIndex2D(row,col,data[1])        
  elif len(indx) == 1:
    ind = int(indx[0])
    for data in dataList:
      if data[0] == array:
        return get_sparseIndex1D(ind,data[1])

def get_sparseIndex1D(ind,indxList) :
  for indx,val in enumerate(indxList):
    if val == ind:
      return indx

def get_sparseIndex2D(row,col,indxList) :
  for indx,val in enumerate(indxList):
    if val[0] == row:
      return compute_offset(indx,indxList) + val[1].index(col)

def prepare_bitVector(entry):
  flag = 0
  for data in dataList:
    if data[0] == get_array(entry):
      flag = 1
      return [1]*data[3]
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
      sparsity = int(lines[i+3].strip().split(':')[1].strip())
      array = (name,int(dim),sparsity)
      arrayList.append(array)
      if sparsity == 1:
        sparseArrayList.append(name)
      i = i+3
    elif lines[i] == 'loop':
      iters = re.sub('\s+','',lines[i+1].strip().split(':')[1].strip()).split(',')
      for it in iters:
        loopIters.append(it)
      i = i+1
    elif lines[i] == 'node':
      name = lines[i+1].strip().split(':')[1].strip()
      access = lines[i+2].strip().split(':')[1].strip()
      index = lines[i+3].strip().split(':')[1].strip().split(',')
      lb = lines[i+4].strip().split(':')[1].strip().split(',')
      for indx,l1 in enumerate(lb):
        l2 = re.sub(r'[1-9][0-9]*','',l1)
        if l2 == '':
          lb[indx] = int(l1)
      ub = lines[i+5].strip().split(':')[1].strip().split(',')
      for indx,l1 in enumerate(ub):
        l2 = re.sub(r'[1-9][0-9]*','',l1)
        if l2 == '':
          ub[indx] = int(l1)
      array = lines[i+6].strip().split(':')[1].strip()
      offset = [int(j) for j in lines[i+7].strip().split(':')[1].strip().split(',')]
      func = lines[i+8].split(':')[1].strip()
      node = (name,access,index,lb,ub,array,offset,func)
      nodeList.append(node)
      i = i+8
    elif lines[i] == 'computation':
      abstrExpr = lines[i+1].strip().split(':')[1].strip()
      lhs = abstrExpr.strip().split('=')[0].strip()
      rhs = re.sub('\s+','',abstrExpr.strip().split('=')[1].strip())
      cond = lines[i+2].strip().split(':')[1].strip()
      origExpr = lines[i+3].strip().split(':')[1].strip()
      computation = (lhs,rhs,cond,origExpr)
      computationList.append(computation)
      i = i+4
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
  while (len(workList) > 0):
    rmList = []
    for entry in workList:
      compute_inInfo(entry)	    
      localInfoVec = compute_localInfoVec(entry)
      outInfoVec = compute_outInfoVec(entry,localInfoVec)
      if (get_bitVector(get_outInfo(entry)) == []) | (is_equal(get_bitVector(get_outInfo(entry)),outInfoVec) == 0):
  	outInfo = []
  	outInfo.append(entry)
   	outInfo.append(get_array(entry))
  	outInfo.append(outInfoVec)
	set_outInfo(outInfo, entry)
      else:
	rmList.append(entry)
    workList = remove_entry(rmList,workList)

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
      update_value(indxList,array)
      bv = compute_localInfoVec1(indxList,length)
      if len(indxList) != 0:
        update_bitVector(indxList,get_array(entry))
    return bv

def update_value(indxList,array):
  for ind,data in enumerate(dataList):
    if data[0] == array:
      for indx in indxList:
        dataList[ind][2].insert(indx,0)
      break

def compute_indxList(relIndxList,array):
  indxList = []
  for data in dataList:
    if data[0] == array:
      if get_dimension(array) == 2:
        for relIndx in relIndxList:
          indxList.append(compute_offset(relIndx[0],data[1]) + relIndx[1])
      if get_dimension(array) == 1:
        for relIndx in relIndxList:
	  indxList.append(relIndx[1])
  return indxList

def compute_offset(indx,list1):
  indx1 = 0
  offset = 0
  while indx1 < indx:
    offset = offset + list1[indx1][2]
    indx1 = indx1 + 1
  return offset

def compute_localInfoVec1(indxList, length):
  bv = [0]*length
  for indx in indxList:
    bv[indx] = 1
  return bv

def compute_localInfo(entry):
    localEntryList = []
    expr = get_abstrExpr(entry)
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
        andEntryList = create_andEntryList(proCompList,baseIndex,baseRelOffset)
        modify_andEntryListLhsRelOffset(andEntryList,lhsRelOffset,lhsRelIndex)
	for baseEntryNZ in baseEntryNZList:
          andOprdList = create_andOprdList(baseEntryNZ,andEntryList,baseIndex,baseEntry)
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
            localEntry = check_limit(get_lb(entry),get_ub(entry),localEntry,entry)
            localEntry = check_condition(get_condition(entry),localEntry,entry)
            for l1 in localEntry:
              localEntryList.append(l1)
            pseudoCode_gen(localEntry,flatten(andOprdList),comp,entry)
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
          localEntry = check_limit(get_lb(entry),get_ub(entry),localEntry,entry)
          localEntry = check_condition(get_condition(entry),localEntry,entry)
          for l1 in localEntry:            
            localEntryList.append(l1) 
          pseudoCode_gen(localEntry,toList(toList(baseEntryNZ)),comp,entry)
    localEntryList = rmDup_sort(localEntryList,get_dimension(get_array(entry)))
    return localEntryList

def toList(item):
  retList = []
  retList.append(item)
  return retList

def toTuple(list1):
  if len(list1) == 1:
    return '(' + str(list1[0]) + ')'
  if len(list1) > 1:
    return tuple(list1)

def create_andOprdList(baseEntryNZ,andEntryList,baseIndex,baseEntry):
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
  return andOprdList

def modify_andEntryListLhsRelOffset(andEntryList,lhsRelOffset,lhsRelIndex):
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

def create_andEntryList(proCompList,baseIndex,baseRelOffset):
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
  return andEntryList

def compute_instr(lhs,indx,rhsList,entry,comp):
  instr = entry+'@'+str(toTuple(lhs))+'='+compute_oprd(rhsList,indx,entry,comp)
  return instr

def compute_oprd(rhsList, indx, entry, comp):
  arrayList = []
  compList = comp.split("*")
  codeEntry = compute_codeEntry(rhsList,indx)
  oprdList = []
  for ce in codeEntry:
    for ind,c in enumerate(ce):
      if ind == 0:
        instr = compList[ind]+'@'+str(toTuple(c))
      else:
        instr = instr + '*' + compList[ind]+'@'+str(toTuple(c))
  return instr

def pseudoCode_gen(lhsList,rhsList,comp,entry):  
  indexList = get_index(entry)
  offsetList = get_offset(entry)
  entryIndx = -1
  if entry in entryList:
    entryIndx = entryList.index(entry)
  if entryIndx == -1:
    entryList.append(entry)
    entryIndx = entryList.index(entry)
    instrList = []
    for indx,lhs in enumerate(lhsList):    
      instr = []
      iterVec = compute_iter(lhs,loopIters,indexList,offsetList)
      instr.append(iterVec)
      instr1 = compute_instr(lhs,indx,rhsList,entry,comp)
      instr.append(instr1)
      instrList.append(instr)
    codeList.append(instrList)
  else:
    for indx,lhs in enumerate(lhsList):    
      iterVec = compute_iter(lhs,loopIters,indexList,offsetList)      
      flag = 0
      for indx1, item in enumerate(codeList[entryIndx]):
        if item[0] == iterVec:
          flag = 1
          oprd = compute_oprd(rhsList, indx, entry, comp)
          if not oprd in item[1].split('=')[1]:
            codeList[entryIndx][indx1][1] = item[1] + '+' + oprd
          break
      if flag == 0:
        instr = []
        instr.append(iterVec)
        instr1 = compute_instr(lhs,indx,rhsList,entry,comp)
        instr.append(instr1)
        codeList[entryIndx].append(instr)
          
def compute_iter(lhs,loopIters,indexList,offsetList):
  iterList = []
  for i in loopIters:
    if i in indexList:
      iterList.append(lhs[indexList.index(i)] - offsetList[indexList.index(i)])
    else:
      iterList.append(0)
  return toTuple(iterList)    

def compute_codeEntry(rhsList,indx):
  codeEntry = []
  if len(rhsList) == 1:
    codeEntry = rhsList
  else:
    codeEntry.append(rhsList[indx])
  return codeEntry

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
  tmpList = [list(tup) for tup in {tuple(item) for item in tmpList}]
  if dim == 2:
    return sortList2D(tmpList)
  if dim == 1:
    return sortList1D(tmpList)
    

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
  resList = sortList1D(resList)
  return resList

def sortList1D(list1):
    return sorted(list1, key=lambda x: int(x[0]))

def sortList2D(list1):
    return sorted(list1, key=lambda x: (x[0],x[1]))

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
  if dim == 1:
    for l1 in list1:
      indx1 = l1[0]
      if indx1 not in dataList[indx][1]:
	bisect.insort(dataList[indx][1],indx1)
        relIndxList.append((indx1,dataList[indx][1].index(indx1)))
  return relIndxList
    
def check_condition(cond,list1,entry):
  if cond == '':
    return list1
  else:
    retList = []
    for l1 in list1:
      if get_value(cond,entry,l1) == True:
        retList.append(l1)
    return retList

def check_limit(lb,ub,list1,entry):
  retList = []
  for l1 in list1:
    limit = 0
    for indx in range(len(l1)):
      if type(lb[indx]) != int:        
        lb[indx] = get_value(lb[indx],entry,l1)
      if type(ub[indx]) != int:
        ub[indx] = get_value(ub[indx],entry,l1)
      if (l1[indx] >= lb[indx])&(l1[indx] <= ub[indx]):
        limit = 1
      else:
        limit = 0
    if limit == 1:
      retList.append(l1)          
  return retList

def get_value(item,entry,list1):
  indxList = get_index(entry)
  cmd  = ''
  for i in item:
    if i in indxList:
      cmd = cmd + str(list1[indxList.index(i)])
    else:
      cmd = cmd + str(i)
  return eval(cmd)

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

def get_abstrExpr(item):
  for comp in computationList:
    if comp[0] == item:
      return comp[1]	    

def get_condition(item):
  for comp in computationList:
    if comp[0] == item:
      return comp[2]	    

def get_origExpr(item):
  for comp in computationList:
    if comp[0] == item:
      return comp[3]	    

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

def get_sparsity(array):
  for ar in arrayList:
    if ar[0] == array:
      return ar[2]

def get_dataLength(array):
  for data in dataList:
    if data[0] == array:
      return data[3]

def get_instrSet(component):
  for code in codeList:
    if code[0] == component:
      return code[1]

def get_instrRhs(component,lhs):
  instrSet = get_instrSet(component)
  for instr in instrSet:
    if instr[0] == lhs:
      return instr[1]

def substitute(item):
  return item.strip().split(",")

def dump_dfaEntry(entry):
  for dfa in dfaList:
    if dfa[0] == entry:
      print dfa

def dump_dfaList():
  for dfa in dfaList:
    print dfa

def generate_code(f1, codeList):
  prologue_code(f1)
  length = len(codeList)
  for j in range(length):
    instr = process_finalCodeList(codeList[j][1])
    f1.write(instr+';\n')

def prologue_code(f1):  
  for data in dataList:
    if get_sparsity(data[0]) == 1:
      instr = 'val'+str(data[0])+'['+str(data[3])+']={'+str(data[2][0])
    else:
      instr = str(data[0])+'['+str(data[3])+']={'+str(data[2][0])
    for indx in range(1,len(data[2])):
      instr = instr+','+str(data[2][indx])
    instr = instr + '};\n'
    f1.write(instr)

def process_finalCodeList(codeLine):
  codeLineList = re.split('=|\+|\*',codeLine)
  oprtList = re.sub('[^=\*\+]','',codeLine)
  instr = ''
  for indx,code in enumerate(codeLineList):
    tmpList = code.split('@')
    if indx != len(codeLineList)-1:
      instr = instr+compute_sparseArray(tmpList)+oprtList[indx]
    else:
      instr = instr+compute_sparseArray(tmpList)
  return instr

def compute_sparseArray(oprd):
    array = get_array(oprd[0])
    indx = re.sub('[\s+()]','',oprd[1]).split(',')
    if get_sparsity(array) == 1:
      retArray = 'val'+array
      retIndex = compute_sparseIndex(array,indx)
      return retArray + '['+ str(retIndex) + ']'
    else:
      if len(indx) == 2 :
        return array+'['+str(indx[0])+']['+str(indx[1])+']'
      elif len(indx) == 1 :
        return array+'['+str(indx[0])+']'

def sort_codeList(newCodeList):
  return sorted(newCodeList,key=lambda x:(x[0],x[1]))

def merge_codeList():
  retCodeList = codeList[0]
  for indx,code in enumerate(codeList):
    if indx != 0:
      retCodeList.extend(code)
  return retCodeList

def process_codeList():
  newCodeList = merge_codeList()
  newCodeList = sort_codeList(newCodeList)
  return newCodeList

if __name__ == "__main__":
###############################    
# code to process graph file  #  
###############################    
  graphFile = sys.argv[1]
  prepare_graph(graphFile)
###############################    
# code to process dataFile    #
###############################    
  dataFile = []
  for i in range(2,len(sys.argv)-1):
    dataFile.append(sys.argv[i])
  dataList = prepare_data(dataFile)  
  postProcess_dataList(dataList)
###############################    
# code to prepare dfaList     #
###############################    
  prepare_dfaList()
###############################
# code for non-zero analysis  #
###############################
  analysis_mayNZ(dataList)
###############################
# code generation             #
###############################
  codeList = process_codeList()
  print codeList
  f1 = open(sys.argv[len(sys.argv)-1], "w")
  generate_code(f1,codeList)
  f1.close()
