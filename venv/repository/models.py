from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String


class Music(declarative_base()):
    __tablename__ = "Music"
    id = Column(String, primary_key=True)
    title = Column(String)
    path = Column(String)

