# user_config.py

# Định nghĩa các quyền hạn cụ thể. Key là tên quyền (nên dùng hằng số), value là mô tả (tùy chọn).
PERMISSIONS = {
    "VIEW_ALL_DATA": "Xem tất cả dữ liệu",
    "EDIT_ALL_DATA": "Sửa tất cả dữ liệu",
    "SAVE_SYSTEM_DATA": "Lưu dữ liệu hệ thống (file menu)",

    "ACCESS_DATA_MANAGEMENT_TAB": "Truy cập tab Quản lý Dữ liệu",
    # "ACCESS_ADD_STUDENT_TAB": "Truy cập tab Thêm Sinh viên", # Sẽ được thay thế
    "ACCESS_MANAGE_STUDENTS_TAB": "Truy cập tab Quản lý Sinh viên (Danh sách, Thêm, Sửa, Xóa)",
    "SUBMIT_ADD_STUDENT": "Thực hiện thêm sinh viên",
    "EDIT_STUDENT_INFO": "Sửa thông tin sinh viên",
    "DELETE_STUDENT": "Xóa sinh viên",
    "ACCESS_MANAGE_SUBJECTS_TAB": "Truy cập tab Quản lý Môn học",
    "ADD_EDIT_SUBJECT": "Thêm/Sửa môn học",
    "DELETE_SUBJECT": "Xóa môn học",

    "ACCESS_GRADE_MANAGEMENT_TAB": "Truy cập tab Quản lý Điểm",
    "ACCESS_ENTER_GRADES_TAB": "Truy cập tab Nhập Điểm",
    "SUBMIT_ENTER_GRADES": "Thực hiện nhập điểm",
    "ACCESS_VIEW_GRADES_TAB": "Truy cập tab Xem/Xóa Điểm",
    "DELETE_GRADES": "Thực hiện xóa điểm",
    "ACCESS_EDIT_GRADES_TAB": "Truy cập tab Sửa Điểm",
    "SUBMIT_EDIT_GRADES": "Thực hiện sửa điểm",
    "ACCESS_QUICK_ENTER_GRADES_TAB": "Truy cập tab Nhập Điểm Nhanh",
    "SUBMIT_QUICK_ENTER_GRADES": "Thực hiện nhập điểm nhanh",

    "ACCESS_ANALYSIS_TAB": "Truy cập tab Phân tích & Báo cáo",
    "ACCESS_SEARCH_TAB": "Truy cập tab Tìm kiếm",
    "PERFORM_SEARCH": "Thực hiện tìm kiếm",
    "ACCESS_RANKING_TAB": "Truy cập tab Xếp hạng",
    "VIEW_RANKING": "Xem bảng xếp hạng",
    "ACCESS_REPORT_TAB": "Truy cập tab Báo cáo",
    "GENERATE_CLASS_REPORT": "Tạo báo cáo lớp",

    "ACCESS_ADMIN_TAB": "Truy cập tab Quản trị Hệ thống",
    "ACCESS_USER_MANAGEMENT_TAB": "Truy cập tab Quản lý Người dùng",
    "ADD_USER": "Thêm người dùng mới",
    "EDIT_USER_ROLE": "Sửa vai trò người dùng",
    "DELETE_USER": "Xóa người dùng",
    "RESET_USER_PASSWORD": "Đặt lại mật khẩu người dùng",
    "VIEW_OWN_GRADES_ONLY": "Chỉ xem điểm của bản thân (Sinh viên)",
}

