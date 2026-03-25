from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.modules.documents.service import DocumentService


class FakeEmailSender:
    def __init__(self):
        self.messages = []

    async def send_html(self, *, settings, recipient_email: str, subject: str, html_body: str):
        self.messages.append(
            {
                "settings": settings,
                "recipient_email": recipient_email,
                "subject": subject,
                "html_body": html_body,
            }
        )


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


class FakeNaradRepository:
    def __init__(self, narad):
        self.narad = narad

    async def get(self, narad_id: str):
        if isinstance(self.narad, list):
            return next((item for item in self.narad if item.id == narad_id), None)
        return self.narad if self.narad.id == narad_id else None

    async def list_closed_by_client(self, client_id: str, *, date_from=None, date_to=None):
        narads = [item for item in self.narad if item.client.id == client_id] if isinstance(self.narad, list) else []
        result = []
        for narad in narads:
            closed_at = narad.closed_at
            if closed_at is None:
                continue
            if date_from and closed_at < date_from:
                continue
            if date_to and closed_at > date_to:
                continue
            result.append(narad)
        return result


class FakeClientRepository:
    def __init__(self, client):
        self.client = client

    async def get(self, client_id: str):
        return self.client if self.client.id == client_id else None


class FakeContextUoW:
    def __init__(self, *, work, narad, organization):
        self.works = FakeWorkRepository(work)
        self.narads = FakeNaradRepository(narad)
        self.clients = FakeClientRepository(work.client)
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
        smtp_host="smtp.severny-most-lab.ru",
        smtp_port=587,
        smtp_username="notifications",
        smtp_password="secret",
        smtp_from_email="office@severny-most-lab.ru",
        smtp_from_name="Северный Мост",
        smtp_reply_to="office@severny-most-lab.ru",
        smtp_use_tls=True,
        smtp_use_ssl=False,
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
    narad = SimpleNamespace(
        id=str(uuid4()),
        narad_number="NAR-2026-0003",
        client=client,
        description="Общий заказ пациента",
        received_at=datetime(2026, 2, 11, 10, 0, tzinfo=timezone.utc),
        completed_at=datetime(2026, 2, 28, 15, 0, tzinfo=timezone.utc),
        closed_at=datetime(2026, 2, 28, 15, 30, tzinfo=timezone.utc),
        works=[],
    )
    narad_second = SimpleNamespace(
        id=str(uuid4()),
        narad_number="NAR-2026-0004",
        client=client,
        description="Повторный заказ пациента",
        received_at=datetime(2026, 3, 4, 10, 0, tzinfo=timezone.utc),
        completed_at=datetime(2026, 3, 11, 15, 0, tzinfo=timezone.utc),
        closed_at=datetime(2026, 3, 11, 15, 30, tzinfo=timezone.utc),
        works=[],
    )
    work = SimpleNamespace(
        id=str(uuid4()),
        order_number="3",
        narad=narad,
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
    work_second = SimpleNamespace(
        id=str(uuid4()),
        order_number="4",
        narad=narad_second,
        client=client,
        client_id=client.id,
        executor=None,
        executor_id=None,
        work_type="Временная коронка",
        description="Контрольная корректировка",
        doctor_name="Шипилов",
        doctor_phone="+79998887766",
        patient_name="Иванов Иван",
        patient_age=34,
        patient_gender="male",
        require_color_photo=False,
        face_shape="oval",
        implant_system=None,
        metal_type=None,
        shade_color="A1",
        tooth_formula="15",
        tooth_selection=[{"tooth_code": "15", "state": "target", "surfaces": ["occlusal"]}],
        status="completed",
        received_at=datetime(2026, 3, 4, 10, 0, tzinfo=timezone.utc),
        deadline_at=datetime(2026, 3, 11, 10, 0, tzinfo=timezone.utc),
        completed_at=datetime(2026, 3, 11, 15, 0, tzinfo=timezone.utc),
        closed_at=datetime(2026, 3, 11, 15, 30, tzinfo=timezone.utc),
        base_price_for_client=Decimal("6000.00"),
        price_adjustment_percent=Decimal("0.00"),
        price_for_client=Decimal("6000.00"),
        cost_price=Decimal("2400.00"),
        margin=Decimal("3600.00"),
        additional_expenses=Decimal("0.00"),
        labor_hours=Decimal("1.50"),
        labor_cost=Decimal("1600.00"),
        amount_paid=Decimal("0.00"),
        materials=[],
        work_operations=[],
    )
    narad.works = [work]
    narad_second.works = [work_second]
    service = DocumentService(FakeContextUoW(work=work, narad=[narad, narad_second], organization=organization))

    invoice_html = await service.render_invoice(work.id)
    act_html = await service.render_act(work.id)
    job_order_html = await service.render_job_order(work.id)
    narad_invoice_html = await service.render_narad_invoice(narad.id)
    grouped_invoice_html = await service.render_client_invoice(client.id, date_from=None, date_to=None)
    grouped_act_html = await service.render_client_act(client.id, date_from=None, date_to=None)

    assert "Счет № NAR-2026-0003" in invoice_html
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

    assert "Наряд № NAR-2026-0003" in job_order_html
    assert "Straumann" in job_order_html
    assert "Цирконий" in job_order_html
    assert "A2" in job_order_html
    assert "Подпись врача" in job_order_html
    assert "Счет № NAR-2026-0003" in narad_invoice_html
    assert "Счет по нарядам клиента ООО БИЗНЕС РЕШЕНИЯ" in grouped_invoice_html
    assert "NAR-2026-0003" in grouped_invoice_html
    assert "NAR-2026-0004" in grouped_invoice_html
    assert "25 000,00" in grouped_invoice_html
    assert "Акт по нарядам клиента ООО БИЗНЕС РЕШЕНИЯ" in grouped_act_html
    assert "Закрытые наряды за период" in grouped_act_html


@pytest.mark.asyncio
async def test_document_service_sends_narad_and_client_documents_via_email():
    email_sender = FakeEmailSender()
    organization = SimpleNamespace(
        display_name="ООО Северный Мост",
        legal_name="ООО Северный Мост",
        legal_address="620075, Екатеринбург, ул. Луначарского, 80-12",
        mailing_address=None,
        phone="+79995554433",
        email="office@severny-most-lab.ru",
        inn="6678123456",
        kpp="667801001",
        bank_name="АО Банк Развитие",
        bik="044525987",
        settlement_account="40702810400000004321",
        correspondent_account="30101810400000000987",
        recipient_name="ООО Северный Мост",
        director_name="Петрова Н.А.",
        accountant_name="",
        smtp_host="smtp.severny-most-lab.ru",
        smtp_port=587,
        smtp_username="notifications",
        smtp_password="secret",
        smtp_from_email="office@severny-most-lab.ru",
        smtp_from_name="Северный Мост",
        smtp_reply_to="office@severny-most-lab.ru",
        smtp_use_tls=True,
        smtp_use_ssl=False,
        vat_mode="without_vat",
        vat_label="Без налога (НДС)",
    )
    client = SimpleNamespace(
        id=str(uuid4()),
        name="Клиника Улыбка",
        legal_name="ООО Клиника Улыбка",
        email="manager@ulybka-clinic.ru",
        address="Екатеринбург",
        legal_address="Екатеринбург",
        phone="+79990000000",
        inn="6677001122",
        kpp="667701001",
        contract_number="15",
        contract_date=date(2026, 3, 1),
        signer_name="Соколова Е.А.",
    )
    narad = SimpleNamespace(
        id=str(uuid4()),
        narad_number="NAR-2026-0021",
        client=client,
        description="Письмо по наряду",
        received_at=datetime(2026, 3, 20, 10, 0, tzinfo=timezone.utc),
        completed_at=datetime(2026, 3, 22, 15, 0, tzinfo=timezone.utc),
        closed_at=datetime(2026, 3, 22, 15, 30, tzinfo=timezone.utc),
        works=[],
    )
    work = SimpleNamespace(
        id=str(uuid4()),
        order_number="NAR-2026-0021",
        narad=narad,
        client=client,
        client_id=client.id,
        executor=None,
        executor_id=None,
        work_type="Циркониевая коронка",
        description="Отправка счета",
        status="completed",
        received_at=datetime(2026, 3, 20, 10, 0, tzinfo=timezone.utc),
        deadline_at=datetime(2026, 3, 22, 10, 0, tzinfo=timezone.utc),
        completed_at=datetime(2026, 3, 22, 15, 0, tzinfo=timezone.utc),
        closed_at=datetime(2026, 3, 22, 15, 30, tzinfo=timezone.utc),
        base_price_for_client=Decimal("15500.00"),
        price_adjustment_percent=Decimal("0.00"),
        price_for_client=Decimal("15500.00"),
        cost_price=Decimal("8300.00"),
        margin=Decimal("7200.00"),
        additional_expenses=Decimal("0.00"),
        labor_hours=Decimal("2.50"),
        labor_cost=Decimal("3200.00"),
        amount_paid=Decimal("0.00"),
        materials=[],
        work_operations=[],
    )
    narad.works = [work]
    service = DocumentService(
        FakeContextUoW(work=work, narad=[narad], organization=organization),
        email_sender=email_sender,
    )

    narad_result = await service.send_narad_document_email(narad.id, kind="invoice")
    client_result = await service.send_client_document_email(client.id, kind="act", date_from=None, date_to=None)

    assert narad_result.recipient_email == "manager@ulybka-clinic.ru"
    assert "NAR-2026-0021" in narad_result.subject
    assert client_result.recipient_email == "manager@ulybka-clinic.ru"
    assert "Клиника Улыбка" in client_result.subject
    assert len(email_sender.messages) == 2
    assert "Счет № NAR-2026-0021" in email_sender.messages[0]["html_body"]
    assert "Акт по нарядам клиента" in email_sender.messages[1]["html_body"]
