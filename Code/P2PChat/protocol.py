import socket
def recv_exact(sock,n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n-len(data))
        if not chunk:
            return None
        data += chunk
    return data
def read_msg(sock):
    header = recv_exact(sock,4)
    if header is None:
        return None
    length = int.from_bytes(header,"big")
    payload = recv_exact(sock,length)
    if payload is None:
        return None
    return payload.decode("utf-8")
def send_msg(sock,msg):
    payload = msg.encode("utf-8")
    header = len(payload).to_bytes(4,"big")
    sock.sendall(header+payload)

# === P5a - Framing Functions ===
MAX_MESSAGE_LENGTH = 1048576

def encode_frame(text: str) -> bytes:
    """Implement packet format: [4 byte big-endian length][UTF-8 payload]"""
    payload = text.encode("utf-8")
    header = len(payload).to_bytes(4, "big")
    return header + payload

def decode_frame(sock: socket.socket) -> str | None:
    """Decode network packet, returns None and handles disconnection smoothly."""
    header = recvall(sock, 4)
    if header is None:
        return None
    length = int.from_bytes(header, "big")
    if length == 0:
        return ""
    if length > MAX_MESSAGE_LENGTH:
        return None
        
    payload = recvall(sock, length)
    if payload is None:
        return None
        
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError:
        return None

def recvall(sock: socket.socket, n: int) -> bytes | None:
    """Read exactly n bytes, handling timeouts and disconnections."""
    buffer = b""
    while len(buffer) < n:
        try:
            chunk = sock.recv(n - len(buffer))
        except socket.timeout:
            continue
        except (OSError, ConnectionResetError):
            return None
            
        if not chunk:
            return None
        buffer += chunk
    return buffer