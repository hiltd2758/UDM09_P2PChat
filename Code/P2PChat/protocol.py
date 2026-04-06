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

