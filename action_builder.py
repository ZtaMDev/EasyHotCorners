# pyrefly: ignore [missing-import]
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QComboBox, QCheckBox, QFileDialog,
    QStackedWidget, QWidget, QFrame, QMessageBox, QSizePolicy
)
# pyrefly: ignore [missing-import]
from PySide6.QtCore import Qt
from actions import load_custom_actions, save_custom_actions, CUSTOM_ACTION_PREFIX
from i18n import t

# Key name -> VK code
KEY_MAP = {
    "A": 0x41, "B": 0x42, "C": 0x43, "D": 0x44, "E": 0x45, "F": 0x46,
    "G": 0x47, "H": 0x48, "I": 0x49, "J": 0x4A, "K": 0x4B, "L": 0x4C,
    "M": 0x4D, "N": 0x4E, "O": 0x4F, "P": 0x50, "Q": 0x51, "R": 0x52,
    "S": 0x53, "T": 0x54, "U": 0x55, "V": 0x56, "W": 0x57, "X": 0x58,
    "Y": 0x59, "Z": 0x5A,
    "0": 0x30, "1": 0x31, "2": 0x32, "3": 0x33, "4": 0x34,
    "5": 0x35, "6": 0x36, "7": 0x37, "8": 0x38, "9": 0x39,
    "F1": 0x70, "F2": 0x71, "F3": 0x72, "F4": 0x73, "F5": 0x74,
    "F6": 0x75, "F7": 0x76, "F8": 0x77, "F9": 0x78, "F10": 0x79,
    "F11": 0x7A, "F12": 0x7B,
    "Space": 0x20, "Enter": 0x0D, "Escape": 0x1B, "Tab": 0x09,
    "Backspace": 0x08, "Delete": 0x2E, "Insert": 0x2D,
    "Home": 0x24, "End": 0x23, "PgUp": 0x21, "PgDn": 0x22,
    "↑": 0x26, "↓": 0x28, "←": 0x25, "→": 0x27,
    "PrintScreen": 0x2C, "Pause": 0x13,
}

DIALOG_QSS = """
QDialog, QWidget {
    background-color: #121218;
    color: #e0e0e0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}
QListWidget {
    background-color: #0d0d14;
    border: 1px solid #333344;
    border-radius: 6px;
    padding: 4px;
    outline: none;
}
QListWidget::item {
    padding: 8px 12px;
    border-radius: 4px;
}
QListWidget::item:selected {
    background-color: #a78bfa;
    color: #050508;
}
QListWidget::item:hover:!selected {
    background-color: #1e1e2e;
}
QLineEdit {
    background-color: #0d0d14;
    border: 1px solid #333344;
    border-radius: 4px;
    padding: 6px 10px;
    color: #e0e0e0;
    font-size: 10pt;
}
QLineEdit:focus {
    border-color: #a78bfa;
}
QComboBox {
    background-color: #0d0d14;
    border: 1px solid #333344;
    border-radius: 4px;
    padding: 5px 8px;
    color: #e0e0e0;
}
QComboBox:hover { border-color: #a78bfa; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox::down-arrow {
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #a78bfa;
    margin-right: 8px;
}
QPushButton {
    background-color: #2a2a3a;
    border: 1px solid #444455;
    border-radius: 5px;
    padding: 7px 16px;
    color: #fff;
    font-weight: bold;
    min-width: 70px;
}
QPushButton:hover {
    background-color: #a78bfa;
    color: #050508;
    border-color: #a78bfa;
}
QPushButton:pressed { background-color: #8b5cf6; }
QPushButton#primaryBtn {
    background-color: #a78bfa;
    color: #050508;
    border-color: #a78bfa;
}
QPushButton#primaryBtn:hover { background-color: #8b5cf6; }
QPushButton#dangerBtn {
    background-color: transparent;
    border-color: #ef4444;
    color: #ef4444;
}
QPushButton#dangerBtn:hover {
    background-color: #ef4444;
    color: #fff;
}
QCheckBox { spacing: 8px; }
QCheckBox::indicator {
    width: 16px; height: 16px;
    border-radius: 4px;
    border: 2px solid #444455;
    background-color: #0d0d14;
}
QCheckBox::indicator:checked {
    background-color: #a78bfa;
    border-color: #a78bfa;
}
QLabel#sectionLabel {
    color: #a78bfa;
    font-weight: bold;
    font-size: 9pt;
    text-transform: uppercase;
    letter-spacing: 1px;
}
QFrame#divider {
    background-color: #333344;
    max-height: 1px;
}
"""


