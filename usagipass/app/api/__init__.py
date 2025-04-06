from fastapi import APIRouter
from usagipass.app.api import users, images, servers, accounts, announcements

router = APIRouter()
router.include_router(users.router)
router.include_router(accounts.router)
router.include_router(images.router)
router.include_router(servers.router)
router.include_router(announcements.router)
