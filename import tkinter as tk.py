import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog # Cần cho lưu file
from quan_ly_diem import QuanLyDiem 

# import tkinter as tk # Đã import ở trên
# from tkinter import ttk, messagebox # Đã import ở trên
from ttkthemes import ThemedTk # Import ThemedTk
# from tkinter import filedialog
from quan_ly_diem import QuanLyDiem # Đảm bảo file này tồn tại và đã cập nhật

class QuanLyDiemGUI:
    def __init__(self, master):
        self.master = master
        # master.title("Hệ thống Quản lý Điểm Sinh viên") # Sẽ được đặt bởi ThemedTk
        # master.geometry("800x650") # Tăng kích thước cửa sổ một chút nữa cho thoải mái
        
        # --- Khởi tạo đối tượng quản lý điểm ---
        self.ql_diem = QuanLyDiem()

        # --- Thiết lập Style ---
        self.setup_styles() # Gọi hàm thiết lập style

        # --- Tạo các tab cho từng chức năng ---
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        # Tạo các Frame cho tab với padding
        self.tab_them_sv = ttk.Frame(self.notebook, padding="15")
        self.tab_ql_mon_hoc = ttk.Frame(self.notebook, padding="15") # Tab mới
        self.tab_nhap_diem = ttk.Frame(self.notebook, padding="15")
        self.tab_xem_diem = ttk.Frame(self.notebook, padding="15")
        self.tab_sua_diem = ttk.Frame(self.notebook, padding="15")
        self.tab_tim_kiem = ttk.Frame(self.notebook, padding="15")
        self.tab_xep_hang = ttk.Frame(self.notebook, padding="15")
        self.tab_bao_cao = ttk.Frame(self.notebook, padding="15")

        self.notebook.add(self.tab_them_sv, text='Thêm Sinh viên')
        self.notebook.add(self.tab_ql_mon_hoc, text='Quản lý Môn học') # Thêm tab
        self.notebook.add(self.tab_xem_diem, text='Xem/Xóa Điểm')
        self.notebook.add(self.tab_nhap_diem, text='Nhập Điểm')
        self.notebook.add(self.tab_sua_diem, text='Sửa Điểm')
        self.notebook.add(self.tab_tim_kiem, text='Tìm kiếm')
        self.notebook.add(self.tab_xep_hang, text='Xếp Hạng')
        self.notebook.add(self.tab_bao_cao, text='Báo cáo')

        # --- Status Bar ---
        self.status_label = ttk.Label(master, text="Sẵn sàng", relief=tk.SUNKEN, anchor=tk.W, padding=(5,2))
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # --- Giao diện các Tab ---
        self.setup_them_sv_tab()
        self.setup_ql_mon_hoc_tab() # Gọi setup cho tab mới
        self.setup_nhap_diem_tab()
        self.setup_xem_xoa_diem_tab()
        self.setup_sua_diem_tab()
        self.setup_tim_kiem_tab()
        self.setup_xep_hang_tab()
        self.setup_bao_cao_tab()

        # Cập nhật bộ lọc sau khi giao diện được tạo và dữ liệu có thể đã được tải
        self._populate_all_combobox_filters() # Hàm tổng hợp để gọi các populate
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)


    def _populate_all_combobox_filters(self):
        """Gọi tất cả các hàm populate cho combobox một cách có thứ tự."""
        self._populate_them_sv_comboboxes() 
        self._populate_xh_filters() 
        self._populate_mon_hoc_comboboxes() 
        self._populate_search_filters() 

    def on_tab_change(self, event):
        """Gọi khi chuyển tab để cập nhật bộ lọc nếu cần."""
        selected_tab_index = self.notebook.index(self.notebook.select())
        selected_tab_text = self.notebook.tab(selected_tab_index, "text")

        if selected_tab_text == "Tìm kiếm":
            self._populate_search_filters()
            self._populate_mon_hoc_comboboxes() 
        elif selected_tab_text == "Xếp Hạng":
            self._populate_xh_filters()
        elif selected_tab_text == "Nhập Điểm":
            self._populate_mon_hoc_comboboxes()
        elif selected_tab_text == "Sửa Điểm":
            self._populate_mon_hoc_comboboxes()
        elif selected_tab_text == "Thêm Sinh viên":
            self._populate_them_sv_comboboxes()
        elif selected_tab_text == "Quản lý Môn học":
            self.hien_thi_danh_sach_mon_hoc()

    def setup_styles(self):
        """Thiết lập các kiểu dáng cho ứng dụng."""
        style = ttk.Style(self.master)
        # print(style.theme_names()) # In ra các theme có sẵn để chọn
        # style.theme_use("clam") # Thử các theme khác như 'alt', 'default', 'clam', 'vista', 'xpnative'
                                # Hoặc các theme từ ThemedTk như 'arc', 'breeze', 'plastik', v.v.
        
        # Font chữ chung
        default_font = ('Segoe UI', 10) # Hoặc 'Calibri', 'Arial'
        heading_font = ('Segoe UI', 11, 'bold')
        label_font = ('Segoe UI', 10)
        entry_font = ('Segoe UI', 10)
        button_font = ('Segoe UI', 10, 'bold')
        
        # Cấu hình style chung
        style.configure('.', font=default_font, padding=5)

        # Style cho Label
        style.configure("TLabel", font=label_font, padding=(0, 5)) # Thêm padding dưới cho label
        style.configure("Header.TLabel", font=heading_font, padding=(0,10)) # Style cho tiêu đề lớn

        # Style cho Entry (Thực ra Entry của ttk là TEntry nhưng thường dùng tk.Entry)
        # Nếu dùng tk.Entry, cần cấu hình font riêng khi tạo widget
        # Nếu dùng ttk.Entry, style này sẽ áp dụng
        style.configure("TEntry", font=entry_font, padding=5)

        # Style cho Button
        # Nút thường: Nền xám, chữ đen
        style.configure("TButton", font=button_font, padding=8, background="#e0e0e0", foreground="black")
        # Nút nổi bật (cũng dùng style tương tự cho đồng bộ, hoặc bạn có thể tùy chỉnh khác đi)
        style.configure("Accent.TButton", font=button_font, padding=8, background="#cccccc", foreground="black") # Một màu xám hơi đậm hơn cho Accent

        # Style cho Treeview
        style.configure("Treeview", font=default_font, rowheight=28) # Tăng chiều cao hàng
        style.configure("Treeview.Heading", font=heading_font, padding=5)
        # Thêm màu nền xen kẽ cho các hàng (nếu theme hỗ trợ hoặc cần tùy chỉnh sâu hơn)
        # style.map("Treeview", background=[('selected', '#007bff')], foreground=[('selected', 'white')])


        # Style cho Notebook Tabs
        style.configure("TNotebook.Tab", font=button_font, padding=(10, 5))
        
        # Style cho LabelFrame
        style.configure("TLabelframe", padding=10)
        style.configure("TLabelframe.Label", font=heading_font)

        # Style cho Combobox
        style.configure("TCombobox", font=entry_font, padding=5)
        self.master.option_add("*TCombobox*Listbox*Font", entry_font) # Font cho danh sách thả xuống


    # --- Các phương thức setup tab và xử lý sự kiện (đã có từ code của bạn) ---
    # ... (Giữ nguyên các phương thức setup_..._tab và các hàm xử lý sự kiện của bạn)
    # Chỉ cần đảm bảo các widget được tạo là ttk widget nếu muốn chúng kế thừa style
    # Ví dụ: thay tk.Label -> ttk.Label, tk.Button -> ttk.Button

    # Sửa: Thêm phương thức setup_them_sv_tab
    def setup_them_sv_tab(self):
        """Thiết lập các widget cho tab Thêm Sinh viên."""
        # Sử dụng Frame con để nhóm và căn giữa nếu muốn
        content_frame = ttk.Frame(self.tab_them_sv)
        content_frame.pack(expand=True) # Căn giữa Frame

        ttk.Label(content_frame, text="Mã số sinh viên (9 chữ số):").grid(row=0, column=0, padx=5, pady=8, sticky=tk.W)
        self.entry_ma_sv_them = ttk.Entry(content_frame, width=40) # Bỏ font riêng, dùng style chung
        self.entry_ma_sv_them.grid(row=0, column=1, padx=5, pady=8)

        ttk.Label(content_frame, text="Họ và tên:").grid(row=1, column=0, padx=5, pady=8, sticky=tk.W)
        self.entry_ho_ten_them = ttk.Entry(content_frame, width=40)
        self.entry_ho_ten_them.grid(row=1, column=1, padx=5, pady=8)

        ttk.Label(content_frame, text="Lớp học:").grid(row=2, column=0, padx=5, pady=8, sticky=tk.W)
        self.combo_lop_hoc_them = ttk.Combobox(content_frame, width=38) # Thay Entry bằng Combobox
        self.combo_lop_hoc_them.grid(row=2, column=1, padx=5, pady=8)

        ttk.Label(content_frame, text="Trường:").grid(row=3, column=0, padx=5, pady=8, sticky=tk.W)
        self.combo_truong_them = ttk.Combobox(content_frame, width=38) # Thay Entry bằng Combobox
        self.combo_truong_them.grid(row=3, column=1, padx=5, pady=8)

        ttk.Label(content_frame, text="Khoa:").grid(row=4, column=0, padx=5, pady=8, sticky=tk.W)
        self.combo_khoa_them = ttk.Combobox(content_frame, width=38) # Thay Entry bằng Combobox
        self.combo_khoa_them.grid(row=4, column=1, padx=5, pady=8)

        btn_them_sv = ttk.Button(content_frame, text="Thêm Sinh viên", command=self._handle_add_student_submit, style="Accent.TButton")
        btn_them_sv.grid(row=5, column=0, columnspan=2, pady=20)


    def _handle_add_student_submit(self):
        ma_sv = self.entry_ma_sv_them.get().strip()
        ho_ten = self.entry_ho_ten_them.get().strip()
        lop_hoc = self.combo_lop_hoc_them.get().strip() # Lấy từ combobox
        truong = self.combo_truong_them.get().strip()   # Lấy từ combobox
        khoa = self.combo_khoa_them.get().strip()     # Lấy từ combobox

        if not ma_sv or not ho_ten or not lop_hoc or not truong or not khoa:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin sinh viên.")
            self.update_status("Thêm sinh viên thất bại: Thiếu thông tin")
            return
        
        ket_qua_them = self.ql_diem.them_sinh_vien(ma_sv, ho_ten, lop_hoc, truong, khoa)

        if ket_qua_them == "Thêm sinh viên thành công.":
            messagebox.showinfo("Thành công", f"Đã thêm sinh viên {ho_ten} ({ma_sv}).")
            self.update_status(f"Đã thêm sinh viên {ho_ten} ({ma_sv})")
            self.entry_ma_sv_them.delete(0, tk.END)
            self.entry_ho_ten_them.delete(0, tk.END)
            self.combo_lop_hoc_them.set("") # Xóa combobox
            self.combo_truong_them.set("")   # Xóa combobox
            self.combo_khoa_them.set("")     # Xóa combobox
            self._populate_all_combobox_filters() # Cập nhật tất cả các bộ lọc

        elif ket_qua_them == "Mã số sinh viên đã tồn tại!":
            messagebox.showerror("Lỗi", f"Mã số sinh viên '{ma_sv}' đã tồn tại!")
            self.update_status(f"Thêm thất bại: Mã SV '{ma_sv}' đã tồn tại.")
        elif ket_qua_them == "Mã SV chỉ được chứa chữ số.":
            messagebox.showerror("Lỗi", "Mã sinh viên không hợp lệ: chỉ được chứa chữ số.")
            self.update_status("Thêm thất bại: Mã SV chứa ký tự không phải số.")
        elif ket_qua_them == "Mã SV phải có đúng 9 chữ số.":
            messagebox.showerror("Lỗi", "Mã sinh viên không hợp lệ: phải có đúng 9 chữ số.")
            self.update_status("Thêm thất bại: Mã SV không đủ 9 chữ số.")
        else: 
            messagebox.showerror("Lỗi", f"Không thể thêm sinh viên: {ket_qua_them}")
            self.update_status(f"Thêm sinh viên thất bại: {ket_qua_them}")

    def _populate_them_sv_comboboxes(self):
        """Điền dữ liệu vào các combobox Lớp, Trường, Khoa trên tab Thêm Sinh viên."""
        all_student_objects = list(self.ql_diem.danh_sach_sinh_vien.values())

        lop_hoc_values = sorted(list(set(sv_obj.lop_hoc for sv_obj in all_student_objects if sv_obj.lop_hoc)))
        truong_values = sorted(list(set(sv_obj.truong for sv_obj in all_student_objects if sv_obj.truong)))
        khoa_values = sorted(list(set(sv_obj.khoa for sv_obj in all_student_objects if sv_obj.khoa)))

        for combo, new_values in [
            (self.combo_lop_hoc_them, lop_hoc_values),
            (self.combo_truong_them, truong_values),
            (self.combo_khoa_them, khoa_values)
        ]:
            # Giữ lại giá trị hiện tại nếu người dùng đang nhập dở
            # current_text = combo.get() 
            combo['values'] = new_values
            # if current_text not in new_values: # Nếu giá trị đang nhập không có trong list thì vẫn giữ
            #     combo.set(current_text)
            # else: # Nếu có trong list thì set lại để đảm bảo (thường không cần)
            #     combo.set(current_text) 
            # Để đơn giản, không set lại giá trị đang nhập.

    def setup_ql_mon_hoc_tab(self):
        """Thiết lập các widget cho tab Quản lý Môn học."""
        frame_input_mh = ttk.LabelFrame(self.tab_ql_mon_hoc, text="Thêm/Cập nhật Môn học")
        frame_input_mh.pack(fill=tk.X, padx=5, pady=10)

        ttk.Label(frame_input_mh, text="Mã Môn học:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_ma_mh_ql = ttk.Entry(frame_input_mh, width=30)
        self.entry_ma_mh_ql.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(frame_input_mh, text="Tên Môn học:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_ten_mh_ql = ttk.Entry(frame_input_mh, width=40)
        self.entry_ten_mh_ql.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(frame_input_mh, text="Số tín chỉ:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_so_tin_chi_ql = ttk.Entry(frame_input_mh, width=10)
        self.entry_so_tin_chi_ql.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        frame_input_mh.grid_columnconfigure(1, weight=1)

        btn_them_mh = ttk.Button(frame_input_mh, text="Thêm Môn học", command=self._handle_them_mon_hoc, style="Accent.TButton")
        btn_them_mh.grid(row=3, column=0, columnspan=2, pady=10)

        frame_ds_mh = ttk.LabelFrame(self.tab_ql_mon_hoc, text="Danh sách Môn học")
        frame_ds_mh.pack(fill="both", expand=True, padx=5, pady=5)

        cols_mh = ('Mã MH', 'Tên Môn học', 'Số Tín chỉ')
        self.tree_ql_mon_hoc = ttk.Treeview(frame_ds_mh, columns=cols_mh, show='headings')
        for col in cols_mh:
            self.tree_ql_mon_hoc.heading(col, text=col)
        self.tree_ql_mon_hoc.column("Mã MH", width=100, anchor=tk.W)
        self.tree_ql_mon_hoc.column("Tên Môn học", width=250, anchor=tk.W)
        self.tree_ql_mon_hoc.column("Số Tín chỉ", width=80, anchor=tk.CENTER)

        scrollbar_mh = ttk.Scrollbar(frame_ds_mh, orient=tk.VERTICAL, command=self.tree_ql_mon_hoc.yview)
        self.tree_ql_mon_hoc.configure(yscrollcommand=scrollbar_mh.set)
        self.tree_ql_mon_hoc.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar_mh.pack(side=tk.RIGHT, fill=tk.Y)

        self.hien_thi_danh_sach_mon_hoc() 

    def setup_nhap_diem_tab(self):
        content_frame = ttk.Frame(self.tab_nhap_diem)
        content_frame.pack(expand=True)

        ttk.Label(content_frame, text="Mã số sinh viên:").grid(row=0, column=0, padx=5, pady=8, sticky=tk.W)
        self.entry_ma_sv_nhapdiem = ttk.Entry(content_frame, width=40)
        self.entry_ma_sv_nhapdiem.grid(row=0, column=1, padx=5, pady=8)

        ttk.Label(content_frame, text="Chọn Môn học:").grid(row=1, column=0, padx=5, pady=8, sticky=tk.W)
        self.combo_mon_hoc_nhapdiem = ttk.Combobox(content_frame, width=38, state="readonly")
        self.combo_mon_hoc_nhapdiem.grid(row=1, column=1, padx=5, pady=8)

        ttk.Label(content_frame, text="Điểm (0-10):").grid(row=2, column=0, padx=5, pady=8, sticky=tk.W)
        self.entry_diem_nhapdiem = ttk.Entry(content_frame, width=40)
        self.entry_diem_nhapdiem.grid(row=2, column=1, padx=5, pady=8)

        btn_nhap_diem = ttk.Button(content_frame, text="Nhập Điểm", command=self.nhap_diem_submit)
        btn_nhap_diem.grid(row=3, column=0, columnspan=2, pady=20)
        
    def nhap_diem_submit(self):
        ma_sv = self.entry_ma_sv_nhapdiem.get().strip()
        selected_mon_hoc_display = self.combo_mon_hoc_nhapdiem.get() # Đây là "Tên MH (Mã MH)"
        diem_str = self.entry_diem_nhapdiem.get().strip()

        if not ma_sv or not selected_mon_hoc_display or not diem_str:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ Mã số SV, Môn học và Điểm.")
            self.update_status("Nhập điểm thất bại: Thiếu thông tin")
            return
        
        ma_mon_hoc = self.mon_hoc_display_to_code_map.get(selected_mon_hoc_display)
        if not ma_mon_hoc:
            messagebox.showerror("Lỗi", "Môn học được chọn không hợp lệ. Vui lòng chọn lại từ danh sách.")
            self.update_status("Nhập điểm thất bại: Môn học không hợp lệ.")
            return

        try:
            diem = float(diem_str)
            if not (0 <= diem <= 10):
                messagebox.showwarning("Cảnh báo", "Điểm phải nằm trong khoảng từ 0 đến 10.")
                self.update_status("Nhập điểm thất bại: Điểm ngoài khoảng 0-10")
                return

            result = self.ql_diem.nhap_diem(ma_sv, ma_mon_hoc, diem) # Truyền ma_mon_hoc
            
            if result is True: 
                sv_info = self.ql_diem.xem_diem(ma_sv) # xem_diem đã trả về tên môn
                ten_sv = sv_info.get('ho_ten', ma_sv) if sv_info else ma_sv
                ten_mon_hien_thi = selected_mon_hoc_display.split(' (')[0] 
                messagebox.showinfo("Thành công", f"Đã nhập điểm môn {ten_mon_hien_thi} ({diem}) cho SV {ten_sv}.")
                self.update_status(f"Đã nhập điểm môn {ten_mon_hien_thi} ({diem}) cho SV {ma_sv}")
                self.entry_ma_sv_nhapdiem.delete(0, tk.END)
                self.combo_mon_hoc_nhapdiem.set("") 
                self.entry_diem_nhapdiem.delete(0, tk.END)
                self._populate_xh_filters()
            elif isinstance(result, str): 
                messagebox.showerror("Lỗi", result)
                self.update_status(f"Nhập điểm thất bại: {result}")
            else: 
                messagebox.showerror("Lỗi", "Có lỗi xảy ra khi nhập điểm.")
                self.update_status(f"Nhập điểm thất bại không rõ nguyên nhân cho SV {ma_sv}.")
        except ValueError:
            messagebox.showwarning("Cảnh báo", "Điểm nhập vào không phải là số hợp lệ.")
            self.update_status("Nhập điểm thất bại: Điểm không phải là số")

    def setup_xem_xoa_diem_tab(self): # Đổi tên phương thức
        frame_input_xem = ttk.Frame(self.tab_xem_diem)
        frame_input_xem.pack(fill=tk.X, padx=5, pady=(5,10)) # Tăng pady dưới

        ttk.Label(frame_input_xem, text="Mã số sinh viên:").pack(side=tk.LEFT, padx=(0,5))
        self.entry_ma_sv_xem = ttk.Entry(frame_input_xem, width=30)
        self.entry_ma_sv_xem.pack(side=tk.LEFT, padx=5)

        btn_xem = ttk.Button(frame_input_xem, text="Xem Điểm", command=self.xem_diem)
        btn_xem.pack(side=tk.LEFT, padx=5)

        self.info_label = ttk.Label(self.tab_xem_diem, text="", justify=tk.LEFT, font=('Segoe UI', 10, "italic"), wraplength=700)
        self.info_label.pack(fill=tk.X, padx=5, pady=(0,10))

        frame_tree_xem = ttk.Frame(self.tab_xem_diem)
        frame_tree_xem.pack(fill="both", expand=True, padx=5, pady=5)

        self.tree_xem_diem = ttk.Treeview(frame_tree_xem, columns=('Môn học', 'Điểm'), show='headings')
        self.tree_xem_diem.heading('Môn học', text='Môn học')
        self.tree_xem_diem.heading('Điểm', text='Điểm')
        self.tree_xem_diem.column("Môn học", width=300, stretch=tk.YES)
        self.tree_xem_diem.column("Điểm", width=100, anchor=tk.CENTER, stretch=tk.NO)

        scrollbar_xem_diem = ttk.Scrollbar(frame_tree_xem, orient=tk.VERTICAL, command=self.tree_xem_diem.yview)
        self.tree_xem_diem.configure(yscrollcommand=scrollbar_xem_diem.set)

        self.tree_xem_diem.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar_xem_diem.pack(side=tk.RIGHT, fill=tk.Y)
        
        btn_xoa_diem_chon = ttk.Button(self.tab_xem_diem, text="Xóa Điểm Đã Chọn", command=self.xoa_diem_da_chon, style="Accent.TButton")
        btn_xoa_diem_chon.pack(pady=15)
        
    def xem_diem(self):
        ma_sv = self.entry_ma_sv_xem.get().strip()

        for item in self.tree_xem_diem.get_children():
            self.tree_xem_diem.delete(item)
        self.info_label.config(text="") 

        if not ma_sv:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập Mã số sinh viên cần xem.")
            self.update_status("Xem điểm thất bại: Thiếu Mã SV")
            return

        sv_data = self.ql_diem.xem_diem(ma_sv) # sv_data['diem'] giờ là {ten_mh: diem}
        if sv_data:
            info_text = (f"Mã số: {ma_sv}   |   Họ tên: {sv_data.get('ho_ten', 'N/A')}\n"
                         f"Lớp: {sv_data.get('lop_hoc', 'N/A')}\n"
                         f"Trường: {sv_data.get('truong', 'N/A')}   |   Khoa: {sv_data.get('khoa', 'N/A')}\n"
                         f"Cập nhật lần cuối: {str(sv_data.get('ngay_cap_nhat', 'N/A'))}")
            self.info_label.config(text=info_text)
            
            # Lưu lại mapping tên môn hiển thị -> mã môn gốc cho việc xóa/sửa
            self.current_sv_diem_map_ten_to_ma = {}
            original_sv_obj_for_map = self.ql_diem.danh_sach_sinh_vien.get(ma_sv) # Lấy đối tượng SinhVien gốc
            if original_sv_obj_for_map and original_sv_obj_for_map.diem:
                for ma_mh_goc, diem_goc in original_sv_obj_for_map.diem.items():
                    mon_hoc_obj_goc = self.ql_diem.lay_thong_tin_mon_hoc(ma_mh_goc) # Lấy đối tượng MonHoc
                    ten_mh_goc_display = mon_hoc_obj_goc.ten_mh if mon_hoc_obj_goc else ma_mh_goc
                    self.current_sv_diem_map_ten_to_ma[ten_mh_goc_display] = ma_mh_goc


            diem_sv_display = sv_data.get('diem') # Đây là {ten_mh: diem}
            if isinstance(diem_sv_display, dict) and diem_sv_display:
                for mon, diem_val in diem_sv_display.items():
                    self.tree_xem_diem.insert('', tk.END, values=(mon, diem_val))
            else:
                self.tree_xem_diem.insert('', tk.END, values=('Chưa có điểm', ''))
            self.update_status(f"Đã hiển thị điểm của SV {ma_sv}")
        else:
            messagebox.showerror("Lỗi", f"Không tìm thấy sinh viên với mã số '{ma_sv}'.")
            self.update_status(f"Xem điểm thất bại: Không tìm thấy SV '{ma_sv}'")
            self.info_label.config(text=f"Không tìm thấy sinh viên với mã số '{ma_sv}'.")

    def xoa_diem_da_chon(self):
        selected_item = self.tree_xem_diem.focus() 
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một môn học trong bảng để xóa.")
            self.update_status("Xóa điểm thất bại: Chưa chọn môn học")
            return

        ma_sv = self.entry_ma_sv_xem.get().strip()
        if not ma_sv:
            messagebox.showwarning("Cảnh báo", "Mã số sinh viên đang trống. Vui lòng nhập và xem điểm trước.")
            self.update_status("Xóa điểm thất bại: Thiếu Mã SV")
            return
        
        try:
            ten_mon_hoc_display_can_xoa = self.tree_xem_diem.item(selected_item)['values'][0]
            if ten_mon_hoc_display_can_xoa == 'Chưa có điểm': 
                messagebox.showinfo("Thông tin", "Sinh viên này chưa có điểm nào để xóa.")
                self.update_status("Không có điểm để xóa.")
                return
            
            # Lấy mã môn học từ tên hiển thị
            if not hasattr(self, 'current_sv_diem_map_ten_to_ma'):
                messagebox.showerror("Lỗi", "Không tìm thấy thông tin ánh xạ môn học. Vui lòng Xem Điểm lại.")
                self.update_status("Lỗi xóa điểm: Thiếu ánh xạ môn học.")
                return
            
            ma_mon_hoc_thuc_te_can_xoa = self.current_sv_diem_map_ten_to_ma.get(ten_mon_hoc_display_can_xoa)
            if not ma_mon_hoc_thuc_te_can_xoa:
                messagebox.showerror("Lỗi", f"Không tìm thấy mã môn học tương ứng với '{ten_mon_hoc_display_can_xoa}'.")
                self.update_status("Lỗi xóa điểm: Không tìm thấy mã môn học.")
                return

        except (IndexError, TypeError):
            messagebox.showerror("Lỗi", "Không thể lấy thông tin môn học từ bảng.")
            self.update_status("Lỗi khi lấy thông tin môn học để xóa.")
            return

        confirm = messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc chắn muốn xóa điểm môn '{ten_mon_hoc_display_can_xoa}' của sinh viên '{ma_sv}' không?")
        if confirm:
            if self.ql_diem.xoa_diem(ma_sv, ma_mon_hoc_thuc_te_can_xoa): # Truyền mã môn
                messagebox.showinfo("Thành công", f"Đã xóa điểm môn {ten_mon_hoc_display_can_xoa} của SV {ma_sv}.")
                self.update_status(f"Đã xóa điểm môn {ten_mon_hoc_display_can_xoa} của SV {ma_sv}")
                self.xem_diem() 
                self._populate_all_combobox_filters()
            else:
                messagebox.showerror("Lỗi", f"Không thể xóa điểm môn {ten_mon_hoc_display_can_xoa}. Sinh viên hoặc môn học có thể không tồn tại trong dữ liệu.")
                self.update_status(f"Xóa điểm môn {ten_mon_hoc_display_can_xoa} thất bại")
        else:
            self.update_status("Hủy thao tác xóa điểm.")
            
    def setup_sua_diem_tab(self):
        content_frame = ttk.Frame(self.tab_sua_diem)
        content_frame.pack(expand=True)

        ttk.Label(content_frame, text="Mã số sinh viên:").grid(row=0, column=0, padx=5, pady=8, sticky=tk.W)
        self.entry_ma_sv_sua = ttk.Entry(content_frame, width=40)
        self.entry_ma_sv_sua.grid(row=0, column=1, padx=5, pady=8)

        ttk.Label(content_frame, text="Chọn Môn học cần sửa:").grid(row=1, column=0, padx=5, pady=8, sticky=tk.W)
        self.combo_mon_hoc_sua = ttk.Combobox(content_frame, width=38, state="readonly") # Thay Entry bằng Combobox
        self.combo_mon_hoc_sua.grid(row=1, column=1, padx=5, pady=8)
        
        ttk.Label(content_frame, text="Điểm mới (0-10):").grid(row=2, column=0, padx=5, pady=8, sticky=tk.W)
        self.entry_diem_moi_sua = ttk.Entry(content_frame, width=40)
        self.entry_diem_moi_sua.grid(row=2, column=1, padx=5, pady=8)

        btn_sua_diem_submit = ttk.Button(content_frame, text="Cập Nhật Điểm", command=self.sua_diem_submit)
        btn_sua_diem_submit.grid(row=3, column=0, columnspan=2, pady=20)
        
    def sua_diem_submit(self):
        ma_sv = self.entry_ma_sv_sua.get().strip()
        selected_mon_hoc_display_sua = self.combo_mon_hoc_sua.get() # "Tên MH (Mã MH)"
        diem_moi_str = self.entry_diem_moi_sua.get().strip()

        if not ma_sv or not selected_mon_hoc_display_sua or not diem_moi_str:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ Mã SV, Môn học và Điểm mới.")
            self.update_status("Sửa điểm thất bại: Thiếu thông tin.")
            return

        ma_mon_hoc_sua = self.mon_hoc_display_to_code_map.get(selected_mon_hoc_display_sua)
        if not ma_mon_hoc_sua:
            messagebox.showerror("Lỗi", "Môn học được chọn để sửa không hợp lệ.")
            self.update_status("Sửa điểm thất bại: Môn học không hợp lệ.")
            return

        try:
            diem_moi = float(diem_moi_str)
            if not (0 <= diem_moi <= 10):
                messagebox.showwarning("Cảnh báo", "Điểm mới phải nằm trong khoảng từ 0 đến 10.")
                self.update_status("Sửa điểm thất bại: Điểm mới ngoài khoảng 0-10.")
                return
            
            if self.ql_diem.sua_diem(ma_sv, ma_mon_hoc_sua, diem_moi): # Truyền mã môn
                ten_mon_hien_thi_sua = selected_mon_hoc_display_sua.split(' (')[0]
                messagebox.showinfo("Thành công", f"Đã cập nhật điểm môn {ten_mon_hien_thi_sua} cho SV {ma_sv} thành {diem_moi}.")
                self.update_status(f"Đã cập nhật điểm môn {ten_mon_hien_thi_sua} cho SV {ma_sv}.")
                self.entry_ma_sv_sua.delete(0, tk.END)
                self.combo_mon_hoc_sua.set("")
                self.entry_diem_moi_sua.delete(0, tk.END)
                self._populate_xh_filters() # GPA có thể thay đổi
            else:
                messagebox.showerror("Lỗi", f"Không thể sửa điểm. Sinh viên '{ma_sv}' hoặc môn học '{selected_mon_hoc_display_sua}' có thể không tồn tại, hoặc điểm cũ không có.")
                self.update_status(f"Sửa điểm thất bại cho SV {ma_sv}, môn {selected_mon_hoc_display_sua}.")
        except ValueError:
            messagebox.showwarning("Cảnh báo", "Điểm mới nhập vào không phải là số hợp lệ.")
            self.update_status("Sửa điểm thất bại: Điểm mới không phải là số.")

    def setup_tim_kiem_tab(self):
        frame_options = ttk.LabelFrame(self.tab_tim_kiem, text="Tiêu chí tìm kiếm") # style sẽ áp dụng padding
        frame_options.pack(fill=tk.X, padx=5, pady=10)

        # Sắp xếp các bộ lọc trong grid cho đẹp hơn
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
        
        # Cho phép frame_options co giãn cột chứa combobox
        frame_options.grid_columnconfigure(1, weight=1)
        frame_options.grid_columnconfigure(3, weight=1)


        btn_tim = ttk.Button(frame_options, text="Tìm kiếm", command=self.thuc_hien_tim_kiem, style="Accent.TButton")
        btn_tim.grid(row=3, column=0, columnspan=4, pady=15)

        frame_results = ttk.LabelFrame(self.tab_tim_kiem, text="Kết quả tìm kiếm")
        frame_results.pack(fill="both", expand=True, padx=5, pady=5)

        cols = ('Mã SV', 'Họ Tên', 'Lớp', 'Trường', 'Khoa', 'Môn học', 'Điểm')
        self.tree_tim_kiem = ttk.Treeview(frame_results, columns=cols, show='headings')
        for col in cols:
            self.tree_tim_kiem.heading(col, text=col)
        
        # Điều chỉnh độ rộng cột (tùy ý)
        self.tree_tim_kiem.column("Mã SV", width=80, anchor=tk.W)
        self.tree_tim_kiem.column("Họ Tên", width=150, anchor=tk.W)
        self.tree_tim_kiem.column("Lớp", width=80, anchor=tk.W)
        self.tree_tim_kiem.column("Trường", width=100, anchor=tk.W)
        self.tree_tim_kiem.column("Khoa", width=100, anchor=tk.W)
        self.tree_tim_kiem.column("Môn học", width=120, anchor=tk.W)
        self.tree_tim_kiem.column("Điểm", width=60, anchor=tk.CENTER)
        
        scrollbar_tim_kiem = ttk.Scrollbar(frame_results, orient=tk.VERTICAL, command=self.tree_tim_kiem.yview)
        self.tree_tim_kiem.configure(yscrollcommand=scrollbar_tim_kiem.set)
        
        self.tree_tim_kiem.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar_tim_kiem.pack(side=tk.RIGHT, fill=tk.Y)
        
    def _populate_mon_hoc_comboboxes(self):
        """Điền dữ liệu vào các combobox chọn môn học (hiển thị Tên MH (Mã MH), giá trị là Mã MH)."""
        mon_hoc_list = self.ql_diem.lay_tat_ca_mon_hoc() 
        
        self.mon_hoc_display_to_code_map = {f"{mh['ten_mh']} ({mh['ma_mh']})": mh['ma_mh'] for mh in mon_hoc_list}
        mon_hoc_display_values = sorted(list(self.mon_hoc_display_to_code_map.keys()))

        combos_to_update = []
        if hasattr(self, 'combo_mon_hoc_nhapdiem'): combos_to_update.append(self.combo_mon_hoc_nhapdiem)
        if hasattr(self, 'combo_mon_hoc_sua'): combos_to_update.append(self.combo_mon_hoc_sua)

        for combo in combos_to_update:
            current_selection = combo.get()
            combo['values'] = [""] + mon_hoc_display_values 
            if current_selection in combo['values']:
                combo.set(current_selection)
            else:
                combo.set("")
        
        # Cập nhật Combobox tìm kiếm môn học (hiển thị Tên Môn)
        mon_hoc_names_only = sorted(list(set(mh['ten_mh'] for mh in mon_hoc_list)))
        if hasattr(self, 'combo_search_mon_hoc'):
            current_search_mon = self.combo_search_mon_hoc.get()
            self.combo_search_mon_hoc['values'] = ["Tất cả"] + mon_hoc_names_only
            if current_search_mon in self.combo_search_mon_hoc['values']:
                 self.combo_search_mon_hoc.set(current_search_mon)
            else:
                self.combo_search_mon_hoc.set("Tất cả")

    def _populate_search_filters(self):
        all_student_objects = list(self.ql_diem.danh_sach_sinh_vien.values())

        lop_hoc_values = sorted(list(set(sv_obj.lop_hoc for sv_obj in all_student_objects if sv_obj.lop_hoc)))
        truong_values = sorted(list(set(sv_obj.truong for sv_obj in all_student_objects if sv_obj.truong)))
        khoa_values = sorted(list(set(sv_obj.khoa for sv_obj in all_student_objects if sv_obj.khoa)))

        for combo, new_values in [
            (self.combo_search_lop_hoc, lop_hoc_values),
            (self.combo_search_truong, truong_values),
            (self.combo_search_khoa, khoa_values),
        ]:
            current_selection = combo.get()
            full_values = ["Tất cả"] + new_values
            combo['values'] = full_values
            if current_selection in full_values:
                combo.set(current_selection)
            else:
                combo.set("Tất cả")
                
    def thuc_hien_tim_kiem(self):
        for item in self.tree_tim_kiem.get_children():
            self.tree_tim_kiem.delete(item)

        search_ma_sv_val = self.entry_search_ma_sv.get().strip()
        search_lop_hoc_val = self.combo_search_lop_hoc.get()
        search_truong_val = self.combo_search_truong.get()
        search_khoa_val = self.combo_search_khoa.get()
        search_ten_mon_hoc_val = self.combo_search_mon_hoc.get() # Đây là tên môn

        final_ma_sv = search_ma_sv_val if search_ma_sv_val else None
        final_lop_hoc = search_lop_hoc_val if search_lop_hoc_val != "Tất cả" else None
        final_truong = search_truong_val if search_truong_val != "Tất cả" else None
        final_khoa = search_khoa_val if search_khoa_val != "Tất cả" else None
        
        # Tìm mã môn học tương ứng với tên môn được chọn
        final_ma_mon_hoc_tim = None
        if search_ten_mon_hoc_val != "Tất cả" and search_ten_mon_hoc_val:
            found_ma_mh = False
            # Ưu tiên tìm trong self.mon_hoc_display_to_code_map nếu có (chứa "Tên (Mã)")
            # Hoặc duyệt qua self.ql_diem.danh_sach_mon_hoc
            for code, mon_hoc_obj in self.ql_diem.danh_sach_mon_hoc.items():
                if mon_hoc_obj.ten_mh.lower() == search_ten_mon_hoc_val.lower():
                    final_ma_mon_hoc_tim = code
                    found_ma_mh = True
                    break
            if not found_ma_mh:
                # Nếu không tìm thấy mã, có thể thông báo hoặc tìm kiếm sẽ bỏ qua tiêu chí môn
                # messagebox.showinfo("Thông báo", f"Không tìm thấy mã cho môn '{search_ten_mon_hoc_val}'.")
                pass # Bỏ qua tiêu chí môn nếu không tìm thấy mã
        
        if not any([final_ma_sv, final_lop_hoc, final_truong, final_khoa, final_ma_mon_hoc_tim]):
             pass


        ket_qua = self.ql_diem.tim_kiem_diem(
            ma_sv=final_ma_sv, ma_mon_hoc_tim=final_ma_mon_hoc_tim, lop_hoc=final_lop_hoc, 
            truong=final_truong, khoa=final_khoa
        )

        active_filters = []
        if final_ma_sv: active_filters.append(f"Mã SV: '{final_ma_sv}'")
        if final_lop_hoc: active_filters.append(f"Lớp: '{final_lop_hoc}'")
        if final_truong: active_filters.append(f"Trường: '{final_truong}'")
        if final_khoa: active_filters.append(f"Khoa: '{final_khoa}'")
        if final_ma_mon_hoc_tim: active_filters.append(f"Môn (tên gần đúng): '{search_ten_mon_hoc_val}'")
        keyword_display = ", ".join(active_filters) if active_filters else "tất cả dữ liệu"

        if ket_qua:
            for kq_item in ket_qua:
                self.tree_tim_kiem.insert('', tk.END, values=(
                    kq_item.get('ma_sv', 'N/A'), kq_item.get('ho_ten', 'N/A'),
                    kq_item.get('lop_hoc', 'N/A'), kq_item.get('truong', 'N/A'),
                    kq_item.get('khoa', 'N/A'), kq_item.get('mon_hoc', 'N/A'),
                    kq_item.get('diem', 'N/A')
                ))
            self.update_status(f"Tìm thấy {len(ket_qua)} kết quả cho: {keyword_display}.")
        else:
            messagebox.showinfo("Thông báo", f"Không tìm thấy kết quả nào phù hợp cho: {keyword_display}.")
            self.update_status(f"Không tìm thấy kết quả cho: {keyword_display}.")


    def setup_xep_hang_tab(self):
        filter_frame_xh = ttk.Frame(self.tab_xep_hang)
        filter_frame_xh.pack(pady=(10,5), padx=10, fill=tk.X) # Tăng pady trên

        ttk.Label(filter_frame_xh, text="Lọc theo Lớp:").grid(row=0, column=0, padx=(0,5), pady=5, sticky=tk.W)
        self.combo_lop_filter_xh = ttk.Combobox(filter_frame_xh, state="readonly", width=25)
        self.combo_lop_filter_xh.grid(row=0, column=1, padx=(0,10), pady=5, sticky=tk.EW)

        ttk.Label(filter_frame_xh, text="Lọc theo Khoa:").grid(row=0, column=2, padx=(10,5), pady=5, sticky=tk.W) # Thêm padx trái
        self.combo_khoa_filter_xh = ttk.Combobox(filter_frame_xh, state="readonly", width=25)
        self.combo_khoa_filter_xh.grid(row=0, column=3, padx=(0,5), pady=5, sticky=tk.EW)
        
        filter_frame_xh.grid_columnconfigure(1, weight=1) # Cho combobox co giãn
        filter_frame_xh.grid_columnconfigure(3, weight=1)

        btn_hien_thi_xh = ttk.Button(self.tab_xep_hang, text="Hiển thị / Lọc Bảng Xếp Hạng", command=self.hien_thi_xep_hang, style="Accent.TButton")
        btn_hien_thi_xh.pack(pady=(5,10))

        frame_xh_results = ttk.LabelFrame(self.tab_xep_hang, text="Bảng xếp hạng Sinh viên theo GPA")
        frame_xh_results.pack(fill="both", expand=True, padx=5, pady=5)

        cols_xh = ('Hạng', 'Mã SV', 'Họ Tên', 'Lớp', 'Trường', 'Khoa', 'GPA')
        self.tree_xep_hang = ttk.Treeview(frame_xh_results, columns=cols_xh, show='headings')
        for col in cols_xh:
            self.tree_xep_hang.heading(col, text=col)
        
        self.tree_xep_hang.column("Hạng", width=50, anchor=tk.CENTER)
        self.tree_xep_hang.column("Mã SV", width=100, anchor=tk.W)
        self.tree_xep_hang.column("Họ Tên", width=180, anchor=tk.W) # Điều chỉnh lại
        self.tree_xep_hang.column("Lớp", width=80, anchor=tk.W)
        self.tree_xep_hang.column("Trường", width=100, anchor=tk.W)
        self.tree_xep_hang.column("Khoa", width=100, anchor=tk.W)
        self.tree_xep_hang.column("GPA", width=70, anchor=tk.CENTER)


        scrollbar_xh = ttk.Scrollbar(frame_xh_results, orient=tk.VERTICAL, command=self.tree_xep_hang.yview)
        self.tree_xep_hang.configure(yscrollcommand=scrollbar_xh.set)

        self.tree_xep_hang.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar_xh.pack(side=tk.RIGHT, fill=tk.Y)
        
    def _populate_xh_filters(self):
        all_student_objects = list(self.ql_diem.danh_sach_sinh_vien.values())

        lop_hoc_values = sorted(list(set(sv_obj.lop_hoc for sv_obj in all_student_objects if sv_obj.lop_hoc)))
        khoa_values = sorted(list(set(sv_obj.khoa for sv_obj in all_student_objects if sv_obj.khoa)))

        for combo, new_values in [(self.combo_lop_filter_xh, lop_hoc_values), (self.combo_khoa_filter_xh, khoa_values)]:
            current_selection = combo.get()
            full_values = ["Tất cả"] + new_values
            combo['values'] = full_values
            if current_selection in full_values:
                combo.set(current_selection)
            else:
                combo.set("Tất cả")
                
    def hien_thi_xep_hang(self):
        selected_lop = self.combo_lop_filter_xh.get()
        selected_khoa = self.combo_khoa_filter_xh.get()

        for item in self.tree_xep_hang.get_children():
            self.tree_xep_hang.delete(item)

        full_xep_hang_list = self.ql_diem.xep_hang_sinh_vien()
        
        filtered_list = []
        if full_xep_hang_list:
            for sv_data in full_xep_hang_list:
                match_lop = (selected_lop == "Tất cả" or sv_data.get('lop_hoc', 'N/A') == selected_lop)
                match_khoa = (selected_khoa == "Tất cả" or sv_data.get('khoa', 'N/A') == selected_khoa)
                if match_lop and match_khoa:
                    filtered_list.append(sv_data)

        if filtered_list:
            for i, sv_data in enumerate(filtered_list, 1):
                self.tree_xep_hang.insert('', tk.END, values=(
                    i, sv_data.get('ma_sv', 'N/A'), sv_data.get('ho_ten', 'N/A'),
                    sv_data.get('lop_hoc', 'N/A'), sv_data.get('truong', 'N/A'),
                    sv_data.get('khoa', 'N/A'), f"{sv_data.get('gpa', 0.0):.2f}"
                ))
            self.update_status(f"Đã hiển thị {len(filtered_list)} sinh viên trong bảng xếp hạng.")
        else:
            messagebox.showinfo("Thông báo", "Chưa có dữ liệu điểm để xếp hạng hoặc không có sinh viên nào phù hợp với bộ lọc.")
            self.update_status("Chưa có dữ liệu để xếp hạng hoặc không khớp bộ lọc.")

    def hien_thi_danh_sach_mon_hoc(self):
        """Hiển thị danh sách các môn học trong tab Quản lý Môn học."""
        for item in self.tree_ql_mon_hoc.get_children():
            self.tree_ql_mon_hoc.delete(item)
        
        danh_sach = self.ql_diem.lay_tat_ca_mon_hoc()
        if danh_sach:
            for mh in danh_sach:
                self.tree_ql_mon_hoc.insert('', tk.END, values=(mh["ma_mh"], mh["ten_mh"], mh["so_tin_chi"]))
        self.update_status(f"Hiển thị {len(danh_sach)} môn học.")

    def _handle_them_mon_hoc(self):
        """Xử lý sự kiện khi nhấn nút Thêm Môn học."""
        ma_mh = self.entry_ma_mh_ql.get().strip()
        ten_mh = self.entry_ten_mh_ql.get().strip()
        so_tin_chi_str = self.entry_so_tin_chi_ql.get().strip()

        if not ma_mh or not ten_mh or not so_tin_chi_str:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ Mã MH, Tên MH và Số tín chỉ.")
            self.update_status("Thêm môn học thất bại: Thiếu thông tin.")
            return
        try:
            so_tin_chi = int(so_tin_chi_str)
            # Kiểm tra số tín chỉ đã được thực hiện trong lớp MonHoc và QuanLyDiem.them_mon_hoc
        except ValueError:
            messagebox.showwarning("Cảnh báo", "Số tín chỉ không phải là số hợp lệ.")
            self.update_status("Thêm môn học thất bại: Số tín chỉ không phải số.")
            return

        ket_qua = self.ql_diem.them_mon_hoc(ma_mh, ten_mh, so_tin_chi)

        if "thành công" in ket_qua: # Dựa vào thông báo trả về từ backend
            messagebox.showinfo("Thành công", ket_qua)
            self.update_status(ket_qua)
            self.entry_ma_mh_ql.delete(0, tk.END)
            self.entry_ten_mh_ql.delete(0, tk.END)
            self.entry_so_tin_chi_ql.delete(0, tk.END)
            self.hien_thi_danh_sach_mon_hoc() # Cập nhật lại bảng danh sách môn học
            self._populate_all_combobox_filters() # Cập nhật các combobox môn học ở các tab khác
        else:
            messagebox.showerror("Lỗi", ket_qua) # Hiển thị lỗi từ backend
            self.update_status(f"Thêm môn học thất bại: {ket_qua}")

    def setup_bao_cao_tab(self):
        frame_input = ttk.Frame(self.tab_bao_cao)
        frame_input.pack(pady=10, padx=10, fill=tk.X)

        ttk.Label(frame_input, text="Nhập tên lớp:").pack(side=tk.LEFT, padx=(0,5))
        self.entry_lop_hoc_bao_cao = ttk.Entry(frame_input, width=30)
        self.entry_lop_hoc_bao_cao.pack(side=tk.LEFT, padx=5)
        btn_xuat_bao_cao = ttk.Button(frame_input, text="Hiển thị Báo cáo", command=self.hien_thi_bao_cao, style="Accent.TButton")
        btn_xuat_bao_cao.pack(side=tk.LEFT, padx=5)

        frame_output = ttk.LabelFrame(self.tab_bao_cao, text="Kết quả Báo cáo")
        frame_output.pack(pady=10, padx=10, fill="both", expand=True)

        self.text_bao_cao = tk.Text(frame_output, wrap=tk.WORD, height=15, font=("Consolas", 10), relief=tk.FLAT, borderwidth=1)
        self.text_bao_cao.grid(row=0, column=0, sticky="nsew")
        self.text_bao_cao.config(state=tk.DISABLED) # , background="#f0f0f0" (nếu muốn màu nền khác khi disabled)

        scrollbar_bao_cao = ttk.Scrollbar(frame_output, orient=tk.VERTICAL, command=self.text_bao_cao.yview)
        scrollbar_bao_cao.grid(row=0, column=1, sticky="ns")
        self.text_bao_cao.configure(yscrollcommand=scrollbar_bao_cao.set)

        frame_output.grid_rowconfigure(0, weight=1)
        frame_output.grid_columnconfigure(0, weight=1)

        btn_luu_bao_cao = ttk.Button(frame_input, text="Lưu Báo cáo ra File", command=self._handle_luu_bao_cao)
        btn_luu_bao_cao.pack(side=tk.LEFT, padx=10)
        
    def hien_thi_bao_cao(self):
        lop_hoc = self.entry_lop_hoc_bao_cao.get().strip()

        if not lop_hoc:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên lớp học.")
            self.update_status("Xuất báo cáo thất bại: Thiếu tên lớp")
            return

        self.text_bao_cao.config(state=tk.NORMAL)
        self.text_bao_cao.delete('1.0', tk.END)

        # Sử dụng lower() để so sánh không phân biệt hoa thường
        lop_ton_tai_trong_he_thong = any(sv_obj.lop_hoc.lower() == lop_hoc.lower() 
                                         for sv_obj in self.ql_diem.danh_sach_sinh_vien.values())

        if not lop_ton_tai_trong_he_thong:
            messagebox.showinfo("Thông báo", f"Không tìm thấy lớp '{lop_hoc}' trong hệ thống.")
            self.text_bao_cao.insert(tk.END, f"Không tìm thấy lớp '{lop_hoc}' trong hệ thống.")
            self.update_status(f"Không tìm thấy lớp '{lop_hoc}' để xuất báo cáo.")
        else:
            bao_cao_data = self.ql_diem.xuat_bao_cao_lop(lop_hoc)
            
            if not bao_cao_data or bao_cao_data.get("so_sinh_vien", 0) == 0 :
                messagebox.showinfo("Thông báo", f"Lớp '{bao_cao_data.get('lop_hoc', lop_hoc)}' không có sinh viên nào được ghi nhận.")
                self.text_bao_cao.insert(tk.END, f"Lớp '{bao_cao_data.get('lop_hoc', lop_hoc)}' không có sinh viên nào.")
                self.update_status(f"Lớp '{bao_cao_data.get('lop_hoc', lop_hoc)}' không có sinh viên để xuất báo cáo.")
            elif not bao_cao_data.get("danh_sach_sinh_vien") and bao_cao_data.get("so_sinh_vien", 0) > 0:
                report_str = f"BÁO CÁO LỚP: {bao_cao_data.get('lop_hoc', 'N/A')}\n"
                report_str += "=" * 50 + "\n"
                report_str += f"Tổng số sinh viên của lớp (trong hệ thống): {bao_cao_data.get('so_sinh_vien',0)}\n"
                report_str += "Không có sinh viên nào trong lớp này có điểm để thống kê chi tiết.\n"
                self.text_bao_cao.insert(tk.END, report_str)
                messagebox.showinfo("Thông báo", f"Lớp '{bao_cao_data.get('lop_hoc', 'N/A')}' có sinh viên nhưng không ai có điểm.")
                self.update_status(f"Lớp '{bao_cao_data.get('lop_hoc', 'N/A')}' không có sinh viên nào có điểm.")
            elif bao_cao_data.get("danh_sach_sinh_vien"):
                report_str =  f"{'BÁO CÁO KẾT QUẢ HỌC TẬP LỚP'.center(60)}\n"
                report_str += f"{('Lớp: ' + bao_cao_data.get('lop_hoc', 'N/A')).center(60)}\n"
                report_str += "=" * 60 + "\n"
                report_str += f"Tổng số sinh viên của lớp (trong hệ thống): {bao_cao_data.get('so_sinh_vien',0)}\n"
                report_str += f"Số sinh viên có điểm trong báo cáo: {len(bao_cao_data.get('danh_sach_sinh_vien',[]))}\n"
                report_str += f"Điểm GPA trung bình của lớp (tính trên SV có điểm): {bao_cao_data.get('diem_trung_binh_lop', 0.0):.2f}\n\n"
                report_str += "CHI TIẾT ĐIỂM SINH VIÊN (CÓ ĐIỂM):\n"
                report_str += "-" * 60 + "\n"

                for sv in bao_cao_data['danh_sach_sinh_vien']:
                    report_str += (f"\nMã SV: {sv.get('ma_sv', 'N/A'):<15} Họ tên: {sv.get('ho_ten', 'N/A')}\n"
                                   f"Trường: {sv.get('truong', 'N/A'):<15} Khoa: {sv.get('khoa', 'N/A')}\n"
                                   f"GPA cá nhân: {sv.get('diem_trung_binh', 0.0):.2f}\n"
                                   f"  Bảng điểm chi tiết:\n")
                    bang_diem = sv.get('bang_diem', {})
                    if bang_diem:
                        for mon, diem_val in bang_diem.items():
                            report_str += f"    - {mon:<30}: {diem_val:>4.1f}\n"
                    else:
                        report_str += "    (Chưa có điểm môn nào)\n"
                    report_str += "-" * 30 + "\n"
                self.update_status(f"Đã xuất báo cáo cho lớp {bao_cao_data.get('lop_hoc', 'N/A')}")
                self.text_bao_cao.insert(tk.END, report_str)
            else: 
                messagebox.showerror("Lỗi", f"Không thể tạo báo cáo cho lớp '{lop_hoc}' do dữ liệu không nhất quán.")
                self.text_bao_cao.insert(tk.END, f"Không thể tạo báo cáo cho lớp '{lop_hoc}'.")
                self.update_status(f"Lỗi khi tạo báo cáo cho lớp '{lop_hoc}'.")
        self.text_bao_cao.config(state=tk.DISABLED)

    def _handle_luu_bao_cao(self):
        content = self.text_bao_cao.get("1.0", tk.END).strip()
        if not content or "Không tìm thấy lớp" in content or "không có sinh viên nào" in content or "Không thể tạo báo cáo" in content :
            messagebox.showwarning("Cảnh báo", "Không có nội dung báo cáo hợp lệ để lưu.")
            self.update_status("Lưu báo cáo thất bại: Không có nội dung.")
            return

        lop_hoc_bc = self.entry_lop_hoc_bao_cao.get().strip()
        default_filename = f"BaoCao_Lop_{lop_hoc_bc.replace(' ', '_')}.txt" if lop_hoc_bc else "BaoCaoLop.txt"

        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=default_filename,
            title="Lưu Báo cáo Lớp"
        )
        if not filepath:
            self.update_status("Hủy thao tác lưu báo cáo.")
            return
        try:
            with open(filepath, 'w', encoding='utf-8') as f: f.write(content)
            messagebox.showinfo("Thành công", f"Báo cáo đã được lưu vào:\n{filepath}")
            self.update_status(f"Báo cáo đã được lưu vào {filepath}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")
            self.update_status(f"Lỗi khi lưu báo cáo: {e}")

    def update_status(self, message):
        self.status_label.config(text=message)

if __name__ == "__main__":
    # Sử dụng ThemedTk để có giao diện hiện đại hơn
    # Có thể thử các theme khác: "arc", "breeze", "plastik", "equilux", "itft1", "keramik", etc.
    root = ThemedTk(theme="arc") 
    root.title("Hệ thống Quản lý Điểm Sinh viên")
    root.geometry("850x700") # Kích thước cửa sổ lớn hơn chút
    
    # Tùy chọn: Set icon cho cửa sổ (cần file .ico hoặc .png tùy hệ điều hành)
    # try:
    #     root.iconbitmap('path_to_your_icon.ico') # Cho Windows
    # except tk.TclError:
    #     try:
    #         img = tk.PhotoImage(file='path_to_your_icon.png') # Cho một số hệ thống Linux/macOS
    #         root.tk.call('wm', 'iconphoto', root._w, img)
    #     except tk.TclError:
    #         print("Không thể đặt icon cho cửa sổ.")
            
    app = QuanLyDiemGUI(root)
    root.mainloop()