import threading
import socket
import pickle
import time
import sys

class Server:
    #id, num servers, num neighbors, lookup
    #routingTable: Will have eventually a given entry for all nodes in the network, will have neighbor and cost
    #routing Table
    #(src, dst) => cost
 
    #construct the server
    def __init__(self, file, interval):
      self.numServers, self.numNeighbors, self.lookup, self.routingTable, self.id = self.readConfig(file)
      self.ip, self.port = self.getIPPort()
      self.packets = 0
      #interval between table sends
      self.interval = int(interval)
      self.remotePorts = self.getRemotePorts()
      #create the socket to listen
      client_socket = self.create_socket(int(self.port))
      server_thread = threading.Thread(target=self.server, args=(client_socket,))
      server_thread.daemon = True
      server_thread.start()

      #create separate threads that will handle their own connection between this server and the remote port
      print(f'remote ports: {self.getRemotePorts()}')
      #preserve a shared datastructure with the outside thread
      client_thread = threading.Thread(target=self.client, args=(self.interval,))
      client_thread.start()

      #listen for any arguments
      while True:
        command = input('Enter a command: ').lower()
        args = command.split(' ')
        print(f'Command: {args}')
        if(args[0] == 'update'):
          src = args[1]
          dst = args[2]
          cost = int(args[3])
          #look through my routing table and pull the value with this information
          if((src, dst) in self.routingTable):
            entry = self.routingTable[(src,dst)]
            print(f'Updating {(src, dst)} to {cost}')
            self.routingTable[(src, dst)] = cost
            self.routingTable[(dst, src)] = cost
          
        if(command == 'd' or command == 'display'):
          self.prettyPrintTable()

        if(command == 'step'):
          print(f'Sending Table id: {self.id}')
          self.sendTables()

        if(command == 'packets' or command == 'p'):
          print(f'Packets since last check: {str(self.packets)}')
          self.packets = 0

        if(command == 'crash' or command == 'c'):
          break

        if(args[0] == 'disable'):
          key = args[1]
          if(key not in self.lookup):
            print(f'Could not find server with ID: {key}')
            break
          self.lookup.pop(key)
          print(f'remote ports: {self.getRemotePorts()}')
          #delete all values with given serverID
          for label in list(self.routingTable):
            print(f"label: {label}")
            dst = label[1]
            src = label[0]
            if(dst == key or src == key):
              self.routingTable.pop(label)

        if(command == 'exit'):
          break
                  
      client_thread.join()
      server_thread.join()
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
            table[key] = int(arguments[2])
        #cost to itself is 0
        table[(arguments[0], arguments[0])] = 0
      return numServers, numNeighbors, lookup, table, id
    
    def recieveTable(self, table):
      server_IDs = list(self.lookup.keys())
      #for label in list(table.keys()):
      #  if label[0] not in server_IDs or label[1] not in server_IDs:
      #    del table[label]
      
      #if i have not seen this key in my table, then add it in, otherwise do nothing
      for label in table:
        if (label not in self.routingTable) and (label[0] in self.getNeighbors()):
            self.routingTable[label] = table[label]
      self.updateTable(table)
      return

    def updateTable(self, table):
      #compare results with given entries
      for label in table:
        #entries are denotes as pair keys
        #if the value does not exist, just add it into the dictionary
        cost = table[label]
        #compare this result with mine
        currentCost = self.routingTable.get(label)
        if(currentCost == None):
          continue
        if((cost < currentCost) or (label not in self.routingTable)):
          self.routingTable[label] = cost
      #self.prettyPrintTable()
      self.refactorTable()
      return
    
    def sendTable(self):
      #send table to nearest neighbors
      #send the keys that are respective to me, i.e. keys that start with 1 (id)
      result = {}
      for label in self.routingTable:
        if(label[0] != self.id):
          return
        result[label] = self.routingTable[label]
      return result
    
    #check all the values
    def refactorTable(self):
      for label in self.routingTable:
        src = label[0]
        dst = label[1]
        #only want to consider out entries to update, not anyone elses
        if src != self.id:
          continue
        #If we are visiting the index with 0 value, just skip over
        if (src == dst):
          continue
        #for our entries, we need to check for a new min cost
        currCost = self.routingTable[label]
        newCosts = []
        print(f'Neighbors: {self.getNeighbors()}')
        for n in self.getNeighbors():
          nCost = self.routingTable[(src, n)] 
          dCost = self.routingTable.get((n, dst))
          if(dCost == None):
            dCost = sys.maxsize
          newCost = nCost + dCost
          #print(f'{newCost} = {nCost} + {dCost}')
          newCosts.append(newCost)
          #fill the newCosts, take the minimum, and compare with current and update
        if(len(newCosts) <= 0):
          continue
        minCost = min(newCosts)
        if(minCost < currCost):
          self.routingTable[label] = minCost
        #otherwise if the minimum is not smaller than existing, just continue
        return

    #return the ip and port of the current server
    def getIPPort(self):
       for label in self.lookup:
          if(label == self.id):
             return self.lookup[label]

    def getDetails(self):
      print('My ID:', self.id)
      print('Num Servers:', self.numServers)
      print('Num Neighbors:', self.numNeighbors)
      #print('Lookup IP and Port:', self.lookup)
      self.printLookup()
      self.prettyPrintTable()

    def printLookup(self):
      for label in self.lookup:
        print(label, '   ', self.lookup[label], self.lookup[label][1])

    def prettyPrintTable(self):
      print('Routing Table  (src, dst) -> cost\n_______________________')
      for label in self.routingTable:
        print('| ', label[0], ' | ', label[1],' |   ', self.routingTable[label], '   |')
      print('-----------------------')

    def getNeighbors(self):
      neighbors = list(self.lookup.keys())
      return neighbors
    
    def getRemotePorts(self):
      result = [self.lookup[label][1] for label in self.lookup if self.id not in label]
      result = [int(port) for port in result]
      return result

    #socket functions
    def create_socket(self, port):
      chat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      chat_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      chat_socket.bind(('localhost', port))
      chat_socket.listen(5)
      print(f"Server Listening on port {port}")
      return chat_socket

    def server(self, chat_socket):
       while True:
          client_socket, client_address = chat_socket.accept()
          #print(f'Connection from {client_address}')
          threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
      while True:
        data = client_socket.recv(1024)
        if not data:
          break

        recvd_dict = pickle.loads(data)
        self.recieveTable(recvd_dict)
        self.packets += 1
      client_socket.close()  

    def client(self, interval):   
        while True:
          time.sleep(interval)
          message_dict = self.routingTable
          message_pickle = pickle.dumps(message_dict)

          #print(f'list of my remote ports: {self.getRemotePorts()}')
          self.sendTables()

    def sendTables(self):
      for remote_port in self.getRemotePorts():
        try:
          client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          client_socket.connect(('localhost', remote_port))
          client_socket.sendall(pickle.dumps(self.routingTable))
        except Exception as e:
          print(f'Error: could not connect to port: {remote_port}: {e}')
          continue
        client_socket.close()      

#pull the file name from the command line
path = sys.argv[1]
interval = sys.argv[2]
#create the servers, for now just create all in one terminal for algorithm testing
server1 = Server(file=path, interval=interval)