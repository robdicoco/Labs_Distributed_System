import socket
import threading
import json
import time
import argparse
from typing import Dict, Optional, Tuple


class BullyNode:
    def __init__(self, node_id: int, peers: Dict[int, Tuple[str, int]]):
        self.node_id = node_id
        self.peers = peers  # {id: (host, port)}
        self.host, self.port = peers[node_id]

        self.alive = True
        self.coordinator_id: Optional[int] = None

        self.election_in_progress = False
        self.last_ok_received = False

        self.lock = threading.Lock()
        self.server_socket = None

    # =========================
    # Comunicação TCP
    # =========================
    def send_message(self, target_id: int, message: dict, timeout: float = 2.0) -> Optional[dict]:
        if target_id not in self.peers:
            return None

        host, port = self.peers[target_id]

        try:
            with socket.create_connection((host, port), timeout=timeout) as sock:
                sock.settimeout(timeout)
                sock.sendall((json.dumps(message) + "\n").encode())
                sock.shutdown(socket.SHUT_WR)

                data = b""
                while not data.endswith(b"\n"):
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    data += chunk

                raw = data.decode(errors="ignore").strip()
                if not raw:
                    return None

                return json.loads(raw)

        except Exception:
            return None
    
    def send_no_reply(self, target_id: int, message: dict, timeout: float = 2.0) -> bool:
        if target_id not in self.peers:
            return False

        host, port = self.peers[target_id]

        try:
            with socket.create_connection((host, port), timeout=timeout) as sock:
                sock.sendall((json.dumps(message) + "\n").encode())
                sock.shutdown(socket.SHUT_WR)
            return True
        except Exception:
            return False

    # =========================
    # Servidor TCP
    # =========================
    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(20)

        print(f"[P{self.node_id}] Escutando em {self.host}:{self.port}")

        while self.alive:
            try:
                conn, addr = self.server_socket.accept()
                threading.Thread(
                    target=self.handle_connection,
                    args=(conn, addr),
                    daemon=True
                ).start()
            except OSError:
                break
            except Exception as e:
                print(f"[P{self.node_id}] Erro no accept: {e}")

    def handle_connection(self, conn: socket.socket, addr):
        try:
            data = b""
            while not data.endswith(b"\n"):
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data += chunk

            raw = data.decode(errors="ignore").strip()

            # Conexão aberta e fechada sem enviar conteúdo útil
            if not raw:
                return

            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                print(f"[P{self.node_id}] Mensagem inválida recebida de {addr}: {raw!r}")
                return

            response = self.handle_message(message)

            if response is None:
                response = {"status": "NO_RESPONSE"}

            conn.sendall((json.dumps(response) + "\n").encode())

        except Exception as e:
            print(f"[P{self.node_id}] Erro ao tratar conexão de {addr}: {e}")
        finally:
            conn.close()

    # =========================
    # Protocolo Bully
    # =========================
    def handle_message(self, message: dict) -> dict:
        msg_type = message.get("type")
        sender = message.get("sender")

        if msg_type == "PING":
            print(f"[P{self.node_id}] Recebeu PING de P{sender}")
            return {"status": "OK", "type": "PONG", "sender": self.node_id}

        elif msg_type == "ELECTION":
            print(f"[P{self.node_id}] Recebeu ELECTION de P{sender} -> responde OK")

            # Como este processo tem ID maior e está ativo, ele responde OK
            # e inicia sua própria eleição, se ainda não estiver em andamento.
            threading.Thread(target=self.start_election, daemon=True).start()

            return {"status": "OK", "type": "OK", "sender": self.node_id}

        elif msg_type == "COORDINATOR":
            new_coord = message.get("coordinator")
            with self.lock:
                self.coordinator_id = new_coord
                self.election_in_progress = False

            print(f"[P{self.node_id}] Novo coordenador reconhecido: P{new_coord}")
            return {"status": "OK", "type": "ACK", "sender": self.node_id}

        elif msg_type == "STATUS":
            return {
                "status": "OK",
                "type": "STATUS_RESPONSE",
                "sender": self.node_id,
                "node_id": self.node_id,
                "coordinator_id": self.coordinator_id,
                "election_in_progress": self.election_in_progress
            }

        return {"status": "ERROR", "message": f"Mensagem desconhecida: {msg_type}"}

    def start_election(self):
        with self.lock:
            if self.election_in_progress:
                return
            self.election_in_progress = True
            self.last_ok_received = False

        print(f"\n[P{self.node_id}] Iniciando eleição...")

        higher_nodes = [nid for nid in self.peers if nid > self.node_id]
        got_ok = False

        for nid in sorted(higher_nodes):
            print(f"[P{self.node_id}] Enviando ELECTION para P{nid}")
            response = self.send_message(
                nid,
                {"type": "ELECTION", "sender": self.node_id},
                timeout=2.0
            )

            if response and response.get("type") == "OK":
                print(f"[P{self.node_id}] Recebeu OK de P{nid}")
                got_ok = True

        if not got_ok:
            self.become_coordinator()
            return

        print(f"[P{self.node_id}] Há processos maiores ativos. Aguardando anúncio do coordenador...")

        # Espera algum processo maior concluir a eleição
        wait_seconds = 5
        deadline = time.time() + wait_seconds

        while time.time() < deadline:
            with self.lock:
                if self.coordinator_id is not None and self.coordinator_id > self.node_id:
                    self.election_in_progress = False
                    print(f"[P{self.node_id}] Eleição concluída. Coordenador atual: P{self.coordinator_id}")
                    return
            time.sleep(0.5)

        print(f"[P{self.node_id}] Timeout aguardando coordenador. Reiniciando eleição...")
        with self.lock:
            self.election_in_progress = False

        time.sleep(1)
        self.start_election()

    def become_coordinator(self):
        with self.lock:
            self.coordinator_id = self.node_id
            self.election_in_progress = False

        print(f"\n*** [P{self.node_id}] SOU O NOVO COORDENADOR ***")

        for nid in sorted(self.peers):
            if nid == self.node_id:
                continue
            self.send_no_reply(
                nid,
                {
                    "type": "COORDINATOR",
                    "sender": self.node_id,
                    "coordinator": self.node_id
                },
                timeout=2.0
            )

    def monitor_coordinator(self):
        while self.alive:
            time.sleep(3)

            with self.lock:
                coord = self.coordinator_id

            # Se ainda não conhece coordenador, tenta eleger
            if coord is None:
                print(f"[P{self.node_id}] Não conheço coordenador. Tentando eleger...")
                self.start_election()
                continue

            # Se eu sou o coordenador, não preciso monitorar ninguém
            if coord == self.node_id:
                continue

            response = self.send_message(
                coord,
                {"type": "PING", "sender": self.node_id},
                timeout=2.0
            )

            if not response or response.get("type") != "PONG":
                print(f"\n[P{self.node_id}] Coordenador P{coord} não respondeu. Suspeita de falha.")
                self.start_election()

    # =========================
    # Inicialização
    # =========================
    def initial_discovery(self):
        """
        Ao iniciar, tenta descobrir se já existe coordenador.
        Se ninguém responder como coordenador, inicia eleição.
        """
        print(f"[P{self.node_id}] Descobrindo coordenador atual...")

        known_coords = []

        for nid in sorted(self.peers):
            if nid == self.node_id:
                continue

            response = self.send_message(
                nid,
                {"type": "STATUS", "sender": self.node_id},
                timeout=1.5
            )

            if response and response.get("status") == "OK":
                coord = response.get("coordinator_id")
                if coord is not None:
                    known_coords.append(coord)

        if known_coords:
            highest = max(known_coords)
            with self.lock:
                self.coordinator_id = highest
            print(f"[P{self.node_id}] Coordenador descoberto: P{highest}")
        else:
            print(f"[P{self.node_id}] Nenhum coordenador conhecido encontrado. Iniciando eleição.")
            time.sleep(1)
            self.start_election()

    def run(self):
        server_thread = threading.Thread(target=self.start_server, daemon=True)
        server_thread.start()

        # Dá tempo do servidor subir
        time.sleep(1)

        self.initial_discovery()

        monitor_thread = threading.Thread(target=self.monitor_coordinator, daemon=True)
        monitor_thread.start()

        self.command_loop()

    def command_loop(self):
        print(f"[P{self.node_id}] Comandos disponíveis: status, election, quit")
        while True:
            try:
                cmd = input(f"P{self.node_id}> ").strip().lower()

                if cmd == "status":
                    with self.lock:
                        print(
                            f"[P{self.node_id}] coordinator={self.coordinator_id}, "
                            f"election_in_progress={self.election_in_progress}"
                        )

                elif cmd == "election":
                    self.start_election()

                elif cmd == "quit":
                    print(f"[P{self.node_id}] Encerrando...")
                    self.alive = False
                    try:
                        self.server_socket.close()
                    except Exception:
                        pass
                    break

                elif cmd == "":
                    continue

                else:
                    print("Comandos: status, election, quit")

            except (KeyboardInterrupt, EOFError):
                print(f"\n[P{self.node_id}] Encerrando...")
                self.alive = False
                try:
                    self.server_socket.close()
                except Exception:
                    pass
                break


def build_default_peers(base_port: int = 5000, total_nodes: int = 5) -> Dict[int, Tuple[str, int]]:
    peers = {}
    for i in range(1, total_nodes + 1):
        peers[i] = ("127.0.0.1", base_port + i)
    return peers


def main():
    parser = argparse.ArgumentParser(description="Bully Algorithm com sockets TCP")
    parser.add_argument("--id", type=int, required=True, help="ID do nó")
    parser.add_argument("--nodes", type=int, default=5, help="Quantidade total de nós")
    parser.add_argument("--base-port", type=int, default=5000, help="Porta base")
    args = parser.parse_args()

    peers = build_default_peers(base_port=args.base_port, total_nodes=args.nodes)

    if args.id not in peers:
        raise ValueError(f"ID {args.id} inválido. IDs válidos: {list(peers.keys())}")

    node = BullyNode(node_id=args.id, peers=peers)
    node.run()


if __name__ == "__main__":
    main()