from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from app.common.search_documents import build_work_search_document


class NonLoadingWork:
    order_number = "DL-2026-0001"
    client_id = "client-1"
    executor_id = "executor-1"
    work_type = "Коронка"
    description = "Описание"
    doctor_name = "Иван Сергеев"
    doctor_phone = "+79991234567"
    patient_name = "Мария Петрова"
    patient_age = 32
    patient_gender = "female"
    require_color_photo = False
    face_shape = "oval"
    implant_system = "Straumann"
    metal_type = "Цирконий"
    shade_color = "A2"
    tooth_formula = "16"
    status = "new"
    received_at = datetime.now(timezone.utc)
    deadline_at = None
    completed_at = None
    closed_at = None
    base_price_for_client = Decimal("10000.00")
    price_adjustment_percent = Decimal("0.00")
    price_for_client = Decimal("10000.00")
    cost_price = Decimal("6500.00")
    margin = Decimal("3500.00")
    additional_expenses = Decimal("0.00")
    labor_hours = Decimal("2.00")
    labor_cost = Decimal("1500.00")
    amount_paid = Decimal("0.00")
    tooth_selection = []

    @property
    def client(self):
        raise AssertionError("client relation should not be accessed")

    @property
    def executor(self):
        raise AssertionError("executor relation should not be accessed")

    @property
    def materials(self):
        raise AssertionError("materials relation should not be accessed")

    @property
    def work_operations(self):
        raise AssertionError("work_operations relation should not be accessed")

    @property
    def attachments(self):
        raise AssertionError("attachments relation should not be accessed")


def test_build_work_search_document_respects_explicit_lists_without_loading_relations():
    payload = build_work_search_document(
        NonLoadingWork(),
        client_name="Клиника Улыбка",
        executor_name="Дмитрий Иванов",
        operation_names=[],
        material_names=[],
        attachment_names=[],
    )

    assert payload["client_name"] == "Клиника Улыбка"
    assert payload["executor_name"] == "Дмитрий Иванов"
    assert payload["operation_names"] == []
    assert payload["material_names"] == []
    assert payload["attachment_names"] == []
