
class realNode:
    """
    realNode objects contain:
     1) Name: the node's name.
     2) Running Score: (reassigned from the previous node's in edges dict)...how??
     3) inNodes: A dictionary of the nodes going in and the score coming from that node
     4) outNodes: dictionary of the nodes going out and the score that each of those
       """
    def __init__(self, name, acceptedScore, inNodes, outNodes):
        self.name = name
        self.acceptedScore = acceptedScore
        self.inNodes = inNodes
        self.outNodes = outNodes

class DAG(realNode):
    def __init__(self, inAdjList):
        """DAG objects receive an adjacency list from Rosalind at initialization."""
        self.inAdjList = inAdjList
        self.nodesDict = {}
        self.aftersDict = {}

    def parseAdjacenciesToDict(self):
        """
        This function takes the DAG's adjacency list and parses it.
        It returns a dictionary of node name : realNode (name to be changed) objects.
        This dictionary (nodesDict), is saved to the instance of the DAG class for easier internal use.
        """
        nodesDict = {}
        for line in self.inAdjList:
            #print("line", line)
            line = line.rstrip()

            splitAdjacency = line.split("->")

            parent = splitAdjacency[0]
            child = splitAdjacency[1].split(":")[0]
            weight = splitAdjacency[1].split(":")[1]

            #both parent and child are new
            if parent not in nodesDict.keys() and child not in nodesDict.keys():
                #print("Nonfunctional", parent)
                #build the child and parent nodes
                newParentNode = realNode(parent, acceptedScore = 0, inNodes = {}, outNodes = {child:weight})
                newChildNode = realNode(child, acceptedScore = 0, inNodes = {parent: None}, outNodes = {})

                nodesDict[parent] = newParentNode
                nodesDict[child] = newChildNode
            #only child is new
            if parent in nodesDict.keys() and child not in nodesDict.keys():
                #build only the child node; update the parent
                builtParentNode = nodesDict[parent]
                builtParentNode.outNodes[child] = weight

                newChildNode = realNode(child, acceptedScore=0, inNodes={parent: None}, outNodes={})
                nodesDict[child] = newChildNode
            #only parent is new
            if parent not in nodesDict.keys() and child in nodesDict.keys():
                #build only the parent node; update the child
                newParentNode = realNode(parent, acceptedScore=0, inNodes={}, outNodes={child: weight})
                nodesDict[parent] = newParentNode
                builtChildNode = nodesDict[child]
                builtChildNode.inNodes[parent] = None

            # #neither parent nor child is new (not sure this works)
            # if child in nodesDict.keys() and parent in nodesDict.keys():
            #     #update both child and parent
            #     builtParentNode = nodesDict[parent]
            #     builtParentNode.outNodes[child] = weight
            #     builtChildNode = nodesDict[child]
            #     builtChildNode.inNodes[parent] = None
        self.nodesDict = nodesDict
        print(len(nodesDict))
    #dont use this thing
    def getNodesAfterStart(self, startNode, endNode):
        """This function consolidates all of the nodes from the start node specified in Rosalind to
        a new dictionary that is actually used to from the topological order."""
        afterCandidatesNodeDict = {startNode:self.nodesDict[startNode]}
        afterCandidates = [startNode]
        while len(afterCandidates) != 0:
            for candidate in afterCandidates:
                afterCandidates.remove(candidate)
                nextCandidates = self.nodesDict[candidate].outNodes
                for nextCandidate in nextCandidates:
                    afterCandidatesNodeDict[nextCandidate] = self.nodesDict[nextCandidate]

        #print("afterS", afterCandidatesNodeDict.keys())
        afterCandidatesNodeDict[endNode] = self.nodesDict[endNode]
        self.aftersDict = afterCandidatesNodeDict
        #return afterCandidatesNodeDict
    def solveTopologicalOrder(self, startNode):
        """
        WORKS
        The below function solves the actual topological order.
        Update 11/7: It starts by finding the start node from the nodesDictionary.
        1) This start node is to find the start node object and setting its inNodes dict. to a none:none pair. Otherwise, the algorithm fails
        2) Also, you can use a non-Rosalind adjacency list in this function, as long as you format it right.

            1) First, it selects a candidate from the candidates list and removes it from said list.
            2) It asks if that candidate has any inEdges left (by querying the values of its inNodes dictionary)
            If it doesn't ->
                It gathers its outNodes from its outNodes dictionary and adds them to the candidates list
                It updates all of the outNodes' running scores (the one in the inNodes dict) for the given running score using the sum of the weight of the edge and the score of the resolved node.
            If it does ->
                The process continues

            At the end, it returns the topological order.
        """
        #startNode = ""
        for nodeName, nodeObject in self.nodesDict.items():
            intos = nodeObject.inNodes
            if intos == {}:
                startNode = nodeName
                nodeObject.inNodes[None] = True
            outs = nodeObject.outNodes
            if outs == {}:
                endNode = nodeName
                #nodeObject.outNodes[None] = True

        topoOrder = [startNode]
        candidatesList = []
        for startingCandidates in self.nodesDict[startNode].outNodes.keys():
            candidatesList.append(startingCandidates)
        while len(candidatesList) != 0:
            for candidateName in candidatesList:
                #remove the candidate from the list
                topoOrder.append(candidateName)
                candidatesList.remove(candidateName)

                #travel to all of the out nodes and set the scores pertaining to the candidate-out node to followed
                candidateObjectOuts = self.nodesDict[candidateName].outNodes.keys()
                for outNode in candidateObjectOuts:
                    self.nodesDict[outNode].inNodes[candidateName] = True
                #check each of the out node's in edges are followed. if so, add that out node to the candidates list
                #otherwise, move on to a different candidate
                for outNode in candidateObjectOuts:
                    if all(list(self.nodesDict[outNode].inNodes.values())) == True:
                        candidatesList.append(outNode)

        print(topoOrder)
        return topoOrder

    def backtrackScore(self, topoOrder, startNode, sinkNode):
        """
        This function receives a topological order and evaluates the longest path. 
        It does this by calling on the nodes dictionary that is part of the class and traveling from node to node
        picking the proper weight from the proper edge. 
        1) for the current node, it calls its inNodes dictionary
        if the current node =! start node
        2) for each of the inEdges, it adds the score of the preeceeding node (via object = nodeDict[node].inNodes.score)
        *To-Do: Not sure how to score the starting node yet, will be 0 for now.*  
        """""
        #setting the score of the first node to 0 (for now???)
        longestPathScore = 0
        longestPathReal = []
        #startNodeIndex = topoOrder.index(startNode)
        self.nodesDict[startNode].acceptedScore = 0

        for currentNode in topoOrder:
            if currentNode == startNode:
                currentInNodes = self.nodesDict[currentNode].inNodes
                for inNode in currentInNodes:
                    currentInNodes[inNode] = 0
            if currentNode != startNode:
                currentNodeObj = self.nodesDict[currentNode]
                currentInNodes = self.nodesDict[currentNode].inNodes
                #dictionary contains inNodes as keys and the sum of the weight going between it and the previous node, and the score
                inNodeRunningScores = {}
                for inNode in currentInNodes:
                    runningScore = self.nodesDict[inNode].acceptedScore + int(self.nodesDict[inNode].outNodes[currentNode])
                    #print("runningScore", runningScore)
                    inNodeRunningScores[inNode] = runningScore
                #picking the highest running score and assigning that score to the accepted score of the current node

                maxRunningScore = max(inNodeRunningScores.values())
                #maxInNode = max(inNodeRunningScores, key = inNodeRunningScores.get())
                maxInNode = max(inNodeRunningScores, key = lambda x: inNodeRunningScores[x])
                longestPathReal.append(str(maxInNode))
                currentNodeObj.acceptedScore = maxRunningScore
                longestPathScore = maxRunningScore
        formattedPath = str(startNode) + "->"
        #setPath = set(longestPathReal)
        #longestPathReal.remove(startNode)
        for item in longestPathReal:
            formattedPath += str(item) + "->"
        formattedPath += str(sinkNode)


        return longestPathScore, formattedPath

