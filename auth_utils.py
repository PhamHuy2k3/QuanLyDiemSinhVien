# auth_utils.py

# CẢNH BÁO: Đây là phiên bản đơn giản hóa, KHÔNG SỬ DỤNG BĂM MẬT KHẨU.
# Trong ứng dụng thực tế, BẮT BUỘC phải băm mật khẩu để đảm bảo an toàn.

def verify_password_simple(stored_password, provided_password):
    """
    Kiểm tra mật khẩu đơn giản (so sánh chuỗi trực tiếp).
    CHỈ DÙNG CHO MỤC ĐÍCH MINH HỌA, RẤT KHÔNG AN TOÀN CHO THỰC TẾ.
    """
    return stored_password == provided_password

# --- Ví dụ về cách triển khai băm mật khẩu (KHUYẾN NGHỊ MẠNH MẼ CHO ỨNG DỤNG THỰC TẾ) ---
import hashlib
import os

def hash_password(password, salt=None):
    """Băm mật khẩu với salt. Nếu salt không được cung cấp, một salt mới sẽ được tạo."""
    if salt is None:
        salt = os.urandom(16)  # Tạo salt ngẫu nhiên, 16 bytes là đủ tốt
    elif isinstance(salt, str): # Nếu salt là hex string, chuyển về bytes
        salt = bytes.fromhex(salt)

    salted_password = salt + password.encode('utf-8')
    hashed_password = hashlib.sha256(salted_password).hexdigest()
    return salt.hex() + ":" + hashed_password  # Lưu salt (dạng hex) cùng với hash

def verify_password_hashed(stored_password_with_salt, provided_password):
    """Xác minh mật khẩu đã cung cấp với mật khẩu đã băm (có salt)."""
    try:
        salt_hex, hashed_password_stored = stored_password_with_salt.split(':', 1)
        # Không cần hash lại salt_hex, vì hash_password đã dùng salt bytes để tạo salted_provided_password
        re_hashed_provided_password = hash_password(provided_password, salt_hex) # salt_hex sẽ được chuyển thành bytes trong hash_password
        return re_hashed_provided_password == stored_password_with_salt
    except (ValueError, TypeError, AttributeError): # Bắt lỗi nếu định dạng stored_password_with_salt không đúng hoặc salt không hợp lệ
        return False