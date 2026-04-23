from sqlalchemy import create_engine, select, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from config import MysqlSettings, SQLLiteSettings

MYSQL = (
    f"{MysqlSettings.MYSQL}{MysqlSettings.USER}:{MysqlSettings.PASSWORD}"
    f"@{MysqlSettings.HOST}:{MysqlSettings.PORT}/{MysqlSettings.DATABASE}"
)
SQL_LITE = SQLLiteSettings.SQL_LITE


class Base(DeclarativeBase): pass


DATABASE_URL = SQL_LITE
engine = create_engine(DATABASE_URL, echo=True, future=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(6), nullable=False)
    description: Mapped[str] = mapped_column(String(6), nullable=False)
    is_completed: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        return f'Todo(id={self.id}, title={self.title}, description={self.description}, is_completed={self.is_completed})'


def add_todo_sqlite(db, dict_todo_data) -> Todo:
    todo = Todo(**dict_todo_data)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


def get_all_todo_taking_limit_in_db(db, limit: int | None) -> list[Todo]:
    print(12)
    query = select(Todo)
    db.execute(query).scalars().all()
    if limit:
        query = query.limit(limit)
    lst_todo = db.execute(query).scalars().all()
    print(13)
    return lst_todo


def get_todo_id(db, id_todo) -> Todo | None:
    todo = db.get(Todo, id_todo)
    if not todo:
        return None
    return todo


def update_id_todo_in_db(db, id_todo, dict_todo_data) -> Todo | None:
    todo = get_todo_id(db, id_todo)
    if not todo:
        return None
    if dict_todo_data is None:
        return todo
    for col, value in dict_todo_data.items():
        setattr(todo, col, value)
    db.commit()
    db.refresh(todo)
    return todo


def delete_id_todo_in_db(db, id_todo) -> Todo | None:
    todo = get_todo_id(db, id_todo)
    if not todo:
        return None
    todo_to_delete = todo
    db.delete(todo)
    db.commit()
    return todo_to_delete
