import time
import threading

class GuiLogic:
    def __init__(self, node, ui):
        """
        node: backend P2P (node/client)
        ui: giao diện (Tkinter / PyQt / ...)
        """
        self.node = node
        self.ui = ui

        self.peers = []
        self.selected_peer = None
        self.start_time = time.time()

        # đăng ký callback từ node
        self.node.on_message = self._on_message
        self.node.on_status = self._on_status
        self.node.on_peer_update = self._on_peer_update

        # chạy uptime timer
        self._start_uptime_thread()

    # CONNECT / DISCONNECT

    def _connect(self, peer_ip, peer_port):
        if not peer_ip or not peer_port:
            self._log("❌ IP hoặc Port không hợp lệ")
            return

        try:
            peer_port = int(peer_port)
            self.node.connect_peer(peer_ip, peer_port)
            self._log(f"🔌 Đang kết nối tới {peer_ip}:{peer_port}")
        except Exception as e:
            self._log(f"❌ Lỗi connect: {e}")

    def _disconnect(self):
        if not self.selected_peer:
            self._log("❌ Chưa chọn peer")
            return

        try:
            self.node.disconnect_peer(self.selected_peer)
            self._log(f"🔌 Đã ngắt kết nối {self.selected_peer}")
        except Exception as e:
            self._log(f"❌ Lỗi disconnect: {e}")

    # SEND / BROADCAST

    def _send(self):
        message = self.ui.input_box.get().strip()

        if not message:
            self._log("❌ Tin nhắn rỗng")
            return

        if not self.selected_peer:
            self._log("❌ Chưa chọn peer")
            return

        try:
            self.node.send_to(self.selected_peer, message)
            self._append_chat(f"Bạn → {self.selected_peer}: {message}")
            self.ui.input_box.clear()
            self._update_char_count()
        except Exception as e:
            self._log(f"❌ Lỗi gửi: {e}")

    def _broadcast(self):
        message = self.ui.input_box.get().strip()

        if not message:
            self._log("❌ Tin nhắn rỗng")
            return

        try:
            self.node.broadcast(message)
            self._append_chat(f"Bạn (Broadcast): {message}")
            self.ui.input_box.clear()
            self._update_char_count()
        except Exception as e:
            self._log(f"❌ Lỗi broadcast: {e}")

    # CALLBACK TỪ NODE

    def _on_message(self, peer_id, message):
        self._append_chat(f"{peer_id}: {message}")

    def _on_status(self, status):
        self._update_status_bar(status)

    def _on_peer_update(self, peers):
        self.peers = peers
        self._refresh_peers()

    # PEER LIST

    def _refresh_peers(self):
        try:
            self.ui.peer_list.clear()
            for peer in self.peers:
                self.ui.peer_list.add_item(peer)
        except Exception as e:
            self._log(f"❌ Lỗi refresh peer: {e}")

    def _on_peer_select(self, peer_id):
        self.selected_peer = peer_id
        self._log(f"👉 Đã chọn peer: {peer_id}")

    def _update_status_bar(self, text):
        try:
            self.ui.status_bar.set(text)
        except:
            pass

    # UI HELPER

    def _append_chat(self, message):
        try:
            self.ui.chat_box.append(message)
        except:
            pass

    def _log(self, message):
        try:
            self.ui.log_box.append(message)
        except:
            print(message)

    def _update_char_count(self):
        try:
            text = self.ui.input_box.get()
            self.ui.char_count.set(len(text))
        except:
            pass

    # UPTIME

    def _start_uptime_thread(self):
        def run():
            while True:
                self._tick_uptime()
                time.sleep(1)

        t = threading.Thread(target=run, daemon=True)
        t.start()

    def _tick_uptime(self):
        try:
            uptime = int(time.time() - self.start_time)
            self.ui.uptime_label.set(f"Uptime: {uptime}s")
        except:
            pass
        
    # CLOSE APP

    def _on_close(self):
        try:
            self._log("🛑 Đang tắt hệ thống...")
            self.node.shutdown()
        except:
            pass

        try:
            self.ui.close()
        except:
            pass