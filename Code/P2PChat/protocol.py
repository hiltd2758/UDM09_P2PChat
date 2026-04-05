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
    pass

def decode_frame(sock: socket.socket) -> str | None:
    """Decode network packet, returns None and handles disconnection smoothly."""
    pass

def recvall(sock: socket.socket, n: int) -> bytes | None:
    """Read exactly n bytes, handling timeouts and disconnections."""
    pass