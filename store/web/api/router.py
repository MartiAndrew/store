from fastapi.routing import APIRouter

from store.web.api.docs import router as docs_router
from store.web.api.internal.router import internal_router
from store.web.api.monitoring.router import monitoring_router
from store.web.api.public.router import public_router

api_router = APIRouter()
api_router.include_router(monitoring_router)
api_router.include_router(internal_router, prefix="/internal", tags=["internal"])
api_router.include_router(
    public_router,
    prefix="/store/public",
    tags=["public"],
)
api_router.include_router(docs_router)
