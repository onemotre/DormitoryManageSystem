from dataclasses import asdict, fields
from typing import List, Any

import models
from database.queries import CRUD
from database.models import *
from utils.logs import Data_Logger_history as Logger
from utils.errors import *


def check_tablename(name: str) -> bool:
    if name not in models.tablename_datatype.keys():
        return False
    return True


class Controller:
    def __init__(self, tablename: str):
        self.tablename = tablename
        self.status = False
        self.data_fields = None
        if not check_tablename(self.tablename):
            self.status = False
            raise TableNameError(KeyError(), self.tablename, Logger)
        else:
            self.status = True
        self.crud = CRUD()
        self.data_info = self.read_data_info()
        self.added_instance = []

    def generate_id(self, table_name: str) -> int:
        first_id = models.first_table_dict[table_name]
        size = self.crud.read_info(table_name)
        return first_id + size

    def add_instance(self, data: Dict[str, Any]) -> None:
        if not hasattr(data, '__dataclass_fields__'):
            raise TableKeyError(ValueError(), self.tablename, Logger)
        if self.status is not True:
            raise TableNameError(KeyError(), self.tablename, Logger)
        if 'id' in data.__dataclass_fields__:
            data.id = self.generate_id(self.tablename)
        self.crud.create(self.tablename, asdict(data))
        self.added_instance.append(data)
        Logger.info(f"{__name__} | {self.tablename} Add: [id: {data.id} number：{data.room_number}]")

    def delete_instance(self, fileter: dict):
        if self.status is not True:
            raise TableNameError(KeyError(), self.tablename, Logger)
        for key in fileter.keys():
            if key not in tablename_datatype[self.tablename].__dataclass_fields__:
                raise TableKeyError(KeyError(), key, Logger)
        self.crud.delete(self.tablename, fileter)
        Logger.info(f"{__name__} | {self.tablename} Remove: [{fileter.keys()} : {fileter.values()}]")

    def search_instance(self, fileter: dict):
        if self.status is not True:
            raise TableNameError(KeyError(), self.tablename, Logger)
        for key in fileter.keys():
            if key not in tablename_datatype[self.tablename].__dataclass_fields__:
                raise TableKeyError(KeyError(), key, Logger)
        res = self.crud.read(self.tablename, fileter)
        return res

    def update_instance(self, fileter: dict, data: dict):
        if self.status is not True:
            raise TableNameError(KeyError(), self.tablename, Logger)
        update_info = dict()
        error_keys = []

        for filter_keys in fileter.keys():
            if filter_keys not in models.tablename_datatype[self.tablename].__dataclass_fields__:
                raise TableKeyError(KeyError(), filter_keys, Logger)
            if not self.crud.exists(self.tablename, {filter_keys: fileter[filter_keys]}):
                error_info = str({filter_keys: fileter[filter_keys]}) + " in " + self.tablename + " can not be update"
                raise TableKeyError(KeyError(), error_info, Logger)
        for key in data.keys():
            if key not in models.tablename_datatype[self.tablename].__dataclass_fields__:
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


if __name__ == "__main__":
    test_data = RoomData(room_number="471", capacity=2)
    test_controller = Controller("rooms")
    try:
        # 更改数据测试
        test_controller.update_instance({'id': 10003, 'room_number': '472', 'capacity': 2, 'occupants': 0},
                                        {'capacity': 3})
        print(test_controller.search_instance({'id': 10003}))
    except TableKeyError as e:
        # 异常捕获测试
        print("hello")

    try:
        # 增加数据测试
        test_controller.add_instance({'room_number': '472', 'capacity': 10, 'occupants': 5})
    except (TableKeyError, TableNameError) as e:
        print("add data error: details in Data_Logger.log")

    try:
        # 删除数据测试
        test_controller.delete_instance({'capacity': 3})
    except (TableKeyError, TableNameError) as e:
        print("delete data error: details in Data_Logger.log")

    try:
        # 查询数据测试
        res = test_controller.search_instance({"room_number": "*"})
        print(res)
    except (TableKeyError, TableNameError) as e:
        print("no data")
