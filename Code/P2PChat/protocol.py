# protocol.py
import struct
from enum import Enum

MAX_MESSAGE_LENGTH = 10_000
CONNECT_TIMEOUT    = 5
RECV_TIMEOUT       = None
SEND_TIMEOUT       = 5
HEARTBEAT_INTERVAL = 30

class PeerStatus(Enum):
    CONNECTING   = "⏳ Đang kết nối"
    CONNECTED    = "🟢 Đã kết nối"
    DISCONNECTED = "🔴 Đã ngắt"
    ERROR        = "❌ Lỗi"
    TIMEOUT      = "⏱ Timeout"

def pack_message(text: str) -> bytes:
    data = text.encode("utf-8")
    return struct.pack(">I", len(data)) + data

def recv_exact(sock, n: int) -> bytes | None:
    buf = b""
    while len(buf) < n:
        try:
            chunk = sock.recv(n - len(buf))
        except Exception:
            return None
        if not chunk:
            return None
        buf += chunk
    return buf

def recv_message(sock) -> str | None:
    header = recv_exact(sock, 4)
    if header is None:
        return None
    try:
        length = struct.unpack(">I", header)[0]
    except struct.error:
        return None
    if length == 0:
        return ""
    if length > MAX_MESSAGE_LENGTH:
        return None
    data = recv_exact(sock, length)
    if data is None:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None