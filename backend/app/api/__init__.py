from fastapi import APIRouter
from app.api import users, elements

router = APIRouter()
router.include_router(users.router)
router.include_router(elements.router)
