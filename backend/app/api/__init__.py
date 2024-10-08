from fastapi import APIRouter
from app.api import users, images

router = APIRouter()
router.include_router(users.router)
router.include_router(images.router)
