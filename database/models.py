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
