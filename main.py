from fastapi import FastAPI, status, HTTPException, Path, Query
from pydantic import BaseModel, Field
from typing import Optional, Annotated
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import os
from fastapi import Depends


import dbsqllite as dbsql


class TodoCreate(BaseModel):
    title: str = Field(
        min_length=6,
        max_length=100,
        description="Название задачи"
    )
    description: Optional[str] = Field(
        min_length=6,
        max_length=100,
        description="Описание поставленной задачи"
    )
    is_completed: bool = Field(
        default=False,
        description="Отметка о выполнении"
    )


class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    is_completed: bool


class UpdateData(BaseModel):
    title: Optional[str] = Field(
        default=None,
        min_length=6,
        max_length=100,
        description="Описание поставленной задачи"
    )
    description: Optional[str] = Field(
        default=None,
        min_length=6,
        max_length=100,
        description="Описание поставленной задачи"
    )
    is_completed: bool = Field(
        default=None,
        description="Отметка о выполнении"
    )


class TodosListResponse(BaseModel):
    todos_list: list[TodoResponse] = []


app = FastAPI()
engine = create_engine(os.environ['DATABASE_URL'], future=True)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()

def sqlalchemymodel_in_basemodel(sqlalchemymodel):
    return TodoResponse(
        id=sqlalchemymodel.id,
        title=sqlalchemymodel.title,
        description=sqlalchemymodel.description,
        is_completed=sqlalchemymodel.is_completed
    )

# Создать задачу
@app.post('/todos', response_model=TodoResponse, status_code=201)
async def add_todo(todo_data: TodoCreate, db: Session = Depends(get_db)) -> TodoResponse:
    dict_todo_data = todo_data.model_dump()
    obj_todo_sqlite = dbsql.add_todo_sqlite(db, dict_todo_data)
    return sqlalchemymodel_in_basemodel(obj_todo_sqlite)


# Получить все задачи
@app.get('/todos', response_model=TodosListResponse, status_code=200)
async def get_all_todo_taking_limit(limit: Annotated[Optional[int], Query()] = None, db: Session = Depends(get_db)) -> TodosListResponse:
    lst_todos = dbsql.get_all_todo_taking_limit_in_db(db, limit)
    todos_response = [sqlalchemymodel_in_basemodel(todo) for todo in lst_todos]
    return TodosListResponse(todos_list=todos_response)


# Получить задачу по id
@app.get('/todos/{id_todo}', response_model=TodoResponse, status_code=200)
async def get_todo_id(id_todo: Annotated[int, Path(..., gt=-1)], db: Session = Depends(get_db)) -> TodoResponse:
    obj_todo_sqlite = dbsql.get_todo_id(db, id_todo)
    if obj_todo_sqlite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Задача с указанным ID не найдена')
    return sqlalchemymodel_in_basemodel(obj_todo_sqlite)


# Изменить задачу целиком
@app.put('/todos/{id_todo}', response_model=TodoResponse, status_code=200)
async def update_whole_id_todo(todo_data: TodoCreate, id_todo: Annotated[int, Path(..., gt=-1)], db: Session = Depends(get_db)) -> TodoResponse:
    dict_todo_data = todo_data.model_dump()
    obj_todo_sqlite = dbsql.update_id_todo_in_db(db, id_todo, dict_todo_data)
    if obj_todo_sqlite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Задача с указанным ID не найдена')
    return sqlalchemymodel_in_basemodel(obj_todo_sqlite)


# Изменить указанные поля задачи
@app.patch('/todos/{id_todo}', response_model=TodoResponse, status_code=200)
async def update_select_field_id_todo(id_todo: Annotated[int, Path(..., gt=-1)], update_date: UpdateData = None, db: Session = Depends(get_db)) -> TodoResponse:
    dict_update_date = update_date.model_dump(exclude_unset=True)
    obj_todo_sqlite = dbsql.update_id_todo_in_db(db, id_todo, dict_update_date)
    if obj_todo_sqlite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Задача с указанным ID не найдена')
    return sqlalchemymodel_in_basemodel(obj_todo_sqlite)


# Удалить задачу по id
@app.delete('/todos/{id_todo}', response_model=TodoResponse, status_code=200)
async def delete_todo_id(id_todo: Annotated[int, Path(..., gt=-1)], db: Session = Depends(get_db)) -> TodoResponse:
    obj_todo_sqlite = dbsql.delete_id_todo_in_db(db, id_todo)
    if obj_todo_sqlite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Задача с указанным ID не найдена')
    return sqlalchemymodel_in_basemodel(obj_todo_sqlite)
