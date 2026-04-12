import socket
import threading
import time
from protocol import PeerStatus, CONNECT_TIMEOUT
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

def disconnect_peer(node, peer_addr: str):
    with node.lock:
        info = node.peers.pop(peer_addr, None)

    if info:
        try:
            info.sock.shutdown(socket.SHUT_RDWR)
            info.sock.close()
        except OSError:
            pass
        node.on_status(f"🔌 Đã ngắt kết nối với {peer_addr}", "info")
        node.on_peer_update(peer_addr, PeerStatus.DISCONNECTED)
    else:
        node.on_status(f"⚠️ {peer_addr} không có trong danh sách", "warn")


def get_peers(node) -> dict[str, PeerStatus]:
    with node.lock:
        return {addr: info.status for addr, info in node.peers.items()}


def get_peer_stats(node, peer_addr: str) -> dict | None:
    with node.lock:
        info = node.peers.get(peer_addr)
        if not info:
            return None
        uptime = int(time.time() - info.connected_at)
        return {
            "status": info.status,
            "uptime": uptime,
            "sent":   info.messages_sent,
            "recv":   info.messages_recv,
        }

def _handle_disconnect(node, peer_addr: str,
                        err_status: PeerStatus = PeerStatus.DISCONNECTED):
    with node.lock:
        if peer_addr not in node.peers:
            return
        info = node.peers.pop(peer_addr)

    if info.sock:
        try:
            info.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            info.sock.close()
        except OSError:
            pass

    if err_status == PeerStatus.DISCONNECTED:
        node.on_status(f"⚠️ {peer_addr} mất kết nối", "warn")

    node.on_peer_update(peer_addr, err_status)