from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from ..database import Model


class Ticket(Model):
    __tablename__ = 'tickets'

    id = Column('id', Integer, primary_key=True)
    title = Column('title', String(60))
    author = Column('author', String(60))
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
        _id = ticket_json.get("id")
        title = ticket_json.get("title")
        author = ticket_json.get("author")
        status = ticket_json.get("status")
        description = ticket_json.get("description")
        return Ticket(
            id=_id,
            title=title,
            author=author,
            status=status,
            description=description,
        )

    def __repr__(self):
        return f"<Ticket(title={self.title}, author={self.author}, status={self.status}, description={self.description}, date_created={self.date_created})>"
