import threading
import socket
from protocol import PeerStatus
from node.nodeBase import PeerInfo

RECV_TIMEOUT = 20.0  # timeout in seconds for receiving data

def start_server(self):
        self.running = True
        threading.Thread(target=self._listen, daemon=True, name="p2p-server").start()

def _listen(self):
        server = None
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(("", self.port))
            server.listen(10)
            server.settimeout(1.0)
            self.on_status(f"✅ Đang lắng nghe cổng {self.port}", "info")

            while self.running:
                try:
                    conn, addr = server.accept()
                except socket.timeout:
                    continue
                except OSError:
                    break

                # FIX: nhận handshake để lấy port lắng nghe thật của client
                try:
                    conn.settimeout(3.0)
                    raw = b""
                    while b"\n" not in raw:
                        chunk = conn.recv(32)
                        if not chunk:
                            raise ValueError("empty handshake")
                        raw += chunk
                    declared = raw.decode().strip()          # "HELLO:12001"
                    listen_port = int(declared.split(":")[1])
                    peer_addr = f"{addr[0]}:{listen_port}"  # port thật, không phải ephemeral
                except Exception:
                    peer_addr = f"{addr[0]}:{addr[1]}"      # fallback nếu handshake lỗi

                conn.settimeout(RECV_TIMEOUT)

                with self.lock:
                    info = PeerInfo(conn)
                    info.status = PeerStatus.CONNECTED
                    self.peers[peer_addr] = info

                self.on_status(f"🔗 {peer_addr} vừa kết nối tới", "info")
                self.on_peer_update(peer_addr, PeerStatus.CONNECTED)
                threading.Thread(
                    target=self._recv_loop,
                    args=(peer_addr,),
                    daemon=True,
                    name=f"recv-{peer_addr}"
                ).start()

        except OSError as e:
            if e.errno in (98, 10048):
                self.on_status(f"❌ Cổng {self.port} đã bị chiếm bởi ứng dụng khác", "error")
            elif e.errno == 13:
                self.on_status(f"❌ Cổng {self.port}: thiếu quyền (cần chạy Administrator)", "error")
            else:
                self.on_status(f"❌ Lỗi server: {e}", "error")
        finally:
            if server:
                try:
                    server.close()
                except OSError:
                    pass