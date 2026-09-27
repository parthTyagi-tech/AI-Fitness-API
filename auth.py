import logging
from fastapi import Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from db_models import User, AnonymousUser
from templates import flash

logger = logging.getLogger("ai_fitness")


class NotAuthenticatedException(Exception):
    pass


def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        user = AnonymousUser()
        request.state.user = user
        return user
    try:
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            user = AnonymousUser()
    except Exception:
        user = AnonymousUser()
    request.state.user = user
    return user


def login_required(request: Request, current_user = Depends(get_current_user)):
    if not current_user.is_authenticated:
        raise NotAuthenticatedException()
    return current_user


def verify_csrf(request: Request, form: dict):
    expected = request.session.get("_csrf_token")
    received = form.get("csrf_token")
    if not expected or not received or received != expected:
        logger.warning("CSRF validation failed for path %s", request.url.path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSRF token missing or invalid."
        )
