from .. import db
from json import loads
from app.models import Base
from sqlalchemy import Column, String, Integer


class Book(Base):

    __tablename__ = "book"
    __searchable__ = ["title", "author", "text"]

    title = Column(String(200), nullable=False, index=True)
    author = Column(String(200), nullable=False, index=True)
    location = Column(Integer, nullable=False, index=True)
    text = Column(String(250), index=True)

    def __repr__(self):
        return f"Title: {self.title}, Author: {self.author}"

    def to_json(self):
        return dict(
            id=self.id,
            date_created=self.date_created,
            date_modified=self.date_modified,
            title=self.title,
            author=self.author,
            locaction=self.location,
            text=self.text
        )

    def from_json(self, book):
        data = loads(book)
        self.title = data["title"]
        self.author = data["author"]
        self.location = data["location"]
        self.text = data["text"]
