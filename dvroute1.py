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
      return

    def updateTable(self, table):
      #compare results with given entries
      for entry in table:
        #entries are denotes as pair keys
        neighbor, cost = table[entry]
        #compare this result with mine
        currentNeighbor, currentCost = self.routingTable[entry]
        if(cost < currentCost):
          self.routingTable[entry] = (neighbor, cost)
      return
    
    def sendTable(self, table):
      return
    
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
        
#pull the file name from the command line
path = sys.argv[1]
print("file:", path)
#create the server
myServer = Server(path)
#every 10 seconds, send the routing table updates
while True:
  time.sleep(5)