inAdjacencyListRos = open("rosalind_ba5d.txt", "r")
rosalindAdjsList = []
for line in inAdjacencyListRos:
    line = line.rstrip()
    rosalindAdjsList.append(line)

"""Main. Default file is one of the Rosalind ones"""
def main(rosalindFile = "rosalind_ba5d.txt"):
    """Rosalind file is parsed here."""
    inAdjacencyListRos = open(rosalindFile, "r")
    rosalindAdjsList = []
    counter = 1
    thisStartNode = ""
    thisEndNode = ""

    for line in inAdjacencyListRos:
        line = line.rstrip()
        if counter == 1:
            thisStartNode = line

        if counter == 2:
            thisEndNode = line

        elif counter > 2:
            rosalindAdjsList.append(line)

        counter += 1

    thisDAG = DAG(rosalindAdjsList)
    thisDAG.parseAdjacenciesToDict()
    thisDAG.getNodesAfterStart(thisStartNode, thisEndNode)
    thisTopoOrder = thisDAG.solveTopologicalOrder(thisStartNode)
    longestPathScore, formattedPath = thisDAG.backtrackScore(thisTopoOrder, thisStartNode, thisEndNode)

    print("Longest Path Score is : ", longestPathScore)
    print("Longest Path is: ", formattedPath)


    with open("DAGOut.txt", "a") as f:
        print("Longest Path Score is : ", longestPathScore, file = f)
        print("Longest Path is: ", formattedPath, file= f)


if __name__ == "__main__":
    main()






































