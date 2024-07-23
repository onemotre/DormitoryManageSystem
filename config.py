import os

# database connection
BASE_DATABASE_URL = "mysql+pymysql://ayachi:11429@localhost:3306"
DATABASE_NAME = "DormitoryManageSystem"
DATABASE_URL = f"{BASE_DATABASE_URL}/{DATABASE_NAME}"

LOG_DIR_NAME = os.path.join(os.path.dirname(__file__), "logs")

# base path file
BASE_PATH = os.path.abspath(os.path.dirname(__file__))

# user configure
EXPORT_DIR_NAME = os.path.join(BASE_PATH, "export")
"""
support type: txt, excel, csv, json
"""
EXPORT_TYPE = "csv"
