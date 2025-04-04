from fastapi import APIRouter
from usagipass.app.api import users, images, servers, accounts, cards, drafts, tasks, announcements

router = APIRouter()
router.include_router(users.router)
router.include_router(cards.router)
router.include_router(drafts.router)
router.include_router(accounts.router)
router.include_router(images.router)
router.include_router(servers.router)
router.include_router(tasks.router)
router.include_router(announcements.router)
