from datetime import datetime
import json
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

engine = create_engine('sqlite:///tickets.db')
connection = engine.connect()


def init_db():
    Model.metadata.create_all(bind=engine)


Model = declarative_base(name='Model')


def conn():
    Session = sessionmaker(bind=engine)
    return Session()


class Ticket(Model):
    __tablename__ = 'tickets'

    id = Column('id', Integer, primary_key=True)
    title = Column('title', String(60))
    author = Column('author', String(15))
    status = Column('status', String(15))
    description = Column('description', String(120))
    date_created = Column('date_created', DateTime, default=datetime.utcnow)

    # Object -> Json
    def to_json(self):
        ticket_json = {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "status": self.status,
            "description": self.description,
            "date_created": self.date_created.strftime("%Y-%m-%d")
        }
        return ticket_json

    # Json -> Object
    @staticmethod
    def from_json(ticket_json):
        id = ticket_json.get("id")
        title = ticket_json.get("title")
        author = ticket_json.get("author")
        status = ticket_json.get("status")
        description = ticket_json.get("description")
        return Ticket(
            id=id,
            title=title,
            author=author,
            status=status,
            description=description,
        )

    def __repr__(self):
        return f"<Ticket(title={self.title}, author={self.author}, status={self.status}, description={self.description}, date_created={self.date_created})>"