# Ánh xạ vai trò với danh sách các quyền (sử dụng giá trị từ PERMISSIONS)
ROLES_PERMISSIONS = {
    "Admin": [
        PERMISSIONS["VIEW_ALL_DATA"], PERMISSIONS["EDIT_ALL_DATA"], PERMISSIONS["SAVE_SYSTEM_DATA"], # Dòng này có thể bị trùng nếu ACCESS_ADD_STUDENT_TAB đã bị xóa
        PERMISSIONS["ACCESS_DATA_MANAGEMENT_TAB"], PERMISSIONS["ACCESS_MANAGE_STUDENTS_TAB"],
        PERMISSIONS["SUBMIT_ADD_STUDENT"], PERMISSIONS["EDIT_STUDENT_INFO"], PERMISSIONS["DELETE_STUDENT"],
        PERMISSIONS["ACCESS_MANAGE_SUBJECTS_TAB"], PERMISSIONS["ADD_EDIT_SUBJECT"], PERMISSIONS["DELETE_SUBJECT"],
        PERMISSIONS["ACCESS_GRADE_MANAGEMENT_TAB"], PERMISSIONS["ACCESS_ENTER_GRADES_TAB"], PERMISSIONS["SUBMIT_ENTER_GRADES"],
        PERMISSIONS["ACCESS_VIEW_GRADES_TAB"], PERMISSIONS["DELETE_GRADES"],
        PERMISSIONS["ACCESS_EDIT_GRADES_TAB"], PERMISSIONS["SUBMIT_EDIT_GRADES"],
        PERMISSIONS["ACCESS_QUICK_ENTER_GRADES_TAB"], PERMISSIONS["SUBMIT_QUICK_ENTER_GRADES"],
        PERMISSIONS["ACCESS_ANALYSIS_TAB"], PERMISSIONS["ACCESS_SEARCH_TAB"], PERMISSIONS["PERFORM_SEARCH"],
        PERMISSIONS["ACCESS_RANKING_TAB"], PERMISSIONS["VIEW_RANKING"],
        PERMISSIONS["ACCESS_REPORT_TAB"], PERMISSIONS["GENERATE_CLASS_REPORT"],
        PERMISSIONS["ACCESS_ADMIN_TAB"], PERMISSIONS["ACCESS_USER_MANAGEMENT_TAB"],
        PERMISSIONS["ADD_USER"], PERMISSIONS["EDIT_USER_ROLE"], PERMISSIONS["DELETE_USER"], PERMISSIONS["RESET_USER_PASSWORD"],
    ],
    "Teacher": [
        # Giáo viên có thể được phép xem danh sách SV, tùy thuộc vào yêu cầu
        PERMISSIONS["ACCESS_DATA_MANAGEMENT_TAB"], PERMISSIONS["ACCESS_MANAGE_STUDENTS_TAB"], # Cho phép xem DS SV
        # PERMISSIONS["SUBMIT_ADD_STUDENT"], PERMISSIONS["EDIT_STUDENT_INFO"], PERMISSIONS["DELETE_STUDENT"], # Quyền thêm/sửa/xóa SV cho GV (tùy chọn)
        PERMISSIONS["ACCESS_MANAGE_SUBJECTS_TAB"], # Cho phép xem DS Môn học
        PERMISSIONS["ACCESS_GRADE_MANAGEMENT_TAB"], PERMISSIONS["ACCESS_ENTER_GRADES_TAB"], PERMISSIONS["SUBMIT_ENTER_GRADES"],
        PERMISSIONS["ACCESS_VIEW_GRADES_TAB"], PERMISSIONS["ACCESS_EDIT_GRADES_TAB"], PERMISSIONS["SUBMIT_EDIT_GRADES"],
        PERMISSIONS["ACCESS_QUICK_ENTER_GRADES_TAB"], PERMISSIONS["SUBMIT_QUICK_ENTER_GRADES"],
        PERMISSIONS["ACCESS_ANALYSIS_TAB"], PERMISSIONS["ACCESS_SEARCH_TAB"], PERMISSIONS["PERFORM_SEARCH"],
        PERMISSIONS["ACCESS_RANKING_TAB"], PERMISSIONS["VIEW_RANKING"], PERMISSIONS["ACCESS_REPORT_TAB"], PERMISSIONS["GENERATE_CLASS_REPORT"],
    ],
    "Student": [
        # Sinh viên có thể không cần truy cập tab "Dữ liệu Nguồn"
        PERMISSIONS["ACCESS_GRADE_MANAGEMENT_TAB"], PERMISSIONS["ACCESS_VIEW_GRADES_TAB"], PERMISSIONS["VIEW_OWN_GRADES_ONLY"],
        PERMISSIONS["ACCESS_ANALYSIS_TAB"], PERMISSIONS["ACCESS_RANKING_TAB"], PERMISSIONS["VIEW_RANKING"],
    ]
}