from fastapi import APIRouter

from stellar.account.endpoints import router as account_router
from stellar.profile.endpoints import router as profile_router

router = APIRouter(prefix="/api/v1")

# /account
router.include_router(account_router)
# /profile
router.include_router(profile_router)
