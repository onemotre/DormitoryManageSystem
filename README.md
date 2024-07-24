# 学生宿舍管理系统实现

## 一、任务目标

实现学生宿舍管理系统，建立数据库，添加相关表格，实现对学生，宿舍，管理员等的管理

### 1.0 项目特点

1. **使用`sqlalchemy`进行数据库的操作**:使代码可与多种 SQL 数据库（PostgreSQL, MySQL, SQLite, Oracle, MS SQL Server）通信，详见[<queries.py>](####queries.py)
2. **数据库自动创建：**database中实现了检查url链接的数据库是否存在，如果不存在会自动创建，详见[<database.py>](####database.py)
3. **使用`errors`进行代码报错管理：**使代码稳定性提高，避免某些特殊错误导致程序退出，同时更方便出问题的时候进行问题定位分析，详见[<logs.py>](####logs.py)
4. **使用`Logs`进行日志记录：**使得代码可溯源，包括随时记录用户对数据库的操作，对报错信息的记录，详见[<日志样例展示>](###日志样例展示)
5. **使用Qt作为项目前端：**使用`Qt5`作为项目前端，使数据可视化更加清晰
6. **使用`git`进行项目管理：**使用`git`作为项目管理工具，可以查询commit

### 1.1 项目环境

- python > 3.8

  ```
  Package           Version
  ----------------- -----------
  cffi              1.16.0
  cryptography      43.0.0
  et-xmlfile        1.1.0
  greenlet          3.0.3
  openpyxl          3.1.5
  pandas            2.2.2
  pip               24.0
  pycparser         2.22
  PyMySQL           1.1.1
  PyQt5             5.15.11
  PyQt5-Qt5         5.15.14
  PyQt5_sip         12.15.0
  python-dateutil   2.9.0.post0
  pytz              2024.1
  setuptools        69.5.1
  six               1.16.0
  SQLAlchemy        2.0.31
  typing_extensions 4.12.2
  tzdata            2024.1
  wheel             0.43.0
  ```
  
- MySQL Server version: 8.0.37-0ubuntu0.22.04.3 (Ubuntu)

- 使用：

  - python环境配置

      ```bash
      pip install -r ./requiremnts.txt
      ```
  - mysql

      运行main.py能会自动运行数据库创建程序，但仍然可以通过一下命令创建数据库
      
      ```bash
      sudo systemctl start mysql
      mysql -u {用户名} -p
      source ./DormitoryManageSystem.sql
      ```


## 二、完成代码

### 2.0 文件目录结构

```bash
./DormitoryManageSystem
├── controller	# 处理数据库相关的逻辑，用于耦合其他组件
│   ├── Controller.py
│   └── __init__.py
├── database	# 数据库的基本操作
│   ├── database.py	# 数据库的初始化等
│   ├── __init__.py
│   ├── models.py	# 定义表的数据类型与信息
│   └── queries.py	# 包含对数据库的增、删、改、查
├── export	# 数据输出目录（另存为）
│   ├── rooms.csv
│   ├── rooms.json
│   └── rooms.xlsx
├── logs	# 日志文件
│   ├── Data_Logger.log	# 数据库操作的日志，包含报错以及对数据库增删改查的记录
│   └── System.log		# 系统操作日志
├── pic		
│   └── database
├── utils	# 小组件
│   ├── errors.py	# Errors处理（日志记录，报错类型定义）
│   ├── __init__.py
│   └── logs.py		# logs处理
├── view	# 前端界面
│   ├── DataEntryDialog.py	# 弹出窗口
│   ├── __init__.py
│   └── MainWindow.py		# 主窗口
├── config.py			# 配置文件
├── main.py				# 主程序入口
├── requirements.txt
├── DormitoryManageSystem.sql
└── README.md
```

### 2.1 config.py 和 main.py

- config.py

  ```python
  import os
  
  # database connection
  BASE_DATABASE_URL = "mysql+pymysql://root:*****@localhost:3306"
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
  ```

- main.py

  ```python
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
  ```
  
  

### 2.2 database/

#### database.py

```python
from sqlalchemy import create_engine, inspect, text, MetaData
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import sessionmaker
from models import Base
from config import BASE_DATABASE_URL, DATABASE_NAME, DATABASE_URL


def get_engine(database_url=None):
    if database_url is None:
        database_url = DATABASE_URL
    return create_engine(database_url)


def init_database():
    try:
        # 尝试连接数据库并检查表
        engine = get_engine()
        connection = engine.connect()
        connection.close()
        check_and_create_tables(engine)
    except (OperationalError, ProgrammingError) as e:
        print(f"Database connection or table check failed: {e}")
        # 如果数据库不存在，创建数据库和表
        create_database()
        engine = get_engine()
        check_and_create_tables(engine)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def create_database():
    try:
        # 连接到默认数据库（不指定具体数据库）
        default_engine = get_engine(BASE_DATABASE_URL)
        default_connection = default_engine.connect()
        default_connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}"))
        default_connection.close()
        print("Database created successfully!")
    except OperationalError as e:
        print(f"Failed to create database: {e}")


def check_and_create_tables(engine):
    inspector = inspect(engine)
    metadata = MetaData()
    metadata.reflect(engine)

    # 手动定义表的创建顺序
    table_creation_order = ['rooms', 'students', 'admins', 'assignments']

    for table_name in table_creation_order:
        model = Base.metadata.tables[table_name]
        if table_name in inspector.get_table_names():
            existing_table = metadata.tables[table_name]
            if not compare_tables(existing_table, model):
                print(f"Table {table_name} structure mismatch, dropping and recreating.")
                drop_and_create_table(engine, model)
            else:
                print(f"Table {table_name} is up to date.")
        else:
            print(f"Table {table_name} is missing, creating.")
            model.create(engine)
            print(f"Created table {table_name}.")


def compare_tables(existing_table, model):
    # 检查列的数量是否一致
    if len(existing_table.columns) != len(model.columns):
        return False

    # 检查列的名称和类型是否一致
    for column in model.columns:
        if column.name not in existing_table.columns:
            return False
        if str(existing_table.columns[column.name].type) != str(column.type):
            return False
    return True


def drop_and_create_table(engine, model):
    model.drop(engine)
    model.create(engine)
    print(f"Recreated table {model.name}.")


# 创建SessionLocal用于数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())

if __name__ == "__main__":
    # 测试用例
    init_database()
```



#### models.py

```python
import dataclasses
from typing import Optional, List, Dict, Any, Type, TypeVar
from datetime import datetime
from dataclasses import dataclass, fields
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()
T = TypeVar('T')

tables_list = ["students", "rooms", "admins", "assignments"]
first_table_dict = {"students": 10000, "rooms": 10000, "admins": 0}


@dataclass
class StudentData:
    name: str
    room_id: int
    id: Optional[int] = None
    age: Optional[int] = 0
    gender: Optional[str] = "none"
    enrollment_date: Optional[datetime] = None


@dataclass
class RoomData:
    room_number: str
    id: Optional[int] = None
    capacity: Optional[int] = 0
    occupants: Optional[int] = 0


@dataclass
class AdminData:
    name: str
    id: Optional[int] = None
    email: Optional[str] = "none"
    password: Optional[str] = ""


@dataclass
class AssignmentData:
    id: Optional[int] = None
    student_id: Optional[int] = None
    room_id: Optional[int] = None
    assigned_date: Optional[datetime] = None


tablename_datatype: Dict[str, Type]= {
    "students": StudentData,
    "rooms": RoomData,
    "admins": AdminData,
    "assignments": AssignmentData
}


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)  # 指定 VARCHAR 长度
    age = Column(Integer)
    gender = Column(String(10))
    room_id = Column(Integer, ForeignKey('rooms.id'))
    enrollment_date = Column(Date)


class Room(Base):
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_number = Column(String(50), nullable=False)  # 指定 VARCHAR 长度
    capacity = Column(Integer)
    occupants = Column(Integer)


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)  # 指定 VARCHAR 长度
    email = Column(String(100), nullable=False)  # 指定 VARCHAR 长度
    password = Column(String(100), nullable=False)  # 指定 VARCHAR 长度


class Assignment(Base):
    __tablename__ = 'assignments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    room_id = Column(Integer, ForeignKey('rooms.id'))
    assigned_date = Column(Date)


def dict2dataclass(data: dict, dataclass_type: Type[Base]):
    fields_info = {field.name: field.type for field in fields(dataclass_type)}
    for key, value in data.items():
        expected_type = fields_info.get(key)
        if expected_type == int or expected_type == Optional[int]:
            data[key] = int(value) if value else 0
        elif expected_type == Optional[str] or expected_type == str:
            data[key] = value if value else ''
        elif expected_type == Optional[datetime]:
            data[key] = datetime.fromisoformat(value) if value else None
    return dataclass_type(**data)
```



#### queries.py

```python
import os.path
import pandas as pd

from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import MetaData, Table, table
from database.database import SessionLocal, get_engine
from sqlalchemy.exc import IntegrityError

from utils.errors import TableOperationError, TableValueError, TableExportError
from utils.logs import Data_Logger_history as Logger
from config import EXPORT_DIR_NAME, EXPORT_TYPE


# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 通用的增删改查函数
class CRUD:
    def __init__(self):
        self.engine = get_engine()
        self.metadata = MetaData()
        self.metadata.reflect(self.engine)

    def create(self, table_name: str, data: dict):
        selected_table = self.metadata.tables.get(table_name)
        if selected_table is None:
            raise TableValueError(ValueError(), f"Table {table_name} does not exist", Logger)

        with self.engine.connect() as conn:
            try:
                insert_stmt = selected_table.insert().values(data)
                conn.execute(insert_stmt)
                conn.commit()
            except IntegrityError as e:
                conn.rollback()
                raise TableOperationError(e, f"Add Item {data}", Logger)

    def read(self, table_name: str, filters: dict = None):
        table = self.metadata.tables.get(table_name)
        if table is None:
            raise TableValueError(ValueError(), f"Table {table_name} does not exist", Logger)

        with self.engine.connect() as conn:
            select_stmt = table.select()
            if filters:
                for key, value in filters.items():
                    select_stmt = select_stmt.where(table.c[key] == value)
            result = conn.execute(select_stmt)
            return result.fetchall()

    def update(self, table_name: str, filters: dict, data: dict):
        table = self.metadata.tables.get(table_name)
        if table is None:
            raise TableValueError(ValueError(), f"Table {table_name} does not exist", Logger)

        with self.engine.connect() as conn:
            update_stmt = table.update()
            for key, value in filters.items():
                update_stmt = update_stmt.where(table.c[key] == value)
            update_stmt = update_stmt.values(data)
            result = conn.execute(update_stmt)
            conn.commit()
            return result.rowcount

    def delete(self, table_name: str, filters: dict):
        table = self.metadata.tables.get(table_name)
        if table is None:
            raise TableValueError(ValueError(), f"Table {table_name} does not exist", Logger)

        with self.engine.connect() as conn:
            delete_stmt = table.delete()
            for key, value in filters.items():
                delete_stmt = delete_stmt.where(table.c[key] == value)
            result = conn.execute(delete_stmt)
            conn.commit()
            return result.rowcount

    def exists(self, table_name: str, filters: Dict[str, Any]) -> bool:
        table = self.metadata.tables.get(table_name)
        if table is None:
            raise TableValueError(ValueError(), f"Table {table_name} does not exist", Logger)

        with self.engine.connect() as conn:
            select_stmt = table.select().limit(1)
            for key, value in filters.items():
                select_stmt = select_stmt.where(table.c[key] == value)
            result = conn.execute(select_stmt)
            return result.fetchone() is not None

    def read_info(self, table_name: str):
        select_dat = self.metadata.tables.get(table_name)
        if select_dat is None:
            raise TableValueError(ValueError(), f"Table {table_name} does not exist", Logger)

        with self.engine.connect() as conn:
            selected_table = select_dat.select()
            result = conn.execute(selected_table)
            count = result.rowcount
            return count

    def export_to_excel(self, tablename: str):
        filename = os.path.join(EXPORT_DIR_NAME, f"{tablename}.xlsx")
        with pd.ExcelWriter(filename) as writer:
            selected_table = self.metadata.tables[tablename]
            query = selected_table.select()
            df = pd.read_sql(query, self.engine)
            df.to_excel(writer, sheet_name=tablename, index=False)
            Logger.info(f"Export to Excel {filename}")

    def export_to_csv(self, tablename: str):
        filename = os.path.join(EXPORT_DIR_NAME, f"{tablename}.csv")
        selected_table = self.metadata.tables[tablename]
        query = selected_table.select()
        df = pd.read_sql(query, self.engine)
        df.to_csv(filename, index=False)
        Logger.info(f"Export to CSV {filename}")

    def export_to_txt(self, tablename: str):
        filename = os.path.join(EXPORT_DIR_NAME, f"{tablename}.txt")
        selected_table = self.metadata.tables[tablename]
        query = selected_table.select()
        df = pd.read_sql(query, self.engine)
        df.to_csv(filename, index=False, sep='\t')
        Logger.info(f"Export to TXT {filename}")

    def export_to_json(self, tablename: str):
        filename = os.path.join(EXPORT_DIR_NAME, f"{tablename}.json")
        selected_table = self.metadata.tables[tablename]
        query = selected_table.select()
        df = pd.read_sql(query, self.engine)
        df.to_json(filename, orient='records')
        Logger.info(f"Export to JSON {filename}")

    def get_all(self, table_name: str):
        if table_name not in self.metadata.tables:
            raise TableValueError(ValueError(), f"Table {table_name} does not exist", Logger)
        session = SessionLocal()
        selected_table = self.metadata.tables.get(table_name)
        try:
            res = session.query(selected_table).all()
            session.commit()
            return res
        except Exception as e:
            session.rollback()
            raise TableOperationError(e, "access data", Logger)
        finally:
            session.close()
```



### 2.3 utils/

#### logs.py

```python
import os
import logging

from config import LOG_DIR_NAME


def set_up_logger(name: str, level: object = logging.ERROR) -> object:
    log_dirname = LOG_DIR_NAME
    if not os.path.exists(log_dirname):
        os.makedirs(log_dirname)
    log_file = os.path.join(log_dirname, f"{name}.log")
    formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level=level)
    logger.addHandler(handler)

    return logger


System_Logger = set_up_logger(name="System", level=logging.ERROR)
Data_Logger_history = set_up_logger(name="Data_Logger", level=logging.INFO)


if __name__ == "__main__":
    set_up_logger("Test_logger")
```

#### erros.py

```python
import logging


class DataBaseError(Exception):
    def __init__(self, e: Exception, logger: logging.Logger):
        super().__init__(e)
        logger.error(f"DataBaseError: failed create database | {e}")


class TableValueError(Exception):
    """
    主要处理数据库中不存在表的错误
    """

    def __init__(self, e: Exception, info: str, logger: logging.Logger):
        super().__init__(e)
        logger.error(info)


class TableExportError(Exception):
    def __init__(self, e: Exception, error_type: str, logger: logging.Logger):
        super().__init__(e)
        logger.error(f"TableExportError: failed export table | {error_type}")


class TableNameError(Exception):
    def __init__(self, e: Exception, name: str, logger: logging.Logger):
        super().__init__(e)
        logger.error(f"TableNameError: failed access table: {name} | {e}")


class TableKeyError(Exception):
    def __init__(self, e: Exception, keyname, logger: logging.Logger):
        super().__init__(e)
        logger.error(f"TableAccessError: no key {keyname}")


class TableOperationError(Exception):
    def __init__(self, e: Exception, operator: str, logger: logging.Logger):
        super().__init__(e)
        logger.error(f"TableOperationError: failed operator {operator} | {e}")
```

### 2.4 view/



## 三、结果截图

### 数据库展示
![database](./pic/database)

### 日志样例展示

![日志样例](./pic/logs.png)



### Qt界面展示
