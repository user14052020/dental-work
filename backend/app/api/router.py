from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.clients.router import router as clients_router
from app.modules.cost_calculation.router import router as cost_calculation_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.delivery.router import router as delivery_router
from app.modules.doctors.router import router as doctors_router
from app.modules.documents.router import router as documents_router
from app.modules.executors.router import router as executors_router
from app.modules.materials.router import router as materials_router
from app.modules.organization.router import router as organization_router
from app.modules.operations.router import router as operations_router
from app.modules.work_catalog.router import router as work_catalog_router
from app.modules.works.router import router as works_router


api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(clients_router)
api_router.include_router(doctors_router)
api_router.include_router(executors_router)
api_router.include_router(materials_router)
api_router.include_router(organization_router)
api_router.include_router(operations_router)
api_router.include_router(work_catalog_router)
api_router.include_router(works_router)
api_router.include_router(delivery_router)
api_router.include_router(documents_router)
api_router.include_router(cost_calculation_router)
api_router.include_router(dashboard_router)
