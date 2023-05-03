import threading
import socket
import pickle
import time
import sys

class Server:
    #id, num servers, num neighbors, lookup
    #routingTable: Will have eventually a given entry for all nodes in the network, will have neighbor and cost

    #construct the server
    def __init__(self, file):
      self.numServers, self.numNeighbors, self.lookup, self.routingTable, self.id = self.readConfig(file)
      self.ip, self.port = self.getIPPort()
      #create the socket to listen
      client_socket = self.create_socket(int(self.port))
      server_thread = threading.Thread(target=self.server, args=(client_socket,))
      server_thread.daemon = True
      server_thread.start()

      #create separate threads that will handle their own connection between this server and the remote port
      print(f'remote ports: {self.getRemotePorts()}')
      client_thread = threading.Thread(target=self.client, args=(self.getRemotePorts(),))
      client_thread.start()
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
        #if the value does not exist, just add it into the dictionary
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
      print('Routing Table  (source,dest)(neighbor,cost)\n-------------')
      for label in self.routingTable:
        print(label,'    ', self.routingTable[label])

    def getNeighbors(self):
      neighbors = []
      for label in self.routingTable:
        if(label[1] == self.routingTable[label][0]):
          neighbors.append(label[1])
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
          print(f'Connection from {client_address}')
          threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
      while True:
        data = client_socket.recv(1024)
        if not data:
          break

        recvd_dict = pickle.loads(data)

        #the data is going to be the routing tables
        print(f'Received Message: {recvd_dict}')
        #self.updateTable(data)
      client_socket.close()  

    def client(self, remote_ports):   
       while True:
          time.sleep(3)
          message_dict = self.routingTable
          message_pickle = pickle.dumps(message_dict)

          for remote_port in remote_ports:
            try:
              client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
              client_socket.connect(('localhost', remote_port))
              client_socket.sendall(message_pickle)
            except Exception as e:
              print(f'Error: could not connect to port: {remote_port}: {e}')
              continue
            client_socket.close()

#pull the file name from the command line
path = sys.argv[1]
#create the servers, for now just create all in one terminal for algorithm testing
server1 = Server(file=path)