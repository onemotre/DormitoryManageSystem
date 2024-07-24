import os.path
from dataclasses import asdict, fields, is_dataclass
from typing import List, Any, Type

import models
from database.queries import CRUD
from database.models import *
from utils.logs import Data_Logger_history as Logger
from utils.errors import *
from config import EXPORT_TYPE, EXPORT_DIR_NAME


def check_tablename(tablename: str):
    if tablename not in tables_list:
        return False
    return True


class Controller:
    def __init__(self, tablename: str):
        self.crud = CRUD()
        self.tablename = tablename
        self.dataclass_type = None
        self.data_fields = None
        self.status = False
        self.check_status()

        self.data_info = self.read_data_info()
        self.added_instance = []

    def check_status(self) -> bool:
        try:
            if not check_tablename(self.tablename):
                self.status = False
                raise TableNameError(ValueError(), f"{self.tablename}", Logger)
            self.dataclass_type = tablename_datatype.get(self.tablename)
            if self.dataclass_type is None:
                self.status = False
                raise TableNameError(KeyError(), f"{self.tablename}", Logger)
            if not hasattr(self.dataclass_type, '__dataclass_fields__'):
                self.status = False
                raise TableValueError(ValueError(), f"wrong dataclass type", Logger)
            self.data_fields = [field.name for field in fields(self.dataclass_type)]
            self.status = True
        except (TableNameError, TableValueError) as e:
            Logger.error(f"access {self.tablename} error: {e}")
            return False
        return True

    def change_tablename(self, tablename: str):
        old_tablename = self.tablename
        self.tablename = tablename
        try:
            if self.check_status():
                raise TableNameError(ValueError(), f"{tablename}", Logger)
        except TableNameError as e:
            Logger.warning(f"change tablename {old_tablename} error: {e}")

    def generate_id(self, table_name: str) -> int:
        first_id = models.first_table_dict[table_name]
        size = self.crud.read_info(table_name)
        return first_id + size

    def clean_data(self, data: Any):
        """
        Clean the data before inserting it into the database.
        """
        if not is_dataclass(data):
            raise TableKeyError(ValueError(), self.tablename, Logger)

        for field in fields(data):
            value = getattr(data, field.name)
            if field.type == Optional[datetime]:
                if isinstance(value, str) and value:
                    try:
                        setattr(data, field.name, datetime.fromisoformat(value))
                    except ValueError:
                        raise TableValueError(ValueError(), f"Incorrect date format for {field.name}", Logger)
                elif value is None or value == '':
                    setattr(data, field.name, datetime.now())
            elif field.type == int:
                if value == '' or value is None:
                    setattr(data, field.name, 0)
            elif field.type == str:
                if value is None:
                    setattr(data, field.name, '')

    def add_instance(self, data: Any) -> None:
        if self.status is not True:
            raise TableNameError(KeyError(), self.tablename, Logger)
        if 'id' in self.data_fields:
            data.id = self.generate_id(self.tablename)

        # 数据清理
        self.clean_data(data)

        self.crud.create(self.tablename, asdict(data))
        self.added_instance.append(data)
        Logger.info(f"{__name__} | {self.tablename} Add: {data}")

    def delete_instance(self, fileter: dict):
        if self.status is not True:
            raise TableNameError(KeyError(), self.tablename, Logger)
        for key in fileter.keys():
            if key not in self.data_fields:
                raise TableKeyError(KeyError(), key, Logger)
        self.crud.delete(self.tablename, fileter)
        Logger.info(f"{__name__} | {self.tablename} Remove: [{fileter.keys()} : {fileter.values()}]")

    def search_instance(self, fileter: dict):
        if self.status is not True:
            raise TableNameError(KeyError(), self.tablename, Logger)
        for key in fileter.keys():
            if key not in self.data_fields:
                raise TableKeyError(KeyError(), key, Logger)
        res = self.crud.read(self.tablename, fileter)
        return res

    def update_instance(self, fileter: dict, data: dict):
        if self.status is not True:
            raise TableNameError(KeyError(), self.tablename, Logger)
        update_info = dict()
        error_keys = []

        for filter_keys in fileter.keys():
            if filter_keys not in self.data_fields:
                raise TableKeyError(KeyError(), filter_keys, Logger)
            if not self.crud.exists(self.tablename, {filter_keys: fileter[filter_keys]}):
                error_info = str({filter_keys: fileter[filter_keys]}) + " in " + self.tablename + " can not be update"
                raise TableKeyError(KeyError(), error_info, Logger)
        for key in data.keys():
            if key not in self.data_fields:
                error_keys.append(key)
            else:
                update_info[key] = data[key]

        self.crud.update(self.tablename, fileter, update_info)
        if error_keys is not None and len(error_keys) > 0:
            raise TableKeyError(KeyError(), error_keys, Logger)

    def read_data_info(self):
        if self.status is not True:
            raise TableNameError(KeyError(), self.tablename, Logger)
        room_info = self.crud.read_info(table_name=self.tablename)
        return room_info

    def file_output(self):
        if not os.path.exists(EXPORT_DIR_NAME):
            os.makedirs(EXPORT_DIR_NAME, exist_ok=True)
        if EXPORT_TYPE not in {"csv", "excel", "json", "txt"}:
            raise TableExportError(ValueError(), EXPORT_TYPE, Logger)
        if EXPORT_TYPE == "csv":
            self.crud.export_to_csv(self.tablename)
        elif EXPORT_TYPE == "excel":
            self.crud.export_to_excel(self.tablename)
        elif EXPORT_TYPE == "json":
            self.crud.export_to_json(self.tablename)
        elif EXPORT_TYPE == "txt":
            self.crud.export_to_txt(self.tablename)
        else:
            raise TableExportError(ValueError(), EXPORT_TYPE, Logger)

    def get_data(self):
        data = self.crud.get_all(self.tablename)
        return [row._asdict() for row in data]

    def get_fields(self):
        return self.data_fields


if __name__ == "__main__":
    test_data = RoomData(room_number="471", capacity=2)
    test_students = [
        StudentData(name='students1', room_id=10002, age=18),
        StudentData(name='students2', room_id=10002, age=19),
        StudentData(name='students3', room_id=10002, age=17),
        StudentData(name='students4', room_id=10002, age=16),
        StudentData(name='students5', room_id=10002, age=15),
        StudentData(name='students6', room_id=10002, age=18),
        StudentData(name='students7', room_id=10002, age=20),
    ]
    test_admini = Admin()
    test_controller = Controller("students")
    # try:
    #     # 更改数据测试
    #     test_controller.update_instance({'id': 10003, 'room_number': '472', 'capacity': 2, 'occupants': 0},
    #                                     {'capacity': 3})
    #     print(test_controller.search_instance({'id': 10003}))
    # except TableKeyError as e:
    #     # 异常捕获测试
    #     print("hello")
    #
    try:
        # 增加数据测试
        for item in test_students:
            test_controller.add_instance(item)
    except (TableKeyError, TableNameError) as e:
        print("add data error: details in Data_Logger.log")
    #
    # try:
    #     # 删除数据测试
    #     test_controller.delete_instance({'capacity': 3})
    # except (TableKeyError, TableNameError) as e:
    #     print("delete data error: details in Data_Logger.log")
    #
    # try:
    #     # 查询数据测试
    #     res = test_controller.search_instance({"room_number": "*"})
    #     print(res)
    # except (TableKeyError, TableNameError) as e:
    #     print("no data")
    #
    # try:
    #     # 导出为excel表格
    #     test_controller.file_output()
    # except TableExportError as e:
    #     print("failed to export, details in Data_Logger.log")
    print(test_controller.get_data())
