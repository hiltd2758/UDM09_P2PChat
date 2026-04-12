import threading
import socket
from Code.P2PChat.src.protocol import PeerStatus
from nodeBase import PeerInfo

RECV_TIMEOUT = 5.0  # timeout in seconds for receiving data

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
            server.settimeout(1.0)   # timeout để kiểm tra self.running
            self.on_status(f"✅ Đang lắng nghe cổng {self.port}", "info")

            while self.running:
                try:
                    conn, addr = server.accept()
                except socket.timeout:
                    continue          # kiểm tra lại self.running
                except OSError:
                    break

                peer_addr = f"{addr[0]}:{addr[1]}"
                conn.settimeout(RECV_TIMEOUT)   # nhận tin không timeout (thread riêng)

                with self.lock:
                    info = PeerInfo(conn)
                    info.status = PeerStatus.CONNECTED
                    self.peers[peer_addr] = info

                self.on_status(f" {peer_addr} vừa kết nối tới", "info")
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