from fastapi import APIRouter

from stellar.account.endpoints import router as account_router
from stellar.dev.endpoints import router as dev_router
from stellar.profile.endpoints import router as profile_router
from stellar.teams.endpoints import router as teams_router

router = APIRouter(prefix="/api/v1")

# /dev
router.include_router(dev_router)
# /account
router.include_router(account_router)
# /profile
router.include_router(profile_router)
# /teams
router.include_router(teams_router)
