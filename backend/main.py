"""Snake API application."""

import logging
import sys
from pathlib import Path
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from backend.config import LOG_LEVEL
from backend.database import get_db
from backend.models import Score, User
from backend.schemas import Credentials, ScoreCreate, ScoreResult
from backend.security import create_access_token, decode_access_token, hash_password, verify_password


logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    stream=sys.stdout,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("snake_api")
app = FastAPI(title="Snake API", version="1.0.0")
bearer_scheme = HTTPBearer(auto_error=False)
FRONTEND_FILE = Path(__file__).resolve().parent.parent / "frontend" / "index.html"


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(FRONTEND_FILE)


@app.get("/health")
def health(db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ok"}
    except SQLAlchemyError:
        logger.exception("Health check: database is unavailable")
        raise HTTPException(status_code=503, detail={"status": "error", "database": "unavailable"})


@app.post("/api/register", status_code=status.HTTP_201_CREATED)
def register(data: Credentials, db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    user = User(username=data.username, password_hash=hash_password(data.password))
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Username already exists")
    logger.info("Registered user id=%s", user.id)
    return {"message": "registered", "username": user.username}


@app.post("/api/login")
def login(data: Credentials, db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    user = db.query(User).filter(User.username == data.username).first()
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    logger.info("User logged in id=%s", user.id)
    return {"access_token": create_access_token(user.id), "token_type": "bearer"}


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Not authenticated", headers={"WWW-Authenticate": "Bearer"})
    try:
        user_id = decode_access_token(credentials.credentials)
    except (jwt.InvalidTokenError, KeyError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found", headers={"WWW-Authenticate": "Bearer"})
    return user


@app.post("/api/scores", status_code=status.HTTP_201_CREATED)
def submit_score(
    data: ScoreCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict[str, int | str]:
    score = Score(user_id=user.id, score=data.score)
    db.add(score)
    db.commit()
    db.refresh(score)
    logger.info("Score submitted user_id=%s score=%s", user.id, score.score)
    return {"message": "score_saved", "score": score.score}


@app.get("/api/scores/top", response_model=list[ScoreResult])
def top_scores(db: Annotated[Session, Depends(get_db)]) -> list[dict[str, object]]:
    rows = (
        db.query(Score, User.username)
        .join(User, User.id == Score.user_id)
        .order_by(Score.score.desc(), Score.created_at.asc())
        .limit(10)
        .all()
    )
    return [
        {"username": username, "score": score.score, "created_at": score.created_at}
        for score, username in rows
    ]