class ActionBuilderDialog(QDialog):
    def __init__(self, parent=None, lang="en"):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(t("ab_title", lang))
        self.setMinimumSize(680, 460)
        self.setStyleSheet(DIALOG_QSS)
        self.custom_actions = load_custom_actions()
        self.current_name = None

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ---- Left sidebar: list of actions ----
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: #0d0d14; border-right: 1px solid #1e1e2e;")
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(12, 16, 12, 12)
        sb_layout.setSpacing(8)

        lbl_list = QLabel(t("ab_your_actions", lang))
        lbl_list.setObjectName("sectionLabel")
        sb_layout.addWidget(lbl_list)

        self.list_widget = QListWidget()
        self.list_widget.currentItemChanged.connect(self.on_item_selected)
        sb_layout.addWidget(self.list_widget)

        btn_row = QHBoxLayout()
        btn_add = QPushButton(t("ab_add", lang))
        btn_add.clicked.connect(self.add_new_action)
        self.btn_delete = QPushButton(t("ab_delete", lang))
        self.btn_delete.setObjectName("dangerBtn")
        self.btn_delete.clicked.connect(self.delete_action)
        btn_row.addWidget(btn_add)
        btn_row.addWidget(self.btn_delete)
        sb_layout.addLayout(btn_row)

        root.addWidget(sidebar)

        # ---- Right panel: editor ----
        # ---- Right panel: stacked (placeholder vs editor) ----
        self.right_stack = QStackedWidget()

        # Page 0: placeholder
        placeholder_page = QWidget()
        ph_layout = QVBoxLayout(placeholder_page)
        ph_layout.setAlignment(Qt.AlignCenter)
        ph_lbl = QLabel(t("ab_placeholder", lang))
        ph_lbl.setAlignment(Qt.AlignCenter)
        ph_lbl.setWordWrap(True)
        ph_lbl.setStyleSheet("color: #555577; font-size: 10pt; padding: 40px;")
        ph_layout.addWidget(ph_lbl)
        self.right_stack.addWidget(placeholder_page)

        # Page 1: editor
        self.editor_panel = QWidget()
        ep_layout = QVBoxLayout(self.editor_panel)
        ep_layout.setContentsMargins(24, 20, 24, 20)
        ep_layout.setSpacing(14)

        # Name field
        name_row = QHBoxLayout()
        name_row.addWidget(QLabel(t("ab_name", lang)))
        self.edit_name = QLineEdit()
        self.edit_name.setPlaceholderText("e.g. Open Spotify")
        name_row.addWidget(self.edit_name)
        ep_layout.addLayout(name_row)

        # Type selector
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel(t("ab_type", lang)))
        self.combo_type = QComboBox()
        self.combo_type.addItem(t("ab_type_launch", lang), "launch")
        self.combo_type.addItem(t("ab_type_url", lang), "url")
        self.combo_type.addItem(t("ab_type_hotkey", lang), "hotkey")
        self.combo_type.currentIndexChanged.connect(self._update_type_panel)
        type_row.addWidget(self.combo_type)
        ep_layout.addLayout(type_row)

        divider = QFrame()
        divider.setObjectName("divider")
        ep_layout.addWidget(divider)

        # Stacked pages per type
        self.type_stack = QStackedWidget()

        # Page 0: Launch
        launch_page = QWidget()
        ll = QVBoxLayout(launch_page)
        ll.setContentsMargins(0, 0, 0, 0)
        path_row = QHBoxLayout()
        path_row.addWidget(QLabel(t("ab_path", lang)))
        self.edit_path = QLineEdit()
        self.edit_path.setPlaceholderText("C:\\Program Files\\App\\app.exe")
        btn_browse = QPushButton(t("ab_browse", lang))
        btn_browse.clicked.connect(self.browse_path)
        path_row.addWidget(self.edit_path)
        path_row.addWidget(btn_browse)
        ll.addLayout(path_row)
        ll.addStretch()
        self.type_stack.addWidget(launch_page)

        # Page 1: URL
        url_page = QWidget()
        ul = QVBoxLayout(url_page)
        ul.setContentsMargins(0, 0, 0, 0)
        url_row = QHBoxLayout()
        url_row.addWidget(QLabel(t("ab_url", lang)))
        self.edit_url = QLineEdit()
        self.edit_url.setPlaceholderText("https://example.com")
        url_row.addWidget(self.edit_url)
        ul.addLayout(url_row)
        ul.addStretch()
        self.type_stack.addWidget(url_page)

        # Page 2: Hotkey
        hk_page = QWidget()
        hkl = QVBoxLayout(hk_page)
        hkl.setContentsMargins(0, 0, 0, 0)

        mod_lbl = QLabel(t("ab_modifiers", lang))
        hkl.addWidget(mod_lbl)
        mod_row = QHBoxLayout()
        self.chk_win = QCheckBox("Win")
        self.chk_ctrl = QCheckBox("Ctrl")
        self.chk_shift = QCheckBox("Shift")
        self.chk_alt = QCheckBox("Alt")
        for c in [self.chk_win, self.chk_ctrl, self.chk_shift, self.chk_alt]:
            mod_row.addWidget(c)
        mod_row.addStretch()
        hkl.addLayout(mod_row)

        key_row = QHBoxLayout()
        key_row.addWidget(QLabel(t("ab_key", lang)))
        self.combo_key = QComboBox()
        for k in KEY_MAP.keys():
            self.combo_key.addItem(k, KEY_MAP[k])
        self.combo_key.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        key_row.addWidget(self.combo_key)
        hkl.addLayout(key_row)
        hkl.addStretch()
        self.type_stack.addWidget(hk_page)

        ep_layout.addWidget(self.type_stack)
        ep_layout.addStretch()

        # Save button
        save_row = QHBoxLayout()
        save_row.addStretch()
        btn_save = QPushButton(t("ab_save", lang))
        btn_save.setObjectName("primaryBtn")
        btn_save.clicked.connect(self.save_current)
        btn_done = QPushButton(t("ab_done", lang))
        btn_done.clicked.connect(self.accept)
        save_row.addWidget(btn_save)
        save_row.addWidget(btn_done)
        ep_layout.addLayout(save_row)

        self.right_stack.addWidget(self.editor_panel)
        root.addWidget(self.right_stack)

        self._populate_list()
        self._update_type_panel(0)
        # Start on placeholder (page 0)
        self.right_stack.setCurrentIndex(0)


    def _populate_list(self):
        self.list_widget.clear()
        for name in sorted(self.custom_actions.keys()):
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, name)
            self.list_widget.addItem(item)

    def _update_type_panel(self, idx):
        self.type_stack.setCurrentIndex(idx)

    def on_item_selected(self, current, previous):
        if not current:
            self.right_stack.setCurrentIndex(0)
            return
        self.right_stack.setCurrentIndex(1)
        name = current.data(Qt.UserRole)
        self.current_name = name
        data = self.custom_actions.get(name, {})
        self.edit_name.setText(name)
        action_type = data.get("type", "launch")
        type_idx = {"launch": 0, "url": 1, "hotkey": 2}.get(action_type, 0)
        self.combo_type.setCurrentIndex(type_idx)

        if action_type == "launch":
            self.edit_path.setText(data.get("path", ""))
        elif action_type == "url":
            self.edit_url.setText(data.get("url", ""))
        elif action_type == "hotkey":
            mods = data.get("modifiers", [])
            self.chk_win.setChecked("win" in mods)
            self.chk_ctrl.setChecked("ctrl" in mods)
            self.chk_shift.setChecked("shift" in mods)
            self.chk_alt.setChecked("alt" in mods)
            key_vk = data.get("key_vk", 0)
            for i in range(self.combo_key.count()):
                if self.combo_key.itemData(i) == key_vk:
                    self.combo_key.setCurrentIndex(i)
                    break

    def add_new_action(self):
        base = "New Action"
        name = base
        counter = 1
        while name in self.custom_actions:
            name = f"{base} {counter}"
            counter += 1
        self.custom_actions[name] = {"type": "launch", "path": ""}
        save_custom_actions(self.custom_actions)
        self._populate_list()
        # Select the new item
        for i in range(self.list_widget.count()):
            if self.list_widget.item(i).data(Qt.UserRole) == name:
                self.list_widget.setCurrentRow(i)
                break

    def delete_action(self):
        item = self.list_widget.currentItem()
        if not item:
            return
        name = item.data(Qt.UserRole)
        if name in self.custom_actions:
            del self.custom_actions[name]
            save_custom_actions(self.custom_actions)
            self._populate_list()
            self.right_stack.setCurrentIndex(0)
            self.current_name = None

    def browse_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Application", "", "Executables (*.exe);;All Files (*)")
        if path:
            self.edit_path.setText(path)

    def save_current(self):
        if not self.current_name and not self.edit_name.text().strip():
            return
        new_name = self.edit_name.text().strip() or self.current_name
        action_type = self.combo_type.currentData()

        data = {"type": action_type}
        if action_type == "launch":
            data["path"] = self.edit_path.text().strip()
        elif action_type == "url":
            data["url"] = self.edit_url.text().strip()
        elif action_type == "hotkey":
            mods = []
            if self.chk_win.isChecked(): mods.append("win")
            if self.chk_ctrl.isChecked(): mods.append("ctrl")
            if self.chk_shift.isChecked(): mods.append("shift")
            if self.chk_alt.isChecked(): mods.append("alt")
            data["modifiers"] = mods
            data["key_vk"] = self.combo_key.currentData()

        # Rename if needed
        if self.current_name and self.current_name != new_name:
            del self.custom_actions[self.current_name]
        self.custom_actions[new_name] = data
        self.current_name = new_name
        save_custom_actions(self.custom_actions)
        self._populate_list()
        # Re-select
        for i in range(self.list_widget.count()):
            if self.list_widget.item(i).data(Qt.UserRole) == new_name:
                self.list_widget.setCurrentRow(i)
                break
