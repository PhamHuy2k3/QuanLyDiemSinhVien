"""Subject management tab implementation."""
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, Optional
from base_tab import BaseTab
from constants_new import ColumnNames, Messages, Validation
from models_new import MonHoc

class SubjectManagementTab(BaseTab):
    def __init__(self, parent: ttk.Frame, controller: Any):
        self.current_subject: Optional[str] = None
        super().__init__(parent, controller)

    def setup_ui(self) -> None:
        """Setup the subject management UI."""
        # Create main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create input form
        form_frame = ttk.LabelFrame(main_frame, text="Thông tin Môn học")
        form_frame.pack(fill=tk.X, padx=5, pady=5)

        # Create form fields
        self.widgets['entry_ma_mh'] = self.create_labeled_entry(
            form_frame, "Mã môn học:", 0, 0)
        self.widgets['entry_ten_mh'] = self.create_labeled_entry(
            form_frame, "Tên môn học:", 1, 0)
        self.widgets['entry_tin_chi'] = self.create_labeled_entry(
            form_frame, "Số tín chỉ:", 2, 0, width=10)

        # Create buttons frame
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        # Create buttons
        self.widgets['btn_add'] = self.create_button(
            button_frame, "Thêm", self.handle_add)
        self.widgets['btn_update'] = self.create_button(
            button_frame, "Cập nhật", self.handle_update)
        self.widgets['btn_delete'] = self.create_button(
            button_frame, "Xóa", self.handle_delete)
        self.widgets['btn_clear'] = self.create_button(
            button_frame, "Làm mới", self.clear_subject_form)

        for i, btn in enumerate(
            ['btn_add', 'btn_update', 'btn_delete', 'btn_clear']):
            self.widgets[btn].pack(side=tk.LEFT, padx=5)

        # Create subject list
        list_frame = ttk.LabelFrame(main_frame, text="Danh sách Môn học")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ['ma_mh', 'ten_mh', 'tin_chi']
        headings = ["Mã MH", "Tên môn học", "Tín chỉ"]

        self.widgets['tree_subjects'] = self.create_treeview(
            list_frame, columns, headings)
        self.widgets['tree_subjects'].pack(fill=tk.BOTH, expand=True)
        
        # Bind events
        self.widgets['tree_subjects'].bind('<<TreeviewSelect>>', 
                                         self.on_subject_select)

        # Initial load
        self.refresh_subject_list()

    def refresh_subject_list(self) -> None:
        """Refresh the subject list."""
        self.clear_treeview(self.widgets['tree_subjects'])
        
        subjects = list(self.controller.ql_diem.danh_sach_mon_hoc.values())
        for mh in sorted(subjects, key=lambda x: x.ma_mh):
            self.widgets['tree_subjects'].insert('', tk.END, values=(
                mh.ma_mh, mh.ten_mh, mh.so_tin_chi
            ))

    def clear_subject_form(self) -> None:
        """Clear the subject form."""
        self.current_subject = None
        form_widgets = ['entry_ma_mh', 'entry_ten_mh', 'entry_tin_chi']
        
        for widget_name in form_widgets:
            self.widgets[widget_name].delete(0, tk.END)
        
        self.widgets['entry_ma_mh'].configure(state='normal')
        self.widgets['btn_add'].configure(state='normal')
        self.widgets['entry_ma_mh'].focus()

    def on_subject_select(self, event=None) -> None:
        """Handle subject selection from tree."""
        selected_item = self.get_selected_treeview_item(
            self.widgets['tree_subjects'])
        if not selected_item:
            return

        values = selected_item['values']
        self.current_subject = values[0]  # ma_mh

        # Populate form
        self.widgets['entry_ma_mh'].configure(state='normal')
        self.widgets['entry_ma_mh'].delete(0, tk.END)
        self.widgets['entry_ma_mh'].insert(0, values[0])
        self.widgets['entry_ma_mh'].configure(state='readonly')
        
        self.widgets['entry_ten_mh'].delete(0, tk.END)
        self.widgets['entry_ten_mh'].insert(0, values[1])
        
        self.widgets['entry_tin_chi'].delete(0, tk.END)
        self.widgets['entry_tin_chi'].insert(0, values[2])

        self.widgets['btn_add'].configure(state='disabled')

    def get_form_data(self) -> Dict[str, Any]:
        """Get form data as dictionary."""
        return {
            'ma_mh': self.widgets['entry_ma_mh'].get().strip(),
            'ten_mh': self.widgets['entry_ten_mh'].get().strip(),
            'so_tin_chi': self.widgets['entry_tin_chi'].get().strip()
        }

    def validate_subject_data(self, data: Dict[str, Any]) -> bool:
        """Validate subject form data."""
        if not self.validate_required_fields(data):
            return False

        try:
            tin_chi = int(data['so_tin_chi'])
            if not Validation.MIN_TIN_CHI <= tin_chi <= Validation.MAX_TIN_CHI:
                raise ValueError(
                    f"Số tín chỉ phải từ {Validation.MIN_TIN_CHI} "
                    f"đến {Validation.MAX_TIN_CHI}")
        except ValueError as e:
            self.show_message(Messages.ERROR, str(e), "error")
            return False

        return True

    def handle_add(self) -> None:
        """Handle add subject action."""
        data = self.get_form_data()
        if not self.validate_subject_data(data):
            return

        success, message = self.controller.ql_diem.them_mon_hoc(**data)
        if success:
            self.show_message(Messages.SUCCESS, message)
            self.clear_subject_form()
            self.refresh_subject_list()
        else:
            self.show_message(Messages.ERROR, message, "error")

    def handle_update(self) -> None:
        """Handle update subject action."""
        if not self.current_subject:
            self.show_message(Messages.WARNING,
                            "Vui lòng chọn môn học để cập nhật", "warning")
            return

        data = self.get_form_data()
        if not self.validate_subject_data(data):
            return

        success, message = self.controller.ql_diem.sua_mon_hoc(**data)
        if success:
            self.show_message(Messages.SUCCESS, message)
            self.clear_subject_form()
            self.refresh_subject_list()
        else:
            self.show_message(Messages.ERROR, message, "error")

    def handle_delete(self) -> None:
        """Handle delete subject action."""
        if not self.current_subject:
            self.show_message(Messages.WARNING,
                            "Vui lòng chọn môn học để xóa", "warning")
            return

        if not self.confirm_action(Messages.CONFIRM,
                                 f"Xóa môn học {self.current_subject}?"):
            return

        success, message = self.controller.ql_diem.xoa_mon_hoc(
            self.current_subject)
        if success:
            self.show_message(Messages.SUCCESS, message)
            self.clear_subject_form()
            self.refresh_subject_list()
        else:
            self.show_message(Messages.ERROR, message, "error")
