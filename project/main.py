from enum import Enum
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, APIRouter, Request
from pydantic import ValidationError, BaseModel
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, JSONResponse
from sqlalchemy.orm import Session
from project.database import engine
from project import models
from project.database import get_db
from project import schemas, crud


class Settings(BaseModel):
    authjwt_secret_key: str = 'y*8qw1#=46i^%v2&a#3%!wg$s+jw@e3@4e%gzou6=qqx-e=2@p'
    authjwt_access_token_expires:int = 3600 * 24
    authjwt_refresh_token_expires: int = 604800


@AuthJWT.load_config
def get_config():
    return Settings()


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": {'status': 'error', 'message': exc.message}}
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=500)

base_prefix = "/test-task-backend/v2"


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


router = APIRouter()


def check_developer(developer: str = None):
    if developer == 'Sam':
        return developer
    raise HTTPException(status_code=400, detail={'status': 'error', 'message': 'Не передано имя разработчика'})


@router.post('/login', status_code=200, dependencies=[Depends(check_developer)])
def login(user: schemas.UserLogIn, authorize: AuthJWT = Depends()):
    try:
        users = crud.get_users()
    except Exception:
        raise HTTPException(status_code=404)
    ret = None
    for item in users:
        if item.get('username') == user.username and item.get('password') == user.password:
            ret = {
                'username': item.get('username'),
                'access_token': authorize.create_access_token(subject=item.get('id')),
            }
    if ret is None:
        raise HTTPException(status_code=401, detail={'status': 'error', 'message': 'Bad username or password'})
    return schemas.ActionResponse(status='ok', message=ret)


class SortFieldTasks(str, Enum):
    id = "id"
    username = "username"
    email = "email"
    status = "status"


class SortDirection(str, Enum):
    asc = "asc"
    desc = "desc"


@router.get(base_prefix + "/", response_model=schemas.ActionResponse, dependencies=[Depends(check_developer)])
def task_list(
        sort_filed: SortFieldTasks,
        sort_direction: SortDirection,
        page: int = 1,
        db: Session = Depends(get_db)
):

    db_task = crud.get_task(db, sort_filed=sort_filed, sort_direction=sort_direction, page=page)
    count_task = crud.get_count_task(db)
    msg = schemas.TaskList(tasks=db_task, total_task_count=count_task)
    return {'status': 'ok', 'message': msg}


@router.post(base_prefix + "/create/", response_model=schemas.Task, dependencies=[Depends(check_developer)])
def create_tasks(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    new_task = crud.create_task(db=db, task=task)
    return new_task


@router.post(base_prefix + "/edit/{id}/", response_model=schemas.Task, dependencies=[Depends(check_developer)])
def edit_task(id: int, task: schemas.TaskEdit, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    edit = crud.update_task(db=db, id=id, task=task)
    return edit


@router.get("/")
def read_root():
    return {"App": "Test-Task-Backend"}


app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
