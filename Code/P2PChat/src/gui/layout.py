import tkinter as tk
from tkinter import scrolledtext, ttk

from ..validation.validation import validate_ip, validate_port 

# ============ MÀU SẮC ============

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


# ============ GIAO DIỆN CHÍNH ============

class ChatApp(tk.Tk):
    """
    Lớp giao diện chính — chỉ chứa layout và widget.
    Callback và logic được TV6 triển khai trong gui/logic.py.
    """

    def __init__(self, port: int = 12000):
        super().__init__()
        self.title(f"💬 P2P Chat v2.0  —  Port {port}")
        self.geometry("900x650")
        self.minsize(700, 500)
        self.configure(bg="#1e1e2e")

        self.port = port

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):

        # ── Thanh kết nối (trên cùng) ──
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

        tk.Button(bar, text="🔗 Kết nối", command=self._connect,
                  bg="#89b4fa", fg="#11111b", font=("Consolas", 9, "bold"),
                  relief="flat", padx=8, pady=3,
                  cursor="hand2").pack(side="left", padx=3)

        tk.Button(bar, text="✂️ Ngắt", command=self._disconnect,
                  bg="#f38ba8", fg="#11111b", font=("Consolas", 9, "bold"),
                  relief="flat", padx=8, pady=3,
                  cursor="hand2").pack(side="left", padx=3)

        # ── Khu vực chính ──
        main = tk.Frame(self, bg="#1e1e2e")
        main.pack(fill="both", expand=True, padx=8, pady=(6, 4))

        # Chat log (trái)
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

        # Panel peers (phải)
        right = tk.Frame(main, bg="#1e1e2e", width=200)
        right.pack(side="right", fill="y", padx=(10, 0))
        right.pack_propagate(False)

        tk.Label(right, text="🌐  Peers",
                 bg="#1e1e2e", fg="#cdd6f4",
                 font=("Consolas", 10, "bold")).pack(anchor="w", pady=(0, 4))

        list_frame = tk.Frame(right, bg="#181825")
        list_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, bg="#313145",
                                  troughcolor="#181825")
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

        # ── Thanh trạng thái (dưới cùng) ──
        self.status_bar = tk.Label(
            self, text="🔄 Đang khởi động...",
            bg="#11111b", fg="#6c7086",
            font=("Consolas", 8), anchor="w", padx=8
        )
        self.status_bar.pack(fill="x", side="bottom")

    # ── Placeholder — TV6 sẽ override trong logic.py ──

    def _connect(self):          pass
    def _disconnect(self):       pass
    def _send(self):             pass
    def _broadcast(self):        pass
    def _refresh_peers(self):    pass
    def _on_peer_select(self, event=None): pass
    def _update_char_count(self, event=None): pass
    def _on_close(self):         self.destroy()