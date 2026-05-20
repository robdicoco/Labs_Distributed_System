import socket

HOST = '0.0.0.0'
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("Servidor aguardando conexão...")

conn, addr = server.accept()
print(f"Conectado por {addr}")

data = conn.recv(1024)
print(f"Recebido: {data.decode()}")

conn.sendall(b"Mensagem recebida com sucesso!")
conn.close()
