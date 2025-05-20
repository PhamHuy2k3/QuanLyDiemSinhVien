"""Grade entry tab implementation."""
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, List, Optional
from base_tab import BaseTab
from constants_new import ColumnNames, Messages, Validation

class GradeEntryTab(BaseTab):
    def __init__(self, parent: ttk.Frame, controller: Any):
        self.current_student: Optional[str] = None
        self.subject_display_to_code: Dict[str, str] = {}
        super().__init__(parent, controller)

    def setup_ui(self) -> None:
        """Setup the grade entry UI."""
        # Create main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create student selection section
        student_frame = ttk.LabelFrame(main_frame, text="Chọn Sinh viên")
        student_frame.pack(fill=tk.X, padx=5, pady=5)

        # Create filter frame
        filter_frame = ttk.Frame(student_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        self.widgets['filter_lop'] = self.create_labeled_combobox(
            filter_frame, "Lớp:", 0, 0, ["Tất cả"])
        self.widgets['filter_khoa'] = self.create_labeled_combobox(
            filter_frame, "Khoa:", 0, 2, ["Tất cả"])

        # Create student combobox
        self.widgets['combo_student'] = self.create_labeled_combobox(
            student_frame, "Sinh viên:", 1, 0, [])
        
        # Create student info display
        info_frame = ttk.Frame(student_frame)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        columns = ['field', 'value']
        headings = ["Trường", "Giá trị"]
        self.widgets['tree_student_info'] = self.create_treeview(
            info_frame, columns, headings)
        self.widgets['tree_student_info'].pack(fill=tk.X)

        # Create grade entry section
        grade_frame = ttk.LabelFrame(main_frame, text="Nhập điểm")
        grade_frame.pack(fill=tk.X, padx=5, pady=5)

        # Create grade entry fields
        self.widgets['combo_hoc_ky'] = self.create_labeled_combobox(
            grade_frame, "Học kỳ:", 0, 0, [])
        self.widgets['combo_mon_hoc'] = self.create_labeled_combobox(
            grade_frame, "Môn học:", 1, 0, [])
        self.widgets['entry_diem'] = self.create_labeled_entry(
            grade_frame, "Điểm:", 2, 0, width=10)

        # Create button frame
        button_frame = ttk.Frame(grade_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        self.widgets['btn_submit'] = self.create_button(
            button_frame, "Lưu điểm", self.handle_submit)
        self.widgets['btn_clear'] = self.create_button(
            button_frame, "Làm mới", self.clear_grade_form)

        for btn in ['btn_submit', 'btn_clear']:
            self.widgets[btn].pack(side=tk.LEFT, padx=5)

        # Bind events
        self.widgets['filter_lop'].bind('<<ComboboxSelected>>',
                                      self.on_filter_change)
        self.widgets['filter_khoa'].bind('<<ComboboxSelected>>',
                                       self.on_filter_change)
        self.widgets['combo_student'].bind('<<ComboboxSelected>>',
                                         self.on_student_select)

        # Initial population
        self.populate_filters()
        self.populate_hoc_ky()
        self.populate_mon_hoc()

    def populate_filters(self) -> None:
        """Populate filter comboboxes."""
        students = list(self.controller.ql_diem.danh_sach_sinh_vien.values())
        
        lop_values = sorted(list(set(sv.lop_hoc for sv in students if sv.lop_hoc)))
        khoa_values = sorted(list(set(sv.khoa for sv in students if sv.khoa)))
        
        self.populate_combobox(self.widgets['filter_lop'], 
                             ["Tất cả"] + lop_values)
        self.populate_combobox(self.widgets['filter_khoa'], 
                             ["Tất cả"] + khoa_values)

    def populate_hoc_ky(self) -> None:
        """Populate semester combobox."""
        # This should be customized based on your semester format
        hoc_ky_values = [f"{year}-{semester}" 
                        for year in range(2020, 2026)
                        for semester in [1, 2]]
        self.populate_combobox(self.widgets['combo_hoc_ky'], hoc_ky_values)

    def populate_mon_hoc(self) -> None:
        """Populate subject combobox."""
        subjects = list(self.controller.ql_diem.danh_sach_mon_hoc.values())
        self.subject_display_to_code.clear()
        
        display_values = []
        for subject in sorted(subjects, key=lambda x: x.ten_mh):
            display = f"{subject.ten_mh} ({subject.ma_mh})"
            self.subject_display_to_code[display] = subject.ma_mh
            display_values.append(display)
            
        self.populate_combobox(self.widgets['combo_mon_hoc'], display_values)

    def on_filter_change(self, event=None) -> None:
        """Handle filter change."""
        self.populate_student_combobox()

    def populate_student_combobox(self) -> None:
        """Populate student combobox based on filters."""
        selected_lop = self.widgets['filter_lop'].get()
        selected_khoa = self.widgets['filter_khoa'].get()
        
        students = list(self.controller.ql_diem.danh_sach_sinh_vien.values())
        filtered_students = []
        
        for sv in students:
            if (selected_lop == "Tất cả" or sv.lop_hoc == selected_lop) and \
               (selected_khoa == "Tất cả" or sv.khoa == selected_khoa):
                filtered_students.append(sv)

        display_values = []
        for sv in sorted(filtered_students, key=lambda x: x.ma_sv):
            display_values.append(f"{sv.ho_ten} ({sv.ma_sv})")
            
        self.populate_combobox(self.widgets['combo_student'], display_values)

    def on_student_select(self, event=None) -> None:
        """Handle student selection."""
        selected = self.widgets['combo_student'].get()
        if not selected:
            return

        try:
            ma_sv = selected.split('(')[-1].replace(')', '').strip()
            student = self.controller.ql_diem.danh_sach_sinh_vien.get(ma_sv)
            if student:
                self.current_student = ma_sv
                self.update_student_info(student)
            else:
                self.current_student = None
        except:
            self.current_student = None

    def update_student_info(self, student: Any) -> None:
        """Update student info display."""
        self.clear_treeview(self.widgets['tree_student_info'])
        
        info = [
            ("Mã SV", student.ma_sv),
            ("Họ tên", student.ho_ten),
            ("Lớp", student.lop_hoc),
            ("Khoa", student.khoa),
            ("Trường", student.truong),
            ("Học kỳ ĐK", student.hoc_ky_nhap_hoc)
        ]
        
        for field, value in info:
            self.widgets['tree_student_info'].insert('', tk.END,
                                                   values=(field, value))

    def clear_grade_form(self) -> None:
        """Clear the grade entry form."""
        self.widgets['combo_hoc_ky'].set('')
        self.widgets['combo_mon_hoc'].set('')
        self.widgets['entry_diem'].delete(0, tk.END)

    def validate_grade_data(self) -> bool:
        """Validate grade entry data."""
        if not self.current_student:
            self.show_message(Messages.WARNING,
                            "Vui lòng chọn sinh viên", "warning")
            return False

        hoc_ky = self.widgets['combo_hoc_ky'].get()
        mon_hoc = self.widgets['combo_mon_hoc'].get()
        diem_str = self.widgets['entry_diem'].get().strip()

        if not all([hoc_ky, mon_hoc, diem_str]):
            self.show_message(Messages.WARNING,
                            "Vui lòng nhập đầy đủ thông tin", "warning")
            return False

        try:
            diem = float(diem_str)
            if not Validation.MIN_DIEM <= diem <= Validation.MAX_DIEM:
                raise ValueError(
                    f"Điểm phải từ {Validation.MIN_DIEM} "
                    f"đến {Validation.MAX_DIEM}")
        except ValueError as e:
            self.show_message(Messages.ERROR, str(e), "error")
            return False

        return True

    def handle_submit(self) -> None:
        """Handle grade submission."""
        if not self.validate_grade_data():
            return

        mon_hoc_display = self.widgets['combo_mon_hoc'].get()
        ma_mon = self.subject_display_to_code.get(mon_hoc_display)
        if not ma_mon:
            self.show_message(Messages.ERROR,
                            "Mã môn học không hợp lệ", "error")
            return

        try:
            diem = float(self.widgets['entry_diem'].get())
            success, message = self.controller.ql_diem.nhap_diem(
                self.current_student,
                ma_mon,
                diem,
                self.widgets['combo_hoc_ky'].get()
            )

            if success:
                self.show_message(Messages.SUCCESS, message)
                self.clear_grade_form()
            else:
                self.show_message(Messages.ERROR, message, "error")
        except ValueError as e:
            self.show_message(Messages.ERROR, str(e), "error")
