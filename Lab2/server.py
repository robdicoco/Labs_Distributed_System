import socket
import threading

def handle_client(conn, addr):
    """Function to handle an individual client connection."""
    print(f"[NEW CONNECTION] {addr} connected.")
    try:
        with conn:
            data = conn.recv(1024).decode('utf-8')
            print(f"[{addr}] says: {data}")
            conn.sendall(b"Server received your data.")
    except Exception as e:
        print(f"[ERROR] {addr}: {e}")
    finally:
        print(f"[DISCONNECT] {addr} disconnected.")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 65432))
    server.listen()
    print("[LISTENING] Server is looking for connections...")

    try:
        while True:
            conn, addr = server.accept()
            # Create a thread for the new connection
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
    except KeyboardInterrupt:
        print("[STOPPING] Server shutting down.")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()