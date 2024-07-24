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