import numpy as np
from functools import reduce 
import copy 
import collections, functools, operator

class BayesianNetwork:
    def __init__(self, filename):
        f = open(filename, 'r') 
        N = int(f.readline())
        lines = f.readlines()
        self.nodesX=[]
        self.nodeDomain={}
        self.nodeParent={}
        self.nodeProb={}
        self.nodeFactor=[]
        for line in lines:
            node, parents, domain, shape, probabilities = self.__extract_model(line)
            # YOUR CODE HERE
            self.nodesX.append(node)
            self.nodeDomain[node]=domain
            self.nodeParent[node]=parents
            
            sumParent=""
            for p in parents:
                sumParent+=p
            self.nodeFactor.append(sumParent+node)

            mulShape=1
            if (type(shape)==tuple):
                for s in shape:
                    mulShape*=s
            else:
                mulShape=1

            probList=[]
            if mulShape!=1:
                for i in range(mulShape):
                    probList.append({})
            else:
                for i in range(shape):
                    probList.append({})

            # objectProbList={}
            len_parents=len(parents)
            mulShape_=mulShape
            i=-1
            prob=np.reshape(probabilities,-1)
            if (mulShape!=1):
                while (mulShape_!=1):
                    i+=1
                    index=-1
                    mulShape_=int(mulShape_/shape[i])
                    if (i<len_parents):
                        while (index!=mulShape-1):
                            for k in self.nodeDomain[parents[i]]:
                                for j in range(mulShape_):
                                    index+=1
                                    probList[index][parents[i]]=k
                    else:
                        while (index!=mulShape-1):
                            for d in self.nodeDomain[node]:
                                index+=1
                                probList[index][node]=d
                                probList[index]['prob']=prob[index]
            else:
                for k in range(shape):
                    probList[k][node]=self.nodeDomain[node][k]
                    probList[k]['prob']=prob[k]
            self.nodeProb[self.nodeFactor[-1:][0]]=probList
            # print(probList)
        # print(self.nodeProb)
        f.close()

    def findFactorWithVariable(self,factors,var):
        return list(filter(lambda factor: var in factor,factors))

    def findProbWithVariable(self,probDis,var):
        return [item for item in probDis if item.get(var)]

    def findShareVariableAndMerge(self,varA,varB):
        shareVars=set(varA).intersection(set(varB))
        mergeVars=set(varA).union(set(varB))
        # print(mergeVars)
        return shareVars,mergeVars

    def setIntoString(self,sample):
        result=""
        for s in sample:
            result+=str(s)
        return result

    def varEliminate(self,factor,eliminateVar):
        remainingSet=list(set(factor).difference(set(eliminateVar)))
        factorProb=copy.deepcopy(self.nodeProb[factor])
        # print('Factor ',self.nodeProb[factor])
        
        recallDict={}
        for f in factorProb:
            if (f!={}):
                del f[eliminateVar]
                mergeName=""
                tempName={}
                for r in remainingSet:
                    mergeName+=f[r]
                    tempName[r]=f[r]
                    del f[r]
                if not(mergeName in recallDict) :
                    recallDict[mergeName]=tempName
                f[mergeName]=f['prob']
                del f['prob']
        
        # print('107777:',factorProb)
        result = dict(functools.reduce(operator.add, 
        map(collections.Counter, factorProb))) 
        resultList=[]
        # print('106:',result)
        for key in result:
            tempObj={}
            for reKey in recallDict[key]:
                tempObj[reKey]=recallDict[key][reKey]
            tempObj['prob']=result[key]
            resultList.append(tempObj)
        # print('116:',resultList)

        # print(factor)
        # print(factorProb)
        # print(result)
        # print(resultList)
        return {self.setIntoString(set(remainingSet)):resultList}    

    def varEliminateByEvidence(self,evidence):
        for noFa in self.nodeFactor:
            for ev in evidence:
                if ev in noFa:
                    index=0
                    while (index!=len(self.nodeProb[noFa])):
                        # print('135:',noPr)
                        # print('136:',evidence[ev])
                        if (self.nodeProb[noFa][index][ev]!=evidence[ev]):
                            self.nodeProb[noFa].pop(index)
                        else:
                            index+=1
                        # print('138:',self.nodeProb[noFa])

    def mulFactorOverlap(self,elementOne,elementTwo,name):
        shareVars=set(name)
        countShareVar=len(shareVars)
        for fA in elementOne:
            for fB in elementTwo:
                countS=0
                for s in shareVars:
                    if fA[s]==fB[s]:
                        countS+=1
                        if countS==countShareVar:
                            temp=fA['prob']*fB['prob']
                            fA['prob']=temp
                            fB['prob']=temp
                            countS=0
        return {name:elementOne if len(elementOne)>len(elementTwo) else elementTwo}


    def mulFactor(self,facA,facB):
        shareVars,mergeVars=self.findShareVariableAndMerge(facA,facB)        
        SetShareInFacA=self.nodeProb[facA]
        SetShareInFacB=self.nodeProb[facB]
                
        mulFactorAB=[]
        lenMulFactorAB=1
        for me in mergeVars:
            lenMulFactorAB*=len(self.nodeDomain[me])

        for i in range(lenMulFactorAB):
            mulFactorAB.append({})
        j=-1
        countShareVar=len(shareVars)
        for fA in SetShareInFacA:
            for fB in SetShareInFacB:
                countS=0
                for s in shareVars:
                    if (fA!={}) and (fB!={}):
                        if (fA[s]==fB[s]):
                            countS+=1
                            if countS==countShareVar:
                                j=j+1
                                mulFactorAB[j]['prob']=fA['prob']*fB['prob']
                                countS=0
                                for m in mergeVars:
                                    # mulFactorAB[j][m]=fShareA[m] if (fShareA[m]) else fShareB[m]
                                    try:
                                        mulFactorAB[j][m]=fA[m]
                                    except KeyError:
                                        mulFactorAB[j][m]=fB[m]
        return {self.setIntoString(mergeVars):mulFactorAB}

    def exact_inference(self, filename):
        result = 0
        f = open(filename, 'r')
        query_variables, evidence_variables = self.__extract_query(f.readline())


        # nodeX=copy.deepcopy(self.nodesX)
        # nodeDomain=copy.deepcopy(self.nodeDomain)
        # nodeProb=copy.deepcopy(self.nodeProb)
        # nodeFactor=copy.deepcopy(self.nodeFactor)
        # YOUR CODE HERE
        #Tim tap X cac node khong nam trong cau truy van (can loai bobo)
        if not(evidence_variables):
            for qu in query_variables:
                self.nodesX.remove(qu)
            # print(self.nodesX)
            for z in self.nodesX :
                FZ=[]
                for n in self.nodeFactor:
                    if z in n :
                        #tap cac nhan to F co chua bien Z
                        FZ.append(n)
                # FZcopy=copy.deepcopy(FZ)
                mulFac=FZ.pop()
                if (FZ):
                    while (FZ):
                        # print("181:",mulFac)
                        # print("182:",self.nodeFactor)
                        mulFacOne=FZ.pop()
                        # print("183:",mulFacOne)
                        # print("184:",self.nodeProb)

                        resultMulFac=self.mulFactor(mulFac,mulFacOne)
                        
                        del self.nodeProb[mulFac]
                        self.nodeFactor.remove(mulFac)
                        del self.nodeProb[mulFacOne]
                        self.nodeFactor.remove(mulFacOne)

                        for key in resultMulFac:
                            self.nodeProb[key]=resultMulFac[key]
                            self.nodeFactor.append(key)
                            mulFac=key
                    # print('192:',self.nodeProb)
                    # print('193:',self.nodeFactor)
                    resultVarEli=self.varEliminate(mulFac,z)
                    # for keyV in resultVarEli:
                    #     del self.nodeProb[mulFac]
                    #     self.nodeFactor.remove(mulFac)
                    #     self.nodeProb[keyV]=resultVarEli[keyV]
                    #     self.nodeFactor.append(keyV)

                    for keyV in resultVarEli:
                        del self.nodeProb[mulFac]
                        self.nodeFactor.remove(mulFac)
                        if (keyV in self.nodeProb):
                            self.nodeProb[keyV]=self.mulFactorOverlap(resultVarEli[keyV],self.nodeProb[keyV],keyV)[keyV]
                        else:
                            self.nodeProb[keyV]=resultVarEli[keyV]
                            self.nodeFactor.append(keyV)
                else:
                    resultVarEli=self.varEliminate(mulFac,z)

                    for keyV in resultVarEli:
                        del self.nodeProb[mulFac]
                        self.nodeFactor.remove(mulFac)
                        if (keyV in self.nodeProb):
                            self.nodeProb[keyV]=self.mulFactorOverlap(resultVarEli[keyV],self.nodeProb[keyV],keyV)[keyV]
                        else:
                            self.nodeProb[keyV]=resultVarEli[keyV]
                            self.nodeFactor.append(keyV)
                # print(FZ)
                
            # print("210:",self.nodeFactor)
            # print("211:",self.nodeProb)
            mulFac=self.nodeFactor.pop()
            resultF=None
            if (self.nodeFactor):
                while (self.nodeFactor):
                    mulFacOne=self.nodeFactor.pop()
                    # print("219:",mulFac)
                    # print("221:",mulFacOne)     

                    # print("220:",self.nodeFactor)
                    # print("220:",self.nodeProb)
                    resultMulFac=self.mulFactor(mulFac,mulFacOne)


                    del self.nodeProb[mulFac]
                    del self.nodeProb[mulFacOne]
                    for key in resultMulFac:
                        self.nodeProb[key]=resultMulFac[key]
                        mulFac=key
                    if (len(self.nodeFactor)==1):
                        break
                resultF= self.nodeProb[mulFac]
            else:
                resultF= self.nodeProb[mulFac]
                
            len_query=len(query_variables)
            # print('247:',resultF)
            # print('248',query_variables)
            for re in resultF:
                coun=0
                for key in query_variables:
                    # print('252:',re)
                    if (re[key]==query_variables[key]):
                        coun=coun+1
                        if coun==len_query:
                            # print('255:',re['prob'])
                            result=re['prob']
        else :
            patten=""
            # print(evidence_variables)
            for ev in evidence_variables:
                patten+=ev
            for qu in query_variables:
                patten+=qu

            if (patten in self.nodeFactor):
                len_query=len(query_variables)+len(evidence_variables)
                for re in self.nodeProb[patten]:
                    coun=0
                    for key in query_variables:
                        # print('252:',re)
                        if (re!={}):
                            if (re[key]==query_variables[key]):
                                for keyTwo in evidence_variables:
                                    if (re[keyTwo]==evidence_variables[keyTwo]):
                                        coun=coun+1
                                    if coun==len_query-1:
                                        # print('255:',re['prob'])
                                        result=re['prob']
                                        break
            else:
                #Buoc 2 thu giam nhan to theo bang chung
                self.varEliminateByEvidence(evidence_variables)
                for ev in evidence_variables:
                    self.nodeDomain[ev].remove(evidence_variables[ev])
                # print(self.nodeProb)
                #buoc 3 xa ddinh bien can duoc loai bo
                for qu in query_variables:
                    self.nodesX.remove(qu)
                for ev in evidence_variables:
                    self.nodesX.remove(ev)
                #buoc 4 chay giai thuat loai bo bien
                for z in self.nodesX :
                    FZ=[]
                    for n in self.nodeFactor:
                        if z in n :
                            #tap cac nhan to F co chua bien Z
                            FZ.append(n)
                    # FZcopy=copy.deepcopy(FZ)
                    mulFac=FZ.pop()
                    if (FZ):
                        while (FZ):
                            # print("181:",mulFac)
                            # print("182:",self.nodeFactor)
                            mulFacOne=FZ.pop()
                            # print("183:",mulFacOne)
                            # print("184:",self.nodeProb)

                            resultMulFac=self.mulFactor(mulFac,mulFacOne)
                            
                            del self.nodeProb[mulFac]
                            self.nodeFactor.remove(mulFac)
                            del self.nodeProb[mulFacOne]
                            self.nodeFactor.remove(mulFacOne)

                            for key in resultMulFac:
                                if (key in self.nodeProb):
                                    self.nodeProb[key]=self.mulFactorOverlap(resultMulFac[key],self.nodeProb[key],key)[key]
                                    mulFac=key
                                else:
                                    self.nodeProb[key]=resultMulFac[key]
                                    self.nodeFactor.append(key)
                                    mulFac=key
                        # print('192:',self.nodeProb)
                        # print('193:',self.nodeFactor)
                        resultVarEli=self.varEliminate(mulFac,z)
                        for keyV in resultVarEli:
                            del self.nodeProb[mulFac]
                            self.nodeFactor.remove(mulFac)
                            if (keyV in self.nodeProb):
                                self.nodeProb[keyV]=self.mulFactorOverlap(resultVarEli[keyV],self.nodeProb[keyV],keyV)[keyV]
                            else:
                                self.nodeProb[keyV]=resultVarEli[keyV]
                                self.nodeFactor.append(keyV)
                    else:
                        resultVarEli=self.varEliminate(mulFac,z)
                        for keyV in resultVarEli:
                            # print(keyV)
                            # print("203:",self.nodeFactor)
                            del self.nodeProb[mulFac]
                            self.nodeFactor.remove(mulFac)

                            if (keyV in self.nodeProb):
                                self.nodeProb[keyV]=self.mulFactorOverlap(resultVarEli[keyV],self.nodeProb[keyV],keyV)[keyV]
                            else:
                                self.nodeProb[keyV]=resultVarEli[keyV]
                                self.nodeFactor.append(keyV)
    
                    # print(FZ)
                    
                # print("210:",self.nodeFactor)
                # print("211:",self.nodeProb)
                mulFac=self.nodeFactor.pop()
                resultF=None
                if (self.nodeFactor):
                    while (self.nodeFactor):
                        mulFacOne=self.nodeFactor.pop()
                        # print("219:",mulFac)
                        # print("221:",mulFacOne)     
                        # print("220:",self.nodeFactor)
                        # print("220:",self.nodeProb)
                        resultMulFac=self.mulFactor(mulFac,mulFacOne)
                        del self.nodeProb[mulFac]
                        del self.nodeProb[mulFacOne]

                        for key in resultMulFac:
                            if (key in self.nodeProb):
                                self.nodeProb[key]=self.mulFactorOverlap(resultMulFac[key],self.nodeProb[key],key)[key]
                            else:
                                self.nodeProb[key]=resultMulFac[key]

                            mulFac=key
                        if (len(self.nodeFactor)==1):
                            break
                    resultF= self.nodeProb[mulFac]
                else:
                    resultF= self.nodeProb[mulFac]
                    
                len_query=len(query_variables)+len(evidence_variables)
                # print('247:',resultF)
                # print('248',query_variables)
                alphaSum=0
                for re in resultF:
                    alphaSum+=re['prob']

                for re in resultF:
                    coun=0
                    for key in query_variables:
                        # print('252:',re)
                        if (re!={}):
                            if (re[key]==query_variables[key]):
                                for keyTwo in evidence_variables:
                                    if (re[keyTwo]==evidence_variables[keyTwo]):
                                        coun=coun+1
                                    if coun==len_query-1:
                                        # print('255:',re['prob'])
                                        result=re['prob']/alphaSum
                                        break
        f.close()
        return result

    def approx_inference(self, filename):
        result = 0
        f = open(filename, 'r')
        # YOUR CODE HERE


        f.close()
        return result

    def __extract_model(self, line):
        parts = line.split(';')
        node = parts[0]
        if parts[1] == '':
            parents = []
        else:
            parents = parts[1].split(',')
        domain = parts[2].split(',')
        shape = eval(parts[3])
        probabilities = np.array(eval(parts[4])).reshape(shape)
        return node, parents, domain, shape, probabilities

    def __extract_query(self, line):
        parts = line.split(';')

        # extract query variables
        query_variables = {}
        for item in parts[0].split(','):
            if item is None or item == '':
                continue
            lst = item.split('=')
            query_variables[lst[0]] = lst[1]

        # extract evidence variables
        evidence_variables = {}
        for item in parts[1].split(','):
            if item is None or item == '':
                continue
            lst = item.split('=')
            evidence_variables[lst[0]] = lst[1]
        return query_variables, evidence_variables
