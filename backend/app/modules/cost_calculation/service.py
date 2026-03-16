from decimal import Decimal

from app.core.exceptions import NotFoundError
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.cost_calculation.schemas import (
    CostBreakdownLine,
    CostCalculationRead,
    CostCalculationRequest,
)


class CostCalculationService:
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow

    async def calculate(self, payload: CostCalculationRequest) -> CostCalculationRead:
        async with self._uow as uow:
            materials = {item.id: item for item in await uow.materials.list_by_ids([line.material_id for line in payload.materials])}
            executor_rate = Decimal("0.00")
            if payload.executor_id:
                executor = await uow.executors.get(payload.executor_id)
                if executor is None:
                    raise NotFoundError("executor", payload.executor_id)
                executor_rate = executor.hourly_rate

        lines: list[CostBreakdownLine] = []
        materials_cost = Decimal("0.00")
        for line in payload.materials:
            material = materials.get(line.material_id)
            if material is None:
                raise NotFoundError("material", line.material_id)
            unit_cost = line.unit_cost_override or material.average_price
            total_cost = unit_cost * line.quantity
            materials_cost += total_cost
            lines.append(
                CostBreakdownLine(
                    name=material.name,
                    quantity=line.quantity,
                    unit_cost=unit_cost,
                    total_cost=total_cost,
                )
            )

        labor_rate = payload.hourly_rate_override or executor_rate
        labor_cost = labor_rate * payload.labor_hours
        total_cost = materials_cost + labor_cost + payload.additional_expenses
        margin = payload.sale_price - total_cost
        profitability = Decimal("0.00") if payload.sale_price == 0 else (margin / payload.sale_price) * 100
        return CostCalculationRead(
            materials_cost=materials_cost,
            labor_cost=labor_cost,
            additional_expenses=payload.additional_expenses,
            total_cost=total_cost,
            sale_price=payload.sale_price,
            margin=margin,
            profitability_percent=profitability.quantize(Decimal("0.01")),
            lines=lines,
        )

