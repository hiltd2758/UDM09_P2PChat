import socket
from Code.P2PChat.src.protocol import recv_message, pack_message

def _recv_loop(self, peer_addr: str):
    with self.lock:
        if peer_addr not in self.peers:
            return
        sock = self.peers[peer_addr].sock

    if sock is None:
        return

    while self.running:
        try:
            msg = recv_message(sock)
            if msg is None:
                break
            if msg == "":
                continue

            with self.lock:
                if peer_addr in self.peers:
                    self.peers[peer_addr].messages_recv += 1
                    
            self.on_message(peer_addr, msg)
            
        except socket.timeout:
            continue
        except OSError:
            break

    self._handle_disconnect(peer_addr)

def send_to(self, peer_addr: str, message: str) -> bool:
    with self.lock:
        if peer_addr not in self.peers:
            return False
        peer = self.peers[peer_addr]
        sock = peer.sock

    if sock is None:
        return False

    try:
        data = pack_message(message)
        sock.sendall(data)
        with self.lock:
            if peer_addr in self.peers:
                self.peers[peer_addr].messages_sent += 1
        return True
    except OSError:
        self._handle_disconnect(peer_addr)
        return False

def broadcast(self, message: str):
    with self.lock:
        targets = list(self.peers.keys())
        
    for addr in targets:
        self.send_to(addr, message)
