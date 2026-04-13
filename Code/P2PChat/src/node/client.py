import socket
import threading
import time
from protocol import PeerStatus, CONNECT_TIMEOUT, RECV_TIMEOUT
from node.nodeBase import PeerInfo


def connect_peer(node, host: str, port: int):
    peer_addr = f"{host}:{port}"

    with node.lock:
        if peer_addr in node.peers:
            node.on_status(f"⚠️ Đã kết nối hoặc đang kết nối với {peer_addr}.", "warn")
            return

        info = PeerInfo(None)
        info.status = PeerStatus.CONNECTING
        node.peers[peer_addr] = info

    node.on_peer_update(peer_addr, PeerStatus.CONNECTING)

    def _do_connect():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(CONNECT_TIMEOUT)
            sock.connect((host, port))
            sock.settimeout(RECV_TIMEOUT)

            with node.lock:
                if peer_addr not in node.peers:
                    sock.close()
                    return
                peer = node.peers[peer_addr]
                peer.sock = sock
                peer.status = PeerStatus.CONNECTED

            node.on_status(f"✅ Đã kết nối tới {peer_addr}", "info")
            node.on_peer_update(peer_addr, PeerStatus.CONNECTED)

            from node.transfer import _recv_loop
            threading.Thread(
                target=_recv_loop,
                args=(node, peer_addr),
                daemon=True,
                name=f"recv-{peer_addr}"
            ).start()

        except socket.timeout:
            node.on_status(f"⏱ Không thể kết nối tới {peer_addr} (Timeout).", "error")
            _handle_disconnect(node, peer_addr, PeerStatus.TIMEOUT)

        except ConnectionRefusedError:
            node.on_status(f"❌ {peer_addr} từ chối kết nối (Refused).", "error")
            _handle_disconnect(node, peer_addr, PeerStatus.ERROR)

        except socket.gaierror as e:
            node.on_status(f"❌ Không tìm được địa chỉ '{host}': {e}", "error")
            _handle_disconnect(node, peer_addr, PeerStatus.ERROR)

        except OSError as e:
            node.on_status(f"❌ Lỗi kết nối tới {peer_addr}: {e}", "error")
        _handle_disconnect(node, peer_addr, PeerStatus.ERROR)

    threading.Thread(
        target=_do_connect,
        daemon=True,
        name=f"connect-{peer_addr}"
    ).start()


def disconnect_peer(node, peer_addr: str):
    with node.lock:
        info = node.peers.pop(peer_addr, None)

        if info:
            if info.sock:
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