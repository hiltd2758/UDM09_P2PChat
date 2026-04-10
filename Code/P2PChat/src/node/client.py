import socket
import threading
from Code.P2PChat.src.protocol import PeerStatus, CONNECT_TIMEOUT, RECV_TIMEOUT
from nodeBase import PeerInfo

def connect_peer(self, host: str, port: int):
    peer_addr = f"{host}:{port}"
    
    with self.lock:
        if peer_addr in self.peers:
            self.on_status(f"⚠️ Đã kết nối hoặc đang kết nối với {peer_addr}.", "warning")
            return
        
        info = PeerInfo(None)
        info.status = PeerStatus.CONNECTING
        self.peers[peer_addr] = info

    self.on_peer_update(peer_addr, PeerStatus.CONNECTING)

    def _do_connect():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(CONNECT_TIMEOUT)
            sock.connect((host, port))
            sock.settimeout(RECV_TIMEOUT)

            with self.lock:
                if peer_addr not in self.peers:
                    sock.close()
                    return
                peer = self.peers[peer_addr]
                peer.sock = sock
                peer.status = PeerStatus.CONNECTED

            self.on_status(f"✅ Đã kết nối tới {peer_addr}", "info")
            self.on_peer_update(peer_addr, PeerStatus.CONNECTED)

            threading.Thread(
                target=self._recv_loop,
                args=(peer_addr,),
                daemon=True,
                name=f"recv-{peer_addr}"
            ).start()

        except socket.timeout:
            self.on_status(f"⏱ Không thể kết nối tới {peer_addr} (Timeout).", "error")
            self._handle_disconnect(peer_addr, PeerStatus.TIMEOUT)
        except ConnectionRefusedError:
            self.on_status(f"❌ {peer_addr} từ chối kết nối (Refused).", "error")
            self._handle_disconnect(peer_addr, PeerStatus.ERROR)
        except OSError as e:
            self.on_status(f"❌ Lỗi kết nối tới {peer_addr}: {e}", "error")
            self._handle_disconnect(peer_addr, PeerStatus.ERROR)

    threading.Thread(target=_do_connect, daemon=True, name=f"connect-{peer_addr}").start()

def _handle_disconnect(self, peer_addr: str, err_status=PeerStatus.DISCONNECTED):
    with self.lock:
        if peer_addr not in self.peers:
            return
        peer = self.peers[peer_addr]
        
        if peer.sock:
            try:
                peer.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                peer.sock.close()
            except OSError:
                pass
                
        del self.peers[peer_addr]

    if err_status == PeerStatus.DISCONNECTED:
        self.on_status(f"🔴 Mất hoặc ngắt kết nối với {peer_addr}", "warning")

    self.on_peer_update(peer_addr, err_status)
