# user_manager.py
import json
import os
from user_config import ROLES_PERMISSIONS
from auth_utils import verify_password_hashed, hash_password

DATA_DIR = "data_ql_diem"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin_password" # CẢNH BÁO: Plain text

class UserManager:
    def __init__(self):
        self._ensure_data_dir_exists()
        self.users_data = self._load_users()
        self.roles_permissions = ROLES_PERMISSIONS

    def _ensure_data_dir_exists(self):
        if not os.path.exists(DATA_DIR):
            try:
                os.makedirs(DATA_DIR)
            except OSError as e:
                print(f"Lỗi: không thể tạo thư mục {DATA_DIR}: {e}")
                # Trong trường hợp nghiêm trọng, bạn có thể raise Exception ở đây

    def _load_users(self):
        if not os.path.exists(USERS_FILE):
            print(f"File {USERS_FILE} không tồn tại. Tạo file mới với người dùng admin mặc định.")
            hashed_admin_pass = hash_password(DEFAULT_ADMIN_PASSWORD)
            default_users = {
                DEFAULT_ADMIN_USERNAME: {"password_hash": hashed_admin_pass, "role": "Admin"}
            }
            self._save_users(default_users)
            return default_users
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Lỗi khi tải {USERS_FILE}: {e}. Sử dụng dữ liệu người dùng trống.")
            return {} # Trả về dict rỗng nếu có lỗi nghiêm trọng

    def _save_users(self, users_data_to_save=None):
        data_to_write = users_data_to_save if users_data_to_save is not None else self.users_data
        try:
            with open(USERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data_to_write, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Lỗi khi lưu {USERS_FILE}: {e}")
            return False

    def get_user_details(self, username):
        """Trả về thông tin chi tiết của người dùng (dict) hoặc None nếu không tìm thấy."""
        return self.users_data.get(username)

    def check_password(self, username, provided_password):
        """Kiểm tra mật khẩu người dùng."""
        user = self.get_user_details(username)
        if user:
            stored_password_hash = user.get("password_hash")
            if stored_password_hash and ":" in stored_password_hash: # Kiểm tra có phải định dạng hash không
                return verify_password_hashed(stored_password_hash, provided_password)
            # print(f"Cảnh báo: Người dùng {username} có mật khẩu không ở định dạng băm hợp lệ.")
        return False # Trả về False nếu user không tồn tại hoặc mật khẩu không đúng định dạng/không khớp

    def get_user_role(self, username):
        """Lấy vai trò của người dùng."""
        user = self.get_user_details(username)
        return user.get("role") if user else None

    def has_permission(self, username, permission_value):
        """Kiểm tra xem người dùng có một quyền cụ thể hay không (dựa trên giá trị của quyền)."""
        role = self.get_user_role(username)
        if not role:
            return False
        user_permissions_list = self.roles_permissions.get(role, [])
        return permission_value in user_permissions_list

    def get_all_users_info(self):
        """Trả về danh sách các dict chứa username và role."""
        return [{"username": uname, "role": udata.get("role", "N/A")}
                for uname, udata in self.users_data.items()]

    def add_user(self, username, password, role):
        username = username.strip()
        if not username or not password or not role:
            return False, "Tên đăng nhập, mật khẩu và vai trò không được để trống."
        if username in self.users_data:
            return False, f"Tên đăng nhập '{username}' đã tồn tại."
        if role not in self.roles_permissions:
            return False, f"Vai trò '{role}' không hợp lệ."

        hashed_pwd = hash_password(password)
        self.users_data[username] = {"password_hash": hashed_pwd, "role": role}
        if self._save_users():
            return True, f"Đã thêm người dùng '{username}' với vai trò '{role}'."
        return False, "Lỗi khi lưu dữ liệu người dùng."

    def edit_user_role(self, username, new_role):
        if username not in self.users_data:
            return False, f"Người dùng '{username}' không tồn tại."
        if new_role not in self.roles_permissions:
            return False, f"Vai trò '{new_role}' không hợp lệ."
        if username == DEFAULT_ADMIN_USERNAME and new_role != "Admin":
            return False, f"Không thể thay đổi vai trò của người dùng quản trị mặc định '{DEFAULT_ADMIN_USERNAME}'."

        self.users_data[username]["role"] = new_role
        if self._save_users():
            return True, f"Đã cập nhật vai trò cho '{username}' thành '{new_role}'."
        return False, "Lỗi khi lưu dữ liệu người dùng."

    def delete_user(self, username):
        if username not in self.users_data:
            return False, f"Người dùng '{username}' không tồn tại."
        if username == DEFAULT_ADMIN_USERNAME:
            return False, f"Không thể xóa người dùng quản trị mặc định '{DEFAULT_ADMIN_USERNAME}'."
        del self.users_data[username]
        if self._save_users():
            return True, f"Đã xóa người dùng '{username}'."
        return False, "Lỗi khi lưu dữ liệu người dùng."

    def reset_password(self, username, new_password):
        if username not in self.users_data:
            return False, f"Người dùng '{username}' không tồn tại."
        hashed_new_password = hash_password(new_password)
        self.users_data[username]["password_hash"] = hashed_new_password
        if self._save_users():
            return True, f"Đã đặt lại mật khẩu cho người dùng '{username}'."
        return False, "Lỗi khi lưu dữ liệu người dùng."