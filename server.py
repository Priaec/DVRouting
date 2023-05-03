import threading
import socket
import pickle
import json

def create_socket(port):
    chat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    chat_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    chat_socket.bind(('localhost', port))
    chat_socket.listen(1)
    return chat_socket

def server(chat_socket):
    while True:
        client_socket, client_address = chat_socket.accept()
        print(f"Connection from {client_address}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()

def handle_client(client_socket):
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        
        received_dict = pickle.loads(data)
        print(f"Received message: {received_dict}")
    client_socket.close()

def client(remote_port):
    while True:
        message = input("Enter message (or 'quit' to exit): ")
        if message.lower() == "quit":
            break

        message_dict = {
          (str(1), str(2)): (str(3), message)}

        message_dict[(str(2), str(2))] = (str(5), message)

        message_pickle = pickle.dumps(message_dict)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', remote_port))

        client_socket.sendall(message_pickle)
        client_socket.close()

if __name__ == '__main__':
    local_port = int(input("Enter local port: "))
    remote_port = int(input("Enter remote port: "))

    chat_socket = create_socket(local_port)

    server_thread = threading.Thread(target=server, args=(chat_socket,))
    server_thread.daemon = True
    server_thread.start()

    client_thread = threading.Thread(target=client, args=(remote_port,))
    client_thread.start()
    client_thread.join()

    server_thread.join()