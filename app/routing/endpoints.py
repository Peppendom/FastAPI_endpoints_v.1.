# Third-party libraries
from cachetools import TTLCache
from cachetools.keys import hashkey
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Modules
from app.business_logic import services
from app.config import (
    CACHE_ITEM_LIMIT as ITEM_LIMIT,
    CACHE_TIME_TO_LIVE as TTL
)
from app.db import setup
from app.routing import schemas, dependencies

router = APIRouter()
cache = TTLCache(maxsize = ITEM_LIMIT, ttl = TTL)


@router.post(
    path = "/signup",
    status_code = status.HTTP_201_CREATED,
    response_model = schemas.SignUpResponse
)
def sign_up(request: schemas.SignUpRequest, db: Session = Depends(setup.get_db)):
    """
    Handles user registration.

    - creates a new user with the provided email and password;
    - returns a JWT token upon success;
    - raises 400 if the email is already in use;
    - raises 500 on unexpected server error.
    """
    try:
        user_service = services.User(db = db)
        user = user_service.create_user(request.email, request.password)
        if not user:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Email already registered"
            )
        token = services.JWT.create_token({"sub" : str(user.id)})
        return {"access_token" : token}

    except Exception:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error occurred"
        )


@router.post(
    path = "/login",
    status_code = status.HTTP_200_OK,
    response_model = schemas.LoginResponse
)
def login(request: schemas.LoginRequest, db: Session = Depends(setup.get_db)):
    """
    Handles user login.

    - verifies provided credentials;
    - returns a JWT token upon success;
    - raises 401 if validation fails;
    - raises 500 on unexpected server error.
    """
    try:
        user_service = services.User(db = db)
        is_valid = user_service.verify_credentials(
            email = request.email,
            password = request.password
        )
        if not is_valid:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Either email or password are incorrect"
            )
        user = user_service.get_by_email(email = request.email)
        token = services.JWT.create_token({"sub": str(user.id)})
        return {"access_token": token}

    except Exception:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error occurred"
        )


@router.post(
    path = "/add_post",
    status_code = status.HTTP_200_OK,
    response_model = schemas.CreatePostResponse
)
def add_post(
        post: schemas.CreatePostRequest,
        token = Depends(dependencies.validate_token),
        db: Session = Depends(setup.get_db),
        _ = Depends(dependencies.validate_payload_size)
):
    """
    Handles new post creation.

    - validates JWT token in authorization headers, raises 403 if missing, 401 if invalid;
    - validates payload size against configured limit, raises 413 if exceeded;
    - extracts user_id from the provided token;
    - saves the post text linked to user_id in the database;
    - returns the ID of the newly created post;
    - raises 500 on unexpected server error.
    """
    try:
        post_service = services.Post(db = db)
        user_id = services.JWT.get_user_id(token)
        post = post_service.add_post(
            user_id = user_id,
            text = post.text
        )
        cache.clear()
        return { "post_id" : post.id }

    except Exception:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error occurred"
        )


@router.get(
    path = "/get_list_of_posts",
    status_code = status.HTTP_200_OK,
    response_model = schemas.GetListOfPostsResponse
)
def get_list_of_posts(
        token = Depends(dependencies.validate_token),
        db: Session = Depends(setup.get_db)
):
    """
    Handles all user's posts retrieval.

    - validates JWT token in authorization headers, raises 403 if missing, 401 if invalid;
    - extracts user_id from the provided token;
    - checks if response is stored in cache, returns it if it is;
    - collects and returns a list of posts for the user_id;
    - each post is a dictionary with 'post_id' and 'text' fields;
    - caches response;
    - raises 500 on unexpected server error.
    """
    try:
        user_id = services.JWT.get_user_id(token)
        key = hashkey(user_id)
        if key in cache:
            return cache[key]

        post_service = services.Post(db = db)
        list_of_posts = post_service.get_list_of_posts(user_id = user_id)
        response = { "list_of_posts" : list_of_posts }
        cache[key] = response
        return response

    except Exception:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error occurred"
        )


@router.post(
    path = "/delete_post",
    status_code = status.HTTP_200_OK,
    response_model = schemas.DeletePostResponse
)
def delete_post(
        post: schemas.DeletePostRequest,
        _ = Depends(dependencies.validate_token),
        db: Session = Depends(setup.get_db)
):
    """
    Handles post deletion.

    - validates JWT token in authorization headers, raises 403 if missing, 401 if invalid;
    - removes a post by the provided post_id, returns a success message;
    - raises 404 if no post matches the provided ID;
    - raises 500 on unexpected server error.
    """
    try:
        post_service = services.Post(db = db)
        result = post_service.delete_post(post_id = post.id)
        if not result:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"No post matching ID {post.id} was found."
            )
        cache.clear()
        return {"success": f"post {post.id} was deleted."}

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )
