import numpy as np
from functools import reduce 
class BayesianNetwork:
    def __init__(self, filename):
        f = open(filename, 'r') 
        N = int(f.readline())
        lines = f.readlines()
        self.nodesX=set()
        self.nodeDomain={}
        self.nodeParent={}
        self.nodeProb={}
        self.nodeFactor=[]
        for line in lines:
            node, parents, domain, shape, probabilities = self.__extract_model(line)
            # YOUR CODE HERE
            self.nodesX.add(node)
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
        print(self.nodeProb)
        f.close()

    def findFactorWithVariable(self,factors,var):
        return list(filter(lambda factor: var in factor,factors))


    def exact_inference(self, filename):
        result = 0
        f = open(filename, 'r')
        query_variables, evidence_variables = self.__extract_query(f.readline())
        # YOUR CODE HERE
        #Tim tap Z cac node khong nam trong cau truy van (can loai bobo)
        nodesZ=self.nodesX.difference(query_variables)
        print(self.findFactorWithVariable(self.nodeFactor,'D'))

        print(nodesZ)


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
