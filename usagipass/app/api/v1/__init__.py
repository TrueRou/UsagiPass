from fastapi import APIRouter

from usagipass.app.api.v1 import accounts


router = APIRouter(prefix="/api/v1", tags=["v1"])
router.include_router(accounts.router)
