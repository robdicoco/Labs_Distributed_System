import os
import socket
import time

# Local: 127.0.0.1 (default). Docker: SERVER_HOST=server python client/client.py
HOST = os.environ.get("SERVER_HOST", "127.0.0.1")
PORT = 5000

time.sleep(3)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
print("Client conectado ao servidor!")

time.sleep(3)
client.sendall(b"Ola servidor!")

print("Mensagem enviada para o servidor!")
data = client.recv(1024)

time.sleep(3)
print(f"Resposta: {data.decode()}")
client.close()
print("Client desconectado do servidor!")
