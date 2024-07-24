import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QVBoxLayout, QWidget, QTableWidget, \
    QTableWidgetItem, QTabWidget, QHBoxLayout

from view.DataEntryDialog import DataEntryDialog
from controller import Controller
from database.models import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Room Management System')
        self.controller = Controller.Controller("students")

        self.tabs = QTabWidget()
        self.table_widgets = {}

        self.initUI()

    def initUI(self):
        self.tabs.currentChanged.connect(self.tab_changed)

        # Initialize tabs
        for tab_name in tables_list:
            tab = QWidget()
            self.init_tab(tab, tab_name)
            self.tabs.addTab(tab, tab_name)

        self.setCentralWidget(self.tabs)

    def init_tab(self, tab, tab_name):
        layout = QVBoxLayout()

        table_widget = QTableWidget()
        self.table_widgets[tab_name] = table_widget
        layout.addWidget(table_widget)

        button_layout = QVBoxLayout()

        add_button = QPushButton('Add Data')
        add_button.clicked.connect(lambda: self.add_data(tab_name))
        button_layout.addWidget(add_button)

        update_button = QPushButton('Update Data')
        update_button.clicked.connect(lambda: self.update_data(tab_name))
        button_layout.addWidget(update_button)

        delete_button = QPushButton('Delete Data')
        delete_button.clicked.connect(lambda: self.delete_data(tab_name))
        button_layout.addWidget(delete_button)

        search_button = QPushButton('Export Data')
        search_button.clicked.connect(lambda: self.export_data(tab_name))
        button_layout.addWidget(search_button)

        hlayout = QHBoxLayout()
        hlayout.addLayout(layout)
        hlayout.addLayout(button_layout)

        tab.setLayout(hlayout)
        self.load_data(tab_name)

    def tab_changed(self):
        tab_name = self.tabs.tabText(self.tabs.currentIndex())
        self.controller.change_tablename(self.tabs.tabText(self.tabs.currentIndex()))
        self.load_data(tab_name)

    def load_data(self, tab_name):
        data = self.controller.get_data()
        table_widget = self.table_widgets[tab_name]
        table_widget.setRowCount(len(data))
        table_widget.setColumnCount(len(data[0]) if data else 0)
        table_widget.setHorizontalHeaderLabels(data[0].keys() if data else [])

        for row_index, row_data in enumerate(data):
            for col_index, (key, value) in enumerate(row_data.items()):
                table_widget.setItem(row_index, col_index, QTableWidgetItem(str(value)))

    def add_data(self, tab_name):
        dialog = DataEntryDialog(tab_name)
        if dialog.exec_():
            data = dialog.get_data()
            dataclass_instance = dict2dataclass(data, tablename_datatype[tab_name])
            self.controller.add_instance(dataclass_instance)
            self.load_data(tab_name)

    def update_data(self, tab_name):
        dialog = DataEntryDialog(tab_name)
        if dialog.exec_():
            data = dialog.get_data()
            dataclass_instance = dict2dataclass(data, tablename_datatype[tab_name])
            self.controller.update_instance(dataclass_instance)
            self.load_data(tab_name)

    def delete_data(self, tab_name):
        dialog = DataEntryDialog(tab_name)
        if dialog.exec_():
            data = dialog.get_data()
            dataclass_instance = dict2dataclass(data, tablename_datatype[tab_name])
            self.controller.delete_instance(dataclass_instance)
            self.load_data(tab_name)

    def export_data(self, tab_name):
        self.controller.file_output()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
