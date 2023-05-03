import socket
import threading
import select
import sys

def server(port, stop_event):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', port))
    server_socket.listen(1)
    print(f"Server listening on port {port}")

    while not stop_event.is_set():
        try:
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")
            threading.Thread(target=handle_client, args=(client_socket,)).start()
        except socket.timeout:
            continue

    server_socket.close()

def handle_client(client_socket):
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        print("Received data:", data.decode('utf-8'))
        client_socket.sendall(data)
    client_socket.close()

def client(port, stop_event):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', port))

    while not stop_event.is_set():
        message = input("Enter message (or 'quit' to exit): ")
        if message.lower() == "quit":
            break

        client_socket.sendall(message.encode('utf-8'))

        data = client_socket.recv(1024)
        if not data:
            break
        print("Received echo:", data.decode('utf-8'))

    client_socket.close()

if __name__ == '__main__':
    port = 12345
    stop_event = threading.Event()

    server_thread = threading.Thread(target=server, args=(port, stop_event))
    server_thread.daemon = True
    server_thread.start()

    client_thread = threading.Thread(target=client, args=(port, stop_event))
    client_thread.start()
    client_thread.join()

    stop_event.set()
    server_thread.join()
