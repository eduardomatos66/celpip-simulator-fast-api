from fastapi import APIRouter
from app.core.deps import DBSession, AdminUser
from app.services import system_service
from app.schemas.system_schemas import SystemHealth, SystemStats
import app.main as main_module

router = APIRouter()

@router.get("/health",
    response_model=SystemHealth,
    summary="System Health Check",
    description="Retrieve system health status, including disk usage, database connectivity, and application uptime. Restricted to administrators.")
def get_health(
    db: DBSession,
    admin: AdminUser
):
    return system_service.get_system_health(db, main_module.START_TIME)

@router.get("/stats",
    response_model=SystemStats,
    summary="Application Statistics",
    description="Retrieve application-level statistics such as total tests taken and question counts per test area. Restricted to administrators.")
def get_stats(
    db: DBSession,
    admin: AdminUser
):
    return system_service.get_system_stats(db)
