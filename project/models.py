from sqlalchemy import Column, Integer, String, MetaData, Text

from project.database import Base, engine


meta = MetaData()


class Task(Base):
    __tablename__ = "tasks"
    metadata = meta

    id = Column(Integer, primary_key=True)
    email = Column(String(length=1024), unique=True, nullable=False)
    username = Column(String(length=1024), nullable=False)
    text = Column(Text, nullable=False)
    status = Column(Integer)


meta.create_all(engine)
