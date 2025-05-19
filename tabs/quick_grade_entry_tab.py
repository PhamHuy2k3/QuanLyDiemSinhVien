import tkinter as tk
from tkinter import ttk, messagebox
from constants import SUB_TAB_QUICK_ENTER_GRADES # Sử dụng relative import

class QuickGradeEntryTab:
    def __init__(self, parent_frame, app_controller):
        self.parent_frame = parent_frame
        self.app_controller = app_controller # Để truy cập ql_diem, update_status, master, etc.
        self.is_cursor_on_grade_column = False
        self.qen_entry_widgets = {} 
        self.qen_active_entry_item_id = None

        self.setup_ui()
        self.populate_filters(initial_call=True)
        self.app_controller.update_status(f"Đã mở tab: {SUB_TAB_QUICK_ENTER_GRADES}")

    def setup_ui(self):
        container_frame = ttk.Frame(self.parent_frame, padding="10")
        container_frame.pack(fill=tk.BOTH, expand=True)

        # --- Khu vực Filter ---
        filter_qen_frame = ttk.LabelFrame(container_frame, text="Chọn Lớp, Học Kỳ và Môn Học", padding="10")
        filter_qen_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(filter_qen_frame, text="Chọn Lớp:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.combo_qen_lop = ttk.Combobox(filter_qen_frame, width=25, state="readonly")
        self.combo_qen_lop.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.combo_qen_lop.bind("<<ComboboxSelected>>", self._on_qen_filter_change)

        ttk.Label(filter_qen_frame, text="Chọn Học Kỳ Nhập Điểm:").grid(row=0, column=2, padx=(10,5), pady=5, sticky="w")
        self.combo_qen_hoc_ky = ttk.Combobox(filter_qen_frame, width=25, state="readonly")
        self.combo_qen_hoc_ky.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        self.combo_qen_hoc_ky.bind("<<ComboboxSelected>>", self._on_qen_filter_change)

        ttk.Label(filter_qen_frame, text="Chọn Môn Học:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.combo_qen_mon_hoc = ttk.Combobox(filter_qen_frame, width=60, state="readonly")
        self.combo_qen_mon_hoc.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        self.combo_qen_mon_hoc.bind("<<ComboboxSelected>>", self._on_qen_filter_change)
       
        filter_qen_frame.columnconfigure(1, weight=1)
        filter_qen_frame.columnconfigure(3, weight=1)

        # Frame cho các nút hành động (Lưu, Làm mới)
        action_buttons_on_filter_frame = ttk.Frame(filter_qen_frame)
        action_buttons_on_filter_frame.grid(row=0, column=5, rowspan=2, padx=(15,5), pady=0, sticky="e")

        btn_qen_save_all = ttk.Button(action_buttons_on_filter_frame, text="Lưu Tất Cả", command=self._save_all_quick_entered_grades, style="Accent.TButton")
        btn_qen_save_all.pack(pady=(0,2), fill=tk.X, ipady=4, ipadx=4)

        btn_qen_clear_form = ttk.Button(action_buttons_on_filter_frame, text="Làm Mới", command=self._clear_quick_enter_form)
        btn_qen_clear_form.pack(pady=(2,0), fill=tk.X, ipady=4, ipadx=4)

        btn_qen_load_sv = ttk.Button(filter_qen_frame, text="Tải DS Sinh Viên", command=self._load_sv_for_quick_enter, style="Accent.TButton")
        btn_qen_load_sv.grid(row=0, column=4, rowspan=2, padx=(10,5), pady=5, sticky="e")

        # --- Khu vực Treeview để nhập điểm ---
        tree_qen_frame = ttk.LabelFrame(container_frame, text="Danh sách Sinh viên và Nhập Điểm", padding="10")
        # Giảm mức độ ưu tiên chiếm không gian của tree_qen_frame để action_qen_frame có chỗ hiển thị
        tree_qen_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5)) # Giảm pady một chút
        instruction_label = ttk.Label(tree_qen_frame, text="Mẹo: Nháy đúp chuột vào ô 'Điểm Nhập' để bắt đầu chỉnh sửa.",
                                      font=('Segoe UI', 9, 'italic'))
        instruction_label.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        cols_qen = ('ma_sv', 'ho_ten', 'diem_so_nhap')
        # Thêm style="Grid.Treeview" để có đường kẻ
        self.tree_qen_diem = ttk.Treeview(tree_qen_frame, columns=cols_qen, show='headings', selectmode="none", style="Grid.Treeview")
        
        # Cấu hình màu nền cho các tag hàng chẵn/lẻ
        self.tree_qen_diem.tag_configure('oddrow', background='#FFFFFF') # Màu trắng cho hàng lẻ
        self.tree_qen_diem.tag_configure('evenrow', background='#F0F0F0') # Màu xám nhạt cho hàng chẵn

       
        self.tree_qen_diem.heading('ma_sv', text='Mã SV')
        self.tree_qen_diem.column('ma_sv', width=100, anchor='w', stretch=tk.NO)
        self.tree_qen_diem.heading('ho_ten', text='Họ Tên')
        self.tree_qen_diem.column('ho_ten', width=200, anchor='w', stretch=tk.YES)
        self.tree_qen_diem.heading('diem_so_nhap', text='Điểm Nhập (0-10)')
        self.tree_qen_diem.column('diem_so_nhap', width=120, anchor='center')

        vsb_qen = ttk.Scrollbar(tree_qen_frame, orient="vertical", command=self.tree_qen_diem.yview)
        hsb_qen = ttk.Scrollbar(tree_qen_frame, orient="horizontal", command=self.tree_qen_diem.xview)
        self.tree_qen_diem.configure(yscrollcommand=vsb_qen.set, xscrollcommand=hsb_qen.set)

        self.tree_qen_diem.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb_qen.pack(side=tk.RIGHT, fill=tk.Y)
        hsb_qen.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree_qen_diem.bind("<Double-1>", self._qen_on_double_click_to_edit)
        self.tree_qen_diem.bind("<Motion>", self._on_tree_motion)
        self.tree_qen_diem.bind("<Leave>", self._on_tree_leave)
        # Bỏ action_qen_frame ở dưới cùng vì đã di chuyển nút lên filter_qen_frame
        # action_qen_frame = ttk.Frame(container_frame)
        # action_qen_frame.pack(pady=(5, 10), fill=tk.X, side=tk.BOTTOM)

    def populate_filters(self, initial_call=False):
        self._populate_qen_lop_combobox(initial_call=initial_call)
        self.app_controller._populate_hoc_ky_comboboxes((self.combo_qen_hoc_ky, "Chọn học kỳ"))
        self._populate_qen_mon_hoc_combobox(initial_call=initial_call)

    def _populate_qen_lop_combobox(self, initial_call=False):
        all_sv_objs = list(self.app_controller.ql_diem.danh_sach_sinh_vien.values())
        lop_values = sorted(list(set(sv.lop_hoc for sv in all_sv_objs if sv.lop_hoc)))
        current_lop = self.combo_qen_lop.get()
        self.combo_qen_lop['values'] = ["Chọn Lớp"] + lop_values
        if current_lop in self.combo_qen_lop['values'] and not initial_call:
            self.combo_qen_lop.set(current_lop)
        else:
            self.combo_qen_lop.set("Chọn Lớp")

    def _populate_qen_mon_hoc_combobox(self, initial_call=False):
        if not self.app_controller.mon_hoc_display_to_code_map:
            self.app_controller._populate_mon_hoc_comboboxes()
            
        mon_hoc_display_values = sorted(list(self.app_controller.mon_hoc_display_to_code_map.keys()))
        current_mh = self.combo_qen_mon_hoc.get()
        self.combo_qen_mon_hoc['values'] = ["Chọn Môn Học"] + mon_hoc_display_values
        if current_mh in self.combo_qen_mon_hoc['values'] and not initial_call:
            self.combo_qen_mon_hoc.set(current_mh)
        else:
            self.combo_qen_mon_hoc.set("Chọn Môn Học")

    def _clear_quick_enter_form(self):
        self.combo_qen_lop.set("Chọn Lớp")
        self.combo_qen_hoc_ky.set("Chọn học kỳ")
        self.combo_qen_mon_hoc.set("Chọn Môn Học")
        
        for item in self.tree_qen_diem.get_children():
            self.tree_qen_diem.delete(item)
        
        self._qen_destroy_active_entry()
        self.qen_entry_widgets.clear()
        self.qen_active_entry_item_id = None
        self.app_controller.update_status("Form Nhập Điểm Nhanh đã làm mới.")

    def _qen_on_double_click_to_edit(self, event):
        tree = event.widget
        region = tree.identify_region(event.x, event.y)
        if region != "cell": return

        column_id_str = tree.identify_column(event.x)
        column_name_clicked = tree.column(column_id_str, "id")
        
        if column_name_clicked != 'diem_so_nhap': return

        selected_item_id = tree.focus()
        if not selected_item_id: return

        if self.qen_active_entry_item_id == selected_item_id and \
           selected_item_id in self.qen_entry_widgets and \
           self.qen_entry_widgets[selected_item_id].winfo_exists():
            self.qen_entry_widgets[selected_item_id].focus_set()
            return

        self._qen_destroy_active_entry()

        x, y, width, height = tree.bbox(selected_item_id, column_id_str)
        current_values = tree.item(selected_item_id, "values")
        current_grade_in_tree = current_values[2] if len(current_values) > 2 else ""

        entry_var = tk.StringVar(value=str(current_grade_in_tree))
        entry = ttk.Entry(tree, textvariable=entry_var, width=width // 7 if width > 0 else 10)
        entry.place(x=x, y=y, width=width, height=height, anchor='nw')
        entry.focus_set()
        entry.select_range(0, tk.END)

        self.qen_entry_widgets[selected_item_id] = entry
        self.qen_active_entry_item_id = selected_item_id

        def _on_commit(commit_event_type="enter"):
            new_value_str = entry_var.get().strip()
            current_tree_values = list(tree.item(selected_item_id, "values"))
            
            if new_value_str:
                try:
                    diem_float = float(new_value_str)
                    if not (0 <= diem_float <= 10):
                        messagebox.showwarning("Điểm không hợp lệ", "Điểm phải từ 0 đến 10.", parent=self.app_controller.master)
                        if entry.winfo_exists(): entry.focus_set(); entry.select_range(0, tk.END)
                        return
                    current_tree_values[2] = f"{diem_float:.1f}"
                except ValueError:
                    messagebox.showwarning("Điểm không hợp lệ", "Vui lòng nhập một số.", parent=self.app_controller.master)
                    if entry.winfo_exists(): entry.focus_set(); entry.select_range(0, tk.END)
                    return
            else:
                current_tree_values[2] = "" 

            tree.item(selected_item_id, values=tuple(current_tree_values))
            
            if entry.winfo_exists(): entry.destroy()
            if selected_item_id in self.qen_entry_widgets: del self.qen_entry_widgets[selected_item_id]
            if self.qen_active_entry_item_id == selected_item_id: self.qen_active_entry_item_id = None

            if commit_event_type == "enter":
                next_item_id = tree.next(selected_item_id)
                if next_item_id:
                    tree.selection_set(next_item_id)
                    tree.focus(next_item_id)
                    x_next, y_next, _, _ = tree.bbox(next_item_id, column_id_str)
                    event_fake = tk.Event(); event_fake.x = x_next + 5; event_fake.y = y_next + 5; event_fake.widget = tree
                    self._qen_on_double_click_to_edit(event_fake)

        entry.bind("<Return>", lambda e: _on_commit("enter"))
        entry.bind("<FocusOut>", lambda e: _on_commit("focusout"))
        entry.bind("<Escape>", lambda e: (entry.destroy(), self.qen_entry_widgets.pop(selected_item_id, None), setattr(self, 'qen_active_entry_item_id', None)))

    def _on_qen_filter_change(self, event=None):
        for item in self.tree_qen_diem.get_children():
            self.tree_qen_diem.delete(item)
        self.qen_entry_widgets.clear()
        self.qen_active_entry_item_id = None
        self.app_controller.update_status("Lựa chọn Lớp/Học Kỳ/Môn Học đã thay đổi. Nhấn 'Tải DS Sinh Viên'.")

    def _load_sv_for_quick_enter(self):
        selected_lop = self.combo_qen_lop.get()
        selected_hoc_ky = self.combo_qen_hoc_ky.get()
        selected_mon_hoc_display = self.combo_qen_mon_hoc.get()

        if not selected_lop or selected_lop == "Chọn Lớp" or \
           not selected_hoc_ky or selected_hoc_ky == "Chọn học kỳ" or \
           not selected_mon_hoc_display or selected_mon_hoc_display == "Chọn Môn Học":
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn đầy đủ Lớp, Học Kỳ và Môn Học.", parent=self.app_controller.master)
            return

        ma_mon_hoc = self.app_controller.mon_hoc_display_to_code_map.get(selected_mon_hoc_display)
        if not ma_mon_hoc:
            messagebox.showerror("Lỗi", f"Không tìm thấy mã cho môn học: {selected_mon_hoc_display}", parent=self.app_controller.master)
            return

        for item in self.tree_qen_diem.get_children(): self.tree_qen_diem.delete(item)
        self.qen_entry_widgets.clear()
        self.qen_active_entry_item_id = None

        students_in_class = [sv for sv in self.app_controller.ql_diem.danh_sach_sinh_vien.values() if sv.lop_hoc == selected_lop]
        students_in_class.sort(key=lambda sv: sv.ho_ten)

        if not students_in_class:
            messagebox.showinfo("Thông báo", f"Không có sinh viên nào trong lớp {selected_lop}.", parent=self.app_controller.master)
            self.app_controller.update_status(f"Không có SV trong lớp {selected_lop}.")
            return

        for i, sv_obj in enumerate(students_in_class):
            current_grade_str = ""
            if selected_hoc_ky in sv_obj.diem and ma_mon_hoc in sv_obj.diem[selected_hoc_ky]:
                current_grade_str = f"{sv_obj.diem[selected_hoc_ky][ma_mon_hoc]:.1f}"
            
            # Thêm tag cho hàng chẵn/lẻ
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree_qen_diem.insert('', 'end', iid=sv_obj.ma_sv, values=(sv_obj.ma_sv, sv_obj.ho_ten, current_grade_str), tags=(tag,))

        self.app_controller.update_status(f"Đã tải {len(students_in_class)} SV lớp {selected_lop} cho môn {selected_mon_hoc_display}, HK {selected_hoc_ky}.")

    def _qen_destroy_active_entry(self):
        if self.qen_active_entry_item_id and self.qen_active_entry_item_id in self.qen_entry_widgets:
            entry_widget = self.qen_entry_widgets[self.qen_active_entry_item_id]
            if entry_widget.winfo_exists():
                entry_widget.destroy()
            del self.qen_entry_widgets[self.qen_active_entry_item_id]
        self.qen_active_entry_item_id = None

    def _on_tree_motion(self, event):
        """Thay đổi con trỏ chuột khi di qua cột điểm."""
        tree = event.widget
        region = tree.identify_region(event.x, event.y)

        if region == "cell":
            column_id_str = tree.identify_column(event.x)
            column_name_clicked = tree.column(column_id_str, "id")

            if column_name_clicked == 'diem_so_nhap':
                if not self.is_cursor_on_grade_column:
                    tree.config(cursor="ibeam") # Con trỏ hình chữ I
                    self.is_cursor_on_grade_column = True
            else:
                if self.is_cursor_on_grade_column:
                    tree.config(cursor="") # Con trỏ mặc định
                    self.is_cursor_on_grade_column = False
        else:
            if self.is_cursor_on_grade_column:
                tree.config(cursor="")
                self.is_cursor_on_grade_column = False

    def _on_tree_leave(self, event):
        """Đặt lại con trỏ chuột khi chuột rời khỏi Treeview."""
        tree = event.widget
        if self.is_cursor_on_grade_column:
            tree.config(cursor="")
            self.is_cursor_on_grade_column = False

    def _save_all_quick_entered_grades(self):
        self._qen_destroy_active_entry()
        selected_hoc_ky = self.combo_qen_hoc_ky.get()
        selected_mon_hoc_display = self.combo_qen_mon_hoc.get()

        if selected_hoc_ky == "Chọn học kỳ" or not selected_mon_hoc_display or selected_mon_hoc_display == "Chọn Môn Học":
            messagebox.showwarning("Thiếu thông tin", "Không rõ Học Kỳ hoặc Môn Học để lưu điểm.", parent=self.app_controller.master)
            return

        ma_mon_hoc = self.app_controller.mon_hoc_display_to_code_map.get(selected_mon_hoc_display)
        if not ma_mon_hoc:
            messagebox.showerror("Lỗi", "Môn học không hợp lệ.", parent=self.app_controller.master)
            return

        grades_to_process = []
        for item_id in self.tree_qen_diem.get_children():
            ma_sv = item_id
            current_tree_values = self.tree_qen_diem.item(item_id, "values")
            diem_nhap_str = str(current_tree_values[2]).strip() if len(current_tree_values) > 2 else ""

            if diem_nhap_str:
                try:
                    diem_float = float(diem_nhap_str)
                    if 0 <= diem_float <= 10:
                        grades_to_process.append({'ma_sv': ma_sv, 'diem': diem_float})
                    else:
                        messagebox.showwarning("Điểm không hợp lệ", f"Điểm '{diem_nhap_str}' cho SV {ma_sv} không hợp lệ (0-10).", parent=self.app_controller.master)
                except ValueError:
                    messagebox.showwarning("Điểm không hợp lệ", f"Giá trị điểm '{diem_nhap_str}' cho SV {ma_sv} không phải là số.", parent=self.app_controller.master)
        
        if not grades_to_process:
            messagebox.showinfo("Thông báo", "Không có điểm hợp lệ nào để lưu.", parent=self.app_controller.master)
            return

        success_count = 0; error_details = []
        for grade_data in grades_to_process:
            sv_obj = self.app_controller.ql_diem.danh_sach_sinh_vien.get(grade_data['ma_sv'])
            is_edit = sv_obj and selected_hoc_ky in sv_obj.diem and ma_mon_hoc in sv_obj.diem[selected_hoc_ky]
            
            if is_edit:
                success, msg = self.app_controller.ql_diem.sua_diem(grade_data['ma_sv'], ma_mon_hoc, grade_data['diem'], selected_hoc_ky)
            else:
                success, msg = self.app_controller.ql_diem.nhap_diem(grade_data['ma_sv'], ma_mon_hoc, grade_data['diem'], selected_hoc_ky)
            
            if success: success_count += 1
            else: error_details.append(f"SV {grade_data['ma_sv']}: {msg}")

        if error_details:
            messagebox.showerror("Lỗi Lưu Điểm", f"Đã lưu {success_count} điểm.\nLỗi:\n" + "\n".join(error_details), parent=self.app_controller.master)
        elif success_count > 0:
            messagebox.showinfo("Thành công", f"Đã lưu thành công {success_count} điểm.", parent=self.app_controller.master)
        else:
            messagebox.showinfo("Thông báo", "Không có thay đổi điểm nào được lưu.", parent=self.app_controller.master)

        self._load_sv_for_quick_enter()
        self.app_controller._populate_all_combobox_filters()