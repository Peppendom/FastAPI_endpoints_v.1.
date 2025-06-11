# Standard libraries
from typing import Optional

# Third-party libraries
from pydantic import EmailStr
from sqlalchemy.orm import Session

# Modules
from app.db import models


class UserRepository:
    """
    Repository for user-related database operations.

    - fetches user by id;
    - fetches user by email;
    - creates a new user.
    """
    def __init__(self, db: Session):
        """
        Initializes with a database session.
        """
        self.db = db

    def get_by_id(self, user_id: str) -> Optional[models.User]:
        """
        Fetches the first user matching the given id.
        """
        return self.db.query(models.User).filter(models.User.id == user_id).first()

    def get_by_email(self, email: EmailStr) -> Optional[models.User]:
        """
        Fetches the first user mathing the given email.
        """
        return self.db.query(models.User).filter(models.User.email == email).first()

    def create(self, email: EmailStr, password: str) -> models.User:
        """
        Creates and returns a new user with the provided email and password.
        """
        user = models.User(email = email, password = password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user


class PostRepository:
    """
    Repository for post-related database operations.

    - creates new posts;
    - fetches posts by user or ID;
    - deletes posts.
    """
    def __init__(self, db: Session):
        """
        Initializes with a database session.
        """
        self.db = db

    def create(self, user_id: str, text: str) -> models.Post:
        """
        Creates a new post.

        - saves and returns a Post object with the given user_id and text.
        """
        post = models.Post(user_id = user_id, text = text)
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def get_list_by_user(self, user_id: str) -> Optional[list[models.Post]]:
        """
        Fetches all posts for a given user_id.
        """
        return self.db.query(models.Post).filter(models.Post.user_id == user_id).all()

    def get_by_id(self, post_id: str) -> Optional[models.Post]:
        """
        Fetches a post by its ID.

        - returns Post object if found, else None.
        """
        return self.db.query(models.Post).filter(models.Post.id == post_id).first()

    def delete(self, post_id: str) -> bool:
        """
        Deletes a post by its ID.

        - returns True if the post was deleted;
        - returns False if no mathcing post was found.
        """
        post = self.get_by_id(post_id = post_id)
        if not post:
            return False
        self.db.delete(post)
        self.db.commit()
        return True
