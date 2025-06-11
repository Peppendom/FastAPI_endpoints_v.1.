# Standatd libraries
import uuid

# Third-party libraries
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.mysql import VARCHAR, CHAR, TEXT
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class User(Base):
    """Represents a user with unique email and hashed password."""
    __tablename__ = "users"
    id = Column(CHAR(36), primary_key = True, default = lambda: str(uuid.uuid4()))
    email = Column(VARCHAR(255), unique = True, nullable = False)
    password = Column(String(255), nullable = False)


class Post(Base):
    """Represents a post with textual content. Post is linked to a user."""
    __tablename__ = "posts"
    id = Column(CHAR(36), primary_key = True, default = lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable = False)
    text = Column(TEXT, nullable = False)
