import time
import threading
import tkinter as tk
from tkinter import messagebox

from gui.layout import ChatApp, STATUS_COLORS, LOG_COLORS
from gui.validation import validate_ip, validate_port
from node import P2PNode
from protocol import PeerStatus, MAX_MESSAGE_LENGTH, CONNECT_TIMEOUT


class ChatAppFull(ChatApp):
    def __init__(self, port: int = 12000):
        super().__init__(port)
        self.nickname = "Tôi"
        self.node     = None
        self.peer_status_map: dict[str, PeerStatus] = {}
        self._start_node()
        self._tick_uptime()

    def _start_node(self):
        self.node = P2PNode(
            port=self.port,
            on_message=self._on_message,
            on_status=self._on_status,
            on_peer_update=self._on_peer_update
        )
        self.node.start_server()

    # ── Kết nối / Ngắt ──

    def _connect(self):
        ip       = self.ip_entry.get().strip()
        port_str = self.port_entry.get().strip()

        ok_ip, err_ip = validate_ip(ip)
        if not ok_ip:
            messagebox.showerror("IP không hợp lệ", err_ip, parent=self)
            self.ip_entry.focus_set()
            return

        ok_p, port, warn_p = validate_port(port_str)
        if not ok_p:
            messagebox.showerror("Port không hợp lệ", warn_p, parent=self)
            self.port_entry.focus_set()
            return
        if warn_p:
            self._log(warn_p, "warn")

        self._log(f"⏳ Đang kết nối {ip}:{port} (timeout {CONNECT_TIMEOUT}s)…", "info")
        threading.Thread(
            target=lambda: self.node.connect_peer(ip, port),
            daemon=True,
            name=f"connect-{ip}:{port}"
        ).start()

    def _disconnect(self):
        sel = self.peer_list.curselection()
        if not sel:
            messagebox.showinfo("Chưa chọn peer",
                                "Hãy click chọn một peer trong danh sách.",
                                parent=self)
            return
        raw  = self.peer_list.get(sel[0])
        peer = raw.split(" ", 1)[-1].strip() if " " in raw else raw

        if not messagebox.askyesno("Xác nhận", f"Ngắt kết nối với:\n{peer}?", parent=self):
            return
        self.node.disconnect_peer(peer)
        self._refresh_peers()

        peers = self.node.get_peers()
        has_connected = any(s == PeerStatus.CONNECTED for s in peers.values())
        self._set_connected_state(has_connected)

    # ── Gửi / Broadcast ──

    def _send(self):
        msg = self.msg_entry.get().strip()
        if not msg:
            return
        if len(msg) > MAX_MESSAGE_LENGTH:
            messagebox.showerror("Tin quá dài",
                                 f"Giới hạn {MAX_MESSAGE_LENGTH:,} ký tự",
                                 parent=self)
            return

        sel = self.peer_list.curselection()
        if not sel:
            messagebox.showinfo("Chưa chọn peer",
                                "Chọn một peer hoặc dùng '📡 Gửi tất cả'.",
                                parent=self)
            return

        raw  = self.peer_list.get(sel[0])
        peer = raw.split(" ", 1)[-1].strip() if " " in raw else raw
        self.nickname = self.nick_entry.get().strip() or "Tôi"
        full = f"[{self.nickname}] {msg}"

        ok, err = self.node.send_to(peer, full)
        if ok:
            self._log(f"→ {full}", "me")
            self.msg_entry.delete(0, "end")
            self._update_char_count()
        else:
            self._log(f"❌ Gửi thất bại → {peer}: {err}", "error")
            messagebox.showerror("Gửi thất bại",
                                 f"Không thể gửi tới {peer}\n\n{err}",
                                 parent=self)
            self._refresh_peers()

    def _broadcast(self):
        msg = self.msg_entry.get().strip()
        if not msg:
            return
        if len(msg) > MAX_MESSAGE_LENGTH:
            messagebox.showerror("Tin quá dài",
                                 f"Giới hạn {MAX_MESSAGE_LENGTH:,} ký tự",
                                 parent=self)
            return

        peers = self.node.get_peers()
        connected = [p for p, s in peers.items() if s == PeerStatus.CONNECTED]
        if not connected:
            messagebox.showinfo("Không có peer",
                                "Chưa có peer nào đang kết nối.",
                                parent=self)
            return

        self.nickname = self.nick_entry.get().strip() or "Tôi"
        full = f"[{self.nickname}] {msg}"
        ok, total, errors = self.node.broadcast(full)

        if ok == total and total > 0:
            self._log(f"📡 Broadcast ({ok}/{total}):  {full}", "me")
        elif ok > 0:
            self._log(f"⚠️ Broadcast một phần ({ok}/{total}):  {full}", "warn")
            messagebox.showwarning("Gửi một phần",
                                   f"Thành công: {ok}/{total}\n\n" +
                                   "\n".join(f"• {e}" for e in errors),
                                   parent=self)
        else:
            self._log(f"❌ Broadcast thất bại (0/{total})", "error")
            messagebox.showerror("Broadcast thất bại",
                                 "Không thể gửi tới bất kỳ peer nào!",
                                 parent=self)

        self.msg_entry.delete(0, "end")
        self._update_char_count()
        self._refresh_peers()

    # ── Callback từ Node ──

    def _on_message(self, peer: str, msg: str):
        self.after(0, lambda: self._log(f"← {msg}", "peer"))
        self.after(0, self._refresh_peers)

    def _on_status(self, msg: str, level: str = "info"):
        tag = {"info": "info", "warn": "warn", "error": "error"}.get(level, "info")
        self.after(0, lambda: self.status_bar.config(text=msg))
        self.after(0, lambda: self._log(msg, tag))
        self.after(0, self._refresh_peers)

    def _on_peer_update(self, peer_addr: str, status: PeerStatus):
        def _do():
            self.peer_status_map[peer_addr] = status
            self._refresh_peers()
            self._update_status_bar()

            peers = self.node.get_peers()
            has_connected = any(s == PeerStatus.CONNECTED for s in peers.values())
            self._set_connected_state(has_connected)
        self.after(0, _do)

    # ── Cập nhật UI ──

    def _refresh_peers(self):
        current_sel = None
        sel = self.peer_list.curselection()
        if sel:
            raw = self.peer_list.get(sel[0])
            current_sel = raw.split(" ", 1)[-1].strip() if " " in raw else raw

        self.peer_list.delete(0, "end")
        active = self.node.get_peers()
        all_peers = dict(self.peer_status_map)
        all_peers.update(active)

        icon_map = {
            PeerStatus.CONNECTING:   "⏳",
            PeerStatus.CONNECTED:    "🟢",
            PeerStatus.DISCONNECTED: "🔴",
            PeerStatus.ERROR:        "❌",
            PeerStatus.TIMEOUT:      "⏱",
        }

        new_sel_idx = None
        for i, (addr, status) in enumerate(sorted(all_peers.items())):
            icon = icon_map.get(status, "❓")
            self.peer_list.insert("end", f"{icon} {addr}")
            color = STATUS_COLORS.get(status.name, "#cdd6f4")
            self.peer_list.itemconfig(i, fg=color)
            if addr == current_sel:
                new_sel_idx = i

        if new_sel_idx is not None:
            self.peer_list.selection_set(new_sel_idx)
            self._on_peer_select()

    def _on_peer_select(self, event=None):
        sel = self.peer_list.curselection()
        if not sel:
            self.peer_info_label.config(text="── Chọn peer để xem ──")
            return
        raw  = self.peer_list.get(sel[0])
        peer = raw.split(" ", 1)[-1].strip() if " " in raw else raw

        stats  = self.node.get_peer_stats(peer)
        status = self.peer_status_map.get(peer, PeerStatus.DISCONNECTED)

        if stats:
            h, r = divmod(stats["uptime"], 3600)
            m, s = divmod(r, 60)
            info = (
                f"📍 {peer}\n"
                f"Trạng thái: {stats['status'].value}\n"
                f"Thời gian: {h:02d}:{m:02d}:{s:02d}\n"
                f"Đã gửi: {stats['sent']} tin\n"
                f"Đã nhận: {stats['recv']} tin"
            )
        else:
            info = f"📍 {peer}\nTrạng thái: {status.value}"

        self.peer_info_label.config(
            text=info,
            fg=STATUS_COLORS.get(status.name, "#6c7086")
        )

    def _update_status_bar(self):
        peers     = self.node.get_peers()
        connected = sum(1 for s in peers.values() if s == PeerStatus.CONNECTED)
        total     = len(peers)
        self.status_bar.config(
            text=f"🌐 Port {self.port}  |  Peers: {connected}/{total} đang kết nối"
        )

    def _update_char_count(self, event=None):
        n = len(self.msg_entry.get())
        self.char_label.config(text=f"{n}/{MAX_MESSAGE_LENGTH}")
        if n > MAX_MESSAGE_LENGTH * 0.9:
            self.char_label.config(fg="#f38ba8")
        elif n > MAX_MESSAGE_LENGTH * 0.7:
            self.char_label.config(fg="#fab387")
        else:
            self.char_label.config(fg="#6c7086")

    def _tick_uptime(self):
        sel = self.peer_list.curselection()
        if sel:
            self._on_peer_select()
        self.after(1000, self._tick_uptime)

    def _log(self, text: str, tag: str = "info"):
        ts = time.strftime("%H:%M:%S")
        self.chat.config(state="normal")
        self.chat.insert("end", f"[{ts}]  {text}\n", tag)
        self.chat.see("end")
        self.chat.config(state="disabled")

    def _on_close(self):
        if self.node:
            self.node.shutdown()
        self.destroy()