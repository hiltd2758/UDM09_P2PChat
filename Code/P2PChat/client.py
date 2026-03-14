import socket
import threading
import protocol
import ipaddress
IP = input("Nhap dia chi can ket noi den: ")
try:
    ipaddress.ip_address(IP)
except ValueError:
    IP = "127.0.0.1"
PORT = int(input("Nhap PORT: "))
if PORT < 0 or PORT > 65535:
    PORT = 5000
def recv_loop(sock):
    while True:
        msg = protocol.read_msg(sock)
        if msg is None:
            print("Host Off")
            break
        print(f"\nHost: {msg}")
        print("Client: ",end="",flush=True)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP,PORT))
print("Connected to Host")
recv_thread = threading.Thread(target=recv_loop,args=(client_socket,))
recv_thread.daemon = True
recv_thread.start()
while True:
    msg = input("Client: ")
    if msg.lower() == "quit":
        break;
    protocol.send_msg(client_socket,msg)
client_socket.close()