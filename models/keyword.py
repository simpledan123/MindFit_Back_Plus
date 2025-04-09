from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from db.database import Base

menu_keywords = Table(
    "menu_keywords",
    Base.metadata,
    Column("menu_id", Integer, ForeignKey("menus.id"), primary_key=True),
    Column("keyword_id", Integer, ForeignKey("keywords.id"), primary_key=True)
)

class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, nullable=False, unique=True)
