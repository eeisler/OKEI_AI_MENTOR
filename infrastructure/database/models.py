from datetime import datetime
from sqlalchemy import BigInteger, Text, ForeignKey, String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from infrastructure.database.connection import Base 

class DepartmentModel(Base):
    __tablename__ = 'departments'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True)
    
    specialties: Mapped[list["SpecialtyModel"]] = relationship(back_populates="department")


class SpecialtyModel(Base):
    __tablename__ = 'specialties'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[str] = mapped_column(Text)
    short_name: Mapped[str] = mapped_column(Text, unique=True)
    full_name: Mapped[str] = mapped_column(Text, unique=True)
    department_id: Mapped[int] = mapped_column(ForeignKey('departments.id'))

    department: Mapped['DepartmentModel'] = relationship(back_populates='specialties') 
    groups: Mapped[list["GroupModel"]] = relationship(back_populates="specialty")
    skill: Mapped[list['SkillMatrixModel']] = relationship(back_populates='specialty')


class GroupModel(Base):
    __tablename__ = 'groups'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    year: Mapped[int] = mapped_column(BigInteger)
    specialty_id: Mapped[int] = mapped_column(ForeignKey('specialties.id'))
    group_number: Mapped[int] = mapped_column(BigInteger)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True) 

    specialty: Mapped['SpecialtyModel'] = relationship(back_populates='groups') 
    users: Mapped[list["UserModel"]] = relationship(back_populates='group')


class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(Text, unique=True)
    hashed_password: Mapped[str] = mapped_column(Text)
    first_name: Mapped[str] = mapped_column(Text)
    middle_name: Mapped[str] = mapped_column(Text) 
    last_name: Mapped[str | None] = mapped_column(Text)
    role: Mapped[str | None] = mapped_column(Text, default="student")
    group_id: Mapped[int | None] = mapped_column(ForeignKey('groups.id'))

    group: Mapped["GroupModel"] = relationship("GroupModel", back_populates='users')
    dialog: Mapped[list["DialogModel"]] = relationship("DialogModel", back_populates='user')
    student_progress: Mapped[list['StudentProgressModel']] = relationship('StudentProgressModel', back_populates='student')


class DialogModel(Base):
    __tablename__ = 'dialogs'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user_message: Mapped[str] = mapped_column(Text)
    ai_response: Mapped[str] = mapped_column(Text) 
    question_id: Mapped[int | None] = mapped_column(BigInteger)
    user_message_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    ai_response_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["UserModel"] = relationship("UserModel", back_populates='dialog')


class SkillMatrixModel(Base):
    __tablename__ = 'skills'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    specialty_id: Mapped[int] = mapped_column(ForeignKey('specialties.id'))
    course: Mapped[int] = mapped_column(BigInteger)
    skill: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    criterions: Mapped[str] = mapped_column(Text)

    specialty: Mapped["SpecialtyModel"] = relationship("SpecialtyModel", back_populates='skill')


class StudentProgressModel(Base):
    __tablename__ = 'student_progress' 

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    skill_id: Mapped[int] = mapped_column(ForeignKey('skills.id'))
    level: Mapped[int | None] = mapped_column(BigInteger, default=0)
    weaknesses: Mapped[str | None] = mapped_column(Text)

    student: Mapped["UserModel"] = relationship("UserModel", back_populates='student_progress')
