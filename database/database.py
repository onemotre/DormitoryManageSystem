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
    init_database()
