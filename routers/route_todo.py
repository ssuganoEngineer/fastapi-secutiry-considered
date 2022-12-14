from typing import List

from fastapi import APIRouter
from fastapi import Request, Response, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi_csrf_protect import CsrfProtect
from starlette import status

from auth_utils import AuthJWTCSRF
from schemas import ToDo, ToDoBody, SuccessMsg
from database import db_create_todo, db_get_todos, db_single_todo, db_update_todo, db_delete_todo

router = APIRouter()
auth = AuthJWTCSRF()


@router.post("/api/todo", response_model=ToDo)
async def create_todo(request: Request, response: Response, data: ToDoBody, csrf_protect: CsrfProtect = Depends()):
    new_token = auth.verify_csrf_update_jwt(request, csrf_protect, request.headers)

    todo = jsonable_encoder(data)
    res = await db_create_todo(todo)
    response.status_code = status.HTTP_201_CREATED
    response.set_cookie(
        key="access_token",
        value=f"Bearer {new_token}",
        httponly=True,
        samesite="none",
        secure=True
    )

    if res:
        return res
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Create task failed")


@router.get("/api/todo", response_model=List[ToDo])
async def get_todos(request: Request):
    # auth.verify_jwt(request)
    res = await db_get_todos()
    return res


@router.get("/api/todo/{todo_id}", response_model=ToDo)
async def get_single_todo(request: Request, response: Response, todo_id: str):
    new_token, _ = auth.verify_update_jwt(request)
    res = await db_single_todo(todo_id)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {new_token}",
        httponly=True,
        samesite="none",
        secure=True
    )
    if res:
        return res
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task of ID {todo_id} does not exist")


@router.put("/api/todo/{todo_id}", response_model=ToDo)
async def update_todo(request: Request, response: Response, todo_id: str, data: ToDoBody, csrf_protect: CsrfProtect = Depends()):
    new_token = auth.verify_csrf_update_jwt(request, csrf_protect, request.headers)
    todo = jsonable_encoder(data)
    res = await db_update_todo(todo_id, todo)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {new_token}",
        httponly=True,
        samesite="none",
        secure=True
    )
    if res:
        return res
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Update task failed")


@router.delete("/api/todo/{todo_id}", response_model=SuccessMsg)
async def delete_todo(request: Request, response: Response, todo_id: str, csrf_protect: CsrfProtect = Depends()):
    new_token = auth.verify_csrf_update_jwt(request, csrf_protect, request.headers)
    res = await db_delete_todo(todo_id)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {new_token}",
        httponly=True,
        samesite="none",
        secure=True
    )
    if res:
        return {"message": "Successfully deleted"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delete task failed")