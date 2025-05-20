import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import matplotlib.pyplot as plt
from ttkthemes import ThemedTk
from quan_ly_diem import QuanLyDiem
from constants import * # Import các hằng số
from user_manager import UserManager
from user_config import PERMISSIONS # Import các hằng số quyền
from tabs.user_management_tab import UserManagementTab
from tabs.quick_grade_entry_tab import QuickGradeEntryTab
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
# Global flag to prevent multiple main executions
_MAIN_HAS_RUN = False

class QuanLyDiemGUI:
    def __init__(self, master):
        self.master = master
        self.ql_diem = QuanLyDiem()
        self.mon_hoc_display_to_code_map = {} # Map: "Tên MH (Mã MH)" -> Mã MH
        self.current_sv_diem_map_ten_to_ma = {} # Map: Tên MH (trong treeview Xem điểm) -> Mã MH
        self.full_sv_display_list_nhap_diem = [] # Danh sách SV đầy đủ cho tab Nhập Điểm
        self.xem_diem_column_to_ma_mh = {} # Map: treeview_column_id -> ma_mh cho tab Xem Điểm
        # self.qen_entry_widgets = {} # Đã chuyển sang QuickGradeEntryTab
        # self.qen_active_entry_item_id = None # Đã chuyển sang QuickGradeEntryTab
        self.xem_diem_selected_sv_ma_mh_to_delete = None # (ma_sv, ma_mh, hoc_ky) để xóa
        self.chart_canvas_widget = None # Để lưu trữ widget canvas của biểu đồ
        self.chart_toolbar = None # Để lưu trữ toolbar của biểu đồ
        self.chart_figure = None # Để lưu trữ đối tượng Figure
        self.user_manager = UserManager()
        self.current_user = None
        self.current_user_role = None
        self.PERMISSIONS = PERMISSIONS # Gán PERMISSIONS làm thuộc tính của instance
        self.login_window = None

        # Tên tab được import từ constants.py
        # SỬA LỖI: Khởi tạo tab_navigation_map
        self.tab_navigation_map = {
            SUB_TAB_MANAGE_STUDENTS: { # Đã sửa từ SUB_TAB_ADD_STUDENT
                "main_tab_text": MAIN_TAB_DATA,
                "sub_notebook_attr": "sub_notebook_data",
                "sub_tab_text": SUB_TAB_MANAGE_STUDENTS # Đã sửa từ SUB_TAB_ADD_STUDENT
            },
            SUB_TAB_CRUD_STUDENTS: { # Tab mới cho form CRUD SV
                "main_tab_text": MAIN_TAB_DATA,
                "sub_notebook_attr": "sub_notebook_data",
                "sub_tab_text": SUB_TAB_CRUD_STUDENTS
            },
            SUB_TAB_MANAGE_SUBJECTS: {
                "main_tab_text": MAIN_TAB_DATA,
                "sub_notebook_attr": "sub_notebook_data",
                "sub_tab_text": SUB_TAB_MANAGE_SUBJECTS
            },
             SUB_TAB_USER_MANAGEMENT: { # Thêm vào map điều hướng
                "main_tab_text": MAIN_TAB_ADMIN,
                "sub_notebook_attr": "sub_notebook_admin",
                "sub_tab_text": SUB_TAB_USER_MANAGEMENT
            },
            SUB_TAB_ENTER_GRADES: {
                "main_tab_text": MAIN_TAB_GRADES,
                "sub_notebook_attr": "sub_notebook_grades",
                "sub_tab_text": SUB_TAB_ENTER_GRADES
            },
            SUB_TAB_VIEW_GRADES: {
                "main_tab_text": MAIN_TAB_GRADES,
                "sub_notebook_attr": "sub_notebook_grades",
                "sub_tab_text": SUB_TAB_VIEW_GRADES
            },
            SUB_TAB_QUICK_ENTER_GRADES: { # Thêm vào map điều hướng
                "main_tab_text": MAIN_TAB_GRADES,
                "sub_notebook_attr": "sub_notebook_grades",
                "sub_tab_text": SUB_TAB_QUICK_ENTER_GRADES
            },
            SUB_TAB_SEARCH: {
                "main_tab_text": MAIN_TAB_ANALYSIS,
                "sub_notebook_attr": "sub_notebook_analysis",
                "sub_tab_text": SUB_TAB_SEARCH
            },
            SUB_TAB_RANKING: {
                "main_tab_text": MAIN_TAB_ANALYSIS,
                "sub_notebook_attr": "sub_notebook_analysis",
                "sub_tab_text": SUB_TAB_RANKING
            },
            SUB_TAB_REPORT: {
                "main_tab_text": MAIN_TAB_ANALYSIS,
                "sub_notebook_attr": "sub_notebook_analysis",
                "sub_tab_text": SUB_TAB_REPORT
            },
            SUB_TAB_CHARTS: { # Thêm vào map điều hướng
                "main_tab_text": MAIN_TAB_ANALYSIS,
                "sub_notebook_attr": "sub_notebook_analysis",
                "sub_tab_text": SUB_TAB_CHARTS
            }
        }

        # Ban đầu ẩn cửa sổ chính và hiển thị dialog đăng nhập
        self.master.withdraw() 
        self._show_login_dialog()


    def _initialize_main_app(self):
        """Khởi tạo giao diện ứng dụng chính sau khi đăng nhập thành công."""
        self.master.deiconify() # Hiển thị cửa sổ chính

        self.setup_styles()
        self.setup_menubar() 

        self.status_label = ttk.Label(self.master, text="Đang khởi tạo...", relief=tk.SUNKEN, anchor=tk.W, padding=(5, 2))
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.notebook = ttk.Notebook(self.master)
        # self.notebook.pack(...) sẽ được kiểm soát bởi _apply_role_permissions
        self.main_tab_frames = {} # Sẽ chứa frame của các tab chính
        
        # Tạo các tab chính - khả năng hiển thị sẽ được kiểm soát bởi vai trò
        self.setup_data_source_tab()
        self.setup_grade_management_tab()
        self.setup_analysis_reporting_tab()
        self.setup_admin_tab()
        self._populate_all_combobox_filters()
        self.update_status(f"Người dùng: {self.current_user} ({self.current_user_role}). Sẵn sàng.")
        self._apply_role_permissions() # Áp dụng các hạn chế UI dựa trên vai trò

        # Đảm bảo notebook được pack sau khi các tab đã được thêm (hoặc cấu hình)
        if not self.notebook.winfo_ismapped():
             self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

    def _show_login_dialog(self):
        print("DEBUG: _show_login_dialog() - Bắt đầu")
        if self.login_window and self.login_window.winfo_exists():
            self.login_window.lift()
            print("DEBUG: _show_login_dialog() - Cửa sổ đăng nhập đã tồn tại, được lift()")
            return
        print("DEBUG: _show_login_dialog() - Đang tạo Toplevel mới")
        # Ensure master window is at least iconified if it was withdrawn,
        # so transient and grab_set can work reliably.
        # self.master.iconify() # Temporarily iconify if withdrawn

        self.login_window = tk.Toplevel(self.master)
        self.login_window.title("Đăng nhập Hệ thống")
        # Try a fixed, simple geometry first to rule out calculation issues
        self.login_window.geometry("380x220+200+200") # Fixed position for testing
        self.login_window.resizable(False, False)
        
        # Attempt to make it viewable *before* transient and grab_set
        print("DEBUG: _show_login_dialog() - Attempting initial deiconify/lift/update.")
        self.login_window.deiconify()
        self.login_window.lift()
        self.login_window.attributes('-topmost', True)
        self.login_window.update_idletasks() # Process deiconify and geometry
        print(f"DEBUG: login_window.winfo_viewable() after initial deiconify/lift/update: {self.login_window.winfo_viewable()}")

        self.login_window.transient(self.master) # Associate with master
        print("DEBUG: _show_login_dialog() - transient(master) called.")

        # Now that it's hopefully viewable (or at least mapped), set grab
        self.login_window.grab_set() # Make it modal (must be visible or iconified)
        print("DEBUG: _show_login_dialog() - grab_set() called.")

        # self.master.update_idletasks() # This was for master, login_window updates are more relevant now
        self.login_window.update_idletasks() # Ensure grab_set effects are processed

        login_frame = ttk.Frame(self.login_window, padding="20")
        login_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(login_frame, text="Tên đăng nhập:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.login_username_entry = ttk.Entry(login_frame, width=30)
        self.login_username_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        ttk.Label(login_frame, text="Mật khẩu:").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.login_password_entry = ttk.Entry(login_frame, show="*", width=30)
        self.login_password_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

        self.login_status_label = ttk.Label(login_frame, text="", foreground="red", wraplength=300)
        self.login_status_label.grid(row=2, column=0, columnspan=2, pady=(5,10))

        button_frame = ttk.Frame(login_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        login_button = ttk.Button(button_frame, text="Đăng nhập", command=self._attempt_login, style="Accent.TButton")
        login_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Thoát", command=self._on_login_close)
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        self.login_password_entry.bind("<Return>", lambda event: self._attempt_login())
        self.login_username_entry.bind("<Return>", lambda event: self.login_password_entry.focus_set())

        self.login_username_entry.focus_set()
        self.login_window.protocol("WM_DELETE_WINDOW", self._on_login_close)

        # Final update before wait_window to ensure all widgets inside are also ready
        self.login_window.update_idletasks()
        print("DEBUG: _show_login_dialog() - Widgets in login_window configured, final update_idletasks() called.")
        
        if not self.login_window.winfo_viewable():
            print("CRITICAL DEBUG: login_window is NOT viewable before wait_window!")
            # This is a strong indication of a problem.
            # Forcing deiconify again.
            print("CRITICAL DEBUG: Re-forcing deiconify/lift/update.")
            self.login_window.deiconify()
            self.login_window.lift()
            self.login_window.update_idletasks() # Corrected: update login_window, not master
            print(f"CRITICAL DEBUG: login_window.winfo_viewable() after RE-forcing: {self.login_window.winfo_viewable()}")

        print("DEBUG: _show_login_dialog() - Calling login_window.wait_window()")
        self.login_window.wait_window() # This will block until login_window is destroyed
        print("DEBUG: _show_login_dialog() - login_window.wait_window() has returned.")
        # self.master.deiconify() # Deiconify master if it was iconified earlier
    def _attempt_login(self):
        print("DEBUG: _attempt_login() - Bắt đầu")
        username = self.login_username_entry.get().strip()
        password = self.login_password_entry.get().strip()

        if not username or not password:
            self.login_status_label.config(text="Tên đăng nhập và mật khẩu không được để trống.")
            print("DEBUG: _attempt_login() - Tên đăng nhập hoặc mật khẩu trống")
            return

        print(f"DEBUG: _attempt_login() - Đang kiểm tra user: {username}")
        if self.user_manager.check_password(username, password):
            self.current_user = username
            self.current_user_role = self.user_manager.get_user_role(username)
            if self.login_window:
                self.login_window.destroy()
                self.login_window = None
            self._initialize_main_app()
            print(f"DEBUG: _attempt_login() - Đăng nhập thành công cho {username}")
        else:
            self.login_status_label.config(text="Tên đăng nhập hoặc mật khẩu không đúng.")
            self.login_password_entry.delete(0, tk.END)
            print(f"DEBUG: _attempt_login() - Đăng nhập thất bại cho {username}")

    def _on_login_close(self):
        print("DEBUG: _on_login_close() - Bắt đầu")
        if self.login_window and self.login_window.winfo_exists():
            self.login_window.destroy()
            self.login_window = None
            print("DEBUG: _on_login_close() - Cửa sổ đăng nhập đã bị hủy.")
        if not self.current_user: # Chỉ thoát nếu chưa đăng nhập
            print("DEBUG: _on_login_close() - Người dùng chưa đăng nhập, đang hủy master window...")
            self.master.destroy()
            print("DEBUG: _on_login_close() - Master window đã bị hủy.")
    def _logout(self):
        self.current_user = None
        self.current_user_role = None

        # Ẩn hoặc phá hủy các widget của ứng dụng chính
        if hasattr(self, 'notebook') and self.notebook.winfo_exists():
            self.notebook.pack_forget() 
        if hasattr(self, 'status_label') and self.status_label.winfo_exists():
            self.status_label.pack_forget()
        
        if hasattr(self, 'master') and self.master.cget('menu'):
            # Xóa menubar cũ, một menubar mới sẽ được tạo trong _initialize_main_app
            # khi người dùng đăng nhập lại.
            self.master.config(menu=tk.Menu(self.master)) 

        # Hủy các frame tab chính để đảm bảo chúng được tạo mới khi đăng nhập lại
        # và không bị lỗi "already managed" nếu pack_forget không đủ.
        for widget_key in list(self.main_tab_frames.keys()):
            widget = self.main_tab_frames.pop(widget_key)
            if widget and widget.winfo_exists():
                widget.destroy()
        
        # Quan trọng: Hủy các sub-notebooks để tránh lỗi khi tạo lại tab
        for sub_notebook_attr in ["sub_notebook_data", "sub_notebook_grades", "sub_notebook_analysis"]:
            if hasattr(self, sub_notebook_attr):
                sub_nb = getattr(self, sub_notebook_attr)
                if sub_nb and sub_nb.winfo_exists():
                    sub_nb.destroy()
                delattr(self, sub_notebook_attr) # Xóa thuộc tính
        
        self.master.withdraw()
        self._show_login_dialog()

    def setup_menubar(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tệp", menu=file_menu)
        # Lưu ID của menu item để có thể thay đổi trạng thái sau này
        self.file_menu_save_all_id = "Lưu tất cả dữ liệu" 
        file_menu.add_command(label=self.file_menu_save_all_id, command=self._save_all_data)
        file_menu.add_command(label="Đăng xuất", command=self._logout)
        file_menu.add_separator()
        file_menu.add_command(label="Thoát", command=self.master.quit)

        functions_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Chức năng", menu=functions_menu)
        
        # Sử dụng hằng số từ constants.py
        functions_menu.add_command(label="Danh sách Sinh viên", command=lambda: self._switch_to_tab_by_text(SUB_TAB_MANAGE_STUDENTS)) # Sửa SUB_TAB_ADD_STUDENT
        functions_menu.add_command(label="Thêm/Sửa/Xóa SV", command=lambda: self._switch_to_tab_by_text(SUB_TAB_CRUD_STUDENTS))
        functions_menu.add_command(label="Quản lý Môn học", command=lambda: self._switch_to_tab_by_text(SUB_TAB_MANAGE_SUBJECTS))
        functions_menu.add_separator()
        functions_menu.add_command(label="Nhập Điểm", command=lambda: self._switch_to_tab_by_text(SUB_TAB_ENTER_GRADES))
        functions_menu.add_command(label="Xem/Xóa Điểm", command=lambda: self._switch_to_tab_by_text(SUB_TAB_VIEW_GRADES))
        functions_menu.add_command(label="Nhập Điểm Nhanh", command=lambda: self._switch_to_tab_by_text(SUB_TAB_QUICK_ENTER_GRADES))
        functions_menu.add_separator()
        functions_menu.add_command(label="Tìm kiếm Điểm", command=lambda: self._switch_to_tab_by_text(SUB_TAB_SEARCH))
        functions_menu.add_command(label="Xếp Hạng Sinh viên", command=lambda: self._switch_to_tab_by_text(SUB_TAB_RANKING))
        functions_menu.add_command(label="Báo cáo Lớp", command=lambda: self._switch_to_tab_by_text(SUB_TAB_REPORT))
        functions_menu.add_separator() 
        functions_menu.add_command(label="Biểu đồ Phân tích", command=lambda: self._switch_to_tab_by_text(SUB_TAB_CHARTS))
        # Định nghĩa admin_menu_item_text ở đây để cả setup_menubar và _apply_role_permissions có thể dùng
        # một cách nhất quán. Hoặc, nếu _apply_role_permissions không cần truy cập biến này trực tiếp
        # mà chỉ cần chuỗi ký tự, thì việc định nghĩa ở đây là đủ cho setup_menubar.
        admin_menu_item_text = "Quản lý Người dùng"

    def _switch_to_tab_by_text(self, tab_key): # Thay tab_text bằng tab_key
        """Chuyển đến tab dựa trên key của tab (thường là tên tab con)."""
        nav_info = self.tab_navigation_map.get(tab_key) # Sử dụng tab_key
        if not nav_info:
            self.update_status(f"Lỗi: Không tìm thấy thông tin điều hướng cho tab key '{tab_key}'")
            print(f"Lỗi: Không tìm thấy thông tin điều hướng cho tab key '{tab_key}'")
            return

        main_tab_text_target = nav_info["main_tab_text"]
        sub_notebook_attr_name = nav_info["sub_notebook_attr"]
        sub_tab_text_target = nav_info["sub_tab_text"]

        main_tab_selected = False
        for i, main_tab_frame_widget_id in enumerate(self.notebook.tabs()): # Sửa tên biến
            if self.notebook.tab(main_tab_frame_widget_id, "text") == main_tab_text_target:
                self.notebook.select(main_tab_frame_widget_id)
                main_tab_selected = True
                break
        
        if not main_tab_selected:
            self.update_status(f"Lỗi: Không tìm thấy tab chính '{main_tab_text_target}'")
            print(f"Lỗi: Không tìm thấy tab chính '{main_tab_text_target}'")
            return

        sub_notebook_widget = getattr(self, sub_notebook_attr_name, None)
        if sub_notebook_widget:
            sub_tab_selected = False
            # Đảm bảo sub_notebook_widget đã được pack và hiển thị
            self.master.update_idletasks() # Quan trọng để đảm bảo widget đã sẵn sàng

            for j, sub_tab_frame_widget_id in enumerate(sub_notebook_widget.tabs()): # Sửa tên biến
                if sub_notebook_widget.tab(sub_tab_frame_widget_id, "text") == sub_tab_text_target:
                    sub_notebook_widget.select(sub_tab_frame_widget_id)
                    sub_tab_selected = True
                    # Event <<NotebookTabChanged>> của sub-notebook sẽ tự động kích hoạt
                    # và gọi các hàm on_sub_tab_*_change tương ứng.
                    return # Thoát sau khi chọn thành công
            if not sub_tab_selected:
                self.update_status(f"Lỗi: Không tìm thấy tab con '{sub_tab_text_target}' trong {sub_notebook_attr_name}")
                print(f"Lỗi: Không tìm thấy tab con '{sub_tab_text_target}' trong {sub_notebook_attr_name}")
        else:
            self.update_status(f"Lỗi: Không tìm thấy sub-notebook '{sub_notebook_attr_name}'")
            print(f"Lỗi: Không tìm thấy sub-notebook '{sub_notebook_attr_name}'")

    def _save_all_data(self):
        self.ql_diem.save_data_sv()
        self.ql_diem.save_data_mh()
        messagebox.showinfo("Lưu dữ liệu", "Đã lưu tất cả dữ liệu sinh viên và môn học!")
        self.update_status("Đã lưu tất cả dữ liệu.")

    def _apply_role_permissions(self):
        """Điều chỉnh các thành phần UI dựa trên vai trò của người dùng hiện tại."""
        if not self.current_user_role or not self.current_user:
            # Nếu không có vai trò hoặc người dùng, có thể ẩn tất cả hoặc hiển thị thông báo
            # Hiện tại, giả sử điều này không xảy ra nếu đã đăng nhập thành công
            return 

        # --- Tiện ích kiểm tra quyền ---
        def has_perm(permission_key_str):
            # Lấy giá trị của hằng số quyền từ chuỗi tên quyền
            permission_value = PERMISSIONS.get(permission_key_str)
            if permission_value is None:
                print(f"Cảnh báo: Khóa quyền '{permission_key_str}' không tồn tại trong PERMISSIONS dict.")
                return False
            return self.user_manager.has_permission(self.current_user, permission_value)

        # --- Kiểm soát Menu Items ---
        main_menu = self.master.nametowidget(self.master.cget('menu'))
        if main_menu:
            try:
                file_menu = main_menu.nametowidget(main_menu.winfo_children()[0]) # File menu
                file_menu.entryconfig(self.file_menu_save_all_id, state=tk.NORMAL if has_perm("SAVE_SYSTEM_DATA") else tk.DISABLED)
            except (tk.TclError, IndexError): print("Lỗi cấu hình menu Tệp.")
            
            try:
                functions_menu = main_menu.nametowidget(main_menu.winfo_children()[1]) # Functions menu
                menu_items_map = { # Ánh xạ label menu tới key quyền (tên hằng số trong PERMISSIONS)
                    "Danh sách Sinh viên": "ACCESS_MANAGE_STUDENTS_TAB", # Sửa key quyền cho phù hợp với tab mới
                    "Quản lý Môn học": "ACCESS_MANAGE_SUBJECTS_TAB",
                    "Thêm/Sửa/Xóa SV": "ACCESS_CRUD_STUDENTS_TAB", # Key quyền cho tab CRUD SV
                    "Nhập Điểm": "ACCESS_ENTER_GRADES_TAB",
                    "Xem/Xóa Điểm": "ACCESS_VIEW_GRADES_TAB",
                    "Nhập Điểm Nhanh": "ACCESS_QUICK_ENTER_GRADES_TAB",
                    "Tìm kiếm Điểm": "ACCESS_SEARCH_TAB",
                    "Xếp Hạng Sinh viên": "ACCESS_RANKING_TAB",
                    "Báo cáo Lớp": "ACCESS_REPORT_TAB",
                    "Quản lý Người dùng": "ACCESS_USER_MANAGEMENT_TAB",
                    "Biểu đồ Phân tích": "ACCESS_CHARTS_TAB", # Sử dụng trực tiếp chuỗi ký tự ở đây
                }
                for i in range(functions_menu.index(tk.END) + 1):
                    try:
                        label = functions_menu.entrycget(i, "label")
                        if label and label in menu_items_map:
                            perm_key_str = menu_items_map[label]
                            functions_menu.entryconfig(i, state=tk.NORMAL if has_perm(perm_key_str) else tk.DISABLED)
                    except tk.TclError: continue # Bỏ qua separator
            except (tk.TclError, IndexError): print("Lỗi cấu hình menu Chức năng.")

        # --- Kiểm soát các Tab Chính và Tab Con ---
        # Tab Quản lý Dữ liệu và các tab con
        self._configure_tab_visibility(self.notebook, self.main_tab_frames.get(MAIN_TAB_DATA), "ACCESS_DATA_MANAGEMENT_TAB")
        if hasattr(self, 'sub_notebook_data'):
            self._configure_tab_visibility(self.sub_notebook_data, 0, "ACCESS_MANAGE_STUDENTS_TAB") # Tab Danh sách SV
            self._configure_tab_visibility(self.sub_notebook_data, 1, "ACCESS_CRUD_STUDENTS_TAB") # Tab Thêm/Sửa/Xóa SV
            self._configure_tab_visibility(self.sub_notebook_data, 1, "ACCESS_MANAGE_SUBJECTS_TAB") # QL Môn học
        self._configure_tab_visibility(self.notebook, self.main_tab_frames.get(MAIN_TAB_ADMIN), "ACCESS_ADMIN_TAB")
        if hasattr(self, 'sub_notebook_admin'):
            self._configure_tab_visibility(self.sub_notebook_admin, 0, "ACCESS_USER_MANAGEMENT_TAB") # QL Người dùng
        # Tab Quản lý Điểm và các tab con
        self._configure_tab_visibility(self.notebook, self.main_tab_frames.get(MAIN_TAB_GRADES), "ACCESS_GRADE_MANAGEMENT_TAB")
        if hasattr(self, 'sub_notebook_grades'):
            self._configure_tab_visibility(self.sub_notebook_grades, 0, "ACCESS_ENTER_GRADES_TAB") # Nhập Điểm
            self._configure_tab_visibility(self.sub_notebook_grades, 1, "ACCESS_VIEW_GRADES_TAB")  # Xem/Xóa
            self._configure_tab_visibility(self.sub_notebook_grades, 2, "ACCESS_QUICK_ENTER_GRADES_TAB") # Nhập Nhanh (index is now 2)

        # Tab Phân tích & Báo cáo và các tab con
        self._configure_tab_visibility(self.notebook, self.main_tab_frames.get(MAIN_TAB_ANALYSIS), "ACCESS_ANALYSIS_TAB")
        if hasattr(self, 'sub_notebook_analysis'):
            self._configure_tab_visibility(self.sub_notebook_analysis, 0, "ACCESS_SEARCH_TAB")    # Tìm kiếm
            self._configure_tab_visibility(self.sub_notebook_analysis, 1, "ACCESS_RANKING_TAB")   # Xếp hạng
            self._configure_tab_visibility(self.sub_notebook_analysis, 2, "ACCESS_REPORT_TAB") 
            self._configure_tab_visibility(self.sub_notebook_analysis, 3, "ACCESS_CHARTS_TAB")    # Báo cáo
        
    def _export_treeview_to_csv(self, treeview_widget, default_filename="export.csv"):
        if not treeview_widget.get_children():
            messagebox.showinfo("Thông tin", "Không có dữ liệu để xuất.")
            self.update_status("Không có dữ liệu để xuất CSV.")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=default_filename, title="Lưu file CSV"
        )
        if not filepath: 
            self.update_status("Đã hủy thao tác xuất CSV.")
            return
        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                columns = treeview_widget["columns"]
                header_texts = [treeview_widget.heading(col)["text"] for col in columns]
                writer.writerow(header_texts)
                for item_id in treeview_widget.get_children():
                    row_values = treeview_widget.item(item_id)["values"]
                    writer.writerow(row_values)
            messagebox.showinfo("Thành công", f"Dữ liệu đã xuất ra:\n{filepath}")
            self.update_status(f"Đã xuất dữ liệu ra {filepath}")
        except Exception as e:
            messagebox.showerror("Lỗi Xuất File", f"Không thể xuất file CSV: {e}")
            self.update_status(f"Lỗi khi xuất CSV: {e}")

    def _populate_all_combobox_filters(self):
        self._populate_student_form_comboboxes() # Đổi tên hàm ở đây
        self._populate_mon_hoc_comboboxes() 
        self._populate_search_filters() 
        self._populate_xh_filters()
        self._populate_nhap_diem_sv_combobox()
        self._populate_xem_diem_filters()
        self._populate_nhap_diem_filters()
        self._populate_bao_cao_lop_filter() # Thêm hàm populate cho combobox báo cáo lớp
        self._populate_hoc_ky_comboboxes_for_all_tabs() # Gọi sau khi các tab UI (bao gồm cả quick_grade_entry_tab_manager) đã được khởi tạo


    # SỬA LỖI: Định nghĩa hàm _populate_hoc_ky_comboboxes
    def _populate_hoc_ky_comboboxes(self, *combos_with_defaults):
        """
        Populates một hoặc nhiều học kỳ comboboxes.
        Mỗi argument là một tuple: (combobox_widget, default_text)
        """
        # Giả sử self.ql_diem có phương thức lay_tat_ca_hoc_ky_da_nhap_diem()
        # trả về một list các chuỗi học kỳ đã được sắp xếp và duy nhất.
        all_hoc_ky_values = self.ql_diem.lay_tat_ca_hoc_ky_da_nhap_diem()
        
        for combo_widget, default_text in combos_with_defaults:
            if not isinstance(combo_widget, ttk.Combobox):
                print(f"Warning: Đối tượng truyền vào không phải Combobox: {combo_widget}")
                self.update_status(f"Lỗi cấu hình combobox học kỳ.")
                continue

            current_val = combo_widget.get()
            
            # Xử lý đặc biệt cho combobox Xếp hạng
            if combo_widget == getattr(self, 'combo_hoc_ky_xep_hang', None):
                # "Tất cả" từ _for_all_tabs nghĩa là "Tích lũy" cho Xếp hạng
                actual_default = "Tích lũy" if default_text == "Tất cả" else default_text
                combo_values = [actual_default] + all_hoc_ky_values
            else:
                combo_values = [default_text] + all_hoc_ky_values
            
            combo_widget['values'] = combo_values

            if current_val in combo_values:
                combo_widget.set(current_val)
            else:
                if combo_widget == getattr(self, 'combo_hoc_ky_xep_hang', None):
                     combo_widget.set("Tích lũy") # Mặc định cho xếp hạng
                else:
                     combo_widget.set(default_text)


    def on_sub_tab_data_change(self, event):
        sub_notebook = event.widget
        try:
            current_tab_index = sub_notebook.index("current")
            selected_sub_tab_text = sub_notebook.tab(current_tab_index, "text")

            if selected_sub_tab_text == SUB_TAB_MANAGE_STUDENTS: # Sửa SUB_TAB_ADD_STUDENT
                self._populate_student_form_comboboxes() # Đổi tên hàm ở đây
                self._populate_student_filters_and_treeview() # Cũng cần populate treeview và filter
                self.update_status(f"Chuyển đến tab: {SUB_TAB_MANAGE_STUDENTS}") 
            elif selected_sub_tab_text == SUB_TAB_CRUD_STUDENTS:
                self._populate_student_form_comboboxes() # Populate combobox cho form
                self._clear_student_form_and_selection(show_status=True) # Đảm bảo form ở trạng thái thêm mới
                self.update_status(f"Chuyển đến tab: {SUB_TAB_MANAGE_STUDENTS}") # Sửa SUB_TAB_ADD_STUDENT
            elif selected_sub_tab_text == SUB_TAB_MANAGE_SUBJECTS:
                if hasattr(self, 'hien_thi_danh_sach_mon_hoc'): self.hien_thi_danh_sach_mon_hoc()
                self.update_status(f"Chuyển đến tab: {SUB_TAB_MANAGE_SUBJECTS}")
        except tk.TclError:
            
            self.update_status("Lỗi khi xác định tab con hiện tại.")


    def on_sub_tab_grades_change(self, event):
        sub_notebook = event.widget
        selected_sub_tab_text = sub_notebook.tab(sub_notebook.index("current"), "text")
        if selected_sub_tab_text == SUB_TAB_ENTER_GRADES:
            self._populate_nhap_diem_sv_combobox()
            self._populate_nhap_diem_filters()
            self._populate_mon_hoc_comboboxes() # Đảm bảo combobox môn học được cập nhật
            if hasattr(self, 'combo_hoc_ky_nhap_diem'): self._populate_hoc_ky_comboboxes((self.combo_hoc_ky_nhap_diem, "Chọn học kỳ"))
            self.update_status(f"Chuyển đến tab: {SUB_TAB_ENTER_GRADES}")
        elif selected_sub_tab_text == SUB_TAB_VIEW_GRADES:
            self._populate_xem_diem_filters()
            if hasattr(self, 'combo_hoc_ky_xem_diem'): self._populate_hoc_ky_comboboxes((self.combo_hoc_ky_xem_diem, "Tất cả")) # This one is fine for "Xem Điểm"
            self.hien_thi_bang_diem_sinh_vien()
            self.update_status(f"Chuyển đến tab: {SUB_TAB_VIEW_GRADES}")
        elif selected_sub_tab_text == SUB_TAB_QUICK_ENTER_GRADES:
            if hasattr(self, 'quick_grade_entry_tab_manager') and self.quick_grade_entry_tab_manager:
                self.quick_grade_entry_tab_manager.populate_filters()
            self.update_status(f"Chuyển đến tab: {SUB_TAB_QUICK_ENTER_GRADES}")


    def on_sub_tab_analysis_change(self, event):
        sub_notebook = event.widget
        selected_sub_tab_text = sub_notebook.tab(sub_notebook.index("current"), "text")
        if selected_sub_tab_text == SUB_TAB_SEARCH:
            self._populate_search_filters()
            self._populate_mon_hoc_comboboxes() 
            if hasattr(self, 'combo_hoc_ky_tim_kiem'): self._populate_hoc_ky_comboboxes((self.combo_hoc_ky_tim_kiem, "Tất cả"))
            self.update_status(f"Chuyển đến tab: {SUB_TAB_SEARCH}")
        elif selected_sub_tab_text == SUB_TAB_RANKING:
            self._populate_xh_filters()
            if hasattr(self, 'combo_hoc_ky_xep_hang'): self._populate_hoc_ky_comboboxes((self.combo_hoc_ky_xep_hang, "Tất cả")) # "Tất cả" ở đây sẽ được map sang "Tích lũy"
            self.hien_thi_xep_hang() # Hiển thị bảng xếp hạng khi chuyển tab
            self.update_status(f"Chuyển đến tab: {SUB_TAB_RANKING}")
        elif selected_sub_tab_text == SUB_TAB_REPORT:
            self._populate_bao_cao_lop_filter() # Cập nhật combobox lớp khi chuyển sang tab này
            self.update_status(f"Chuyển đến tab: {SUB_TAB_REPORT}")
        elif selected_sub_tab_text == SUB_TAB_CHARTS:
            self._populate_chart_filters() # Populate filter cho tab biểu đồ
            self.update_status(f"Chuyển đến tab: {SUB_TAB_CHARTS}")
            self._clear_chart_area() # Xóa biểu đồ cũ khi chuyển tab
    def on_sub_tab_admin_change(self, event):
        # Hiện tại chỉ có 1 tab con là UserManagement, nó tự xử lý khi được chọn
        # thông qua phương thức on_tab_selected() của nó.
        if hasattr(self, 'user_management_tab_manager') and self.user_management_tab_manager:
            # Gọi phương thức on_tab_selected của UserManagementTab để nó tự làm mới
            self.user_management_tab_manager.on_tab_selected()
    def _populate_hoc_ky_comboboxes_for_all_tabs(self):
        combos_to_populate = []
        # ... (các combobox khác)
        if hasattr(self, 'combo_hoc_ky_nhap_diem'):
            combos_to_populate.append((self.combo_hoc_ky_nhap_diem, "Chọn học kỳ"))
        if hasattr(self, 'combo_hoc_ky_xem_diem'):
            combos_to_populate.append((self.combo_hoc_ky_xem_diem, "Tất cả"))
        if hasattr(self, 'combo_hoc_ky_tim_kiem'):
            combos_to_populate.append((self.combo_hoc_ky_tim_kiem, "Tất cả"))
        # Đối với tab Nhập Điểm Nhanh, việc populate combobox học kỳ sẽ do QuickGradeEntryTab tự quản lý
        if hasattr(self, 'quick_grade_entry_tab_manager') and self.quick_grade_entry_tab_manager and hasattr(self.quick_grade_entry_tab_manager, 'combo_qen_hoc_ky'):
            combos_to_populate.append((self.quick_grade_entry_tab_manager.combo_qen_hoc_ky, "Chọn học kỳ"))

        if hasattr(self, 'combo_hoc_ky_xep_hang'): 
            combos_to_populate.append((self.combo_hoc_ky_xep_hang, "Tất cả")) # "Tất cả" sẽ được xử lý thành "Tích lũy" trong _populate_hoc_ky_comboboxes
        
        if combos_to_populate:
            self._populate_hoc_ky_comboboxes(*combos_to_populate)

    def _configure_tab_visibility(self, notebook_widget, tab_identifier, permission_key_str):
        """Helper để cấu hình trạng thái (enabled/disabled) của một tab."""
        if not notebook_widget or not notebook_widget.winfo_exists(): return

        permission_value = PERMISSIONS.get(permission_key_str)
        if permission_value is None:
            print(f"Cảnh báo: Khóa quyền '{permission_key_str}' không tồn tại trong PERMISSIONS dict khi cấu hình tab.")
            # Mặc định là disable nếu quyền không xác định
            try: notebook_widget.tab(tab_identifier, state='disabled')
            except tk.TclError: pass # Bỏ qua nếu tab_identifier không hợp lệ (ví dụ: frame đã bị destroy)
            return
            
        can_access = self.user_manager.has_permission(self.current_user, permission_value)
        try: notebook_widget.tab(tab_identifier, state='normal' if can_access else 'disabled')
        except tk.TclError: pass
    # ... (setup_data_source_tab, setup_grade_management_tab, setup_analysis_reporting_tab giữ nguyên) ...
    def setup_data_source_tab(self):
        main_frame = ttk.Frame(self.notebook, padding="5") 
        self.main_tab_frames[MAIN_TAB_DATA] = main_frame
        self.notebook.add(main_frame, text=MAIN_TAB_DATA)

        self.sub_notebook_data = ttk.Notebook(main_frame)
        self.sub_notebook_data.pack(fill="both", expand=True, padx=5, pady=5)

        # Tab 1: Danh sách Sinh viên (Chỉ hiển thị, lọc, tìm kiếm)
        sub_list_sv_frame = ttk.Frame(self.sub_notebook_data, padding="15")
        self.sub_notebook_data.add(sub_list_sv_frame, text=SUB_TAB_MANAGE_STUDENTS)
        self.setup_list_students_tab(sub_list_sv_frame) # Hàm mới chỉ để hiển thị danh sách

        # Tab 2: Thêm/Sửa/Xóa Sinh viên (Form nhập liệu và các nút)
        sub_crud_sv_frame = ttk.Frame(self.sub_notebook_data, padding="15")
        self.sub_notebook_data.add(sub_crud_sv_frame, text=SUB_TAB_CRUD_STUDENTS)
        self.setup_crud_students_form_tab(sub_crud_sv_frame) # Hàm mới cho form
        
        sub_ql_mh_frame = ttk.Frame(self.sub_notebook_data, padding="15")
        self.sub_notebook_data.add(sub_ql_mh_frame, text=SUB_TAB_MANAGE_SUBJECTS)
        self.setup_ql_mon_hoc_tab(sub_ql_mh_frame)
        
        self.sub_notebook_data.bind("<<NotebookTabChanged>>", self.on_sub_tab_data_change)

    def setup_grade_management_tab(self):
        main_frame = ttk.Frame(self.notebook, padding="5")
        self.main_tab_frames[MAIN_TAB_GRADES] = main_frame
        self.notebook.add(main_frame, text=MAIN_TAB_GRADES)

        self.sub_notebook_grades = ttk.Notebook(main_frame)
        self.sub_notebook_grades.pack(fill="both", expand=True, padx=5, pady=5)

        sub_nhap_diem_frame = ttk.Frame(self.sub_notebook_grades, padding="15")
        self.sub_notebook_grades.add(sub_nhap_diem_frame, text=SUB_TAB_ENTER_GRADES)
        self.setup_nhap_diem_tab(sub_nhap_diem_frame)

        sub_xem_xoa_diem_frame = ttk.Frame(self.sub_notebook_grades, padding="15")
        self.sub_notebook_grades.add(sub_xem_xoa_diem_frame, text=SUB_TAB_VIEW_GRADES)
        self.setup_xem_xoa_diem_tab(sub_xem_xoa_diem_frame)

        # Thêm tab Nhập Điểm Nhanh
        sub_nhap_diem_nhanh_frame = ttk.Frame(self.sub_notebook_grades, padding="15")
        self.sub_notebook_grades.add(sub_nhap_diem_nhanh_frame, text=SUB_TAB_QUICK_ENTER_GRADES)
        self.quick_grade_entry_tab_manager = QuickGradeEntryTab(sub_nhap_diem_nhanh_frame, self)

        self.sub_notebook_grades.bind("<<NotebookTabChanged>>", self.on_sub_tab_grades_change)

    def setup_analysis_reporting_tab(self):
        main_frame = ttk.Frame(self.notebook, padding="5")
        self.main_tab_frames[MAIN_TAB_ANALYSIS] = main_frame
        self.notebook.add(main_frame, text=MAIN_TAB_ANALYSIS)

        self.sub_notebook_analysis = ttk.Notebook(main_frame)
        self.sub_notebook_analysis.pack(fill="both", expand=True, padx=5, pady=5)

        sub_tim_kiem_frame = ttk.Frame(self.sub_notebook_analysis, padding="15")
        self.sub_notebook_analysis.add(sub_tim_kiem_frame, text=SUB_TAB_SEARCH)
        self.setup_tim_kiem_tab(sub_tim_kiem_frame)

        sub_xep_hang_frame = ttk.Frame(self.sub_notebook_analysis, padding="15")
        self.sub_notebook_analysis.add(sub_xep_hang_frame, text=SUB_TAB_RANKING)
        self.setup_xep_hang_tab(sub_xep_hang_frame)

        sub_bao_cao_frame = ttk.Frame(self.sub_notebook_analysis, padding="15")
        self.sub_notebook_analysis.add(sub_bao_cao_frame, text=SUB_TAB_REPORT)
        self.setup_bao_cao_tab(sub_bao_cao_frame)
        sub_charts_frame = ttk.Frame(self.sub_notebook_analysis, padding="15")
        self.sub_notebook_analysis.add(sub_charts_frame, text=SUB_TAB_CHARTS)
        self.setup_charts_tab(sub_charts_frame)
        self.sub_notebook_analysis.bind("<<NotebookTabChanged>>", self.on_sub_tab_analysis_change)
    def setup_admin_tab(self):
        main_frame = ttk.Frame(self.notebook, padding="5")
        self.main_tab_frames[MAIN_TAB_ADMIN] = main_frame
        # Tab này sẽ được thêm vào notebook, và _configure_tab_visibility sẽ ẩn/hiện nó.
        self.notebook.add(main_frame, text=MAIN_TAB_ADMIN, state='disabled') # Mặc định disable

        self.sub_notebook_admin = ttk.Notebook(main_frame)
        self.sub_notebook_admin.pack(fill="both", expand=True, padx=5, pady=5)

        # Tab con: Quản lý Người dùng
        sub_user_management_frame = ttk.Frame(self.sub_notebook_admin, padding="5")
        self.sub_notebook_admin.add(sub_user_management_frame, text=SUB_TAB_USER_MANAGEMENT, state='disabled')
        # Khởi tạo đối tượng quản lý cho tab này
        self.user_management_tab_manager = UserManagementTab(sub_user_management_frame, self)
        self.sub_notebook_admin.bind("<<NotebookTabChanged>>", self.on_sub_tab_admin_change)
    def setup_styles(self):
        style = ttk.Style(self.master)
        default_font = ('Segoe UI', 11)
        heading_font = ('Segoe UI', 12, 'bold')
        label_font = ('Segoe UI', 11)
        entry_font = ('Segoe UI', 11)
        # Tăng kích thước font cho nút
        button_font = ('Segoe UI', 11, 'bold')

        style.configure('.', font=default_font, padding=5)
        style.configure("TLabel", font=label_font, padding=(0, 5))
        style.configure("Header.TLabel", font=heading_font, padding=(0,10))
        style.configure("TEntry", font=entry_font, padding=5)
        style.configure("TButton", font=button_font, padding=(10, 6)) # Tăng padding cho nút
        style.configure("Accent.TButton", font=button_font, padding=(10, 6), background="#007bff", foreground="black") # Đổi foreground sang black
        style.map("Accent.TButton", background=[('active', '#0056b3')], foreground=[('active', 'black')]) # Đổi foreground sang black
        style.configure("Treeview", font=default_font, rowheight=28)
        style.configure("Treeview.Heading", font=heading_font, padding=5)
        style.configure("TNotebook.Tab", font=button_font, padding=(12, 6)) # Tăng padding cho tab
        style.configure("TLabelframe", padding=10)
        style.configure("TLabelframe.Label", font=heading_font, padding=(0, 5)) # Thêm padding cho label của Labelframe
        style.configure("TCombobox", font=entry_font, padding=5)
        self.master.option_add("*TCombobox*Listbox*Font", entry_font)

        # Style cho Treeview có đường kẻ
        style.configure("Grid.Treeview", rowheight=28, font=default_font) # Kế thừa từ Treeview gốc
        style.map("Grid.Treeview", background=[('selected', '#0078D7')], foreground=[('selected', 'white')]) # Màu khi chọn
    
    # ... (setup_them_sv_tab, _handle_add_student_submit, _populate_them_sv_comboboxes giữ nguyên) ...
    def setup_list_students_tab(self, parent_frame):
        """Thiết lập tab chỉ để hiển thị, lọc và tìm kiếm danh sách sinh viên."""
        # Frame chính cho toàn bộ tab
        main_content_frame = ttk.Frame(parent_frame)
        main_content_frame.pack(fill=tk.BOTH, expand=True)

        # Cấu hình grid cho main_content_frame để tree_frame có thể mở rộng
        main_content_frame.grid_rowconfigure(1, weight=1) # Hàng chứa tree_frame sẽ mở rộng
        main_content_frame.grid_columnconfigure(0, weight=1) # Cột sẽ mở rộng
        
        # --- Frame cho Bộ lọc và Tìm kiếm ---
        filter_search_frame = ttk.LabelFrame(main_content_frame, text="Bộ lọc và Tìm kiếm Sinh viên")
        # Đổi từ pack sang grid
        filter_search_frame.grid(row=0, column=0, sticky=tk.EW, padx=10, pady=(10,5))

        ttk.Label(filter_search_frame, text="Lọc theo Lớp:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.combo_filter_sv_lop = ttk.Combobox(filter_search_frame, width=20, state="readonly")
        self.combo_filter_sv_lop.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.combo_filter_sv_lop.bind("<<ComboboxSelected>>", self._filter_and_display_students)
        ttk.Label(filter_search_frame, text="Lọc theo Khoa:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.combo_filter_sv_khoa = ttk.Combobox(filter_search_frame, width=20, state="readonly")
        self.combo_filter_sv_khoa.grid(row=0, column=3, padx=5, pady=5, sticky=tk.EW)
        self.combo_filter_sv_khoa.bind("<<ComboboxSelected>>", self._filter_and_display_students)
        ttk.Label(filter_search_frame, text="Tìm kiếm (Tên/Mã):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_search_sv_text = ttk.Entry(filter_search_frame, width=25)
        self.entry_search_sv_text.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky=tk.EW)
        self.entry_search_sv_text.bind("<KeyRelease>", self._filter_and_display_students)

        filter_search_frame.grid_columnconfigure(1, weight=1)
        filter_search_frame.grid_columnconfigure(3, weight=1)

        # --- Frame cho Treeview hiển thị danh sách sinh viên ---
        tree_frame = ttk.LabelFrame(main_content_frame, text="Danh sách Sinh viên")
        # Sử dụng grid thay vì pack, và sticky=tk.NSEW để nó mở rộng
        tree_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=10, pady=5)

        cols_sv = ('ma_sv', 'ho_ten', 'lop_hoc', 'khoa', 'truong', 'hoc_ky_nhap_hoc')
        self.tree_manage_students = ttk.Treeview(tree_frame, columns=cols_sv, show='headings', height=10)
        for col_key in cols_sv:
            col_text = col_key.replace('_', ' ').title() # Tạo text heading đẹp hơn
            if col_key == 'ma_sv': col_text = "Mã SV"
            if col_key == 'hoc_ky_nhap_hoc': col_text = "HK Nhập Học"
            self.tree_manage_students.heading(col_key, text=col_text)

        self.tree_manage_students.column('ma_sv', width=100, anchor=tk.W, stretch=tk.NO)
        self.tree_manage_students.column('ho_ten', width=200, anchor=tk.W, stretch=tk.YES)
        self.tree_manage_students.column('lop_hoc', width=100, anchor=tk.W, stretch=tk.NO)
        self.tree_manage_students.column('khoa', width=120, anchor=tk.W, stretch=tk.NO)
        self.tree_manage_students.column('truong', width=100, anchor=tk.W, stretch=tk.NO)
        self.tree_manage_students.column('hoc_ky_nhap_hoc', width=100, anchor=tk.W, stretch=tk.NO)

        scrollbar_sv_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_manage_students.yview)
        scrollbar_sv_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree_manage_students.xview)
        self.tree_manage_students.configure(yscrollcommand=scrollbar_sv_y.set, xscrollcommand=scrollbar_sv_x.set)

        self.tree_manage_students.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_sv_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_sv_x.pack(side=tk.BOTTOM, fill=tk.X)
        # Khi chọn SV, có thể chuyển sang tab CRUD và điền form
        self.tree_manage_students.bind("<<TreeviewSelect>>", self._on_student_select_for_crud_tab)

        # Khởi tạo
        self._populate_student_filters_and_treeview() # Populate bộ lọc và treeview ban đầu

    def setup_crud_students_form_tab(self, parent_frame):
        """Thiết lập tab chứa form Thêm/Sửa/Xóa Sinh viên."""
        main_content_frame = ttk.Frame(parent_frame)
        main_content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # Cho phép cột giữa (chứa các entry/combobox) mở rộng
        main_content_frame.columnconfigure(1, weight=1)
        main_content_frame.columnconfigure(3, weight=1)
        # --- Frame cho Form Thêm/Sửa Sinh viên ---
        form_frame = ttk.LabelFrame(main_content_frame, text="Thông tin Sinh viên (Thêm mới / Sửa)")
        # Đổi từ pack sang grid, sticky=tk.EW để frame này mở rộng theo chiều ngang
        form_frame.grid(row=2, column=0, sticky=tk.EW, padx=10, pady=(5,10))

        # Tăng pady để có thêm không gian dọc
        ttk.Label(form_frame, text="Mã SV (9 số):").grid(row=0, column=0, padx=5, pady=8, sticky=tk.W)
        self.entry_ma_sv_manage = ttk.Entry(form_frame, width=30) # Đổi tên biến
        self.entry_ma_sv_manage.grid(row=0, column=1, padx=5, pady=8, sticky="ew")

        ttk.Label(form_frame, text="Họ và tên:").grid(row=1, column=0, padx=5, pady=8, sticky=tk.W)
        self.entry_ho_ten_manage = ttk.Entry(form_frame, width=40) # Đổi tên biến
        self.entry_ho_ten_manage.grid(row=1, column=1, padx=5, pady=8, sticky="ew")

        ttk.Label(form_frame, text="Lớp học:").grid(row=0, column=2, padx=5, pady=8, sticky=tk.W)
        self.combo_lop_hoc_manage = ttk.Combobox(form_frame, width=30) # Đổi tên biến
        self.combo_lop_hoc_manage.grid(row=0, column=3, padx=5, pady=8, sticky="ew")

        ttk.Label(form_frame, text="Khoa:").grid(row=1, column=2, padx=5, pady=8, sticky=tk.W)
        self.combo_khoa_manage = ttk.Combobox(form_frame, width=30) # Đổi tên biến
        self.combo_khoa_manage.grid(row=1, column=3, padx=5, pady=8, sticky="ew")

        ttk.Label(form_frame, text="Trường:").grid(row=2, column=0, padx=5, pady=8, sticky=tk.W)
        self.combo_truong_manage = ttk.Combobox(form_frame, width=30) # Đổi tên biến
        self.combo_truong_manage.grid(row=2, column=1, padx=5, pady=8, sticky="ew")

        ttk.Label(form_frame, text="HK Nhập học:").grid(row=2, column=2, padx=5, pady=8, sticky=tk.W)
        self.entry_hoc_ky_sv_manage = ttk.Entry(form_frame, width=30) # Đổi tên biến
        self.entry_hoc_ky_sv_manage.grid(row=2, column=3, padx=5, pady=8, sticky="ew")

        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(3, weight=1)

        # --- Frame cho các nút hành động ---
        action_buttons_frame_sv = ttk.Frame(form_frame)
        action_buttons_frame_sv.grid(row=3, column=0, columnspan=4, pady=15)

        self.btn_add_sv = ttk.Button(action_buttons_frame_sv, text="Thêm Mới", command=self._handle_add_student_submit, style="Accent.TButton", width=15)
        self.btn_add_sv.pack(side=tk.LEFT, padx=5)

        self.btn_edit_sv = ttk.Button(action_buttons_frame_sv, text="Lưu Sửa", command=self._handle_edit_student_submit, width=15)
        self.btn_edit_sv.pack(side=tk.LEFT, padx=5)

        self.btn_delete_sv = ttk.Button(action_buttons_frame_sv, text="Xóa SV", command=self._handle_delete_student, width=15)
        self.btn_delete_sv.pack(side=tk.LEFT, padx=5)

        self.btn_clear_sv_form = ttk.Button(action_buttons_frame_sv, text="Làm Mới Form", command=self._clear_student_form_and_selection)
        self.btn_clear_sv_form.pack(side=tk.LEFT, padx=5)

        # Khởi tạo
        self._populate_student_filters_and_treeview() # Populate bộ lọc và treeview ban đầu
        self._populate_student_form_comboboxes() # Populate combobox trong form này
        self._clear_student_form_and_selection(show_status=False) # Đặt form về trạng thái thêm mới

    def _handle_add_student_submit(self):
        if not self._check_ui_permission_before_action("SUBMIT_ADD_STUDENT", "thêm sinh viên"): return

        ma_sv = self.entry_ma_sv_manage.get().strip()
        ho_ten = self.entry_ho_ten_manage.get().strip()
        lop_hoc = self.combo_lop_hoc_manage.get().strip()
        truong = self.combo_truong_manage.get().strip()
        khoa = self.combo_khoa_manage.get().strip()
        hoc_ky_sv = self.entry_hoc_ky_sv_manage.get().strip()

        if not all([ma_sv, ho_ten, lop_hoc, truong, khoa, hoc_ky_sv]):
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin sinh viên, bao gồm Học kỳ ĐK.")
            self.update_status("Thêm sinh viên thất bại: Thiếu thông tin")
            return
        
        success, message = self.ql_diem.them_sinh_vien(ma_sv, ho_ten, lop_hoc, truong, khoa, hoc_ky_sv)
        if success:
            messagebox.showinfo("Thành công", message)
            self.update_status(f"Đã thêm SV {ho_ten} ({ma_sv})")
            self._clear_student_form_and_selection()
            self._populate_student_filters_and_treeview() # Làm mới treeview và bộ lọc
            self._populate_student_form_comboboxes() # Làm mới combobox trong form
        else:
            messagebox.showerror("Lỗi", message)
            self.update_status(f"Thêm thất bại: {message}")

    def _handle_edit_student_submit(self):
        if not self._check_ui_permission_before_action("EDIT_STUDENT_INFO", "sửa thông tin sinh viên"): return

        ma_sv = self.entry_ma_sv_manage.get().strip() # Mã SV này là readonly khi sửa
        if not ma_sv:
            messagebox.showwarning("Thiếu thông tin", "Không có Mã SV để sửa. Vui lòng chọn sinh viên từ danh sách.")
            return

        thong_tin_moi = {
            "ho_ten": self.entry_ho_ten_manage.get().strip(),
            "lop_hoc": self.combo_lop_hoc_manage.get().strip(),
            "truong": self.combo_truong_manage.get().strip(),
            "khoa": self.combo_khoa_manage.get().strip(),
            "hoc_ky_nhap_hoc": self.entry_hoc_ky_sv_manage.get().strip()
        }

        if not all(thong_tin_moi.values()):
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ thông tin cập nhật cho sinh viên.")
            return

        success, message = self.ql_diem.sua_sinh_vien(ma_sv, thong_tin_moi)
        if success:
            messagebox.showinfo("Thành công", message)
            self.update_status(message)
            self._clear_student_form_and_selection()
            self._populate_student_filters_and_treeview()
            self._populate_student_form_comboboxes()
        else:
            messagebox.showerror("Lỗi Sửa Sinh viên", message)
            self.update_status(f"Sửa SV thất bại: {message}")

    def _handle_delete_student(self):
        if not self._check_ui_permission_before_action("DELETE_STUDENT", "xóa sinh viên"): return

        selected_item = self.tree_manage_students.focus()
        if not selected_item:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn sinh viên từ danh sách để xóa.")
            return

        try:
            ma_sv_can_xoa = self.tree_manage_students.item(selected_item)['values'][0]
            ten_sv_display = self.tree_manage_students.item(selected_item)['values'][1]
        except (IndexError, TypeError):
            messagebox.showerror("Lỗi", "Không thể lấy thông tin sinh viên đã chọn.")
            return

        confirm = messagebox.askyesno("Xác nhận xóa",
                                      f"Bạn có chắc muốn xóa sinh viên '{ten_sv_display}' ({ma_sv_can_xoa})?\n"
                                      "LƯU Ý: Chỉ xóa được nếu sinh viên này chưa có điểm.",
                                      parent=self.master)
        if confirm:
            success, message = self.ql_diem.xoa_sinh_vien(ma_sv_can_xoa)
            if success:
                messagebox.showinfo("Thành công", message)
                self.update_status(message)
                self._clear_student_form_and_selection()
                self._populate_student_filters_and_treeview()
                self._populate_student_form_comboboxes()
            else:
                messagebox.showerror("Lỗi Xóa Sinh viên", message)
                self.update_status(f"Xóa SV thất bại: {message}")
        else:
            self.update_status("Đã hủy xóa sinh viên.")

    def _clear_student_form_and_selection(self, show_status=True):
        # Xóa lựa chọn trong Treeview
        if hasattr(self, 'tree_manage_students') and self.tree_manage_students.selection():
            self.tree_manage_students.selection_remove(self.tree_manage_students.selection())

        # Làm mới các trường trong form
        self.entry_ma_sv_manage.config(state="normal")
        self.entry_ma_sv_manage.delete(0, tk.END)
        self.entry_ho_ten_manage.delete(0, tk.END)
        self.combo_lop_hoc_manage.set("")
        self.combo_truong_manage.set("")
        self.combo_khoa_manage.set("")
        self.entry_hoc_ky_sv_manage.delete(0, tk.END)

        # Đặt lại trạng thái nút
        self.btn_add_sv.config(state=tk.NORMAL if self._check_ui_permission_before_action("SUBMIT_ADD_STUDENT", "", silent=True) else tk.DISABLED)
        self.btn_edit_sv.config(state=tk.DISABLED)
        self.btn_delete_sv.config(state=tk.DISABLED)

        self.entry_ma_sv_manage.focus()
        if show_status:
            self.update_status("Form sinh viên đã làm mới. Sẵn sàng thêm.")

    def _on_student_select_for_crud_tab(self, event=None):
        """Khi một sinh viên được chọn trong Treeview của tab Danh sách,
           chuyển sang tab CRUD và điền thông tin vào form."""
        selected_item = self.tree_manage_students.focus()
        if not selected_item:
            return # Không làm gì nếu không có item nào được chọn

        # Chuyển sang tab CRUD Sinh viên
        self._switch_to_tab_by_text(SUB_TAB_CRUD_STUDENTS)
        selected_item = self.tree_manage_students.focus()
        if not selected_item:
            self._clear_student_form_and_selection(show_status=False) # Không báo status khi chỉ là bỏ chọn
            return

        item_values = self.tree_manage_students.item(selected_item)['values']
        if item_values:
            ma_sv, ho_ten, lop_hoc, khoa, truong, hoc_ky_nhap_hoc = item_values

            self.entry_ma_sv_manage.config(state="normal")
            self.entry_ma_sv_manage.delete(0, tk.END); self.entry_ma_sv_manage.insert(0, str(ma_sv))
            self.entry_ma_sv_manage.config(state="readonly") # Mã SV không được sửa

            self.entry_ho_ten_manage.delete(0, tk.END); self.entry_ho_ten_manage.insert(0, str(ho_ten))
            self.combo_lop_hoc_manage.set(str(lop_hoc))
            self.combo_khoa_manage.set(str(khoa))
            self.combo_truong_manage.set(str(truong))
            self.entry_hoc_ky_sv_manage.delete(0, tk.END); self.entry_hoc_ky_sv_manage.insert(0, str(hoc_ky_nhap_hoc))

            self.btn_add_sv.config(state=tk.DISABLED)
            self.btn_edit_sv.config(state=tk.NORMAL if self._check_ui_permission_before_action("EDIT_STUDENT_INFO", "", silent=True) else tk.DISABLED)
            self.btn_delete_sv.config(state=tk.NORMAL if self._check_ui_permission_before_action("DELETE_STUDENT", "", silent=True) else tk.DISABLED)
            self.update_status(f"Đã chọn SV: {ho_ten} ({ma_sv}) để xem/sửa/xóa.")
            self.entry_ho_ten_manage.focus() # Focus vào họ tên để dễ sửa

    def _populate_student_form_comboboxes(self):
        all_student_objects = list(self.ql_diem.danh_sach_sinh_vien.values()) 

        lop_hoc_values = sorted(list(set(sv.lop_hoc for sv in all_student_objects if sv.lop_hoc)))
        truong_values = sorted(list(set(sv.truong for sv in all_student_objects if sv.truong)))
        khoa_values = sorted(list(set(sv.khoa for sv in all_student_objects if sv.khoa)))

        # Sử dụng các combobox của form quản lý sinh viên
        if hasattr(self, 'combo_lop_hoc_manage'): self.combo_lop_hoc_manage['values'] = lop_hoc_values
        if hasattr(self, 'combo_truong_manage'): self.combo_truong_manage['values'] = truong_values
        if hasattr(self, 'combo_khoa_manage'): self.combo_khoa_manage['values'] = khoa_values
        # Không set giá trị hiện tại ở đây, để _on_student_select_for_crud_tab
        # hoặc _clear_student_form_and_selection xử lý

    def setup_ql_mon_hoc_tab(self, parent_frame):
        frame_input_mh = ttk.LabelFrame(parent_frame, text="Thêm/Sửa Môn học")
        frame_input_mh.pack(fill=tk.X, padx=10, pady=10) # Tăng padx

        ttk.Label(frame_input_mh, text="Mã Môn học:").grid(row=0, column=0, padx=5, pady=8, sticky=tk.W) # Tăng pady
        self.entry_ma_mh_ql = ttk.Entry(frame_input_mh, width=30)
        self.entry_ma_mh_ql.grid(row=0, column=1, padx=5, pady=8, sticky=tk.EW)

        ttk.Label(frame_input_mh, text="Tên Môn học:").grid(row=1, column=0, padx=5, pady=8, sticky=tk.W)
        self.entry_ten_mh_ql = ttk.Entry(frame_input_mh, width=40)
        self.entry_ten_mh_ql.grid(row=1, column=1, padx=5, pady=8, sticky=tk.EW)

        ttk.Label(frame_input_mh, text="Số tín chỉ:").grid(row=2, column=0, padx=5, pady=8, sticky=tk.W)
        self.entry_so_tin_chi_ql = ttk.Entry(frame_input_mh, width=10)
        self.entry_so_tin_chi_ql.grid(row=2, column=1, padx=5, pady=8, sticky=tk.W)
        
        frame_input_mh.grid_columnconfigure(1, weight=1)

        action_buttons_frame = ttk.Frame(frame_input_mh)
        action_buttons_frame.grid(row=3, column=0, columnspan=2, pady=10)

        btn_them_mh = ttk.Button(action_buttons_frame, text="Thêm/Lưu Mới", command=self._handle_them_sua_mon_hoc, style="Accent.TButton", width=15)
        btn_them_mh.pack(side=tk.LEFT, padx=5) 
        btn_xoa_mh = ttk.Button(action_buttons_frame, text="Xóa Môn học", command=self._handle_xoa_mon_hoc_chon, width=15) 
        btn_xoa_mh.pack(side=tk.LEFT, padx=5)

        btn_clear_mh_fields = ttk.Button(action_buttons_frame, text="Làm mới Form", command=self._clear_mon_hoc_form)
        btn_clear_mh_fields.pack(side=tk.LEFT, padx=5)

        frame_ds_mh = ttk.LabelFrame(parent_frame, text="Danh sách Môn học")
        frame_ds_mh.pack(fill="both", expand=True, padx=10, pady=(5,10)) # Tăng padx, pady

        cols_mh = ('Mã MH', 'Tên Môn học', 'Số Tín chỉ')
        self.tree_ql_mon_hoc = ttk.Treeview(frame_ds_mh, columns=cols_mh, show='headings')
        for col in cols_mh: self.tree_ql_mon_hoc.heading(col, text=col)
        self.tree_ql_mon_hoc.column("Mã MH", width=100, anchor=tk.W)
        self.tree_ql_mon_hoc.column("Tên Môn học", width=250, anchor=tk.W)
        self.tree_ql_mon_hoc.column("Số Tín chỉ", width=80, anchor=tk.CENTER)

        scrollbar_mh = ttk.Scrollbar(frame_ds_mh, orient=tk.VERTICAL, command=self.tree_ql_mon_hoc.yview)
        self.tree_ql_mon_hoc.configure(yscrollcommand=scrollbar_mh.set)
        self.tree_ql_mon_hoc.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar_mh.pack(side=tk.RIGHT, fill=tk.Y)
        
        btn_export_mh_csv = ttk.Button(parent_frame, text="Xuất DS Môn học (CSV)",
                                       command=lambda: self._export_treeview_to_csv(self.tree_ql_mon_hoc, "danh_sach_mon_hoc.csv"), width=25)
        btn_export_mh_csv.pack(pady=5)


        self.tree_ql_mon_hoc.bind("<<TreeviewSelect>>", self._on_mon_hoc_select)
        self.hien_thi_danh_sach_mon_hoc() 
        self._clear_mon_hoc_form(show_status=False)

    def _clear_mon_hoc_form(self, show_status=True):
        self.entry_ma_mh_ql.config(state="normal")
        self.entry_ma_mh_ql.delete(0, tk.END)
        self.entry_ten_mh_ql.delete(0, tk.END)
        self.entry_so_tin_chi_ql.delete(0, tk.END)
        if self.tree_ql_mon_hoc.selection():
            self.tree_ql_mon_hoc.selection_remove(self.tree_ql_mon_hoc.selection())
        self.entry_ma_mh_ql.focus()
        if show_status: self.update_status("Form quản lý môn học đã làm mới. Sẵn sàng thêm.")

    def _check_ui_permission_before_action(self, permission_key_str, action_description="thực hiện hành động này", silent=False):
        if not self.user_manager.has_permission(self.current_user, PERMISSIONS.get(permission_key_str)):
            if not silent:
                messagebox.showerror("Không có quyền", f"Bạn không có quyền {action_description}.", parent=self.master)
            return False # Luôn trả về False nếu không có quyền
        return True
    def _on_mon_hoc_select(self, event=None):
        selected_item = self.tree_ql_mon_hoc.focus()
        if not selected_item: self._clear_mon_hoc_form(); return
        item_values = self.tree_ql_mon_hoc.item(selected_item)['values']
        if item_values:
            ma_mh, ten_mh, so_tin_chi = item_values
            self.entry_ma_mh_ql.config(state="normal"); self.entry_ma_mh_ql.delete(0, tk.END)
            self.entry_ma_mh_ql.insert(0, str(ma_mh)); self.entry_ma_mh_ql.config(state="readonly")
            self.entry_ten_mh_ql.delete(0, tk.END); self.entry_ten_mh_ql.insert(0, str(ten_mh))
            self.entry_so_tin_chi_ql.delete(0, tk.END); self.entry_so_tin_chi_ql.insert(0, str(so_tin_chi))
            self.update_status(f"Đã chọn môn {ma_mh} để xem/sửa.")

    def _handle_them_sua_mon_hoc(self):
        ma_mh = self.entry_ma_mh_ql.get().strip()
        ten_mh = self.entry_ten_mh_ql.get().strip()
        so_tin_chi_str = self.entry_so_tin_chi_ql.get().strip()

        if self.entry_ma_mh_ql.cget("state") == "readonly": # Chế độ Sửa
            if not self._check_ui_permission_before_action("ADD_EDIT_SUBJECT", "sửa môn học", silent=False): return
            success, message = self.ql_diem.sua_mon_hoc(ma_mh, ten_mh, so_tin_chi_str)
            action_type = "Sửa"
        else: # Chế độ Thêm mới
            if not self._check_ui_permission_before_action("ADD_EDIT_SUBJECT", "thêm môn học", silent=False): return
            success, message = self.ql_diem.them_mon_hoc(ma_mh, ten_mh, so_tin_chi_str)
            action_type = "Thêm"


        if success:
            messagebox.showinfo("Thành công", message)
            self.update_status(message)
            self.hien_thi_danh_sach_mon_hoc()
            self._populate_mon_hoc_comboboxes() # Chỉ cần cập nhật combobox môn học
            self._clear_mon_hoc_form()
        else:
            messagebox.showerror(f"Lỗi {action_type} Môn học", message)
            self.update_status(f"{action_type} môn học thất bại: {message}")

    def _handle_xoa_mon_hoc_chon(self):
        selected_item = self.tree_ql_mon_hoc.focus()
        if not selected_item:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn môn học từ danh sách để xóa.")
            return
        if not self._check_ui_permission_before_action("DELETE_SUBJECT", "xóa môn học", silent=False): return
        try:
            ma_mh_can_xoa = self.tree_ql_mon_hoc.item(selected_item)['values'][0]
            ten_mh_display = self.tree_ql_mon_hoc.item(selected_item)['values'][1]
        except (IndexError, TypeError): return

        confirm = messagebox.askyesno("Xác nhận xóa", 
                                      f"Xóa môn '{ten_mh_display}' ({ma_mh_can_xoa})?\n"
                                      "LƯU Ý: Chỉ xóa được nếu không có SV nào có điểm môn này.")
        if confirm:
            success, message = self.ql_diem.xoa_mon_hoc(ma_mh_can_xoa)
            if success:
                messagebox.showinfo("Thành công", message)
                self.update_status(message)
                self.hien_thi_danh_sach_mon_hoc()
                self._clear_mon_hoc_form(show_status=False) # Không cần status ở đây
                self._populate_all_combobox_filters()
            else:
                messagebox.showerror("Lỗi xóa", message)
                self.update_status(f"Xóa thất bại: {message}")
        else: self.update_status("Đã hủy xóa môn học.")
        
    def setup_nhap_diem_tab(self, parent_frame):
        # Hàm xử lý sự kiện cuộn chuột
        def _on_mousewheel(event, canvas_widget):
            scroll_speed_factor = -1 if event.num == 4 else 1
            if event.delta: scroll_speed_factor = int(-1 * (event.delta / 120)) if abs(event.delta) >= 120 else int(-1 * event.delta)
            canvas_widget.yview_scroll(scroll_speed_factor, "units")
            
        canvas = tk.Canvas(parent_frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Tạo thanh cuộn dọc
        scrollbar = ttk.Scrollbar(parent_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Kết nối thanh cuộn với canvas
        canvas.configure(yscrollcommand=scrollbar.set)

        # Tạo một frame bên trong canvas để chứa tất cả các widget
        # Đây sẽ là frame có thể cuộn được
        scrollable_frame = ttk.Frame(canvas, padding=(10, 10))

        # Thêm scrollable_frame vào canvas
        canvas_window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Cấu hình canvas để cập nhật vùng cuộn khi kích thước của scrollable_frame thay đổi
        def _configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Cập nhật chiều rộng của scrollable_frame để khớp với chiều rộng của canvas
            # điều này quan trọng để nội dung không bị cắt ngang khi cửa sổ hẹp
            canvas.itemconfig(canvas_window_id, width=canvas.winfo_width())

        scrollable_frame.bind("<Configure>", _configure_scroll_region)
        canvas.bind("<Configure>", _configure_scroll_region) # Cũng bind vào canvas để xử lý thay đổi kích thước cửa sổ

        # --- Bố cục các widget con bằng grid bên trong scrollable_frame ---
        filter_frame_nhap_diem = ttk.LabelFrame(scrollable_frame, text="Lọc Sinh viên", padding="10")
        filter_frame_nhap_diem.grid(row=0, column=0, sticky="ew", padx=10, pady=(0,10)) # Tăng padx

        ttk.Label(filter_frame_nhap_diem, text="Lọc theo Lớp:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.combo_nhap_diem_filter_lop = ttk.Combobox(filter_frame_nhap_diem, width=25, state="readonly")
        self.combo_nhap_diem_filter_lop.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.combo_nhap_diem_filter_lop.bind("<<ComboboxSelected>>", self._on_nhap_diem_filter_change)

        ttk.Label(filter_frame_nhap_diem, text="Lọc theo Khoa:").grid(row=0, column=2, padx=(10,5), pady=5, sticky="w")
        self.combo_nhap_diem_filter_khoa = ttk.Combobox(filter_frame_nhap_diem, width=25, state="readonly")
        self.combo_nhap_diem_filter_khoa.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        self.combo_nhap_diem_filter_khoa.bind("<<ComboboxSelected>>", self._on_nhap_diem_filter_change)
        
        filter_frame_nhap_diem.columnconfigure(1, weight=1)
        filter_frame_nhap_diem.columnconfigure(3, weight=1)

        sv_frame = ttk.LabelFrame(scrollable_frame, text="Chọn Sinh viên", padding="10")
        sv_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0,10)) # Tăng padx
        ttk.Label(sv_frame, text="Sinh viên (MSSV - Họ tên):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.combo_nhap_diem_mssv = ttk.Combobox(sv_frame, width=50) 
        self.combo_nhap_diem_mssv.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.combo_nhap_diem_mssv.bind("<<ComboboxSelected>>", self._on_nhap_diem_sv_select)
        self.combo_nhap_diem_mssv.bind("<KeyRelease>", self._on_nhap_diem_sv_filter_typed) 
        
        sv_frame.columnconfigure(1, weight=1)

        info_sv_frame = ttk.LabelFrame(scrollable_frame, text="Thông tin Sinh viên đã chọn", padding="10")
        info_sv_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5) # Tăng padx
        self.tree_nhap_diem_sv_info = ttk.Treeview(info_sv_frame, columns=("thuoc_tinh", "gia_tri"), 
                                                   show="headings", height=5, selectmode="none")
        self.tree_nhap_diem_sv_info.heading("thuoc_tinh", text="Thuộc tính")
        self.tree_nhap_diem_sv_info.heading("gia_tri", text="Giá trị")
        self.tree_nhap_diem_sv_info.column("thuoc_tinh", width=120, anchor="w", stretch=tk.NO)
        self.tree_nhap_diem_sv_info.column("gia_tri", width=300, anchor="w", stretch=tk.YES)
        self.tree_nhap_diem_sv_info.pack(fill="x", expand=True, padx=5, pady=5) # Pack bên trong LabelFrame này là ổn
        self.tree_nhap_diem_sv_info.bindtags((self.tree_nhap_diem_sv_info.bindtags()[0],))


        enter_grade_frame = ttk.LabelFrame(scrollable_frame, text="Nhập Điểm cho Môn học", padding="10")
        enter_grade_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(10,0)) # Tăng padx
        
        ttk.Label(enter_grade_frame, text="Chọn Học kỳ Nhập điểm:").grid(row=0, column=0, padx=5, pady=8, sticky=tk.W)
        self.combo_hoc_ky_nhap_diem = ttk.Combobox(enter_grade_frame, width=38, state="readonly") 
        self.combo_hoc_ky_nhap_diem.grid(row=0, column=1, padx=5, pady=8, sticky="ew")

        ttk.Label(enter_grade_frame, text="Chọn Môn học:").grid(row=1, column=0, padx=5, pady=8, sticky=tk.W)
        self.combo_mon_hoc_nhapdiem = ttk.Combobox(enter_grade_frame, width=38, state="readonly")
        self.combo_mon_hoc_nhapdiem.grid(row=1, column=1, padx=5, pady=8, sticky="ew")

        ttk.Label(enter_grade_frame, text="Điểm (0-10):").grid(row=2, column=0, padx=5, pady=8, sticky=tk.W)
        self.entry_diem_nhapdiem = ttk.Entry(enter_grade_frame, width=40)
        self.entry_diem_nhapdiem.grid(row=2, column=1, padx=5, pady=8, sticky="ew")
        
        enter_grade_frame.columnconfigure(1, weight=1)

        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=4, column=0, pady=20)
        btn_nhap_diem = ttk.Button(btn_frame, text="Nhập Điểm", command=self.nhap_diem_submit, style="Accent.TButton", width=15)
        btn_nhap_diem.pack(side=tk.LEFT, padx=5)
        btn_clear_nhap_diem = ttk.Button(btn_frame, text="Làm mới Form", command=self._clear_nhap_diem_form)
        btn_clear_nhap_diem.pack(side=tk.LEFT, padx=5)

        # Cấu hình cột cho scrollable_frame để các LabelFrame con có thể giãn nở theo chiều rộng
        scrollable_frame.columnconfigure(0, weight=1)

        # Binding cuộn chuột
        canvas.bind_all("<MouseWheel>", lambda event: _on_mousewheel(event, canvas)) # Windows, macOS (với delta)
        canvas.bind_all("<Button-4>", lambda event: _on_mousewheel(event, canvas)) # Linux (cuộn lên)
        canvas.bind_all("<Button-5>", lambda event: _on_mousewheel(event, canvas)) # Linux (cuộn xuống)

        self._clear_nhap_diem_form() 

    def _clear_nhap_diem_form(self):
        self.combo_nhap_diem_mssv.set('')
        if hasattr(self, 'combo_nhap_diem_filter_lop'): self.combo_nhap_diem_filter_lop.set('Tất cả')
        if hasattr(self, 'combo_nhap_diem_filter_khoa'): self.combo_nhap_diem_filter_khoa.set('Tất cả')
        
        for item in self.tree_nhap_diem_sv_info.get_children():
            self.tree_nhap_diem_sv_info.delete(item)
        if hasattr(self, 'combo_hoc_ky_nhap_diem'): self.combo_hoc_ky_nhap_diem.set("Chọn học kỳ")
        if hasattr(self, 'combo_mon_hoc_nhapdiem'): 
            self.combo_mon_hoc_nhapdiem.set('') # Xóa lựa chọn hiện tại
            self._populate_mon_hoc_comboboxes() # Tải lại danh sách môn học

        if hasattr(self, 'entry_diem_nhapdiem'): self.entry_diem_nhapdiem.delete(0, tk.END)
        
        self._populate_nhap_diem_sv_combobox()
        self.update_status("Form nhập điểm đã làm mới.")

    def _populate_nhap_diem_filters(self):
        if not hasattr(self, 'combo_nhap_diem_filter_lop'): return 

        all_sv_objs = list(self.ql_diem.danh_sach_sinh_vien.values())
        lop_values = sorted(list(set(sv.lop_hoc for sv in all_sv_objs if sv.lop_hoc)))
        khoa_values = sorted(list(set(sv.khoa for sv in all_sv_objs if sv.khoa)))

        for combo, values in [(self.combo_nhap_diem_filter_lop, lop_values), 
                               (self.combo_nhap_diem_filter_khoa, khoa_values)]:
            current_val = combo.get()
            combo['values'] = ["Tất cả"] + values
            if current_val in combo['values']:
                combo.set(current_val)
            else:
                combo.set("Tất cả")

    def _on_nhap_diem_filter_change(self, event=None):
        self.combo_nhap_diem_mssv.set('') 
        for item in self.tree_nhap_diem_sv_info.get_children(): 
            self.tree_nhap_diem_sv_info.delete(item)
        self._populate_nhap_diem_sv_combobox() 
        self.update_status("Bộ lọc sinh viên đã thay đổi. Vui lòng chọn lại sinh viên.")

    def _populate_nhap_diem_sv_combobox(self):
        if not hasattr(self, 'combo_nhap_diem_mssv'): return

        current_text_in_combo = self.combo_nhap_diem_mssv.get()
        sv_objects_full_list = list(self.ql_diem.danh_sach_sinh_vien.values())

        selected_lop = self.combo_nhap_diem_filter_lop.get() if hasattr(self, 'combo_nhap_diem_filter_lop') else "Tất cả"
        selected_khoa = self.combo_nhap_diem_filter_khoa.get() if hasattr(self, 'combo_nhap_diem_filter_khoa') else "Tất cả"

        filtered_sv_objects = []
        for sv in sv_objects_full_list:
            match_lop = (selected_lop == "Tất cả" or sv.lop_hoc == selected_lop)
            match_khoa = (selected_khoa == "Tất cả" or sv.khoa == selected_khoa)
            if match_lop and match_khoa:
                filtered_sv_objects.append(sv)
        
        self.full_sv_display_list_nhap_diem = sorted([f"{sv.ho_ten} ({sv.ma_sv})" for sv in filtered_sv_objects])

        if not current_text_in_combo:
            self.combo_nhap_diem_mssv['values'] = [""] + self.full_sv_display_list_nhap_diem
            self.combo_nhap_diem_mssv.set("") # Đảm bảo ô trống nếu không có text
        else:
            # Giữ lại text người dùng đã gõ và lọc dựa trên đó
            self._on_nhap_diem_sv_filter_typed() 
            # self.combo_nhap_diem_mssv.set(current_text_in_combo) # Đảm bảo text không bị mất

    def _on_nhap_diem_sv_filter_typed(self, event=None):
        if not hasattr(self, 'combo_nhap_diem_mssv'): return
        
        if not hasattr(self, 'full_sv_display_list_nhap_diem'):
            self.combo_nhap_diem_mssv['values'] = [""]
            return

        current_text = self.combo_nhap_diem_mssv.get()

        if not current_text:
            self.combo_nhap_diem_mssv['values'] = [""] + self.full_sv_display_list_nhap_diem
        else:
            typed_lower = current_text.lower()
            filtered_values = [
                s for s in self.full_sv_display_list_nhap_diem if typed_lower in s.lower()
            ]
            # Để giữ text đã gõ, không nên thêm "" vào đầu ở đây nếu có filtered_values
            self.combo_nhap_diem_mssv['values'] = filtered_values if filtered_values else [current_text] # Hiển thị lại text nếu không match

    def _on_nhap_diem_sv_select(self, event=None):
        for item in self.tree_nhap_diem_sv_info.get_children():
            self.tree_nhap_diem_sv_info.delete(item)
        selected_display_sv = self.combo_nhap_diem_mssv.get()
        if not selected_display_sv:
            self.update_status("Chưa chọn sinh viên.")
            return

        try:
            mssv = selected_display_sv.split('(')[-1].replace(')', '').strip()
        except Exception:
            self.update_status("Lựa chọn sinh viên không hợp lệ.")
            # Có thể xóa lựa chọn không hợp lệ khỏi combobox
            # self.combo_nhap_diem_mssv.set('') 
            # self._populate_nhap_diem_sv_combobox() # Populate lại
            return

        sv_obj = self.ql_diem.danh_sach_sinh_vien.get(mssv)
        if sv_obj:
            self.tree_nhap_diem_sv_info.insert("", "end", values=("Họ tên", sv_obj.ho_ten))
            self.tree_nhap_diem_sv_info.insert("", "end", values=("Lớp", sv_obj.lop_hoc))
            self.tree_nhap_diem_sv_info.insert("", "end", values=("Trường", sv_obj.truong))
            self.tree_nhap_diem_sv_info.insert("", "end", values=("Khoa", sv_obj.khoa))
            self.tree_nhap_diem_sv_info.insert("", "end", values=("Học kỳ ĐK", sv_obj.hoc_ky_nhap_hoc))
            self.update_status(f"Đã chọn SV: {sv_obj.ho_ten} ({mssv}).")
        else:
            self.tree_nhap_diem_sv_info.insert("", "end", values=("Lỗi", f"Không tìm thấy SV: {mssv}"))
            self.update_status(f"Không tìm thấy thông tin cho MSSV: {mssv}")
            # self.combo_nhap_diem_mssv.set('') # Xóa nếu SV không tìm thấy
            # self._populate_nhap_diem_sv_combobox() # Populate lại
        
        if hasattr(self, 'combo_mon_hoc_nhapdiem'): self.combo_mon_hoc_nhapdiem.set('')
        if hasattr(self, 'entry_diem_nhapdiem'): self.entry_diem_nhapdiem.delete(0, tk.END)


    def nhap_diem_submit(self):
        selected_display_sv = self.combo_nhap_diem_mssv.get()
        selected_mon_hoc_display = self.combo_mon_hoc_nhapdiem.get()
        selected_hoc_ky_nhap = self.combo_hoc_ky_nhap_diem.get()
        diem_str = self.entry_diem_nhapdiem.get().strip()

        if not selected_display_sv or not selected_mon_hoc_display or not diem_str or \
           not selected_hoc_ky_nhap or selected_hoc_ky_nhap == "Chọn học kỳ":
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn Sinh viên, Học kỳ, Môn học và nhập Điểm.")
            self.update_status("Nhập điểm thất bại: Thiếu thông tin.")
            return

        try: 
            ma_sv = selected_display_sv.split('(')[-1].replace(')', '').strip()
        except: ma_sv = None

        ma_mon_hoc = self.mon_hoc_display_to_code_map.get(selected_mon_hoc_display)

        if not ma_sv or not ma_mon_hoc:
            messagebox.showerror("Lỗi", "Thông tin Sinh viên hoặc Môn học không hợp lệ.", parent=self.master)
            self.update_status("Nhập điểm thất bại: SV hoặc Môn học không hợp lệ.")
            return

        if not self._check_ui_permission_before_action("SUBMIT_ENTER_GRADES", "nhập điểm"): return
        try:
            diem = float(diem_str)
            success, message = self.ql_diem.nhap_diem(ma_sv, ma_mon_hoc, diem, selected_hoc_ky_nhap)
            if success:
                ten_sv_display = selected_display_sv.split(' (')[0]
                ten_mon_display = selected_mon_hoc_display.split(' (')[0]
                messagebox.showinfo("Thành công", f"Đã nhập điểm môn {ten_mon_display} ({diem}) cho SV {ten_sv_display}.")
                self.update_status(f"Đã nhập điểm: SV {ma_sv} - Môn {ma_mon_hoc} - Điểm {diem}")
                self._clear_nhap_diem_form() 
                self._populate_all_combobox_filters() 
            else: # Lỗi từ backend (ví dụ điểm không hợp lệ đã được validate trong model)
                messagebox.showerror("Lỗi Nhập Điểm", message, parent=self.master)
                self.update_status(f"Nhập điểm thất bại: {message}")
        except ValueError:
            messagebox.showwarning("Lỗi Định Dạng", "Điểm nhập vào không phải là số hợp lệ.", parent=self.master)
            self.update_status("Nhập điểm thất bại: Điểm không phải số.") # Thêm parent
            
    def setup_xem_xoa_diem_tab(self, parent_frame):
        main_frame_xem = ttk.Frame(parent_frame) # Sửa parent
        main_frame_xem.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        filter_frame_xem_diem = ttk.LabelFrame(main_frame_xem, text="Lọc Sinh viên và Điểm", padding="10") # Sửa parent
        filter_frame_xem_diem.pack(fill="x", padx=5, pady=(5,10)) # Thêm padx, điều chỉnh pady

        ttk.Label(filter_frame_xem_diem, text="Lọc theo Lớp:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.combo_xem_diem_filter_lop = ttk.Combobox(filter_frame_xem_diem, width=25, state="readonly")
        self.combo_xem_diem_filter_lop.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.combo_xem_diem_filter_lop.bind("<<ComboboxSelected>>", self._on_xem_diem_filter_change)

        ttk.Label(filter_frame_xem_diem, text="Lọc theo Khoa:").grid(row=1, column=0, padx=5, pady=5, sticky="w") 
        self.combo_xem_diem_filter_khoa = ttk.Combobox(filter_frame_xem_diem, width=25, state="readonly")
        self.combo_xem_diem_filter_khoa.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.combo_xem_diem_filter_khoa.bind("<<ComboboxSelected>>", self._on_xem_diem_filter_change)
        
        ttk.Label(filter_frame_xem_diem, text="Lọc theo Học Kỳ Điểm:").grid(row=0, column=2, padx=(10,5), pady=5, sticky="w") 
        self.combo_hoc_ky_xem_diem = ttk.Combobox(filter_frame_xem_diem, width=25, state="readonly")
        self.combo_hoc_ky_xem_diem.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        self.combo_hoc_ky_xem_diem.bind("<<ComboboxSelected>>", self._on_xem_diem_filter_change)
        
        filter_frame_xem_diem.columnconfigure(1, weight=1)
        filter_frame_xem_diem.columnconfigure(3, weight=1)

        # Bỏ nút Hiển thị Điểm riêng, thay vào đó sẽ tự cập nhật khi filter thay đổi
        # btn_hien_thi_diem = ttk.Button(filter_frame_xem_diem, text="Hiển thị Điểm", command=self.hien_thi_bang_diem_sinh_vien, style="Accent.TButton")
        # btn_hien_thi_diem.grid(row=0, column=4, rowspan=2, padx=10, pady=5, sticky="e") # rowspan nếu cần

        frame_tree_xem = ttk.LabelFrame(main_frame_xem, text="Bảng Điểm Chi Tiết") # Sửa parent
        frame_tree_xem.pack(fill="both", expand=True, padx=5, pady=5) # Thêm padx
        
        initial_cols_xem = ('ma_sv', 'ho_ten', 'lop_hoc', 'khoa', 'hoc_ky_diem', 'ten_mon_hoc', 'diem_so')
        self.tree_xem_diem = ttk.Treeview(frame_tree_xem, columns=initial_cols_xem, show='headings')
        
        self.tree_xem_diem.heading('ma_sv', text='Mã SV')
        self.tree_xem_diem.column('ma_sv', width=80, anchor='w', stretch=tk.NO)
        self.tree_xem_diem.heading('ho_ten', text='Họ Tên')
        self.tree_xem_diem.column('ho_ten', width=150, anchor='w', stretch=tk.YES) # Cho phép co giãn
        self.tree_xem_diem.heading('lop_hoc', text='Lớp'); self.tree_xem_diem.column('lop_hoc', width=80, anchor='w', stretch=tk.NO)
        self.tree_xem_diem.heading('khoa', text='Khoa'); self.tree_xem_diem.column('khoa', width=100, anchor='w', stretch=tk.NO)
        self.tree_xem_diem.heading('hoc_ky_diem', text='HK Điểm'); self.tree_xem_diem.column('hoc_ky_diem', width=80, anchor='w', stretch=tk.NO)
        self.tree_xem_diem.heading('ten_mon_hoc', text='Tên Môn Học'); self.tree_xem_diem.column('ten_mon_hoc', width=150, anchor='w', stretch=tk.YES) # Cho phép co giãn
        self.tree_xem_diem.heading('diem_so', text='Điểm'); self.tree_xem_diem.column('diem_so', width=60, anchor='center', stretch=tk.NO)

        vsb_xem = ttk.Scrollbar(frame_tree_xem, orient="vertical", command=self.tree_xem_diem.yview)
        hsb_xem = ttk.Scrollbar(frame_tree_xem, orient="horizontal", command=self.tree_xem_diem.xview)
        self.tree_xem_diem.configure(yscrollcommand=vsb_xem.set, xscrollcommand=hsb_xem.set)

        self.tree_xem_diem.pack(side="left", fill="both", expand=True) # Đặt treeview trước
        vsb_xem.pack(side='right', fill='y')
        hsb_xem.pack(side='bottom', fill='x')


        self.tree_xem_diem.bind("<<TreeviewSelect>>", self._on_xem_diem_row_select)

        # Button "Xóa Điểm Đã Chọn" moved inside frame_tree_xem, below tree and hsb
        self.btn_xoa_diem_chon = ttk.Button(frame_tree_xem, # Parent is now frame_tree_xem
                                            text="Xóa Điểm Đã Chọn",
                                            command=self.xoa_diem_da_chon,
                                            style="Accent.TButton",
                                            width=20)
        # Pack it at the bottom of frame_tree_xem, after the horizontal scrollbar
        self.btn_xoa_diem_chon.pack(side=tk.BOTTOM, pady=(10,5)) # pady=(top_padding, bottom_padding)

        self._populate_xem_diem_filters()
        self.hien_thi_bang_diem_sinh_vien()
    def _populate_xem_diem_filters(self):
        if not hasattr(self, 'combo_xem_diem_filter_lop'): return

        all_sv_objs = list(self.ql_diem.danh_sach_sinh_vien.values())
        # all_hoc_ky_values đã được populate bởi _populate_hoc_ky_comboboxes_for_all_tabs

        lop_values = sorted(list(set(sv.lop_hoc for sv in all_sv_objs if sv.lop_hoc)))
        khoa_values = sorted(list(set(sv.khoa for sv in all_sv_objs if sv.khoa)))

        for combo, values in [(self.combo_xem_diem_filter_lop, lop_values), 
                               (self.combo_xem_diem_filter_khoa, khoa_values)]:
            current_val = combo.get()
            combo['values'] = ["Tất cả"] + values
            if current_val in combo['values']:
                combo.set(current_val)
            else:
                combo.set("Tất cả")

    def _on_xem_diem_filter_change(self, event=None):
        self.hien_thi_bang_diem_sinh_vien() 
        self.update_status("Bộ lọc Xem Điểm đã thay đổi, bảng điểm được cập nhật.")
        self.xem_diem_selected_sv_ma_mh_to_delete = None

    def hien_thi_bang_diem_sinh_vien(self):
        if not hasattr(self, 'tree_xem_diem'): return # Đảm bảo treeview đã tồn tại
        
        tree = self.tree_xem_diem
        for item in tree.get_children(): tree.delete(item)
        self.xem_diem_selected_sv_ma_mh_to_delete = None

        selected_lop = self.combo_xem_diem_filter_lop.get() if hasattr(self, 'combo_xem_diem_filter_lop') else "Tất cả"
        selected_khoa = self.combo_xem_diem_filter_khoa.get() if hasattr(self, 'combo_xem_diem_filter_khoa') else "Tất cả"
        selected_hoc_ky_diem = self.combo_hoc_ky_xem_diem.get() if hasattr(self, 'combo_hoc_ky_xem_diem') else "Tất cả"

        sv_objects_full_list = list(self.ql_diem.danh_sach_sinh_vien.values())
        
        rows_to_display = []
        for sv in sv_objects_full_list:
            match_lop = (selected_lop == "Tất cả" or (sv.lop_hoc and sv.lop_hoc.lower() == selected_lop.lower()))
            match_khoa = (selected_khoa == "Tất cả" or (sv.khoa and sv.khoa.lower() == selected_khoa.lower()))
            if match_lop and match_khoa:
                if sv.diem: 
                    for hoc_ky, diem_mon_hoc in sv.diem.items():
                        match_hoc_ky_diem = (selected_hoc_ky_diem == "Tất cả" or (hoc_ky and hoc_ky.lower() == selected_hoc_ky_diem.lower()))
                        if match_hoc_ky_diem:
                            for ma_mh, diem_so in diem_mon_hoc.items():
                                mon_hoc_obj = self.ql_diem.lay_thong_tin_mon_hoc(ma_mh)
                                ten_mh_display = mon_hoc_obj.ten_mh if mon_hoc_obj else ma_mh
                                item_iid = f"{sv.ma_sv}_{hoc_ky}_{ma_mh}" # iid phải duy nhất
                                rows_to_display.append({
                                    'iid': item_iid,
                                    'ma_sv': sv.ma_sv, 'ho_ten': sv.ho_ten, 
                                    'lop_hoc': sv.lop_hoc, 'khoa': sv.khoa,
                                    'hoc_ky_diem': hoc_ky, 'ma_mon_hoc': ma_mh, 
                                    'ten_mon_hoc': ten_mh_display, 
                                    'diem_so': f"{diem_so:.1f}" if isinstance(diem_so, (float, int)) else ""
                                })
        
        rows_to_display.sort(key=lambda x: (x['ma_sv'], x['hoc_ky_diem'], x['ten_mon_hoc']))

        for row_data in rows_to_display:
            tree.insert('', 'end', iid=row_data['iid'], values=(
                row_data['ma_sv'], row_data['ho_ten'], row_data['lop_hoc'], row_data['khoa'],
                row_data['hoc_ky_diem'], row_data['ten_mon_hoc'], row_data['diem_so']
            ))
        
        if not rows_to_display:
            self.update_status("Không có điểm nào khớp với bộ lọc.")
        else:
            self.update_status(f"Hiển thị {len(rows_to_display)} dòng điểm.")

    def _on_xem_diem_row_select(self, event):
        tree = event.widget
        selected_items = tree.selection() 
        if not selected_items:
            self.xem_diem_selected_sv_ma_mh_to_delete = None
            return
        
        selected_iid = selected_items[0] 
        try:
            first_underscore = selected_iid.find('_')
            second_underscore = selected_iid.find('_', first_underscore + 1)

            if first_underscore != -1 and second_underscore != -1:
                ma_sv = selected_iid[:first_underscore]
                hoc_ky = selected_iid[first_underscore+1:second_underscore]
                ma_mh = selected_iid[second_underscore+1:]
                self.xem_diem_selected_sv_ma_mh_to_delete = (ma_sv, ma_mh, hoc_ky) 
                self.update_status(f"Đã chọn điểm môn {ma_mh} (HK: {hoc_ky}) của SV {ma_sv} để xóa.")
            else: raise ValueError("Định dạng IID không đúng, không đủ dấu '_' phân tách.")
        except ValueError as e:
            self.xem_diem_selected_sv_ma_mh_to_delete = None 
            self.update_status(f"Lựa chọn không hợp lệ để xóa: {e}")
            print(f"Lỗi parse IID '{selected_iid}': {e}")


    def xoa_diem_da_chon(self):
        if not self.xem_diem_selected_sv_ma_mh_to_delete:
            messagebox.showwarning("Chưa chọn điểm", "Vui lòng chọn một dòng điểm cụ thể trong bảng để xóa.", parent=self.master)
            return
        if not self._check_ui_permission_before_action("DELETE_GRADES", "xóa điểm", silent=False): return

        ma_sv, ma_mh, hoc_ky = self.xem_diem_selected_sv_ma_mh_to_delete 
        mon_hoc_obj = self.ql_diem.lay_thong_tin_mon_hoc(ma_mh)
        ten_mh_display = mon_hoc_obj.ten_mh if mon_hoc_obj else ma_mh

        confirm = messagebox.askyesno("Xác nhận xóa", 
                                      f"Bạn có chắc muốn xóa điểm môn '{ten_mh_display}' ({ma_mh}) của sinh viên '{ma_sv}' trong học kỳ '{hoc_ky}' không?",
                                      parent=self.master)
        if confirm:
            success, message = self.ql_diem.xoa_diem(ma_sv, ma_mh, hoc_ky) 
            if success:
                messagebox.showinfo("Thành công", message, parent=self.master)
                self.update_status(message)
                self.hien_thi_bang_diem_sinh_vien() 
                self._populate_all_combobox_filters() 
            else: 
                messagebox.showerror("Lỗi Xóa Điểm", message, parent=self.master)
                self.update_status(f"Xóa điểm thất bại: {message}")
            self.xem_diem_selected_sv_ma_mh_to_delete = None 
        else:
            self.update_status("Hủy xóa điểm.")    
    # Các phương thức liên quan đến "Nhập Điểm Nhanh" đã được chuyển sang QuickGradeEntryTab

    def setup_tim_kiem_tab(self, parent_frame):
        frame_options = ttk.LabelFrame(parent_frame, text="Tiêu chí tìm kiếm") 
        frame_options.pack(fill=tk.X, padx=10, pady=10) # Tăng padx
        ttk.Label(frame_options, text="Mã Sinh viên:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_search_ma_sv = ttk.Entry(frame_options, width=30) 
        self.entry_search_ma_sv.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Label(frame_options, text="Lớp học:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.combo_search_lop_hoc = ttk.Combobox(frame_options, width=28, state="readonly") 
        self.combo_search_lop_hoc.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Label(frame_options, text="Trường:").grid(row=0, column=2, sticky=tk.W, padx=15, pady=5)
        self.combo_search_truong = ttk.Combobox(frame_options, width=28, state="readonly") 
        self.combo_search_truong.grid(row=0, column=3, padx=5, pady=5, sticky=tk.EW)
        ttk.Label(frame_options, text="Khoa:").grid(row=1, column=2, sticky=tk.W, padx=15, pady=5)
        self.combo_search_khoa = ttk.Combobox(frame_options, width=28, state="readonly") 
        self.combo_search_khoa.grid(row=1, column=3, padx=5, pady=5, sticky=tk.EW)
        ttk.Label(frame_options, text="Môn học:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.combo_search_mon_hoc = ttk.Combobox(frame_options, width=28, state="readonly")
        self.combo_search_mon_hoc.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(frame_options, text="Học kỳ Điểm:").grid(row=2, column=2, sticky=tk.W, padx=15, pady=5) 
        self.combo_hoc_ky_tim_kiem = ttk.Combobox(frame_options, width=28, state="readonly")
        self.combo_hoc_ky_tim_kiem.grid(row=2, column=3, padx=5, pady=5, sticky=tk.EW)

        frame_options.grid_columnconfigure(1, weight=1); frame_options.grid_columnconfigure(3, weight=1)
        search_action_frame = ttk.Frame(frame_options)
        search_action_frame.grid(row=4, column=0, columnspan=4, pady=15) 
        btn_tim = ttk.Button(search_action_frame, text="Tìm kiếm", command=self.thuc_hien_tim_kiem, style="Accent.TButton", width=15)
        btn_tim.pack(side=tk.LEFT, padx=5)
        btn_export_search_csv = ttk.Button(search_action_frame, text="Xuất Kết quả (CSV)", command=lambda: self._export_treeview_to_csv(self.tree_tim_kiem, "ket_qua_tim_kiem.csv"), width=20)
        btn_export_search_csv.pack(side=tk.LEFT, padx=5)
        frame_results = ttk.LabelFrame(parent_frame, text="Kết quả tìm kiếm")
        frame_results.pack(fill="both", expand=True, padx=10, pady=5) # Tăng padx
        cols = ('Mã SV', 'Họ Tên', 'Lớp', 'Trường', 'Khoa', 'HK Điểm', 'Môn học', 'Điểm') 
        self.tree_tim_kiem = ttk.Treeview(frame_results, columns=cols, show='headings') 
        
        for col in cols: self.tree_tim_kiem.heading(col, text=col)
        self.tree_tim_kiem.column("Mã SV", width=80, stretch=tk.NO); self.tree_tim_kiem.column("Họ Tên", width=150, stretch=tk.YES)
        self.tree_tim_kiem.column("Lớp", width=80, stretch=tk.NO); self.tree_tim_kiem.column("Trường", width=100, stretch=tk.NO)
        self.tree_tim_kiem.column("Khoa", width=100, stretch=tk.NO); 
        self.tree_tim_kiem.column("HK Điểm", width=80, anchor=tk.W, stretch=tk.NO) 
        self.tree_tim_kiem.column("Môn học", width=120, stretch=tk.YES)
        self.tree_tim_kiem.column("Điểm", width=60, anchor=tk.CENTER, stretch=tk.NO)


        scrollbar_tim_kiem_y = ttk.Scrollbar(frame_results, orient=tk.VERTICAL, command=self.tree_tim_kiem.yview)
        scrollbar_tim_kiem_x = ttk.Scrollbar(frame_results, orient=tk.HORIZONTAL, command=self.tree_tim_kiem.xview)
        self.tree_tim_kiem.configure(yscrollcommand=scrollbar_tim_kiem_y.set, xscrollcommand=scrollbar_tim_kiem_x.set)
        
        self.tree_tim_kiem.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar_tim_kiem_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_tim_kiem_x.pack(side=tk.BOTTOM, fill=tk.X)


    def _populate_mon_hoc_comboboxes(self): 
        mon_hoc_list = self.ql_diem.lay_tat_ca_mon_hoc() # list of dicts {'ma_mh': ..., 'ten_mh': ..., ...}
        # Tạo map từ "Tên MH (Mã MH)" -> Mã MH cho Nhập và Sửa
        self.mon_hoc_display_to_code_map = {f"{mh['ten_mh']} ({mh['ma_mh']})": mh['ma_mh'] for mh in mon_hoc_list}
        mon_hoc_display_values_for_entry_edit = sorted(list(self.mon_hoc_display_to_code_map.keys()))
        
        if hasattr(self, 'combo_mon_hoc_nhapdiem'):
            current_nhap = self.combo_mon_hoc_nhapdiem.get()
            self.combo_mon_hoc_nhapdiem['values'] = [""] + mon_hoc_display_values_for_entry_edit
            self.combo_mon_hoc_nhapdiem.set(current_nhap if current_nhap in self.combo_mon_hoc_nhapdiem['values'] else "")
        
        # ComboBox môn học cho tab Sửa Điểm (sẽ được populate động khi chọn SV và Học Kỳ)
        # Nên không cần populate ở đây, mà trong _on_hoc_ky_sua_diem_selected

        # ComboBox môn học cho tab Tìm Kiếm (chỉ tên môn) - Phải kiểm tra widget tồn tại
        mon_hoc_names_only_for_search = sorted(list(set(mh['ten_mh'] for mh in mon_hoc_list if mh['ten_mh'])))
        if hasattr(self, 'combo_search_mon_hoc') and \
           self.combo_search_mon_hoc is not None and \
           self.combo_search_mon_hoc.winfo_exists():
            try:
                current_search = self.combo_search_mon_hoc.get()
                self.combo_search_mon_hoc['values'] = ["Tất cả"] + mon_hoc_names_only_for_search
                if current_search and current_search in self.combo_search_mon_hoc['values']:
                    self.combo_search_mon_hoc.set(current_search)
                else:
                    self.combo_search_mon_hoc.set("Tất cả")
            except tk.TclError: # Bắt lỗi nếu widget không hợp lệ ngay cả khi winfo_exists() trả về true (hiếm)
                print(f"Cảnh báo: Lỗi TclError khi cấu hình combo_search_mon_hoc dù winfo_exists là true.")

    def _populate_search_filters(self): 
        if not hasattr(self, 'combo_search_lop_hoc'): return 
        all_sv_objs = list(self.ql_diem.danh_sach_sinh_vien.values())
        
        lop_values = sorted(list(set(sv.lop_hoc for sv in all_sv_objs if sv.lop_hoc)))
        truong_values = sorted(list(set(sv.truong for sv in all_sv_objs if sv.truong)))
        khoa_values = sorted(list(set(sv.khoa for sv in all_sv_objs if sv.khoa)))

        combos_config = [
            (self.combo_search_lop_hoc, lop_values),
            (self.combo_search_truong, truong_values),
            (self.combo_search_khoa, khoa_values)
        ]
        for combo, values in combos_config:
            if combo:
                current = combo.get()
                combo_values = ["Tất cả"] + values # Đảm bảo "Tất cả" là lựa chọn
                combo['values'] = combo_values
                if current in combo_values: combo.set(current)
                else: combo.set("Tất cả")

    def thuc_hien_tim_kiem(self):
        if not self._check_ui_permission_before_action("PERFORM_SEARCH", "thực hiện tìm kiếm", silent=False): return
        for item in self.tree_tim_kiem.get_children(): self.tree_tim_kiem.delete(item)
        search_ma_sv_val = self.entry_search_ma_sv.get().strip()
        search_lop_hoc_val = self.combo_search_lop_hoc.get()
        search_truong_val = self.combo_search_truong.get()
        search_khoa_val = self.combo_search_khoa.get()
        search_ten_mon_hoc_val = self.combo_search_mon_hoc.get()
        search_hoc_ky_diem_val = self.combo_hoc_ky_tim_kiem.get() if hasattr(self, 'combo_hoc_ky_tim_kiem') else "Tất cả"

        final_ma_sv = search_ma_sv_val if search_ma_sv_val else None
        final_lop_hoc = search_lop_hoc_val if search_lop_hoc_val != "Tất cả" else None
        final_truong = search_truong_val if search_truong_val != "Tất cả" else None
        final_khoa = search_khoa_val if search_khoa_val != "Tất cả" else None
        final_hoc_ky_diem = search_hoc_ky_diem_val if search_hoc_ky_diem_val != "Tất cả" else None
        
        final_ma_mon_hoc_tim = None
        if search_ten_mon_hoc_val != "Tất cả" and search_ten_mon_hoc_val:
            # Tìm mã môn học từ tên môn học đã chọn trong combobox tìm kiếm
            # self.mon_hoc_display_to_code_map ánh xạ "Tên (Mã)" -> Mã
            # Còn combo_search_mon_hoc chỉ có Tên. Cần tìm mã từ tên.
            for ma_mh_iter, mh_obj in self.ql_diem.danh_sach_mon_hoc.items():
                if mh_obj.ten_mh.lower() == search_ten_mon_hoc_val.lower():
                    final_ma_mon_hoc_tim = ma_mh_iter
                    break
        
        ket_qua = self.ql_diem.tim_kiem_diem(
            ma_sv_filter=final_ma_sv, ma_mon_hoc_filter=final_ma_mon_hoc_tim, 
            lop_hoc_filter=final_lop_hoc, truong_filter=final_truong, 
            khoa_filter=final_khoa, hoc_ky_filter=final_hoc_ky_diem
        )
        
        active_filters = []
        if final_ma_sv: active_filters.append(f"Mã SV: '{final_ma_sv}'")
        if final_lop_hoc: active_filters.append(f"Lớp: '{final_lop_hoc}'")
        if final_truong: active_filters.append(f"Trường: '{final_truong}'")
        if final_khoa: active_filters.append(f"Khoa: '{final_khoa}'")
        if final_hoc_ky_diem: active_filters.append(f"HK Điểm: '{final_hoc_ky_diem}'")
        if search_ten_mon_hoc_val != "Tất cả" and search_ten_mon_hoc_val : active_filters.append(f"Môn: '{search_ten_mon_hoc_val}'")

        keyword_display = ", ".join(active_filters) if active_filters else "tất cả tiêu chí"
        if ket_qua:
            for kq_item in ket_qua:
                self.tree_tim_kiem.insert('', tk.END, values=(
                    kq_item.get('ma_sv'), kq_item.get('ho_ten'), kq_item.get('lop_hoc'), 
                    kq_item.get('truong'), kq_item.get('khoa'), kq_item.get('hoc_ky_diem'),
                    kq_item.get('mon_hoc'), # Đây là tên môn học từ backend
                    f"{kq_item.get('diem'):.1f}" if isinstance(kq_item.get('diem'), (float, int)) else ""
                ))
            self.update_status(f"Tìm thấy {len(ket_qua)} kết quả cho: {keyword_display}.")
        else:
            messagebox.showinfo("Thông báo", f"Không tìm thấy kết quả nào cho: {keyword_display}.")
            self.update_status(f"Không tìm thấy kết quả cho: {keyword_display}.")
#Xếp hạng tab
    def setup_xep_hang_tab(self, parent_frame):
        filter_frame_xh = ttk.Frame(parent_frame)
        filter_frame_xh.pack(pady=(10,5), padx=10, fill=tk.X)
        ttk.Label(filter_frame_xh, text="Lọc theo Lớp:").grid(row=0, column=0, padx=(0,5), pady=5, sticky=tk.W)
        self.combo_lop_filter_xh = ttk.Combobox(filter_frame_xh, state="readonly", width=25) 
        self.combo_lop_filter_xh.grid(row=0, column=1, padx=(0,10), pady=5, sticky=tk.EW)
        self.combo_lop_filter_xh.bind("<<ComboboxSelected>>", lambda e: self.hien_thi_xep_hang()) # Cập nhật khi chọn

        ttk.Label(filter_frame_xh, text="Lọc theo Khoa:").grid(row=0, column=2, padx=(10,5), pady=5, sticky=tk.W)
        self.combo_khoa_filter_xh = ttk.Combobox(filter_frame_xh, state="readonly", width=25) 
        self.combo_khoa_filter_xh.grid(row=0, column=3, padx=(0,10), pady=5, sticky=tk.EW)
        self.combo_khoa_filter_xh.bind("<<ComboboxSelected>>", lambda e: self.hien_thi_xep_hang()) # Cập nhật khi chọn

        ttk.Label(filter_frame_xh, text="Xếp hạng theo Học kỳ:").grid(row=0, column=4, padx=(10,5), pady=5, sticky=tk.W) 
        self.combo_hoc_ky_xep_hang = ttk.Combobox(filter_frame_xh, state="readonly", width=20)
        self.combo_hoc_ky_xep_hang.grid(row=0, column=5, padx=(0,5), pady=5, sticky=tk.EW)
        # self.combo_hoc_ky_xep_hang.set("Tích lũy") # Sẽ được set bởi _populate_hoc_ky_comboboxes
        self.combo_hoc_ky_xep_hang.bind("<<ComboboxSelected>>", lambda e: self.hien_thi_xep_hang()) # Cập nhật khi chọn


        filter_frame_xh.grid_columnconfigure(1, weight=1); filter_frame_xh.grid_columnconfigure(3, weight=1)
        filter_frame_xh.grid_columnconfigure(5, weight=1)

        rank_action_frame = ttk.Frame(parent_frame) # Không cần nút riêng nếu tự cập nhật
        rank_action_frame.pack(pady=(0,10)) # Giảm pady trên
        # btn_hien_thi_xh = ttk.Button(rank_action_frame, text="Hiển thị / Lọc Xếp Hạng", command=self.hien_thi_xep_hang, style="Accent.TButton")
        # btn_hien_thi_xh.pack(side=tk.LEFT, padx=5)
        btn_export_rank_csv = ttk.Button(rank_action_frame, text="Xuất Xếp Hạng (CSV)", command=lambda: self._export_treeview_to_csv(self.tree_xep_hang, "bang_xep_hang.csv"))
        btn_export_rank_csv.pack(side=tk.LEFT, padx=5)

        frame_xh_results = ttk.LabelFrame(parent_frame, text="Bảng xếp hạng Sinh viên theo GPA")
        frame_xh_results.pack(fill="both", expand=True, padx=10, pady=5) # Tăng padx
        cols_xh = ('Hạng', 'Mã SV', 'Họ Tên', 'Lớp', 'Trường', 'Khoa', 'HK Xếp Hạng', 'GPA') 
        self.tree_xep_hang = ttk.Treeview(frame_xh_results, columns=cols_xh, show='headings') 
        
        for col in cols_xh: self.tree_xep_hang.heading(col, text=col)
        self.tree_xep_hang.column("Hạng", width=50, anchor=tk.CENTER, stretch=tk.NO); self.tree_xep_hang.column("Mã SV", width=100, stretch=tk.NO)
        self.tree_xep_hang.column("Họ Tên", width=180, stretch=tk.YES); self.tree_xep_hang.column("Lớp", width=80, stretch=tk.NO)
        self.tree_xep_hang.column("Trường", width=100, anchor=tk.CENTER, stretch=tk.NO); self.tree_xep_hang.column("Khoa", width=100, anchor=tk.CENTER, stretch=tk.NO) # Đã căn giữa từ trước
        self.tree_xep_hang.column("HK Xếp Hạng", width=100, anchor=tk.CENTER, stretch=tk.NO) # Căn giữa cột HK Xếp Hạng
        self.tree_xep_hang.column("GPA", width=70, anchor=tk.CENTER, stretch=tk.NO)
        
        scrollbar_xh_y = ttk.Scrollbar(frame_xh_results, orient=tk.VERTICAL, command=self.tree_xep_hang.yview)
        scrollbar_xh_x = ttk.Scrollbar(frame_xh_results, orient=tk.HORIZONTAL, command=self.tree_xep_hang.xview)
        self.tree_xep_hang.configure(yscrollcommand=scrollbar_xh_y.set, xscrollcommand=scrollbar_xh_x.set)
        
        self.tree_xep_hang.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar_xh_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_xh_x.pack(side=tk.BOTTOM, fill=tk.X)


    def _populate_xh_filters(self): 
        if not hasattr(self, 'combo_lop_filter_xh'): return
        
        all_sv_objs = list(self.ql_diem.danh_sach_sinh_vien.values())
        lop_values = sorted(list(set(sv.lop_hoc for sv in all_sv_objs if sv.lop_hoc)))
        khoa_values = sorted(list(set(sv.khoa for sv in all_sv_objs if sv.khoa)))
        for combo, values in [(self.combo_lop_filter_xh, lop_values), (self.combo_khoa_filter_xh, khoa_values)]:
            if combo:
                current = combo.get()
                combo_values = ["Tất cả"] + values
                combo['values'] = combo_values
                if current in combo_values: combo.set(current)
                else: combo.set("Tất cả")

    def hien_thi_xep_hang(self):
        if not self._check_ui_permission_before_action("VIEW_RANKING", "xem bảng xếp hạng", silent=False): return
        if not hasattr(self, 'tree_xep_hang'): return # Guard clause

        selected_lop = self.combo_lop_filter_xh.get() if hasattr(self, 'combo_lop_filter_xh') else "Tất cả"
        selected_khoa = self.combo_khoa_filter_xh.get() if hasattr(self, 'combo_khoa_filter_xh') else "Tất cả"
        selected_hoc_ky_xh_display = self.combo_hoc_ky_xep_hang.get() if hasattr(self, 'combo_hoc_ky_xep_hang') else "Tích lũy"
        
        hoc_ky_backend_filter = None # Mặc định là GPA tích lũy cho backend
        if selected_hoc_ky_xh_display != "Tích lũy" and selected_hoc_ky_xh_display != "Tất cả": 
            hoc_ky_backend_filter = selected_hoc_ky_xh_display

        for item in self.tree_xep_hang.get_children(): self.tree_xep_hang.delete(item)
        
        # Backend trả về danh sách đã xếp hạng theo GPA (tích lũy hoặc theo kỳ)
        full_list_ranked = self.ql_diem.xep_hang_sinh_vien(hoc_ky_xh=hoc_ky_backend_filter) 
        
        filtered_list_for_display = [
            sv for sv in full_list_ranked 
            if (selected_lop == "Tất cả" or (sv.get('lop_hoc') and sv.get('lop_hoc') == selected_lop)) and \
               (selected_khoa == "Tất cả" or (sv.get('khoa') and sv.get('khoa') == selected_khoa))
        ]

        if filtered_list_for_display:
            for i, sv_data in enumerate(filtered_list_for_display, 1):
                # hoc_ky_xep_hang_display sẽ là "Tích lũy" nếu backend trả về None cho hoc_ky_xep_hang (GPA tích lũy)
                # hoặc là giá trị hoc_ky cụ thể nếu xếp theo kỳ đó.
                hk_display_val = sv_data.get('hoc_ky_xep_hang') if sv_data.get('hoc_ky_xep_hang') else "Tích lũy"
                
                self.tree_xep_hang.insert('', tk.END, values=(
                    i, sv_data.get('ma_sv'), sv_data.get('ho_ten'), sv_data.get('lop_hoc'),
                    sv_data.get('truong'), sv_data.get('khoa'), 
                    hk_display_val, 
                    f"{sv_data.get('gpa', 0.0):.2f}"
                ))
            self.update_status(f"Hiển thị {len(filtered_list_for_display)} SV trong bảng xếp hạng.")
        else:
            # messagebox.showinfo("Thông báo", "Không có dữ liệu xếp hạng phù hợp với bộ lọc.")
            self.update_status("Không có dữ liệu xếp hạng hoặc không khớp bộ lọc.")

    def _populate_student_filters_and_treeview(self, event=None):
        # Chỉ populate nếu các widget tồn tại (ví dụ, khi ở tab Danh sách SV)
        if hasattr(self, 'combo_filter_sv_lop') and hasattr(self, 'combo_filter_sv_khoa'):
            all_sv_objs = self.ql_diem.lay_tat_ca_sinh_vien() # List of dicts
            lop_values = sorted(list(set(sv['lop_hoc'] for sv in all_sv_objs if sv.get('lop_hoc'))))
            khoa_values = sorted(list(set(sv['khoa'] for sv in all_sv_objs if sv.get('khoa'))))

            for combo, values in [(self.combo_filter_sv_lop, lop_values),
                                   (self.combo_filter_sv_khoa, khoa_values)]:
                current_val = combo.get()
                combo['values'] = ["Tất cả"] + values
                if current_val in combo['values']: combo.set(current_val)
                else: combo.set("Tất cả")
            
            self._filter_and_display_students() # Gọi hàm lọc và hiển thị

    def _filter_and_display_students(self, event=None):
        # Chỉ thực hiện nếu các widget tồn tại
        if not (hasattr(self, 'tree_manage_students') and \
                hasattr(self, 'combo_filter_sv_lop') and \
                hasattr(self, 'combo_filter_sv_khoa') and \
                hasattr(self, 'entry_search_sv_text')):
            return

        for item in self.tree_manage_students.get_children(): self.tree_manage_students.delete(item)
        filter_lop, filter_khoa, search_term = self.combo_filter_sv_lop.get(), self.combo_filter_sv_khoa.get(), self.entry_search_sv_text.get().lower()

        all_sv_data = self.ql_diem.lay_tat_ca_sinh_vien() # List of dicts
        
        for sv in all_sv_data:
            match_lop = (filter_lop == "Tất cả" or sv.get('lop_hoc') == filter_lop)
            match_khoa = (filter_khoa == "Tất cả" or sv.get('khoa') == filter_khoa)
            match_search = (not search_term or search_term in sv.get('ho_ten','').lower() or search_term in sv.get('ma_sv','').lower())
            if match_lop and match_khoa and match_search:
                self.tree_manage_students.insert('', tk.END, values=(
                    sv.get('ma_sv'), sv.get('ho_ten'), sv.get('lop_hoc'), 
                    sv.get('khoa'), sv.get('truong'), sv.get('hoc_ky_nhap_hoc')))
#Danh sách môn học
    def hien_thi_danh_sach_mon_hoc(self):
        if not hasattr(self, 'tree_ql_mon_hoc'):
            return

        for item in self.tree_ql_mon_hoc.get_children():
            self.tree_ql_mon_hoc.delete(item)
        mon_hoc_list_for_tree = sorted(self.ql_diem.lay_tat_ca_mon_hoc(), key=lambda x: x['ma_mh'])

        if not mon_hoc_list_for_tree:
            self.update_status("Chưa có môn học nào được thêm vào hệ thống.")
            return

        for mh_data in mon_hoc_list_for_tree:
            self.tree_ql_mon_hoc.insert('', tk.END, values=(
                mh_data.get('ma_mh', ''),
                mh_data.get('ten_mh', ''),
                mh_data.get('so_tin_chi', '')
            ))
        count = len(mon_hoc_list_for_tree)
        self.update_status(f"Hiển thị {count} môn học.")
        if self.tree_ql_mon_hoc.selection(): # Bỏ chọn nếu có
             self.tree_ql_mon_hoc.selection_remove(self.tree_ql_mon_hoc.selection())
        self._clear_mon_hoc_form(show_status=False) # Làm mới form nhưng không báo status

    def setup_bao_cao_tab(self, parent_frame):
        frame_input = ttk.Frame(parent_frame)
        frame_input.pack(pady=10, padx=10, fill=tk.X)
        ttk.Label(frame_input, text="Chọn Lớp:").pack(side=tk.LEFT, padx=(0,5)) # Đổi text
        self.combo_lop_hoc_bao_cao = ttk.Combobox(frame_input, width=23, state="readonly") # Thay Entry bằng Combobox
        self.combo_lop_hoc_bao_cao.pack(side=tk.LEFT, padx=5)
        btn_xuat_bao_cao = ttk.Button(frame_input, text="Hiển thị Báo cáo", command=self.hien_thi_bao_cao, style="Accent.TButton", width=18) # Giữ nguyên command
        btn_xuat_bao_cao.pack(side=tk.LEFT, padx=5)
        btn_luu_bao_cao = ttk.Button(frame_input, text="Lưu Báo cáo (File)", command=self._handle_luu_bao_cao, width=18)
        btn_luu_bao_cao.pack(side=tk.LEFT, padx=10)
        frame_output = ttk.LabelFrame(parent_frame, text="Kết quả Báo cáo")
        frame_output.pack(pady=(5,10), padx=10, fill="both", expand=True) 
        self.text_bao_cao = tk.Text(frame_output, wrap=tk.WORD, height=15, font=("Consolas", 10), relief=tk.FLAT, borderwidth=1) 
        self.text_bao_cao.grid(row=0, column=0, sticky="nsew")
        self.text_bao_cao.config(state=tk.DISABLED)
        scrollbar_bao_cao = ttk.Scrollbar(frame_output, orient=tk.VERTICAL, command=self.text_bao_cao.yview)
        scrollbar_bao_cao.grid(row=0, column=1, sticky="ns")
        self.text_bao_cao.configure(yscrollcommand=scrollbar_bao_cao.set)
        frame_output.grid_rowconfigure(0, weight=1); frame_output.grid_columnconfigure(0, weight=1)
        self._populate_bao_cao_lop_filter() # Gọi để điền dữ liệu ban đầu

    def _populate_bao_cao_lop_filter(self):
        """Điền dữ liệu vào combobox chọn lớp cho tab Báo cáo."""
        if not hasattr(self, 'combo_lop_hoc_bao_cao'):
            return

        all_sv_objs = self.ql_diem.lay_tat_ca_sinh_vien() # List of dicts
        lop_values = sorted(list(set(sv['lop_hoc'] for sv in all_sv_objs if sv.get('lop_hoc'))))

        current_val = self.combo_lop_hoc_bao_cao.get()
        self.combo_lop_hoc_bao_cao['values'] = lop_values # Không cần "Tất cả" ở đây
        if current_val in lop_values:
            self.combo_lop_hoc_bao_cao.set(current_val)
        elif lop_values: # Nếu có lớp, chọn lớp đầu tiên làm mặc định
            self.combo_lop_hoc_bao_cao.set(lop_values[0])
        else: # Nếu không có lớp nào
            self.combo_lop_hoc_bao_cao.set("")

    def hien_thi_bao_cao(self):
        lop_hoc = self.combo_lop_hoc_bao_cao.get().strip() # Lấy từ combobox
        if not lop_hoc: 
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên lớp để xuất báo cáo.", parent=self.master)
            self.update_status("Cần nhập tên lớp cho báo cáo.")
            return
        
        if not self._check_ui_permission_before_action("GENERATE_CLASS_REPORT", "tạo báo cáo lớp", silent=False): return
        self.text_bao_cao.config(state=tk.NORMAL); self.text_bao_cao.delete('1.0', tk.END)
        
        # Kiểm tra lớp có tồn tại không (dựa trên danh sách SV)
        # Hoặc để ql_diem.xuat_bao_cao_lop xử lý việc này và trả về None/dict rỗng
        bao_cao_data = self.ql_diem.xuat_bao_cao_lop(lop_hoc)

        if not bao_cao_data: # Backend trả về None nếu lớp không tồn tại hoặc không có SV
            messagebox.showinfo("Thông báo", f"Không tìm thấy thông tin hoặc không có sinh viên nào trong lớp '{lop_hoc}'.", parent=self.master)
            self.text_bao_cao.insert(tk.END, f"Không tìm thấy thông tin hoặc không có sinh viên nào trong lớp '{lop_hoc}'.")
            self.update_status(f"Báo cáo: Không tìm thấy lớp '{lop_hoc}' hoặc lớp rỗng.")
        elif bao_cao_data.get("so_sinh_vien", 0) == 0 : # Backend trả về có thông tin lớp, nhưng số SV = 0
            messagebox.showinfo("Thông báo", f"Lớp '{bao_cao_data.get('lop_hoc', lop_hoc)}' không có sinh viên nào.", parent=self.master)
            self.text_bao_cao.insert(tk.END, f"Lớp '{bao_cao_data.get('lop_hoc', lop_hoc)}' không có sinh viên nào.")
            self.update_status(f"Báo cáo: Lớp '{lop_hoc}' không có sinh viên.")
        elif not bao_cao_data.get("danh_sach_sinh_vien"): # Có SV nhưng không có SV nào có điểm để liệt kê chi tiết
            report_str = f"{'BÁO CÁO LỚP'.center(80)}\n"
            report_str += f"{'-'*80}\n"
            report_str += f"Lớp: {bao_cao_data.get('lop_hoc', 'N/A'):<30} Tổng số SV: {bao_cao_data.get('so_sinh_vien', 0)}\n"
            report_str += f"GPA Tích Lũy TB Lớp: {bao_cao_data.get('diem_trung_binh_lop_tich_luy', 0.0):.2f}\n"
            report_str += f"{'-'*80}\n"
            report_str += "Không có sinh viên nào trong lớp này có dữ liệu điểm chi tiết để hiển thị.\n"
            self.text_bao_cao.insert(tk.END, report_str)
            self.update_status(f"Báo cáo cho lớp '{lop_hoc}' (không có SV có điểm chi tiết).")
        else: # Có danh sách sinh viên với điểm
            report_str =  f"{'BÁO CÁO LỚP'.center(80)}\n"
            report_str += f"{'-'*80}\n"
            report_str += f"Lớp: {bao_cao_data.get('lop_hoc', 'N/A'):<30} Tổng số SV: {bao_cao_data.get('so_sinh_vien', 0)}\n"
            report_str += f"GPA Tích Lũy TB Lớp: {bao_cao_data.get('diem_trung_binh_lop_tich_luy', 0.0):.2f}\n"
            report_str += f"{'='*80}\n\n"
            for sv_data in bao_cao_data["danh_sach_sinh_vien"]:
                report_str += f"SV: {sv_data['ho_ten']} ({sv_data['ma_sv']}) - Lớp: {sv_data.get('lop_hoc','N/A')} - Khoa: {sv_data.get('khoa','N/A')}\n"
                report_str += f"GPA Tích Lũy: {sv_data.get('gpa_tich_luy', 0.0):.2f}\n"
                if sv_data.get('diem_theo_hoc_ky'):
                    for hoc_ky, diem_ky_data in sv_data['diem_theo_hoc_ky'].items():
                        report_str += f"  Học kỳ: {hoc_ky} - GPA Kỳ: {diem_ky_data.get('_GPA_HOC_KY_', 0.0):.2f}\n"
                        for mon_display, diem_so_mh in diem_ky_data.items():
                            if mon_display != '_GPA_HOC_KY_': # Không lặp lại GPA Kỳ
                                report_str += f"    + {mon_display}: {diem_so_mh}\n"
                else:
                    report_str += "  (Chưa có dữ liệu điểm theo học kỳ)\n"
                report_str += f"{'-'*60}\n"
            self.text_bao_cao.insert(tk.END, report_str)
            self.update_status(f"Đã hiển thị báo cáo cho lớp '{lop_hoc}'.")
        
        self.text_bao_cao.config(state=tk.DISABLED)
        
    def _handle_luu_bao_cao(self):
        content = self.text_bao_cao.get("1.0", tk.END).strip()
        if not content or "Không tìm thấy thông tin" in content or "không có sinh viên nào" in content or "Chưa có dữ liệu" in content :
            messagebox.showwarning("Cảnh báo", "Không có nội dung báo cáo hợp lệ để lưu.", parent=self.master)
            self.update_status("Lưu báo cáo thất bại: Nội dung không hợp lệ.")
            return

        lop_hoc_bc = self.combo_lop_hoc_bao_cao.get().strip() # Lấy từ combobox
        default_filename = f"BaoCao_Lop_{lop_hoc_bc.replace(' ', '_')}.txt" if lop_hoc_bc else "BaoCaoLop.txt"
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt", 
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")], 
            initialfile=default_filename,
            title="Lưu Báo cáo Lớp",
            parent=self.master
        )
        if not filepath: 
            self.update_status("Đã hủy thao tác lưu báo cáo.")
            return
        try:
            with open(filepath, 'w', encoding='utf-8') as f: f.write(content)
            messagebox.showinfo("Thành công", f"Báo cáo đã được lưu vào:\n{filepath}", parent=self.master)
            self.update_status(f"Đã lưu báo cáo vào: {filepath}")
        except Exception as e: 
            messagebox.showerror("Lỗi Lưu File", f"Không thể lưu file báo cáo: {e}", parent=self.master)
            self.update_status(f"Lỗi khi lưu báo cáo: {e}")
    # --- Tab Biểu đồ ---
    def _clear_chart_area(self):
        """Xóa biểu đồ hiện tại khỏi canvas."""
        # 1. Detach the Matplotlib FigureCanvas's notion of the toolbar
        #    to prevent clf() from trying to update a (soon to be) destroyed Tk widget.
        if self.chart_figure and self.chart_figure.canvas and \
           hasattr(self.chart_figure.canvas, 'toolbar') and \
           self.chart_figure.canvas.toolbar == self.chart_toolbar: # Ensure it's the one we manage
            self.chart_figure.canvas.toolbar = None

        # 2. Clear the Matplotlib Figure's artists.
        #    This needs to happen while the Figure's canvas object and its
        #    underlying Tk canvas widget are still valid.
        if self.chart_figure:
            self.chart_figure.clf() # Clear the figure

        # 3. Now, destroy the Tkinter widgets.
        if self.chart_toolbar:
            self.chart_toolbar.destroy()
            self.chart_toolbar = None

        if self.chart_canvas_widget:
            self.chart_canvas_widget.get_tk_widget().destroy()
            self.chart_canvas_widget = None

    def setup_charts_tab(self, parent_frame):
        control_frame = ttk.Frame(parent_frame)
        control_frame.pack(fill=tk.X, pady=10, padx=10)

        ttk.Label(control_frame, text="Chọn loại biểu đồ:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.combo_chart_type = ttk.Combobox(control_frame, state="readonly", width=30)
        self.combo_chart_type['values'] = [
            "Phân phối điểm môn học theo lớp",
            "Xu hướng GPA của sinh viên",
            "Tỷ lệ sinh viên theo Khoa",
            "Tỷ lệ sinh viên theo Lớp"
        ]
        self.combo_chart_type.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.combo_chart_type.bind("<<ComboboxSelected>>", self._on_chart_type_selected)
        

        self.filters_frame_charts = ttk.Frame(control_frame)
        self.filters_frame_charts.grid(row=1, column=0, columnspan=3, sticky=tk.EW, pady=(10,0))

        self.filter_grade_dist_frame = ttk.Frame(self.filters_frame_charts)
        ttk.Label(self.filter_grade_dist_frame, text="Chọn Lớp:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.combo_chart_lop_hoc = ttk.Combobox(self.filter_grade_dist_frame, state="readonly", width=25)
        self.combo_chart_lop_hoc.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Label(self.filter_grade_dist_frame, text="Chọn Môn học:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.combo_chart_mon_hoc_dist = ttk.Combobox(self.filter_grade_dist_frame, state="readonly", width=30)
        self.combo_chart_mon_hoc_dist.grid(row=0, column=3, padx=5, pady=5, sticky=tk.EW)
        self.filter_grade_dist_frame.grid_columnconfigure(1, weight=1)
        self.filter_grade_dist_frame.grid_columnconfigure(3, weight=1)

        self.filter_gpa_trend_frame = ttk.Frame(self.filters_frame_charts)
        ttk.Label(self.filter_gpa_trend_frame, text="Chọn Sinh viên:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.combo_chart_sv_gpa = ttk.Combobox(self.filter_gpa_trend_frame, state="readonly", width=40)
        self.combo_chart_sv_gpa.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.filter_gpa_trend_frame.grid_columnconfigure(1, weight=1)

        self.filter_student_dist_frame = ttk.Frame(self.filters_frame_charts) # Hiện tại không có filter con

        btn_draw_chart = ttk.Button(control_frame, text="Vẽ Biểu đồ", command=self._draw_selected_chart, style="Accent.TButton")
        btn_draw_chart.grid(row=0, column=2, padx=10, pady=5, sticky=tk.E)
        control_frame.grid_columnconfigure(1, weight=1)

        self.chart_display_frame = ttk.LabelFrame(parent_frame, text="Biểu đồ")
        self.chart_display_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        if self.combo_chart_type['values']: self.combo_chart_type.current(0) # Chọn mặc định nếu có giá trị
        self._on_chart_type_selected() # This will call _clear_chart_area (the correct one now)
        self._populate_chart_filters() # Populate filters after initial setup

    def _on_chart_type_selected(self, event=None):
        selected_type = self.combo_chart_type.get()
        self._clear_chart_area()

        self.filter_grade_dist_frame.pack_forget()
        self.filter_gpa_trend_frame.pack_forget()
        self.filter_student_dist_frame.pack_forget()

        if selected_type == "Phân phối điểm môn học theo lớp":
            self.filter_grade_dist_frame.pack(fill=tk.X, pady=5)
        elif selected_type == "Xu hướng GPA của sinh viên":
            self.filter_gpa_trend_frame.pack(fill=tk.X, pady=5)
        elif selected_type == "Tỷ lệ sinh viên theo Khoa" or selected_type == "Tỷ lệ sinh viên theo Lớp":
            self.filter_student_dist_frame.pack(fill=tk.X, pady=5)
        self.update_status(f"Chọn loại biểu đồ: {selected_type}. Chọn bộ lọc và nhấn 'Vẽ Biểu đồ'.")

    def _populate_chart_filters(self):
        all_sv_dicts = self.ql_diem.lay_tat_ca_sinh_vien()
        lop_values = sorted(list(set(sv['lop_hoc'] for sv in all_sv_dicts if sv.get('lop_hoc'))))
        self.combo_chart_lop_hoc['values'] = lop_values
        if lop_values: self.combo_chart_lop_hoc.current(0)

        mon_hoc_list = self.ql_diem.lay_tat_ca_mon_hoc()
        self.mon_hoc_display_to_code_map.update({f"{mh['ten_mh']} ({mh['ma_mh']})": mh['ma_mh'] for mh in mon_hoc_list})
        mon_hoc_display_values = sorted(list(self.mon_hoc_display_to_code_map.keys()))
        self.combo_chart_mon_hoc_dist['values'] = mon_hoc_display_values
        if mon_hoc_display_values: self.combo_chart_mon_hoc_dist.current(0)

        sv_display_list = sorted([f"{sv.ho_ten} ({sv.ma_sv})" for sv in self.ql_diem.danh_sach_sinh_vien.values()])
        self.combo_chart_sv_gpa['values'] = sv_display_list
        if sv_display_list: self.combo_chart_sv_gpa.current(0)

    def _draw_selected_chart(self):
        if not self._check_ui_permission_before_action("GENERATE_CHARTS", "tạo biểu đồ"): return
        selected_type = self.combo_chart_type.get()
        self._clear_chart_area()

        self.chart_figure = Figure(figsize=(7, 4.5), dpi=100) # Khởi tạo Figure
        plot_drawn = False
        if selected_type == "Phân phối điểm môn học theo lớp":
            plot_drawn = self._draw_grade_distribution_chart(self.chart_figure)
        elif selected_type == "Xu hướng GPA của sinh viên":
            plot_drawn = self._draw_gpa_trend_chart(self.chart_figure)
        elif selected_type == "Tỷ lệ sinh viên theo Khoa":
            plot_drawn = self._draw_student_distribution_chart(self.chart_figure, group_by='khoa')
        elif selected_type == "Tỷ lệ sinh viên theo Lớp":
            plot_drawn = self._draw_student_distribution_chart(self.chart_figure, group_by='lop_hoc')

        if plot_drawn:
            self.chart_canvas_widget = FigureCanvasTkAgg(self.chart_figure, master=self.chart_display_frame)
            self.chart_canvas_widget.draw()
            canvas_tk_widget = self.chart_canvas_widget.get_tk_widget()
            canvas_tk_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            if self.chart_toolbar: self.chart_toolbar.destroy()
            self.chart_toolbar = NavigationToolbar2Tk(self.chart_canvas_widget, self.chart_display_frame)
            self.chart_toolbar.update()
            # canvas_tk_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True) # Đã pack ở trên
            self.update_status(f"Đã vẽ biểu đồ: {selected_type}")
        else:
            self.update_status("Không thể vẽ biểu đồ: Thiếu dữ liệu hoặc lựa chọn không hợp lệ.")

    def _draw_grade_distribution_chart(self, fig):
        lop_hoc = self.combo_chart_lop_hoc.get()
        mon_hoc_display = self.combo_chart_mon_hoc_dist.get()
        ma_mh = self.mon_hoc_display_to_code_map.get(mon_hoc_display)
        if not lop_hoc or not ma_mh:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn Lớp và Môn học.", parent=self.master)
            return False
        data = self.ql_diem.get_grade_distribution_data(lop_hoc, ma_mh)
        if not any(data.values()):
            messagebox.showinfo("Không có dữ liệu", f"Không có dữ liệu điểm cho môn '{mon_hoc_display}' trong lớp '{lop_hoc}'.", parent=self.master)
            return False
        labels = list(data.keys()); values = list(data.values())
        ax = fig.add_subplot(111)
        bars = ax.bar(labels, values, color=['#4CAF50', '#8BC34A', '#FFEB3B', '#FFC107', '#F44336'])
        ax.set_ylabel('Số lượng Sinh viên'); ax.set_title(f'Phân phối điểm môn "{mon_hoc_display}"\nLớp: {lop_hoc}'); ax.set_xlabel('Xếp loại')
        for bar in bars:
            yval = bar.get_height()
            if yval > 0: ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.05 * (max(values) if values else 1), int(yval), ha='center', va='bottom')
        fig.tight_layout(); return True

    def _draw_gpa_trend_chart(self, fig):
        sv_display = self.combo_chart_sv_gpa.get()
        if not sv_display: messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn Sinh viên.", parent=self.master); return False
        try: ma_sv = sv_display.split('(')[-1].replace(')', '').strip()
        except: messagebox.showerror("Lỗi", "Lựa chọn sinh viên không hợp lệ.", parent=self.master); return False
        data = self.ql_diem.get_student_gpa_trend_data(ma_sv)
        if not data: messagebox.showinfo("Không có dữ liệu", f"Không có dữ liệu GPA cho SV: {sv_display}.", parent=self.master); return False
        hoc_ky_labels = list(data.keys()); gpa_values = list(data.values())
        ax = fig.add_subplot(111)
        ax.plot(hoc_ky_labels, gpa_values, marker='o', linestyle='-', color='dodgerblue')
        ax.set_ylabel('Điểm GPA (Hệ 10)'); ax.set_xlabel('Học kỳ'); ax.set_title(f'Xu hướng GPA của: {sv_display}'); ax.set_ylim(0, 10.5); ax.grid(True, linestyle=':', alpha=0.7)
        for i, txt in enumerate(gpa_values): ax.annotate(f"{txt:.2f}", (hoc_ky_labels[i], gpa_values[i]), textcoords="offset points", xytext=(0,5), ha='center')
        if len(hoc_ky_labels) > 4: fig.autofmt_xdate(rotation=30, ha='right')
        fig.tight_layout(); return True

    def _draw_student_distribution_chart(self, fig, group_by='khoa'):
        data = self.ql_diem.get_student_distribution_by_faculty_or_class_data(group_by=group_by)
        if not data: messagebox.showinfo("Không có dữ liệu", f"Không có dữ liệu phân phối SV theo {group_by}.", parent=self.master); return False
        labels = [l for l,v in data.items() if v > 0]; values = [v for v in data.values() if v > 0] # Chỉ lấy mục có giá trị
        if not values: messagebox.showinfo("Không có dữ liệu", f"Không có SV (số lượng > 0) để phân phối theo {group_by}.", parent=self.master); return False
        ax = fig.add_subplot(111)
        def my_autopct(pct):
            total = sum(values); val = int(round(pct*total/100.0))
            return f'{pct:.1f}%\n({val})' if pct > 1 else '' # Chỉ hiển thị % nếu đủ lớn
        wedges, texts, autotexts = ax.pie(values, autopct=my_autopct, startangle=120, pctdistance=0.82,
                                          colors=plt.cm.Paired(range(len(labels)))) # Dùng colormap
        ax.axis('equal'); title_str = f"Tỷ lệ Sinh viên theo {group_by.replace('_',' ').title()}"
        ax.set_title(title_str)
        ax.legend(wedges, labels, title=f"{group_by.replace('_',' ').title()}", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize='small')
        fig.tight_layout(rect=[0, 0, 0.75, 1]); return True # Điều chỉnh rect cho legend

    def update_status(self, message):
        self.status_label.config(text=message)

if __name__ == "__main__":
    if _MAIN_HAS_RUN:
        print("CRITICAL WARNING: Main execution block in app_gui.py is trying to run again. Preventing re-initialization.")
    else:
        _MAIN_HAS_RUN = True
        root = None
        try:
            print("Đang khởi tạo ThemedTk...")
            root = ThemedTk(theme="breeze") 
            print("ThemedTk đã khởi tạo.")
            root.title("Hệ thống Quản lý Điểm Sinh viên")
            root.geometry("1000x750")
            
            print("Đang khởi tạo QuanLyDiemGUI...")
            app = QuanLyDiemGUI(root)
            print("QuanLyDiemGUI đã khởi tạo.")
            
            # Kiểm tra xem app có được khởi tạo thành công không
            if not hasattr(app, 'master') or not app.master:
                print("LỖI: Đối tượng QuanLyDiemGUI không được khởi tạo đầy đủ. Kiểm tra lỗi trong __init__.")
                if root and root.winfo_exists():
                    root.destroy()
            else:
                print("Đang chạy root.mainloop()...")
                root.mainloop()
                print("root.mainloop() đã kết thúc.")

        except Exception as e:
            print(f"LỖI NGOẠI LỆ KHÔNG XÁC ĐỊNH TRONG KHỐI MAIN: {e}")
            import traceback
            traceback.print_exc()
            if root and root.winfo_exists():
                root.destroy()
            try:
                error_root = tk.Tk(); error_root.withdraw()
                messagebox.showerror("Lỗi Khởi Chạy Nghiêm Trọng", f"Đã xảy ra lỗi không mong muốn:\n{e}\n\nVui lòng kiểm tra console.", parent=None)
                error_root.destroy()
            except Exception as e2: print(f"Không thể hiển thị messagebox lỗi: {e2}")