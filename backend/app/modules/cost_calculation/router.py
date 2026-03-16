from fastapi import APIRouter, Depends

from app.api.dependencies import get_cost_calculation_service, get_current_user
from app.modules.cost_calculation.schemas import CostCalculationRead, CostCalculationRequest
from app.modules.cost_calculation.service import CostCalculationService


router = APIRouter(
    prefix="/cost-calculation",
    tags=["cost-calculation"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/estimate", response_model=CostCalculationRead)
async def estimate_cost(
    payload: CostCalculationRequest,
    service: CostCalculationService = Depends(get_cost_calculation_service),
) -> CostCalculationRead:
    return await service.calculate(payload)

