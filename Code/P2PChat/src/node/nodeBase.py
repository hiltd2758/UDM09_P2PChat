import socket          
import threading        
import time           
from enum import Enum   
from Code.P2PChat.src.protocol import PeerStatus 

class PeerInfo:
    """Cấu trúc lưu trữ thông tin của một node đối phương"""
    __slots__ = ("sock", "status", "connected_at", "messages_sent", "messages_recv")
    def __init__(self, sock: socket.socket):
        self.sock           = sock
        self.status         = PeerStatus.CONNECTING
        self.connected_at   = time.time()
        self.messages_sent  = 0
        self.messages_recv  = 0
class P2PNode:
    def __init__(self, port: int, on_message, on_status, on_peer_update):
        """
        Khởi tạo Node:
        - port: Cổng lắng nghe của máy mình.
        - callbacks: Các hàm để đẩy dữ liệu ngược về GUI (logic.py).
        """
        self.port            = port
        self.on_message      = on_message       
        self.on_status       = on_status        
        self.on_peer_update  = on_peer_update   
        self.peers: dict[str, PeerInfo] = {}    # Quản lý danh sách kết nối
        self.lock    = threading.Lock()         # Khóa để tránh xung đột đa luồng
        self.running = False
    def get_peers(self) -> dict[str, PeerStatus]:
        """Lấy danh sách nhanh các peer và trạng thái để hiển thị lên Listbox"""
        with self.lock:
            return {addr: info.status.value for addr, info in self.peers.items()}
    def get_peer_stats(self, peer_addr: str) -> dict | None:
        """Truy xuất thống kê chi tiết cho bảng thông tin bên phải giao diện"""
        with self.lock:
            info = self.peers.get(peer_addr)
            if not info:
                return None
            uptime = int(time.time() - info.connected_at)
            return {
                "status":   info.status,
                "uptime":   uptime,
                "sent":     info.messages_sent,
                "recv":     info.messages_recv,
            }
    def shutdown(self):
        """Dọn dẹp hệ thống khi đóng ứng dụng"""
        self.running = False
        with self.lock:
            snapshot = list(self.peers.values())
            self.peers.clear()
        for info in snapshot:
            try:
                # Ngắt cả đọc và ghi trước khi đóng hẳn socket
                info.sock.shutdown(socket.SHUT_RDWR)
                info.sock.close()
            except OSError:
                pass
        time.sleep(0.3)