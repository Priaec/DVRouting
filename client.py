import socket
import sys
import threading

PEER_PORT = 12345
BUFFER_SIZE = 1024

class PeerClient:
    def __init__(self, servers):
        self.servers = servers
        self.connections = []

    def connect_to_servers(self):
        for server in self.servers:
            try:
                conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                conn.connect((server, PEER_PORT))
                self.connections.append(conn)
                print(f"Connected to {server}:{PEER_PORT}")

                threading.Thread(target=self.receive_from_server, args=(conn,)).start()
            except Exception as e:
                print(f"Failed to connect to {server}:{PEER_PORT} - {e}")

    def receive_from_server(self, conn):
        try:
            while True:
                data = conn.recv(BUFFER_SIZE)
                if data:
                    print(f"Received: {data.decode('utf-8')}")
                else:
                    break
        finally:
            print(f"Disconnected from {conn.getpeername()}")
            self.connections.remove(conn)
            conn.close()

    def send_to_servers(self):
        while True:
            msg = input("Enter message: ")
            for conn in self.connections:
                try:
                    conn.sendall(msg.encode('utf-8'))
                except Exception as e:
                    print(f"Failed to send message to {conn.getpeername()} - {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python client.py <server1_ip> <server2_ip> ...")
        sys.exit(1)

    servers = sys.argv[1:]
    client = PeerClient(servers)
    client.connect_to_servers()
    client.send_to_servers()
    #192.168.86.24