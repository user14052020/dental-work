from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.modules.documents.service import DocumentService


class FakeWorkRepository:
    def __init__(self, work):
        self.work = work

    async def get(self, work_id: str):
        return self.work if self.work.id == work_id else None


class FakeOrganizationRepository:
    def __init__(self, profile):
        self.profile = profile

    async def get_profile(self):
        return self.profile


class FakeContextUoW:
    def __init__(self, *, work, organization):
        self.works = FakeWorkRepository(work)
        self.organization = FakeOrganizationRepository(organization)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None


@pytest.mark.asyncio
async def test_document_service_renders_invoice_act_and_job_order():
    organization = SimpleNamespace(
        display_name="ООО Северный Мост",
        legal_name="ООО Северный Мост",
        legal_address="620075, Екатеринбург, ул. Луначарского, 80-12",
        mailing_address=None,
        phone="+79995554433",
        inn="6678123456",
        kpp="667801001",
        bank_name="АО Банк Развитие",
        bik="044525987",
        settlement_account="40702810400000004321",
        correspondent_account="30101810400000000987",
        recipient_name="ООО Северный Мост",
        director_name="Петрова Н.А.",
        accountant_name="",
        vat_mode="vat_20",
        vat_label="Без налога (НДС)",
    )
    client = SimpleNamespace(
        id=str(uuid4()),
        name="ООО БИЗНЕС РЕШЕНИЯ",
        legal_name="ООО БИЗНЕС РЕШЕНИЯ",
        address="347375, Волгодонск, пр-кт Курчатова, 45-3",
        legal_address="347375, Волгодонск, пр-кт Курчатова, 45-3",
        phone="+79381464100",
        inn="6143070536",
        kpp="614301001",
        contract_number="13025",
        contract_date=date(2026, 2, 6),
        signer_name="Кравцова Л.Ю.",
    )
    work = SimpleNamespace(
        id=str(uuid4()),
        order_number="3",
        client=client,
        client_id=client.id,
        executor=None,
        executor_id=None,
        work_type="Изготовление коронки",
        description="Шинирование и подбор цвета",
        doctor_name="Шипилов",
        doctor_phone="+79998887766",
        patient_name="Иванов Иван",
        patient_age=34,
        patient_gender="male",
        require_color_photo=True,
        face_shape="oval",
        implant_system="Straumann",
        metal_type="Цирконий",
        shade_color="A2",
        tooth_formula="16",
        tooth_selection=[{"tooth_code": "16", "state": "target", "surfaces": ["occlusal"]}],
        status="completed",
        received_at=datetime(2026, 2, 11, 10, 0, tzinfo=timezone.utc),
        deadline_at=datetime(2026, 2, 28, 10, 0, tzinfo=timezone.utc),
        completed_at=datetime(2026, 2, 28, 15, 0, tzinfo=timezone.utc),
        closed_at=datetime(2026, 2, 28, 15, 30, tzinfo=timezone.utc),
        base_price_for_client=Decimal("19000.00"),
        price_adjustment_percent=Decimal("0.00"),
        price_for_client=Decimal("19000.00"),
        cost_price=Decimal("12450.00"),
        margin=Decimal("6550.00"),
        additional_expenses=Decimal("350.00"),
        labor_hours=Decimal("3.00"),
        labor_cost=Decimal("4800.00"),
        amount_paid=Decimal("5000.00"),
        materials=[],
        work_operations=[],
    )
    service = DocumentService(FakeContextUoW(work=work, organization=organization))

    invoice_html = await service.render_invoice(work.id)
    act_html = await service.render_act(work.id)
    job_order_html = await service.render_job_order(work.id)

    assert "Счет № 3" in invoice_html
    assert "ООО Северный Мост" in invoice_html
    assert "ООО БИЗНЕС РЕШЕНИЯ" in invoice_html
    assert "19 000,00" in invoice_html
    assert "Итого без НДС" in invoice_html
    assert "НДС 20%" in invoice_html
    assert "22 800,00" in invoice_html

    assert "Акт выполненных работ" in act_html
    assert "Договор:</b> №13025" in act_html
    assert "Кравцова Л.Ю." in act_html
    assert "двадцать две тысячи восемьсот рублей 00 копеек" in act_html
    assert "Всего с НДС" in act_html

    assert "Наряд № 3" in job_order_html
    assert "Straumann" in job_order_html
    assert "Цирконий" in job_order_html
    assert "A2" in job_order_html
    assert "Подпись врача" in job_order_html
