# ============ PHẦN 3: VALIDATE ĐẦU VÀO ============
import ipaddress
import re

def validate_ip(ip: str) -> tuple[bool, str]:
    """
    Kiểm tra địa chỉ IP hoặc hostname.
    Trả (hợp_lệ, thông_báo_lỗi).
    """
    if not ip or not ip.strip():
        return False, "Địa chỉ IP không được để trống"
    ip = ip.strip()
    try:
        ipaddress.ip_address(ip)
        return True, ""
    except ValueError:
        pass
    if ip == "localhost":
        return True, ""
    hostname_re = re.compile(
        r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*"
        r"[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$"
    )
    if hostname_re.match(ip):
        return True, ""
    return False, f"'{ip}' không phải IP hợp lệ\nVí dụ: 192.168.1.5 | 127.0.0.1 | localhost"


def validate_port(port_str: str) -> tuple[bool, int, str]:
    """
    Kiểm tra chuỗi port.
    Trả (hợp_lệ, giá_trị_int, cảnh_báo_hoặc_lỗi).
    """
    try:
        port = int(port_str.strip())
    except (ValueError, AttributeError):
        return False, 0, f"Port phải là số nguyên (nhập: '{port_str}')"

    if port < 1 or port > 65535:
        return False, 0, f"Port phải từ 1–65535 (nhập: {port})"
    if port < 1024:
        return True, port, f"Port {port} là port hệ thống, cần quyền admin"
    return True, port, ""
