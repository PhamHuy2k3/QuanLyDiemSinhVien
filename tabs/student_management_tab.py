"""Student management tab implementation."""
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, Optional
from base_tab import BaseTab
from constants_new import ColumnNames, Messages, Validation
from models_new import SinhVien

class StudentManagementTab(BaseTab):
    def __init__(self, parent: ttk.Frame, controller: Any):
        self.current_student: Optional[str] = None
        super().__init__(parent, controller)

    def setup_ui(self) -> None:
        """Setup the student management UI."""
        # Create main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create input form
        form_frame = ttk.LabelFrame(main_frame, text="Thông tin Sinh viên")
        form_frame.pack(fill=tk.X, padx=5, pady=5)

        # Create form fields
        self.widgets['entry_ma_sv'] = self.create_labeled_entry(
            form_frame, ColumnNames.MA_SV, 0, 0)
        self.widgets['entry_ho_ten'] = self.create_labeled_entry(
            form_frame, ColumnNames.HO_TEN, 1, 0)
        self.widgets['combo_lop'] = self.create_labeled_combobox(
            form_frame, ColumnNames.LOP_HOC, 2, 0, [])
        self.widgets['combo_truong'] = self.create_labeled_combobox(
            form_frame, ColumnNames.TRUONG, 3, 0, [])
        self.widgets['combo_khoa'] = self.create_labeled_combobox(
            form_frame, ColumnNames.KHOA, 4, 0, [])
        self.widgets['entry_hoc_ky'] = self.create_labeled_entry(
            form_frame, ColumnNames.HOC_KY, 5, 0)

        # Create buttons frame
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)

        # Create buttons
        self.widgets['btn_add'] = self.create_button(
            button_frame, "Thêm", self.handle_add)
        self.widgets['btn_update'] = self.create_button(
            button_frame, "Cập nhật", self.handle_update)
        self.widgets['btn_delete'] = self.create_button(
            button_frame, "Xóa", self.handle_delete)
        self.widgets['btn_clear'] = self.create_button(
            button_frame, "Làm mới", self.clear_student_form)

        for i, btn in enumerate(
            ['btn_add', 'btn_update', 'btn_delete', 'btn_clear']):
            self.widgets[btn].pack(side=tk.LEFT, padx=5)

        # Create filter frame
        filter_frame = ttk.LabelFrame(main_frame, text="Lọc Sinh viên")
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        # Create filter fields
        self.widgets['filter_lop'] = self.create_labeled_combobox(
            filter_frame, "Lớp:", 0, 0, ["Tất cả"])
        self.widgets['filter_khoa'] = self.create_labeled_combobox(
            filter_frame, "Khoa:", 0, 2, ["Tất cả"])

        # Create student list
        list_frame = ttk.LabelFrame(main_frame, text="Danh sách Sinh viên")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ['ma_sv', 'ho_ten', 'lop_hoc', 'truong', 'khoa', 'hoc_ky']
        headings = [ColumnNames.MA_SV, ColumnNames.HO_TEN, ColumnNames.LOP_HOC,
                   ColumnNames.TRUONG, ColumnNames.KHOA, ColumnNames.HOC_KY]

        self.widgets['tree_students'] = self.create_treeview(
            list_frame, columns, headings)
        self.widgets['tree_students'].pack(fill=tk.BOTH, expand=True)
        
        # Bind events
        self.widgets['tree_students'].bind('<<TreeviewSelect>>', 
                                         self.on_student_select)
        self.widgets['filter_lop'].bind('<<ComboboxSelected>>', 
                                      self.refresh_student_list)
        self.widgets['filter_khoa'].bind('<<ComboboxSelected>>', 
                                       self.refresh_student_list)

        # Initial population
        self.populate_filters()
        self.refresh_student_list()

    def populate_filters(self) -> None:
        """Populate filter comboboxes."""
        students = list(self.controller.ql_diem.danh_sach_sinh_vien.values())
        
        lop_values = sorted(list(set(sv.lop_hoc for sv in students if sv.lop_hoc)))
        khoa_values = sorted(list(set(sv.khoa for sv in students if sv.khoa)))
        
        self.populate_combobox(self.widgets['filter_lop'], 
                             ["Tất cả"] + lop_values)
        self.populate_combobox(self.widgets['filter_khoa'], 
                             ["Tất cả"] + khoa_values)
        
        # Also update form comboboxes
        self.populate_combobox(self.widgets['combo_lop'], lop_values)
        self.populate_combobox(self.widgets['combo_truong'], 
                             list(set(sv.truong for sv in students if sv.truong)))
        self.populate_combobox(self.widgets['combo_khoa'], khoa_values)

    def refresh_student_list(self, event=None) -> None:
        """Refresh the student list based on filters."""
        self.clear_treeview(self.widgets['tree_students'])
        
        selected_lop = self.widgets['filter_lop'].get()
        selected_khoa = self.widgets['filter_khoa'].get()
        
        students = list(self.controller.ql_diem.danh_sach_sinh_vien.values())
        filtered_students = []
        
        for sv in students:
            if (selected_lop == "Tất cả" or sv.lop_hoc == selected_lop) and \
               (selected_khoa == "Tất cả" or sv.khoa == selected_khoa):
                filtered_students.append(sv)

        for sv in sorted(filtered_students, key=lambda x: x.ma_sv):
            self.widgets['tree_students'].insert('', tk.END, values=(
                sv.ma_sv, sv.ho_ten, sv.lop_hoc, sv.truong, sv.khoa,
                sv.hoc_ky_nhap_hoc
            ))

    def clear_student_form(self) -> None:
        """Clear the student form."""
        self.current_student = None
        form_widgets = ['entry_ma_sv', 'entry_ho_ten', 'combo_lop',
                       'combo_truong', 'combo_khoa', 'entry_hoc_ky']
        
        for widget_name in form_widgets:
            widget = self.widgets[widget_name]
            if isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
            elif isinstance(widget, ttk.Combobox):
                widget.set('')
        
        self.widgets['entry_ma_sv'].configure(state='normal')
        self.widgets['btn_add'].configure(state='normal')
        self.widgets['entry_ma_sv'].focus()

    def on_student_select(self, event=None) -> None:
        """Handle student selection from tree."""
        selected_item = self.get_selected_treeview_item(
            self.widgets['tree_students'])
        if not selected_item:
            return

        values = selected_item['values']
        self.current_student = values[0]  # ma_sv

        # Populate form
        self.widgets['entry_ma_sv'].configure(state='normal')
        self.widgets['entry_ma_sv'].delete(0, tk.END)
        self.widgets['entry_ma_sv'].insert(0, values[0])
        self.widgets['entry_ma_sv'].configure(state='readonly')
        
        self.widgets['entry_ho_ten'].delete(0, tk.END)
        self.widgets['entry_ho_ten'].insert(0, values[1])
        
        self.widgets['combo_lop'].set(values[2])
        self.widgets['combo_truong'].set(values[3])
        self.widgets['combo_khoa'].set(values[4])
        
        self.widgets['entry_hoc_ky'].delete(0, tk.END)
        self.widgets['entry_hoc_ky'].insert(0, values[5])

        self.widgets['btn_add'].configure(state='disabled')

    def get_form_data(self) -> Dict[str, str]:
        """Get form data as dictionary."""
        return {
            'ma_sv': self.widgets['entry_ma_sv'].get().strip(),
            'ho_ten': self.widgets['entry_ho_ten'].get().strip(),
            'lop_hoc': self.widgets['combo_lop'].get().strip(),
            'truong': self.widgets['combo_truong'].get().strip(),
            'khoa': self.widgets['combo_khoa'].get().strip(),
            'hoc_ky_nhap_hoc': self.widgets['entry_hoc_ky'].get().strip()
        }

    def validate_student_data(self, data: Dict[str, str]) -> bool:
        """Validate student form data."""
        if not self.validate_required_fields(data):
            return False

        try:
            if not data['ma_sv'].isdigit() or \
               len(data['ma_sv']) != Validation.MIN_MA_SV_LENGTH:
                raise ValueError(
                    f"Mã SV phải là {Validation.MIN_MA_SV_LENGTH} chữ số")
        except ValueError as e:
            self.show_message(Messages.ERROR, str(e), "error")
            return False

        return True

    def handle_add(self) -> None:
        """Handle add student action."""
        data = self.get_form_data()
        if not self.validate_student_data(data):
            return

        success, message = self.controller.ql_diem.them_sinh_vien(**data)
        if success:
            self.show_message(Messages.SUCCESS, message)
            self.clear_student_form()
            self.populate_filters()
            self.refresh_student_list()
        else:
            self.show_message(Messages.ERROR, message, "error")

    def handle_update(self) -> None:
        """Handle update student action."""
        if not self.current_student:
            self.show_message(Messages.WARNING, 
                            "Vui lòng chọn sinh viên để cập nhật", "warning")
            return

        data = self.get_form_data()
        if not self.validate_student_data(data):
            return

        success, message = self.controller.ql_diem.sua_sinh_vien(**data)
        if success:
            self.show_message(Messages.SUCCESS, message)
            self.clear_student_form()
            self.populate_filters()
            self.refresh_student_list()
        else:
            self.show_message(Messages.ERROR, message, "error")

    def handle_delete(self) -> None:
        """Handle delete student action."""
        if not self.current_student:
            self.show_message(Messages.WARNING,
                            "Vui lòng chọn sinh viên để xóa", "warning")
            return

        if not self.confirm_action(Messages.CONFIRM,
                                 f"Xóa sinh viên {self.current_student}?"):
            return

        success, message = self.controller.ql_diem.xoa_sinh_vien(
            self.current_student)
        if success:
            self.show_message(Messages.SUCCESS, message)
            self.clear_student_form()
            self.populate_filters()
            self.refresh_student_list()
        else:
            self.show_message(Messages.ERROR, message, "error")
