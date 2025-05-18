# tabs/user_management_tab.py
import tkinter as tk
from tkinter import ttk, messagebox

class UserManagementTab:
    def __init__(self, parent_frame, app_gui_instance):
        self.parent_frame = parent_frame
        self.app = app_gui_instance # Để gọi UserManager, update_status, etc.
        self.user_manager = self.app.user_manager

        self.selected_username_for_edit = None

        # --- Main Frame cho tab này ---
        self.main_frame = ttk.Frame(self.parent_frame, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Frame Nhập liệu/Sửa ---
        input_form_frame = ttk.LabelFrame(self.main_frame, text="Thông tin Người dùng")
        input_form_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(input_form_frame, text="Tên đăng nhập:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_username = ttk.Entry(input_form_frame, width=30)
        self.entry_username.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_form_frame, text="Mật khẩu:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_password = ttk.Entry(input_form_frame, width=30, show="*")
        self.entry_password.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.lbl_password_note = ttk.Label(input_form_frame, text="(Để trống nếu không đổi khi sửa vai trò)")
        self.lbl_password_note.grid(row=1, column=2, padx=5, pady=5, sticky="w")


        ttk.Label(input_form_frame, text="Vai trò:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.combo_role = ttk.Combobox(input_form_frame, width=28, state="readonly")
        self.combo_role.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.combo_role['values'] = sorted(list(self.user_manager.roles_permissions.keys()))
        if self.combo_role['values']:
            self.combo_role.current(0) # Chọn vai trò đầu tiên mặc định

        input_form_frame.columnconfigure(1, weight=1)

        # --- Frame Nút Hành động ---
        action_buttons_frame = ttk.Frame(input_form_frame)
        action_buttons_frame.grid(row=3, column=0, columnspan=3, pady=10)

        self.btn_add_user = ttk.Button(action_buttons_frame, text="Thêm Người dùng", command=self._add_user, style="Accent.TButton")
        self.btn_add_user.pack(side=tk.LEFT, padx=5)

        self.btn_edit_user = ttk.Button(action_buttons_frame, text="Lưu Thay đổi", command=self._edit_user)
        self.btn_edit_user.pack(side=tk.LEFT, padx=5)
        self.btn_edit_user.config(state=tk.DISABLED) # Disable ban đầu

        self.btn_delete_user = ttk.Button(action_buttons_frame, text="Xóa Người dùng", command=self._delete_user)
        self.btn_delete_user.pack(side=tk.LEFT, padx=5)
        self.btn_delete_user.config(state=tk.DISABLED) # Disable ban đầu

        self.btn_clear_form = ttk.Button(action_buttons_frame, text="Làm mới Form", command=self._clear_form)
        self.btn_clear_form.pack(side=tk.LEFT, padx=5)

        # --- Frame Danh sách Người dùng ---
        users_list_frame = ttk.LabelFrame(self.main_frame, text="Danh sách Người dùng")
        users_list_frame.pack(fill=tk.BOTH, expand=True)

        cols_users = ('username', 'role')
        self.tree_users = ttk.Treeview(users_list_frame, columns=cols_users, show='headings', selectmode="browse")
        self.tree_users.heading('username', text='Tên đăng nhập')
        self.tree_users.heading('role', text='Vai trò')
        self.tree_users.column('username', width=200, anchor=tk.W)
        self.tree_users.column('role', width=150, anchor=tk.W)

        scrollbar_users = ttk.Scrollbar(users_list_frame, orient=tk.VERTICAL, command=self.tree_users.yview)
        self.tree_users.configure(yscrollcommand=scrollbar_users.set)

        self.tree_users.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_users.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_users.bind("<<TreeviewSelect>>", self._on_user_select)

        self._populate_users_treeview()
        self._apply_permissions_to_tab_widgets()

    def _apply_permissions_to_tab_widgets(self):
        """Áp dụng quyền cho các widget trong tab này."""
        can_add = self.app.user_manager.has_permission(self.app.current_user, self.app.PERMISSIONS["ADD_USER"])
        can_edit = self.app.user_manager.has_permission(self.app.current_user, self.app.PERMISSIONS["EDIT_USER_ROLE"]) # Hoặc RESET_USER_PASSWORD
        can_delete = self.app.user_manager.has_permission(self.app.current_user, self.app.PERMISSIONS["DELETE_USER"])

        self.btn_add_user.config(state=tk.NORMAL if can_add else tk.DISABLED)
        # Nút Sửa/Xóa sẽ được enable/disable dựa trên việc có item nào được chọn không nữa
        # và quyền của người dùng.

    def _populate_users_treeview(self):
        for item in self.tree_users.get_children():
            self.tree_users.delete(item)

        users_info = self.user_manager.get_all_users_info()
        for user_data in sorted(users_info, key=lambda x: x['username']):
            self.tree_users.insert('', tk.END, values=(user_data['username'], user_data['role']))
        self.app.update_status(f"Hiển thị {len(users_info)} người dùng.")

    def _clear_form(self, clear_selection=True):
        self.entry_username.config(state=tk.NORMAL)
        self.entry_username.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)
        if self.combo_role['values']:
            self.combo_role.current(0)
        self.selected_username_for_edit = None
        self.btn_edit_user.config(state=tk.DISABLED)
        self.btn_delete_user.config(state=tk.DISABLED)
        self.btn_add_user.config(text="Thêm Người dùng") # Reset text nút
        self.lbl_password_note.grid() # Hiển thị lại ghi chú mật khẩu

        if clear_selection and self.tree_users.selection():
            self.tree_users.selection_remove(self.tree_users.selection())
        self.entry_username.focus()
        self.app.update_status("Form quản lý người dùng đã làm mới.")

    def _on_user_select(self, event=None):
        selected_item = self.tree_users.focus()
        if not selected_item:
            self._clear_form(clear_selection=False)
            return

        item_values = self.tree_users.item(selected_item)['values']
        if item_values:
            username, role = item_values
            self.selected_username_for_edit = username

            self.entry_username.config(state=tk.NORMAL)
            self.entry_username.delete(0, tk.END)
            self.entry_username.insert(0, username)
            self.entry_username.config(state=tk.DISABLED) # Không cho sửa username

            self.entry_password.delete(0, tk.END) # Xóa field mật khẩu
            self.lbl_password_note.grid()

            if role in self.combo_role['values']:
                self.combo_role.set(role)
            else: # Nếu vai trò không có trong combobox (ít khi xảy ra)
                self.combo_role.set(self.combo_role['values'][0] if self.combo_role['values'] else "")

            self.btn_edit_user.config(state=tk.NORMAL if self.app.user_manager.has_permission(self.app.current_user, self.app.PERMISSIONS["EDIT_USER_ROLE"]) or self.app.user_manager.has_permission(self.app.current_user, self.app.PERMISSIONS["RESET_USER_PASSWORD"]) else tk.DISABLED)
            self.btn_delete_user.config(state=tk.NORMAL if self.app.user_manager.has_permission(self.app.current_user, self.app.PERMISSIONS["DELETE_USER"]) else tk.DISABLED)
            self.btn_add_user.config(text="Thêm Mới (Hủy chọn)") # Đổi text nút Thêm
            self.app.update_status(f"Đã chọn người dùng: {username}. Sẵn sàng sửa hoặc xóa.")

    def _add_user(self):
        if self.selected_username_for_edit: # Nếu đang ở chế độ sửa/xóa mà bấm nút này
            self._clear_form()
            return

        if not self.app.user_manager.has_permission(self.app.current_user, self.app.PERMISSIONS["ADD_USER"]):
            messagebox.showerror("Không có quyền", "Bạn không có quyền thêm người dùng.", parent=self.parent_frame)
            return

        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip() # CẢNH BÁO: Plain text
        role = self.combo_role.get()

        if not username or not password or not role:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập Tên đăng nhập, Mật khẩu và chọn Vai trò.", parent=self.parent_frame)
            return

        success, message = self.user_manager.add_user(username, password, role)
        if success:
            messagebox.showinfo("Thành công", message, parent=self.parent_frame)
            self._populate_users_treeview()
            self._clear_form()
        else:
            messagebox.showerror("Lỗi", message, parent=self.parent_frame)
        self.app.update_status(message)

    def _edit_user(self):
        if not self.selected_username_for_edit:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn người dùng từ danh sách để sửa.", parent=self.parent_frame)
            return

        username_to_edit = self.selected_username_for_edit
        new_password = self.entry_password.get().strip() # Có thể trống
        new_role = self.combo_role.get()

        # Sửa vai trò
        if self.app.user_manager.has_permission(self.app.current_user, self.app.PERMISSIONS["EDIT_USER_ROLE"]):
            current_role = self.user_manager.get_user_role(username_to_edit)
            if new_role != current_role:
                success_role, msg_role = self.user_manager.edit_user_role(username_to_edit, new_role)
                if success_role:
                    messagebox.showinfo("Thành công", msg_role, parent=self.parent_frame)
                    self.app.update_status(msg_role)
                else:
                    messagebox.showerror("Lỗi sửa vai trò", msg_role, parent=self.parent_frame)
                    self.app.update_status(msg_role)
                    # Không clear form nếu lỗi để user sửa lại

        # Đặt lại mật khẩu (nếu có nhập)
        if new_password and self.app.user_manager.has_permission(self.app.current_user, self.app.PERMISSIONS["RESET_USER_PASSWORD"]):
            success_pass, msg_pass = self.user_manager.reset_password(username_to_edit, new_password)
            if success_pass:
                messagebox.showinfo("Thành công", msg_pass, parent=self.parent_frame)
                self.app.update_status(msg_pass)
            else:
                messagebox.showerror("Lỗi đặt lại mật khẩu", msg_pass, parent=self.parent_frame)
                self.app.update_status(msg_pass)

        self._populate_users_treeview()
        self._clear_form() # Xóa form sau khi thực hiện

    def _delete_user(self):
        if not self.selected_username_for_edit:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn người dùng từ danh sách để xóa.", parent=self.parent_frame)
            return

        if not self.app.user_manager.has_permission(self.app.current_user, self.app.PERMISSIONS["DELETE_USER"]):
            messagebox.showerror("Không có quyền", "Bạn không có quyền xóa người dùng.", parent=self.parent_frame)
            return

        username_to_delete = self.selected_username_for_edit
        confirm = messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc muốn xóa người dùng '{username_to_delete}' không?", parent=self.parent_frame)
        if confirm:
            success, message = self.user_manager.delete_user(username_to_delete)
            if success:
                messagebox.showinfo("Thành công", message, parent=self.parent_frame)
                self._populate_users_treeview()
                self._clear_form()
            else:
                messagebox.showerror("Lỗi", message, parent=self.parent_frame)
            self.app.update_status(message)

    def on_tab_selected(self):
        """Được gọi khi tab này được chọn."""
        self._populate_users_treeview()
        self._clear_form()
        self._apply_permissions_to_tab_widgets()
        self.app.update_status("Chuyển đến tab Quản lý Người dùng.")