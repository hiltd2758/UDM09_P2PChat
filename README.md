#  UDM_09 · P2P Chat

> Ứng dụng chat ngang hàng (peer-to-peer) không cần server trung tâm.

**Nhóm:** 09 &nbsp;|&nbsp; **Lớp:** 012012301305 &nbsp;|&nbsp; **Python:** 3.13+

---

##  Tính năng

| Tính năng | Mô tả |
|---|---|
|  Kết nối trực tiếp | Mỗi node vừa là server, vừa là client |
|  Nhắn tin 1-1 | Gửi tin đến một peer cụ thể |
|  Broadcast | Gửi tin đến tất cả peer cùng lúc |
|  Trạng thái realtime | Theo dõi kết nối từng peer theo thời gian thực |


---

##  Cài đặt & Chạy

```bash
# 1. Clone repo
git clone https://github.com/hiltd2758/UDM09_P2PChat.git
cd UDM09_P2PChat/Code/P2PChat

# 2. Chạy với port mặc định (12000)
python src/main.py

# 3. Hoặc chỉ định port tuỳ chọn
python src/main.py 12001
```

### Chạy nhiều instance để test

```bash
# Terminal 1          Terminal 2          Terminal 3
python src/main.py    python src/main.py  python src/main.py
       12000                 12001               12002
```

---

##  Hướng dẫn sử dụng

```
1. Nhập IP + Port của peer muốn kết nối
2. Nhấn [🔗 Kết nối]
3. Chọn peer trong danh sách
4. Gõ tin nhắn → [▶ Gửi]  hoặc  [📡 Gửi tất cả]
```

**Giới hạn:** tối đa 10 000 ký tự / tin nhắn · tối đa 20 ký tự biệt danh

---

##  Cấu trúc dự án

```
src/
├── main.py              ← Điểm khởi động
├── protocol.py          ← Định nghĩa giao thức (framing, constants)
├── gui/
│   ├── layout.py        ← Giao diện (Tkinter)
│   ├── logic.py         ← Điều khiển GUI
│   └── validation.py    ← Kiểm tra đầu vào
└── node/
    ├── nodeBase.py      ← Lớp cơ sở P2PNode
    ├── server.py        ← Lắng nghe kết nối đến
    ├── client.py        ← Kết nối đến peer khác
    └── transfer.py      ← Gửi / nhận tin
```

---

## ⚙️ Kiến trúc kỹ thuật

### Giao thức truyền tin
```
┌──────────────┬──────────────────────────┐
│  4 bytes     │  N bytes                 │
│  (length)    │  (UTF-8 payload)         │
└──────────────┴──────────────────────────┘
```
Dùng **length-prefix framing** để tránh lỗi phân tách gói tin (packet fragmentation).

### Mô hình luồng (Threading)
```
Main Thread
├── Server Thread       ← lắng nghe cổng, chấp nhận kết nối mới
├── Recv Thread [A]     ← nhận tin từ peer A
├── Recv Thread [B]     ← nhận tin từ peer B
└── Connect Thread      ← kết nối đến peer mới (non-blocking)
```

Thread safety được đảm bảo bởi `threading.Lock()` trên mọi truy cập vào danh sách peer.

---

##  Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Cách xử lý |
|---|---|---|
| Cổng đã bị chiếm | Port đang được dùng bởi app khác | Dùng port khác (1024–65535) |
| Thiếu quyền | Port < 1024 yêu cầu quyền admin | Dùng port > 1024 hoặc chạy Administrator |
| Kết nối timeout | Peer chưa chạy / firewall chặn | Kiểm tra peer đã khởi động, mở firewall cho port |

---

##  Yêu cầu hệ thống

- **Python** 3.13 trở lên
- **Hệ điều hành:** Windows / macOS / Linux
- **Thư viện:** không cần cài thêm (dùng `tkinter`, `socket`, `threading`)
