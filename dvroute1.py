import sys
import time

class Server:
    #id, num servers, num neighbors, lookup
    #routingTable: Will have eventually a given entry for all nodes in the network, will have neighbor and cost

    #construct the server
    def __init__(self, file):
      self.numServers, self.numNeighbors, self.lookup, self.routingTable, self.id = self.readConfig(file)
      self.getDetails()
      return
    
    #read initialization file
    def readConfig(self, file):
      # Open the file in read mode
      with open(file, 'r') as file:
        table = {}
        lookup = {}
        for i, line in enumerate(file):
          line = line.strip()
          arguments = line.split()
          if(i == 0):
            numServers = int(arguments[0])
            continue       
          elif(i == 1):
            numNeighbors = int(arguments[0])
            continue
          elif('.' in arguments[1]):
            lookup[arguments[0]] = (arguments[1], arguments[2])
          else:
            id = arguments[0]
            key = (arguments[0], arguments[1])
            table[key] = (arguments[1],int(arguments[2]))
      return numServers, numNeighbors, lookup, table, id
    
    def recieveTable(self, table):
      #if i have not seen this key in my table, then add it in, otherwise do nothing
      for label in table:
        if label not in self.routingTable:
          self.routingTable[label] = table[label]
      return self.updateTable(table)

    def updateTable(self, table):
      #compare results with given entries
      for label in table:
        #entries are denotes as pair keys
        neighbor, cost = table[label]
        #compare this result with mine
        print(self.routingTable[label])
        currentNeighbor, currentCost = self.routingTable[label]
        if((cost < currentCost) or (label not in self.routingTable)):
          self.routingTable[label] = (neighbor, cost)
      return self.prettyPrintTable()
    
    def sendTable(self):
      #send table to nearest neighbors
      #send the keys that are respective to me, i.e. keys that start with 1 (id)
      result = {}
      for label in self.routingTable:
        if(label[0] != self.id):
          return
        result[label] = self.routingTable[label]
      return result
    
    def getDetails(self):
      print('My ID:', self.id)
      print('Num Servers:', self.numServers)
      print('Num Neighbors:', self.numNeighbors)
      #print('Lookup IP and Port:', self.lookup)
      self.printLookup()
      self.prettyPrintTable()

    def printLookup(self):
      for label in self.lookup:
        print(label, '   ', self.lookup[label])

    def prettyPrintTable(self):
      print('Routing Table  (source,dest)(neighbor,cost)\n-------------')
      for label in self.routingTable:
        print(label,'    ', self.routingTable[label])

    def getNeighbors(self):
      neighbors = []
      for label in self.routingTable:
        if(label[1] == self.routingTable[label][0]):
          neighbors.append(label[1])
      return neighbors

#pull the file name from the command line
path = sys.argv[1]
print("file:", path)
#create the servers, for now just create all in one terminal for algorithm testing
server = Server(file=path)
server2 = Server(file='topology2.txt')
#every 10 seconds, send the routing table updates
while True:
  time.sleep(2)
  for neighbor in server.getNeighbors():
    send = server.sendTable()
    print(send)
    #send server2 table to server 1
    send2 = server2.sendTable()
    server.recieveTable(send2)