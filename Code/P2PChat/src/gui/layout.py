import tkinter as tk
from tkinter import scrolledtext

STATUS_COLORS = {
    "CONNECTING":   "#f9e2af",
    "CONNECTED":    "#a6e3a1",
    "DISCONNECTED": "#f38ba8",
    "ERROR":        "#f38ba8",
    "TIMEOUT":      "#fab387",
}

LOG_COLORS = {
    "info":  "#f9e2af",
    "warn":  "#fab387",
    "error": "#f38ba8",
    "me":    "#a6e3a1",
    "peer":  "#89dceb",
}


class ChatApp(tk.Tk):
    def __init__(self, port: int = 12000):
        super().__init__()
        self.title(f"💬 P2P Chat —  Port {port}")
        self.geometry("900x650")
        self.minsize(700, 500)
        self.configure(bg="#1e1e2e")
        self.port = port
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        # ── Thanh kết nối ──
        bar = tk.Frame(self, bg="#181825", pady=8)
        bar.pack(fill="x")

        tk.Label(bar, text="Biệt danh:", bg="#181825", fg="#cdd6f4",
                 font=("Consolas", 9)).pack(side="left", padx=(12, 4))
        self.nick_entry = tk.Entry(bar, width=10, bg="#313145", fg="#cdd6f4",
                                   insertbackground="#cdd6f4", relief="flat",
                                   font=("Consolas", 9))
        self.nick_entry.insert(0, "Tôi")
        self.nick_entry.pack(side="left", padx=(0, 10))

        tk.Label(bar, text="IP:", bg="#181825", fg="#cdd6f4",
                 font=("Consolas", 9)).pack(side="left", padx=4)
        self.ip_entry = tk.Entry(bar, width=14, bg="#313145", fg="#cdd6f4",
                                  insertbackground="#cdd6f4", relief="flat",
                                  font=("Consolas", 9))
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.pack(side="left", padx=(0, 6))

        tk.Label(bar, text="Port:", bg="#181825", fg="#cdd6f4",
                 font=("Consolas", 9)).pack(side="left", padx=4)
        self.port_entry = tk.Entry(bar, width=7, bg="#313145", fg="#cdd6f4",
                                    insertbackground="#cdd6f4", relief="flat",
                                    font=("Consolas", 9))
        self.port_entry.insert(0, "12001")
        self.port_entry.pack(side="left", padx=(0, 10))
        self.port_entry.bind("<Return>", lambda e: self._connect())

        # FIX: lưu tham chiếu để disable/enable sau
        self._connect_btn = tk.Button(bar, text="🔗 Kết nối", command=self._connect,
                  bg="#89b4fa", fg="#11111b", font=("Consolas", 9, "bold"),
                  relief="flat", padx=8, pady=3,
                  cursor="hand2")
        self._connect_btn.pack(side="left", padx=3)

        self._disconnect_btn = tk.Button(bar, text="✂️ Ngắt", command=self._disconnect,
                  bg="#f38ba8", fg="#11111b", font=("Consolas", 9, "bold"),
                  relief="flat", padx=8, pady=3,
                  cursor="hand2")
        self._disconnect_btn.pack(side="left", padx=3)

        # ── Khu vực chính ──
        main = tk.Frame(self, bg="#1e1e2e")
        main.pack(fill="both", expand=True, padx=8, pady=(6, 4))

        chat_frame = tk.Frame(main, bg="#1e1e2e")
        chat_frame.pack(side="left", fill="both", expand=True)

        tk.Label(chat_frame, text="💬  Nhật ký trò chuyện",
                 bg="#1e1e2e", fg="#cdd6f4",
                 font=("Consolas", 10, "bold")).pack(anchor="w", pady=(0, 4))

        self.chat = scrolledtext.ScrolledText(
            chat_frame, state="disabled",
            bg="#181825", fg="#cdd6f4",
            font=("Consolas", 10),
            relief="flat", bd=0, wrap="word"
        )
        self.chat.pack(fill="both", expand=True)
        for key, color in LOG_COLORS.items():
            self.chat.tag_config(key, foreground=color)

        right = tk.Frame(main, bg="#1e1e2e", width=200)
        right.pack(side="right", fill="y", padx=(10, 0))
        right.pack_propagate(False)

        tk.Label(right, text="🌐  Peers",
                 bg="#1e1e2e", fg="#cdd6f4",
                 font=("Consolas", 10, "bold")).pack(anchor="w", pady=(0, 4))

        list_frame = tk.Frame(right, bg="#181825")
        list_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, bg="#313145", troughcolor="#181825")
        scrollbar.pack(side="right", fill="y")

        self.peer_list = tk.Listbox(
            list_frame,
            bg="#181825", fg="#89b4fa",
            selectbackground="#313145",
            selectforeground="#cdd6f4",
            font=("Consolas", 9),
            relief="flat", bd=0,
            yscrollcommand=scrollbar.set,
            activestyle="none"
        )
        self.peer_list.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.peer_list.yview)
        self.peer_list.bind("<<ListboxSelect>>", self._on_peer_select)

        self.peer_info_label = tk.Label(
            right, text="── Chọn peer để xem ──",
            bg="#1e1e2e", fg="#6c7086",
            font=("Consolas", 8), justify="left",
            wraplength=195
        )
        self.peer_info_label.pack(anchor="w", pady=(6, 0))

        tk.Button(right, text="🔄 Làm mới", command=self._refresh_peers,
                  bg="#313145", fg="#cdd6f4", font=("Consolas", 8),
                  relief="flat", cursor="hand2").pack(fill="x", pady=(6, 0))

        # ── Vùng nhập tin ──
        inp = tk.Frame(self, bg="#181825", pady=8)
        inp.pack(fill="x", padx=8, pady=(0, 4))

        self.msg_entry = tk.Entry(
            inp, bg="#313145", fg="#cdd6f4",
            insertbackground="#cdd6f4",
            font=("Consolas", 11), relief="flat"
        )
        self.msg_entry.pack(side="left", fill="x", expand=True, padx=(6, 6))
        self.msg_entry.bind("<Return>", lambda e: self._send())
        self.msg_entry.bind("<KeyRelease>", self._update_char_count)

        self.char_label = tk.Label(
            inp, text="0/10000",
            bg="#181825", fg="#6c7086",
            font=("Consolas", 8)
        )
        self.char_label.pack(side="left", padx=(0, 6))

        tk.Button(inp, text="▶ Gửi", command=self._send,
                  bg="#89b4fa", fg="#11111b", font=("Consolas", 10, "bold"),
                  relief="flat", padx=10, pady=4,
                  cursor="hand2").pack(side="left", padx=3)

        tk.Button(inp, text="📡 Gửi tất cả", command=self._broadcast,
                  bg="#a6e3a1", fg="#11111b", font=("Consolas", 10, "bold"),
                  relief="flat", padx=10, pady=4,
                  cursor="hand2").pack(side="left", padx=3)

        # ── Thanh trạng thái ──
        self.status_bar = tk.Label(
            self, text="🔄 Đang khởi động...",
            bg="#11111b", fg="#6c7086",
            font=("Consolas", 8), anchor="w", padx=8
        )
        self.status_bar.pack(fill="x", side="bottom")

        # FIX: khởi tạo trạng thái mặc định — chưa kết nối
        self._set_connected_state(False)

    # ── FIX: quản lý trạng thái UI ──
    def _set_connected_state(self, connected: bool):
        """Disable/enable connection fields dựa trên trạng thái kết nối.
        Gọi từ logic.py sau khi connect thành công hoặc disconnect.
        """
        field_state = "disabled" if connected else "normal"
        self.nick_entry.config(state=field_state)
        self.ip_entry.config(state=field_state)
        self.port_entry.config(state=field_state)
        self._connect_btn.config(state="disabled" if connected else "normal")
        self._disconnect_btn.config(state="normal" if connected else "disabled")

    # Placeholder — được override trong logic.py
    def _connect(self):                   pass
    def _disconnect(self):                pass
    def _send(self):                      pass
    def _broadcast(self):                 pass
    def _refresh_peers(self):             pass
    def _on_peer_select(self, e=None):    pass
    def _update_char_count(self, e=None): pass
    def _on_close(self):                  self.destroy()