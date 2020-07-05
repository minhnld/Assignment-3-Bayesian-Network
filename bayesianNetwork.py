import numpy as np
from functools import reduce 
import copy 
import collections, functools, operator
import string
import random

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
        self.acronymDict={}
        self.acronymList=[]
        for line in lines:
            node, parents, domain, shape, probabilities = self.__extract_model(line)
            # YOUR CODE HERE
            acronymNode=copy.deepcopy(node[0])

            if acronymNode in self.acronymList:
                letter=string.ascii_uppercase+string.ascii_lowercase
                while acronymNode in self.acronymList:
                    acronymNode=random.choice(letter)

            self.acronymList.append(acronymNode)        
            self.acronymDict[node]=acronymNode

            self.nodesX.append(acronymNode)
            self.nodeDomain[self.acronymDict[node]]=domain
            self.nodeParent[self.acronymDict[node]]=parents


            sumParent=""
            for p in parents:
                sumParent+=self.acronymDict[p]
                
            self.nodeFactor.append(sumParent+self.acronymDict[node])

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
                            for k in self.nodeDomain[self.acronymDict[parents[i]]]:
                                for _ in range(mulShape_):
                                    index+=1
                                    probList[index][self.acronymDict[parents[i]]]=k
                    else:
                        while (index!=mulShape-1):
                            for d in self.nodeDomain[self.acronymDict[node]]:
                                index+=1
                                probList[index][self.acronymDict[node]]=d
                                probList[index]['prob']=prob[index]
            else:
                for k in range(shape):
                    probList[k][self.acronymDict[node]]=self.nodeDomain[self.acronymDict[node]][k]
                    probList[k]['prob']=prob[k]
            self.nodeProb[self.nodeFactor[-1:][0]]=probList
        f.close()



    def findShareVariableAndMerge(self,varA,varB):
        shareVars=set(varA).intersection(set(varB))
        mergeVars=set(varA).union(set(varB))
        return shareVars,mergeVars

    def setIntoString(self,sample):
        result=""
        for s in sample:
            result+=str(s)
        return result

    def varEliminate(self,factor,eliminateVar):
        remainingSet=list(set(factor).difference(set(eliminateVar)))
        factorProb=copy.deepcopy(self.nodeProb[factor])        
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
        
        result = dict(functools.reduce(operator.add, 
        map(collections.Counter, factorProb))) 
        resultList=[]
        for key in result:
            tempObj={}
            for reKey in recallDict[key]:
                tempObj[reKey]=recallDict[key][reKey]
            tempObj['prob']=result[key]
            resultList.append(tempObj)

        return {self.setIntoString(set(remainingSet)):resultList}    

    def varEliminateByEvidence(self,evidence):
        for noFa in self.nodeFactor:
            for ev in evidence:
                if self.acronymDict[ev] in noFa:
                    index=0
                    while (index!=len(self.nodeProb[noFa])):
                        if (self.nodeProb[noFa][index][self.acronymDict[ev]]!=evidence[ev]):
                            self.nodeProb[noFa].pop(index)
                        else:
                            index+=1

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
        # lenMulFactorAB=1
        # for me in mergeVars:
        #     lenMulFactorAB*=len(self.nodeDomain[me])

        # for _ in range(lenMulFactorAB):
        #     mulFactorAB.append({})
        # j=-1

        countShareVar=len(shareVars)
        for fA in SetShareInFacA:
            for fB in SetShareInFacB:
                countS=0
                for s in shareVars:
                    if (fA!={}) and (fB!={}):
                        if (fA[s]==fB[s]):
                            countS+=1
                            if countS==countShareVar:
                                tempObj={}
                                tempObj['prob']=fA['prob']*fB['prob']
                                countS=0
                                for m in mergeVars:
                                    try:
                                        tempObj[m]=fA[m]
                                    except KeyError:
                                        tempObj[m]=fB[m]
                                mulFactorAB.append(tempObj)

        return {self.setIntoString(mergeVars):mulFactorAB}

    def exact_inference(self, filename):
        result = 0
        f = open(filename, 'r')
        query_variables, evidence_variables = self.__extract_query(f.readline())
        # YOUR CODE HERE
        #Tim tap X cac node khong nam trong cau truy van (can loai bobo)
        if not(evidence_variables):
            for qu in query_variables:
                self.nodesX.remove(self.acronymDict[qu])
            for z in self.nodesX :
                FZ=[]
                for n in self.nodeFactor:
                    if z in n :
                        #tap cac nhan to F co chua bien Z
                        FZ.append(n)
                mulFac=FZ.pop()
                if (FZ):
                    while (FZ):

                        mulFacOne=FZ.pop()
                        resultMulFac=self.mulFactor(mulFac,mulFacOne)
                        
                        del self.nodeProb[mulFac]
                        self.nodeFactor.remove(mulFac)
                        del self.nodeProb[mulFacOne]
                        self.nodeFactor.remove(mulFacOne)

                        for key in resultMulFac:
                            self.nodeProb[key]=resultMulFac[key]
                            self.nodeFactor.append(key)
                            mulFac=key

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
                        del self.nodeProb[mulFac]
                        self.nodeFactor.remove(mulFac)
                        if (keyV in self.nodeProb):
                            self.nodeProb[keyV]=self.mulFactorOverlap(resultVarEli[keyV],self.nodeProb[keyV],keyV)[keyV]
                        else:
                            self.nodeProb[keyV]=resultVarEli[keyV]
                            self.nodeFactor.append(keyV)

            mulFac=self.nodeFactor.pop()
            resultF=None
            if (self.nodeFactor):
                while (self.nodeFactor):
                    mulFacOne=self.nodeFactor.pop()
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
            for re in resultF:
                coun=0
                for key in query_variables:
                    if (re[self.acronymDict[key]]==query_variables[key]):
                        coun=coun+1
                        if coun==len_query:
                            result=re['prob']
        else :
            patten=""
            for ev in evidence_variables:
                patten+=self.acronymDict[ev]
            for qu in query_variables:
                patten+=self.acronymDict[qu]

            if (patten in self.nodeFactor):
                len_query=len(query_variables)+len(evidence_variables)
                for re in self.nodeProb[patten]:
                    coun=0
                    for key in query_variables:
                        if (re!={}):
                            if (re[self.acronymDict[key]]==query_variables[key]):
                                for keyTwo in evidence_variables:
                                    if (re[self.acronymDict[keyTwo]]==evidence_variables[keyTwo]):
                                        coun=coun+1
                                    if coun==len_query-1:
                                        result=re['prob']
                                        break
            else:
                #Buoc 2 thu giam nhan to theo bang chung
                self.varEliminateByEvidence(evidence_variables)
                for ev in evidence_variables:
                    self.nodeDomain[self.acronymDict[ev]].remove(evidence_variables[ev])
                #buoc 3 xa ddinh bien can duoc loai bo
                for qu in query_variables:
                    self.nodesX.remove(self.acronymDict[qu])
                for ev in evidence_variables:
                    self.nodesX.remove(self.acronymDict[ev])

                #buoc 4 chay giai thuat loai bo bien
                for z in self.nodesX :
                    FZ=[]
                    for n in self.nodeFactor:
                        if z in n :
                            #tap cac nhan to F co chua bien Z
                            FZ.append(n)
                    mulFac=FZ.pop()
                    if (FZ):
                        while (FZ):

                            mulFacOne=FZ.pop()
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

                            del self.nodeProb[mulFac]
                            self.nodeFactor.remove(mulFac)

                            if (keyV in self.nodeProb):
                                self.nodeProb[keyV]=self.mulFactorOverlap(resultVarEli[keyV],self.nodeProb[keyV],keyV)[keyV]
                            else:
                                self.nodeProb[keyV]=resultVarEli[keyV]
                                self.nodeFactor.append(keyV)
    
                resultF=None
                if (len(self.nodeFactor)>1):
                    while (self.nodeFactor):
                        mulFac=self.nodeFactor.pop()
                        mulFacOne=self.nodeFactor.pop()

                        resultMulFac=self.mulFactor(mulFac,mulFacOne)
                        del self.nodeProb[mulFac]
                        del self.nodeProb[mulFacOne]

                        for key in resultMulFac:
                            if (key in self.nodeProb):
                                self.nodeProb[key]=self.mulFactorOverlap(resultMulFac[key],self.nodeProb[key],key)[key]
                                mulFac=key
                            else:
                                self.nodeProb[key]=resultMulFac[key]
                                self.nodeFactor.append(key)
                                mulFac=key
                        if (len(self.nodeFactor)==1):
                            break
                    resultF= self.nodeProb[mulFac]
                else:
                    mulFac=self.nodeFactor.pop()
                    resultF= self.nodeProb[mulFac]
                    
                len_query=len(query_variables)+len(evidence_variables)

                alphaSum=0
                for re in resultF:
                    alphaSum+=re['prob']

                for re in resultF:
                    coun=0
                    for key in query_variables:
                        if (re!={}):
                            if (re[self.acronymDict[key]]==query_variables[key]):
                                for keyTwo in evidence_variables:
                                    if (re[self.acronymDict[keyTwo]]==evidence_variables[keyTwo]):
                                        coun=coun+1
                                    if coun==len_query-1:
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
