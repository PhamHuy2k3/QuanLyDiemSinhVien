"""Base class for tab interfaces."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Callable, Dict, List, Optional
from base_handler import BaseHandler
from constants_new import Messages, UI

class BaseTab(BaseHandler):
    def __init__(self, parent: ttk.Frame, controller: Any):
        super().__init__()
        self.parent = parent
        self.controller = controller
        self.widgets: Dict[str, Any] = {}
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the UI components. Override in subclass."""
        raise NotImplementedError

    def create_labeled_entry(self, parent: ttk.Frame, label_text: str,
                           row: int, column: int, width: int = UI.ENTRY_WIDTH,
                           padx: int = UI.PADDING, pady: int = UI.PADDING) -> ttk.Entry:
        """Create a labeled entry widget."""
        ttk.Label(parent, text=label_text).grid(row=row, column=column, padx=padx, pady=pady, sticky=tk.W)
        entry = ttk.Entry(parent, width=width)
        entry.grid(row=row, column=column + 1, padx=padx, pady=pady, sticky=tk.EW)
        return entry

    def create_labeled_combobox(self, parent: ttk.Frame, label_text: str,
                              row: int, column: int, values: List[str],
                              width: int = UI.ENTRY_WIDTH, padx: int = UI.PADDING,
                              pady: int = UI.PADDING) -> ttk.Combobox:
        """Create a labeled combobox widget."""
        ttk.Label(parent, text=label_text).grid(row=row, column=column, padx=padx, pady=pady, sticky=tk.W)
        combo = ttk.Combobox(parent, width=width, values=values, state="readonly")
        combo.grid(row=row, column=column + 1, padx=padx, pady=pady, sticky=tk.EW)
        return combo

    def create_button(self, parent: ttk.Frame, text: str,
                     command: Callable, width: int = UI.BUTTON_WIDTH) -> ttk.Button:
        """Create a button widget."""
        button = ttk.Button(parent, text=text, command=command, width=width)
        return button

    def create_treeview(self, parent: ttk.Frame, columns: List[str],
                       headings: List[str], show: str = "headings") -> ttk.Treeview:
        """Create a treeview widget with scrollbars."""
        # Create frame for treeview and scrollbars
        frame = ttk.Frame(parent)
        
        # Create treeview
        tree = ttk.Treeview(frame, columns=columns, show=show)
        for col, heading in zip(columns, headings):
            tree.heading(col, text=heading)
            tree.column(col, anchor=tk.W)
            
        # Create scrollbars
        vsb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        tree.grid(row=0, column=0, sticky=tk.NSEW)
        vsb.grid(row=0, column=1, sticky=tk.NS)
        hsb.grid(row=1, column=0, sticky=tk.EW)
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        return tree

    def show_message(self, title: str, message: str,
                    message_type: str = "info") -> None:
        """Show a message dialog."""
        func = getattr(messagebox, f"show{message_type}")
        func(title, message, parent=self.parent)

    def confirm_action(self, title: str, message: str) -> bool:
        """Show a confirmation dialog."""
        return messagebox.askyesno(title, message, parent=self.parent)

    def validate_required_fields(self, fields: Dict[str, Any]) -> bool:
        """Validate that required fields are not empty."""
        empty_fields = [name for name, value in fields.items() if not str(value).strip()]
        if empty_fields:
            self.show_message(Messages.WARNING,
                            f"Các trường sau không được để trống: {', '.join(empty_fields)}",
                            "warning")
            return False
        return True

    def clear_form(self, widgets: List[ttk.Entry]) -> None:
        """Clear form fields."""
        for widget in widgets:
            widget.delete(0, tk.END)

    def clear_treeview(self, tree: ttk.Treeview) -> None:
        """Clear all items from treeview."""
        for item in tree.get_children():
            tree.delete(item)

    def disable_widgets(self, widgets: List[Any]) -> None:
        """Disable multiple widgets."""
        for widget in widgets:
            widget.configure(state="disabled")

    def enable_widgets(self, widgets: List[Any]) -> None:
        """Enable multiple widgets."""
        for widget in widgets:
            widget.configure(state="normal")

    def populate_combobox(self, combo: ttk.Combobox,
                         values: List[str],
                         default: Optional[str] = None) -> None:
        """Populate a combobox with values."""
        combo['values'] = values
        if default and default in values:
            combo.set(default)
        elif values:
            combo.set(values[0])

    def get_selected_treeview_item(self, tree: ttk.Treeview) -> Optional[Dict[str, Any]]:
        """Get the selected item from a treeview."""
        selection = tree.selection()
        if not selection:
            return None
        item = tree.item(selection[0])
        return {'values': item['values'], 'tags': item['tags']}
