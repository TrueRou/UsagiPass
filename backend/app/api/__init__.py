from fastapi import APIRouter
from app.api import users, images, servers

router = APIRouter()
router.include_router(users.router)
router.include_router(images.router)
router.include_router(servers.router)
