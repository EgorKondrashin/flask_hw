from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgresql://postgres:postgres123@127.0.0.1:5431/flask_db')
Session = sessionmaker(bind=engine)
Base = declarative_base(bind=engine)


class User(Base):

    __tablename__ = 'app_users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    creation_time = Column(DateTime, server_default=func.now())
    advertisements = relationship('Advertisements', back_populates='app_user')


class Advertisements(Base):

    __tablename__ = 'advertisements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    creation_time = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey('app_users.id'))
    app_user = relationship('User', back_populates='advertisements')


Base.metadata.create_all()
