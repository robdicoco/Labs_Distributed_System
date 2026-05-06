import socket
import threading

# The 'starter pistol'
start_signal = threading.Event()

def client_task(id):
    # Wait here until start_signal.set() is called
    start_signal.wait() 
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', 65432))
            s.sendall(f"Hello from Client {id}".encode())
            print(f"Client {id} sent data!")
    except Exception as e:
        print(f"Client {id} failed: {e}")

# 1. Create and prepare 10 threads
threads = []
for i in range(10):
    t = threading.Thread(target=client_task, args=(i,))
    threads.append(t)
    t.start()

print("All threads ready. Synchronizing start...")

# 2. Fire! (Releases all threads at once)
start_signal.set()

# 3. Clean up
for t in threads:
    t.join()