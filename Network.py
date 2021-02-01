class Node:

    edges = []
    DVs = [ ]

    def __init__(self, id):
        self.id = str(id)
        self.RT = []
        self.adjecencyList = []
        self.updated = False
        self.dvCount = 0

    def __str__(self):
        return "Node " + self.id

    # rich comparison overload
    def __lt__(self, other):
        return int(self.id) < int(other.id)

    def printRT(self):
        out_string = ''
        for row in self.RT:
            out_string += ( f'{str(row.get("node")):>5}' + '|' +
                   f'{str(row.get("cost")):>6}' + '|' +
                   f'{str(row.get("nextHop")):>7}' + '\n'  )
        return out_string

    def appendEntry(self, dest, cost, nextHop):
        self.RT.append({"node": int(dest), "cost": int(cost), "nextHop": int(nextHop)})

    def appendAdjacency(self, dest):
        self.adjecencyList.append(int(dest))

    def generateDVs(self):
        for neighbor in self.adjecencyList:
            self.DVs.append( {"source": self.id, "dest": neighbor, "DVs": self.RT[:]} )

    def handleDVs(self):

        if self.DVs: # check to see if the buffer is empty

            for packet in self.DVs[:]: # changes to the packet will occur to old and new lists

                if str(self.id) == str(packet["dest"]):

                    self.searchRT(packet["DVs"], packet["source"])
                    self.DVs.remove(packet)
                    self.dvCount += 1

    def searchRT(self, table, sender):

        cost = 0

        for row in self.RT:
            
            if str(row["node"]) == str(sender):
                cost = int(row["cost"])
                break
        
        # Compare my DV to the RT
        for entry in table:
            found = False
            for line in self.RT:
                
                # if im in the list
                if str(entry["node"]) == str(self.id):
                    found = True
                    continue
                # if there is another instance of this node
                if str(entry["node"]) == str(line["node"]):
                    found = True

                    if (int(entry["cost"]) + int(cost)) < line["cost"]:
                        self.updateRT(line["node"], (int(entry["cost"]) + int(cost)), sender)
                        self.updated = True
                        found = True

                    elif (int(entry["cost"]) + int(cost)) == line["cost"]:
                        self.updateRT(line["node"], (int(entry["cost"]) + int(cost)), sender)
                        found = True
            
            # else: add the route to the table
            if not found:
                self.appendEntry(entry["node"], (entry["cost"] + cost), sender)
                self.updated = True

    def updateRT(self, node, cost, nextHop):
        for entry in self.RT:
            if str(entry["node"]) == str(node):
                entry["cost"] = cost
                entry["nextHop"] = nextHop

    def isUpdated(self):
        return self.updated

    def receivePacket(self, src, dest, nodes):
        if str(self.id) == str(dest):
            self.edges.append(self.id)
            return
        else:
            for entry in self.RT:
                if str(entry["node"]) == str(dest):
                    self.forwardPacket(src, dest, int(entry["nextHop"]), nodes)
                    self.edges.append(self.id)

    def forwardPacket(self, src, dest, nextHop, nodes):
        for node in nodes:
            if str(node.id) == str(nextHop):
                node.receivePacket(src, dest, nodes)

class Network:
    nodeList = []
    lastNode = []

    def __init__(self, fileName, fileData ):
        self.numRounds = 0
        self.fileName = fileName
        self.fileData = fileData
        self.convergence = False
        self.roundNumber = 0
        self.route = ""

    def sendPacket(self, src, dest):
        nodes = self.nodeList[:] # changes the contents of the list that both the
                                 # original list and new list
        self.nodeList[src].receivePacket(src, dest, nodes)

    def getLastConverged(self):
    #keep track of last updated node
        last = self.nodeList[0]
        for node in self.nodeList:
            if node.updated:
                last = node
        return last.id

    def returnRoutes(self):
        length = len(self.nodeList[0].edges)
        route = ""
        for index in range(0, length):
            if index != length-1:
                route += "Node {0} to ".format(self.nodeList[0].edges[(length - 1) - index])
            else:
                route += "Node {0}".format(self.nodeList[0].edges[(length - 1) - index] +'\n\n')

        return route

    def createNodes(self):
        nodes = []

        for line in self.fileData:
            src = int(line["node1"])
            dest = int(line["node2"])
            cost = int(line["cost"])

            if src not in nodes:
                newNode = Node(src)
                newNode.appendEntry(dest, cost, dest)
                newNode.appendAdjacency(dest)
                self.nodeList.append(newNode)
                nodes.append(src)

            elif src in nodes:
                for index, r in enumerate(self.nodeList):
                    if int(r.id) == src:
                        self.nodeList[index].appendEntry(dest, cost, dest)
                        self.nodeList[index].appendAdjacency(dest)

            if dest not in nodes:
                newNode = Node(dest)
                newNode.appendEntry(src, cost, src)
                newNode.appendAdjacency(src)

                self.nodeList.append(newNode)
                nodes.append(dest)

            elif dest in nodes:
                for index, r in enumerate(self.nodeList):
                    if int(r.id) == dest:
                        self.nodeList[index].appendEntry(src, cost, src)
                        self.nodeList[index].appendAdjacency(src)

    def beginRounds(self, rounds):
        self.nodeList.sort ( )
        round = 0
        while round < rounds:
            if not self.convergence:
                for node in self.nodeList:
                    node.generateDVs()

                for node in self.nodeList:
                    node.handleDVs()

                update = False
                for node in self.nodeList:
                    if node.isUpdated():
                        update = True

                if update:
                    self.convergence = False
                else:
                    self.convergence = True

                self.lastNode.append(self.getLastConverged())

                for node in self.nodeList:
                    node.updated = False

                round += 1

            else:
                print("Only needed " + str(round) + " rounds to converge")
                break

        self.numRounds = round

        total = 0
        for node in self.nodeList:
            total += node.dvCount

        if not self.convergence:
            print("Error: Insufficient Rounds to convergence.")

        else:
            if self.fileName == "topology1.txt":
                self.route = "\nNode 0 receives packet for node 3 via, "
                self.sendPacket(src = 0, dest = 3)

            elif self.fileName == "topology2.txt":
                self.route = "\nNode 0 receives packet for node 7 via, "

                self.sendPacket(src = 0, dest = 7)

            elif self.fileName == "topology3.txt":
                self.route = "\nNode 0 receives packet for node 23 via, "
                self.sendPacket(src = 0, dest = 23)

        with open ( 'outputfile.txt' , 'a' ) as outFile :
            outFile.write( self.fileName + "\n"
                           + "Then number of rounds till covergence is "
                           + str(self.numRounds) + ".\n"
                           + "The total Distance Vector Sent is "
                           + str(total) + ", and the  last converged node is "
                           + str(self.lastNode[len(self.lastNode) - 2]) + ".")

    def printResult( self ):
        with open('outputfile.txt', 'a') as outFile:
            for node in self.nodeList :
                outFile.write ( "\nNode " + str ( node.id ) + '\n' )
                outFile.write ( "Dest | cost | source\n" )
                outFile.write( node.printRT ( ))
