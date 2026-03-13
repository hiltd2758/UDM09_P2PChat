import socket

HOST = '127.0.0.1'  # IP của máy host cần kết nối tới
PORT = 50000        

# tạo socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# kết nối tới host
# connect() = chủ động gọi sang host
# host dùng accept() = thụ động chờ
print(f"kết nối tới {HOST}:{PORT}...")
try:
    client_socket.connect((HOST, PORT))
    print("sucess")

    # gửi rồi nhận
    while True:
        message = input("client: ")
        if message.lower() == 'quit':
            break

        client_socket.sendall(message.encode('utf-8'))

        # nhận tin từhost
        data = client_socket.recv(1024)
        if not data:
            print("host disconnect.")
            break


        print(f"host: {data.decode('utf-8')}")

except Exception as e:
    print(f"lỗi: {e}")

finally:

    client_socket.close()
    print("close.")