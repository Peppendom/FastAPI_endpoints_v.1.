from pydantic import BaseModel, EmailStr


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str


class SignUpResponse(BaseModel):
    access_token: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str


class CreatePostRequest(BaseModel):
    text: str


class CreatePostResponse(BaseModel):
    post_id: str


class PostResponse(BaseModel):
    post_id: str
    text: str


class GetListOfPostsResponse(BaseModel):
    list_of_posts: list[PostResponse]


class DeletePostRequest(BaseModel):
    id: str


class DeletePostResponse(BaseModel):
    success: str
