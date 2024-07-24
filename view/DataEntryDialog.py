from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QDialog, QLineEdit, QFormLayout

from database.models import *


class DataEntryDialog(QDialog):
    def __init__(self, tablename, parent=None):
        super(DataEntryDialog, self).__init__(parent)
        self.setWindowTitle(f"Edit {tablename}")

        self.layout = QVBoxLayout()

        self.form_layout = QFormLayout()
        self.inputs = {}
        self.datatype = tablename_datatype[tablename]
        for filed in fields(self.datatype):
            line_edit = QLineEdit(self)
            line_edit.setPlaceholderText(filed.name)
            self.layout.addWidget(line_edit)
            self.inputs[filed.name] = line_edit

        self.layout.addLayout(self.form_layout)

        self.button_box = QHBoxLayout()
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self.confirm)
        self.button_box.addWidget(self.confirm_button)
        self.layout.addLayout(self.button_box)

        self.setLayout(self.layout)
        self.data = None

    def confirm(self):
        data = {}
        for field in fields(self.datatype):
            value = self.inputs[field.name].text()
            if field.type == int or field.type == Optional[int]:
                value = int(value) if value else 0
            elif field.type == str or field.type == Optional[str]:
                value = value if value else ''
            elif field.type == Optional[datetime]:
                value = datetime.fromisoformat(value) if value else None
            data[field.name] = value
        self.data = data
        self.accept()

    def get_data(self):
        return self.data
