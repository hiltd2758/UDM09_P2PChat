# Format: [4 byte big-endian length][UTF-8 body]

import socket, struct
from src.constants import MAX_MESSAGE_LENGTH

def pack_message(text: str) -> bytes:
    """Đóng gói tin: [4 byte độ dài][nội dung UTF-8]"""
    data = text.encode("utf-8")
    return struct.pack(">I", len(data)) + data


def recv_exact(sock: socket.socket, n: int) -> bytes | None:
    """
    Nhận đúng n byte từ socket.
    Trả None nếu kết nối đóng hoặc lỗi.
    """
    buf = b""
    while len(buf) < n:
        try:
            chunk = sock.recv(n - len(buf))
        except socket.timeout:
            # Timeout khi nhận — bỏ qua, thử lại
            continue
        except (OSError, ConnectionResetError):
            return None
        if not chunk:
            return None
        buf += chunk
    return buf


def recv_message(sock: socket.socket) -> str | None:
    """
    nhận tin nhắn đã đóng gói
    xu ly: timeout, lỗi socket, lỗi decode, tin quá lớn.
    return  None nếu kết nối đóng.
    """

    # đọc header ( độ dài tin nhắn)
    header = recv_exact(sock, 4)
    if header is None:
        return None

    try:
        length = struct.unpack(">I", header)[0]
    except struct.error:
        return None

    # chặn tin bất thường
    if length == 0:
        return ""                          # tin rỗng hợp lệ
    if length > MAX_MESSAGE_LENGTH:
        return None                        # tin quá lớn → ngắt kết nối

    # Đọc nội dung
    data = recv_exact(sock, length)
    if data is None:
        return None

    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None                        # không decode được → bỏ qua

