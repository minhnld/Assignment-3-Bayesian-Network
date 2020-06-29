import numpy as np
<<<<<<< Updated upstream
=======
from functools import reduce 
import copy 
import collections, functools, operator
>>>>>>> Stashed changes

class BayesianNetwork:
    def __init__(self, filename):
        f = open(filename, 'r') 
        N = int(f.readline())
        lines = f.readlines()
        self.nodesX=set()
        self.nodeDomain={}
        self.nodeParent={}
        for line in lines:
            node, parents, domain, shape, probabilities = self.__extract_model(line)
            # YOUR CODE HERE
            self.nodesX.add(node)
            self.nodeDomain[node]=domain
            self.nodeParent[node]=parents
            

                

            print(parents)
            print(probabilities[])



<<<<<<< Updated upstream
        
        f.close()
=======
    def varEliminate(self,factor,eliminateVar):
        remainingSet=list(set(factor).difference(set(eliminateVar)))
        factorProb=copy.deepcopy(self.nodeProb[factor])
        for f in factorProb:
            if eliminateVar in factor: del f[eliminateVar]
            mergeName=""
            mergeNameList={}
            for r in remainingSet:
                mergeName+=f[r]
                del f[r]
            f[mergeName]=f['prob']
            del f['prob']
        result = dict(functools.reduce(operator.add, 
        map(collections.Counter, factorProb))) 
        resultList=[]
        for key in result:
            tempObj={}
            for r in remainingSet:
                for d in self.nodeDomain[r]:
                    if d in key:
                        tempObj[r]=d
            tempObj['prob']=result[key]
            resultList.append(tempObj)

        print(factor)
        print(factorProb)
        print(result)
        print(resultList)
        return None
        
        
        # mulShapeFactor=1
        # for r in set(remainingSet):
        #     mulShapeFactor*=len(self.nodeDomain[r])

        # probList=[]
        # for i in range(mulShapeFactor):
        #     probList.append({})

        # len_remainingSet=len(remainingSet)-1
        # mulShape_=mulShapeFactor
        # i=-1

        # prob=[]
        # for m in mulShapeFactor:
        #     pro

        # while (mulShape_!=1):
        #     i+=1
        #     index=-1
        #     mulShape_=int(mulShape_/len(self.nodeDomain[r]))
        #     if (i<len_remainingSet):
        #         while (index!=mulShapeFactor-1):
        #             for k in self.nodeDomain[remainingSet[i]]:
        #                 for j in range(mulShape_):
        #                     index+=1
        #                     probList[index][remainingSet[i]]=k
        #     else:
        #         i+=1
        #         while (index!=mulShapeFactor-1):
        #             for d in self.nodeDomain[remainingSet[i]]:
        #                 index+=1
        #                 probList[index][remainingSet[i]]=d
        #                 probList[index]['prob']=prob[index]
        
        # self.nodeProb[self.nodeFactor[-1:][0]]=probList

    def mulFactor(self,facA,facB):
        shareVars,mergeVars=self.findShareVariableAndMerge(facA,facB)
        shareFactor=[]
        
        SetShareInFacA=self.nodeProb[facA]
        SetShareInFacB=self.nodeProb[facB]
        # i=-1 
        # for fShare in shareVars:
        #     i+=1
        #     if (i==0):
        #         SetShareInFacA=self.findProbWithVariable(self.nodeProb[facA],fShare)
        #         SetShareinFacB=self.findProbWithVariable(self.nodeProb[facB],fShare)
        #         print('fasfsa',SetShareInFacA)
        #         print('fdsad',SetShareinFacB)
        #     else:
        #         [SetShareInFacA.append(p) for p in self.findProbWithVariable(self.nodeProb[facA],fShare) if p not in SetShareInFacA ]
        #         [SetShareInFacB.append(p) for p in self.findProbWithVariable(self.nodeProb[facB],fShare) if p not in SetShareInFacB ]
                
        mulFactorAB=[]
        for i in range(len(SetShareInFacA) if (len(SetShareInFacA)>len(SetShareInFacB)) else len(SetShareInFacB)):
            mulFactorAB.append({})
        j=-1
        countShareVar=len(shareVars)
        for fA in SetShareInFacA:
            for fB in SetShareInFacB:
                countS=0
                for s in shareVars:
                    if fA[s]==fB[s]:
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
>>>>>>> Stashed changes

    def exact_inference(self, filename):
        result = 0
        f = open(filename, 'r')
        query_variables, evidence_variables = self.__extract_query(f.readline())
        # YOUR CODE HERE
        #Tim tap Z cac node khong nam trong cau truy van (can loai bobo)
        nodesZ=self.nodesX.difference(query_variables)
<<<<<<< Updated upstream

=======
        print(query_variables)
        FZ=[]
        for z in nodesZ :
            for n in self.nodeFactor:
                if z in n :
                    #tap cac nhan to F co chua bien Z
                    FZ.append(n)
            print(FZ)
>>>>>>> Stashed changes
        print(nodesZ)
        print(FZ)



        # testT=self.mulFactor('D','IDG')
        # for key in testT :
        #     self.nodeProb[key]=testT[key]

        # print(nodesZ)
        # self.varEliminate('DGI','D')
        # print(self.nodeProb['IDG'])
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
