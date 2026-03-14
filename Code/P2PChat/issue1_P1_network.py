import socket

HOST = '127.0.0.1'
PORT = 50000

def start_host():
    # Bước 1: tạo socket
    # AF_INET = dùng IPv4, SOCK_STREAM = dùng TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bước 2: cho phép dùng lại port ngay sau khi tắt
    # Không có dòng này → lỗi "Address already in use" khi restart nhanh
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bước 3: bind vào địa chỉ HOST:PORT
    # Đăng ký "tôi lắng nghe tại địa chỉ này"
    s.bind((HOST, PORT))

    # Bước 4: bắt đầu lắng nghe
    # 1 = chỉ chấp nhận 1 kết nối chờ (P2P chỉ cần 1)
    s.listen(1)

    print(f"Đang chờ kết nối tại {HOST}:{PORT}...")

    # Bước 5: chờ client kết nối — DỪNG TẠI ĐÂY cho đến khi có client
    # accept() trả về (conn, addr)
    # conn = socket để nói chuyện với client
    # addr = (ip, port) của client
    conn, addr = s.accept()

    print(f"Client đã kết nối từ: {addr}")

    # Bước 6: vòng lặp nhận và gửi tin nhắn
    while True:
        # Nhận tin từ client, tối đa 1024 byte
        # recv() DỪNG TẠI ĐÂY cho đến khi có data
        data = conn.recv(1024)

        if not data:
            print("Client đã ngắt kết nối.")
            break

        print(f"Client: {data.decode('utf-8')}")

        message = input("Host: ")
        if message.lower() == 'quit':
            break

        # Gửi tin — encode chữ → bytes trước khi gửi
        # sendall() đảm bảo gửi hết, không bị thiếu
        conn.sendall(message.encode('utf-8'))

    # Bước 7: đóng cả 2 socket
    conn.close()
    s.close()
    print("Đã đóng kết nối.")


def start_client():
    # Bước 1: tạo socket — giống hệt host
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print(f"Đang kết nối tới {HOST}:{PORT}...")

    # Bước 2: kết nối tới host
    # connect() chủ động gọi sang host đang accept()
    s.connect((HOST, PORT))

    print("Kết nối thành công!")

    # Bước 3: vòng lặp gửi và nhận tin nhắn
    while True:
        message = input("Client: ")
        if message.lower() == 'quit':
            break

        # Gửi tin
        s.sendall(message.encode('utf-8'))

        # Nhận tin từ host
        data = s.recv(1024)

        if not data:
            print("Host đã ngắt kết nối.")
            break

        print(f"Host: {data.decode('utf-8')}")

    # Bước 4: đóng socket
    s.close()
    print("Đã đóng kết nối.")


if __name__ == "__main__":
    mode = input("Chọn mode (host/client): ").strip().lower()
    if mode == "host":
        start_host()
    elif mode == "client":
        start_client()
    else:
        print("Nhập 'host' hoặc 'client'")