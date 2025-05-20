"""Constants for the application."""
from enum import Enum

# Tab names
class TabNames:
    MAIN_TAB_DATA = "Dữ liệu"
    MAIN_TAB_GRADES = "Điểm số" 
    MAIN_TAB_ANALYSIS = "Phân tích"
    MAIN_TAB_ADMIN = "Quản trị"
    
    SUB_TAB_MANAGE_STUDENTS = "Danh sách Sinh viên"
    SUB_TAB_CRUD_STUDENTS = "Thêm/Sửa/Xóa SV"
    SUB_TAB_MANAGE_SUBJECTS = "Quản lý Môn học"
    SUB_TAB_ENTER_GRADES = "Nhập Điểm"
    SUB_TAB_VIEW_GRADES = "Xem/Xóa Điểm"
    SUB_TAB_QUICK_ENTER_GRADES = "Nhập Điểm Nhanh"
    SUB_TAB_SEARCH = "Tìm kiếm Điểm"
    SUB_TAB_RANKING = "Xếp Hạng SV"
    SUB_TAB_REPORT = "Báo cáo Lớp"
    SUB_TAB_USER_MANAGEMENT = "Quản lý Người dùng"

# Column names
class ColumnNames:
    MA_SV = "Mã SV"
    HO_TEN = "Họ tên"
    LOP_HOC = "Lớp"
    TRUONG = "Trường"
    KHOA = "Khoa"
    HOC_KY = "Học kỳ"
    MON_HOC = "Môn học"
    DIEM = "Điểm"
    TIN_CHI = "Tín chỉ"

# File paths
class FilePaths:
    DATA_DIR = "data_ql_diem"
    SINH_VIEN_FILE = "sinh_vien.csv"
    MON_HOC_FILE = "mon_hoc.csv"
    DIEM_FILE = "diem_sinh_vien.csv"
    USERS_FILE = "users.json"

# Messages
class Messages:
    SUCCESS = "Thành công"
    ERROR = "Lỗi"
    WARNING = "Cảnh báo"
    CONFIRM = "Xác nhận"
    MISSING_INFO = "Thiếu thông tin"
    INVALID_INPUT = "Dữ liệu không hợp lệ"
    NO_PERMISSION = "Không có quyền"
    NO_DATA = "Không có dữ liệu"

# Status codes
class StatusCodes(Enum):
    SUCCESS = 1
    ERROR = 0
    WARNING = -1

# Validation
class Validation:
    MIN_MA_SV_LENGTH = 9
    MAX_MA_SV_LENGTH = 9
    MIN_DIEM = 0.0
    MAX_DIEM = 10.0
    MIN_TIN_CHI = 1
    MAX_TIN_CHI = 10

# UI Constants
class UI:
    WINDOW_TITLE = "Quản Lý Điểm Sinh Viên"
    WINDOW_MIN_WIDTH = 800
    WINDOW_MIN_HEIGHT = 600
    PADDING = 10
    BUTTON_WIDTH = 15
    ENTRY_WIDTH = 30
    TREE_ROW_HEIGHT = 25
