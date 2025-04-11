from fastapi import APIRouter
from usagipass.app.api import users, images, servers, accounts, announcements, v1

router = APIRouter()
router.include_router(v1.router)
router.include_router(users.router)
router.include_router(accounts.router)
router.include_router(images.router)
router.include_router(servers.router)
router.include_router(announcements.router)
