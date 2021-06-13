from project import schemas, models
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc


def get_users():
    return [
        {'id': 1, 'username': 'admin', 'password': 'test'}
    ]


def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(**task.dict(), status=0)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, id: int, task: schemas.TaskEdit):
    db_edit_task = db.query(models.Task).get(id)
    db_edit_task.text = task.text
    db_edit_task.status = task.status
    db.flush()
    db.commit()
    return db_edit_task


def get_task(db: Session, sort_filed, sort_direction, page):
    limit = 3
    skip = page * 3 - 3
    query_obj = db.query(models.Task)
    order_var = {'desc': desc(getattr(models.Task, sort_filed)), 'asc': asc(getattr(models.Task, sort_filed))}
    order_by_query = query_obj.order_by(order_var[sort_direction])
    return order_by_query.offset(skip).limit(limit).all()


def get_count_task(db: Session):
    query_obj = db.query(models.Task).count()
    return query_obj

