import numpy as np

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

            parentsList=parents.copy()
            probList=[]
            probListFinal=[]
            if parentsList:
                for d in self.nodeDomain[parentsList[0]]:
                    parentsList_=parentsList[1:].copy()+self.nodeDomain[node]
                    probListItem=[[d]]
                    while parentsList_:
                        try:
                            for d_ in self.nodeDomain[parentsList_[0]]:
                                probListItem[0]=probListItem[0]+[d_]
                                probList.append(probListItem[0])
                            parentsList_=parentsList_[1:]
                        except KeyError:
                            for fa in probList:
                                probListFinal.append(fa+[parentsList_[0]])
                            parentsList_=parentsList_[1:]
            print(probListFinal)
            print(probabilities)

        f.close()

    def exact_inference(self, filename):
        result = 0
        f = open(filename, 'r')
        query_variables, evidence_variables = self.__extract_query(f.readline())
        # YOUR CODE HERE
        #Tim tap Z cac node khong nam trong cau truy van (can loai bobo)
        nodesZ=self.nodesX.difference(query_variables)

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
