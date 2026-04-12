import socket
from protocol import PeerStatus, SEND_TIMEOUT, pack_message, recv_message
from node.client import _handle_disconnect


def _recv_loop(node, peer_addr: str):
    with node.lock:
        info = node.peers.get(peer_addr)
    if not info or info.sock is None:
        return
    sock = info.sock

    while node.running:
        try:
            msg = recv_message(sock)
            if msg is None:
                break
            if msg == "":
                continue

            with node.lock:
                if peer_addr in node.peers:
                    node.peers[peer_addr].messages_recv += 1

            node.on_message(peer_addr, msg)

        except socket.timeout:
            continue
        except OSError:
            break

    _handle_disconnect(node, peer_addr, PeerStatus.DISCONNECTED)


def send_to(node, peer_addr: str, text: str) -> tuple[bool, str]:
    with node.lock:
        info = node.peers.get(peer_addr)

    if not info or info.sock is None:
        return False, f"Không tìm thấy kết nối với {peer_addr}"
    if info.status != PeerStatus.CONNECTED:
        return False, f"{peer_addr} không ở trạng thái kết nối ({info.status.value})"

    sock = info.sock
    try:
        sock.settimeout(SEND_TIMEOUT)
        sock.sendall(pack_message(text))
        sock.settimeout(None)

        with node.lock:
            if peer_addr in node.peers:
                node.peers[peer_addr].messages_sent += 1

        return True, ""

    except socket.timeout:
        _handle_disconnect(node, peer_addr, PeerStatus.TIMEOUT)
        return False, f"Timeout ({SEND_TIMEOUT}s): {peer_addr} không nhận được tin"

    except BrokenPipeError:
        _handle_disconnect(node, peer_addr, PeerStatus.DISCONNECTED)
        return False, f"{peer_addr} đã ngắt kết nối đột ngột"

    except ConnectionResetError:
        _handle_disconnect(node, peer_addr, PeerStatus.DISCONNECTED)
        return False, f"{peer_addr} reset kết nối"

    except OSError as e:
        _handle_disconnect(node, peer_addr, PeerStatus.DISCONNECTED)
        return False, f"Lỗi gửi tin: {e}"


def broadcast(node, text: str) -> tuple[int, int, list[str]]:
    with node.lock:
        snapshot = {
            addr: info for addr, info in node.peers.items()
            if info.status == PeerStatus.CONNECTED
        }

    success, failed = 0, []
    for peer_addr in snapshot:
        ok, err = send_to(node, peer_addr, text)
        if ok:
            success += 1
        else:
            failed.append(f"{peer_addr}: {err}")

    return success, len(snapshot), failed