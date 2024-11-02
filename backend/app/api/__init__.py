from fastapi import APIRouter
from app.api import users, images, servers, bits

router = APIRouter()
router.include_router(users.router)
router.include_router(images.router)
router.include_router(servers.router)
router.include_router(bits.router)
