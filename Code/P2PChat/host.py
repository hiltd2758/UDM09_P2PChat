import socket
import threading
import protocol
import ipaddress
IP = input("Nhap dia chi can ket noi den: ")
if not ipaddress.ip_address(IP):
    IP = "127.0.0.1"
PORT = int(input("Nhap PORT: "))
if PORT < 0 and PORT > 65535:
    PORT = 5000

def recv_loop(sock):
    while True:
        msg = protocol.read_msg(sock)
        if msg is None:
            print("Client Disconnected")
            break
        print(f"\nClient: {msg}")
        print("Host: ",end="",flush=True)
host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_socket.bind((IP,PORT))
host_socket.listen(1)
print("Waiting to connect...")
conn,addr = host_socket.accept()
print("Client connected: ",addr)
recv_thread = threading.Thread(target=recv_loop,args=(conn,))
recv_thread.daemon = True
recv_thread.start()
while True:
    msg = input("Host: ")
    if msg == "quit":
        break
    protocol.send_msg(conn, msg)
conn.close()
host_socket.close()