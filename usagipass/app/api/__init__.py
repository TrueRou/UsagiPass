from fastapi import APIRouter

from usagipass.app.api import accounts, announcements, images, users, v1

router = APIRouter()
router.include_router(v1.router)
router.include_router(users.router)
router.include_router(accounts.router)
router.include_router(images.router)
router.include_router(announcements.router)
