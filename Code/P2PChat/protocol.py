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