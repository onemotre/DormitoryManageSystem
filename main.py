import sys

from PyQt5.QtWidgets import QApplication

from database.database import init_database
from view.MainWindow import MainWindow


def main():
    # 其他主程序逻辑
    print("/************** Welcome to Dormitory Manage System *****************/")
    init_database()
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
