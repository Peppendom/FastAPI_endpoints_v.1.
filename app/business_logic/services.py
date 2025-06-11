# Standard libraries
from datetime import datetime, timedelta
from typing import Optional

# Third-party libraries
import jwt
from passlib.context import CryptContext
from pydantic import EmailStr
from sqlalchemy.orm import Session

# Modules
from app.config import (
    JWT_KEY as KEY,
    JWT_ALGORITHM as ALGORITHM,
    JWT_TOKEN_INVALIDATION_TIME as INVALIDATION_TIME,
    PASSWORD_HASHING_ALGORITHM as PASS_ALGORITHM
)
from app.db import models, repositories
from app.routing import schemas


class User:
    """
    Service layer for user-related operations.

    - handles user creation;
    - retrieves user based on email;
    - handles credentials verification.
    """
    pwd_context = CryptContext(schemes = [PASS_ALGORITHM], deprecated = "auto")

    def __init__(self, db: Session):
        """
        Initializes UserService with a database session.
        """
        self.repo = repositories.UserRepository(db = db)

    def create_user(self, email: EmailStr, password: str) -> Optional[models.User]:
        """
        Creates a new user.

        - receives email and password;
        - checks if user with provided email exists;
        - if not, hashes password and returns a UserModel object;
        - returns None otherwise.
        """
        if self.repo.get_by_email(email = email):
            return None
        hashed_pass = self.pwd_context.hash(password)
        return self.repo.create(email = email, password = hashed_pass)

    def get_by_email(self, email: EmailStr) -> Optional[models.User]:
        """
        Retrieves a UserModel object by email.
        """
        return self.repo.get_by_email(email)

    def verify_credentials(self, email: EmailStr, password: str) -> bool:
        """
        Checks if the provided credentials are valid.

        - retrieves user by email;
        - compares provided password to the stored hash;
        - returns True if valid, False otherwise.
        """
        user = self.get_by_email(email = email)
        if not user:
            return False
        return self.pwd_context.verify(password, user.password)


class Post:
    """
    Service layer for post-related operations.

    - handles saving new posts;
    - retrieves a post by ID;
    - retrieves all posts for a specific user;
    - deletes a post.
    """
    def __init__(self, db: Session):
        """
        Initializes PostService with a database session.
        """
        self.repo = repositories.PostRepository(db = db)

    def add_post(self, user_id: str, text: str) -> Optional[models.Post]:
        """
        Saves new post.

        - receives user_id and post text;
        - stores them and returns a PostModel object.
        """
        return self.repo.create(user_id = user_id, text = text)

    def get_post(self, post_id: str) -> Optional[models.Post]:
        """
        Retrieves a post by its ID.
        """
        return self.repo.get_by_id(post_id = post_id)

    def get_list_of_posts(self, user_id: str) -> Optional[list[schemas.PostResponse]]:
        """
        Retrieves a list of posts by user ID.

        - fetches all posts by user;
        - maps each to PostResponse (excluding user_id).
        """
        list_of_posts = self.repo.get_list_by_user(user_id=user_id)
        return [schemas.PostResponse(post_id = str(post.id), text = post.text) for post in list_of_posts]

    def delete_post(self, post_id: str) -> bool:
        """
        Deletes a post by its ID.
        """
        return self.repo.delete(post_id = post_id)


class JWT:
    """
    Service layer for authentication handling

    - creates a JWT token;
    - validates a provided token;
    - extracts user_id from a token.
    """
    @staticmethod
    def create_token(data: dict) -> str:
        """
        Creates a JWT token.

        - receives data to encode (currently user_id);
        - adds expiration timestamp based on config value;
        - returns an encoded JWT using the configured key and algorithm.
        """
        data_to_encode = data.copy()
        expire = datetime.now() + timedelta(seconds = INVALIDATION_TIME)
        data_to_encode.update({"exp": expire})
        return jwt.encode(data_to_encode, KEY, algorithm = ALGORITHM)

    @staticmethod
    def _decode_token(token: str) -> Optional[dict]:
        """
        Decodes a JWT token.

        - uses configured key and algorithm;
        - returns the decoded payload if successful;
        - returns None on error.
        """
        try:
            return jwt.decode(token, KEY, algorithms = [ALGORITHM])
        except jwt.PyJWTError:
            return None

    @staticmethod
    def validate_token(token: str) -> bool:
        """
        Validates a JWT token.

        - returns True if the token is successfully decoded;
        - returns False otherwise.
        """
        return JWT._decode_token(token) is not None

    @staticmethod
    def get_user_id(token: str) -> Optional[str]:
        """
        Extracts user_id from a JWT token.

        - decodes the token;
        - returns the value of 'sub' key if it exists;
        - otherwise returns None.
        """
        payload = JWT._decode_token(token)
        if payload and "sub" in payload:
            return payload["sub"]
        return None
