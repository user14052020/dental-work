from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.modules.documents.formatting import (
    amount_to_words_ru,
    checkbox,
    format_date_ru,
    format_money,
    html_multiline,
    html_text,
)


def render_invoice_html(context: dict[str, Any]) -> str:
    organization = context["organization"]
    client = context["client"]
    line_items = context["line_items"]
    vat = context["vat"]
    document_number = context["document_number"]
    scope_note = context.get("scope_note")
    heading = context.get("document_heading") or (
        f"Счет № {html_text(document_number)} от {format_date_ru(context['document_date'])}"
    )

    rows = "".join(
        f"""
        <tr>
          <td>{index}</td>
          <td>{html_text(item['description'])}</td>
          <td class="right">{format_money(item['total'])}</td>
        </tr>
        """
        for index, item in enumerate(line_items, start=1)
    )

    return _document_shell(
        title=heading,
        body=f"""
        <div class="headline">{html_text(organization.display_name)}</div>
        <div class="subline">{html_text(organization.legal_address or organization.mailing_address)}</div>

        <table class="bank-table">
          <tr>
            <td>ИНН {html_text(organization.inn)}</td>
            <td>КПП {html_text(organization.kpp)}</td>
            <td></td>
            <td></td>
          </tr>
          <tr>
            <td colspan="2">Получатель</td>
            <td>Сч. №</td>
            <td>{html_text(organization.settlement_account)}</td>
          </tr>
          <tr>
            <td colspan="2">{html_text(organization.recipient_name or organization.legal_name)}</td>
            <td></td>
            <td></td>
          </tr>
          <tr>
            <td colspan="2">Банк получателя</td>
            <td>БИК</td>
            <td>{html_text(organization.bik)}</td>
          </tr>
          <tr>
            <td colspan="2">{html_text(organization.bank_name)}</td>
            <td>Сч. №</td>
            <td>{html_text(organization.correspondent_account)}</td>
          </tr>
        </table>

        <div class="section-title">Плательщик: {html_text(client.legal_name or client.name)}</div>
        <div><b>Адрес:</b> {html_text(client.legal_address or client.address)}</div>
        <div><b>ИНН:</b> {html_text(client.inn)} &nbsp;&nbsp; <b>КПП:</b> {html_text(client.kpp)}</div>
        <div><b>Договор:</b> {html_text(client.contract_number)} от {format_date_ru(client.contract_date)}</div>
        <div><b>Валюта:</b> Российский рубль, 643</div>
        {_render_scope_note(scope_note)}

        <table class="items-table">
          <thead>
            <tr>
              <th class="narrow">№</th>
              <th>Наименование товара/услуги</th>
              <th class="money">Сумма</th>
            </tr>
          </thead>
          <tbody>
            {rows}
            <tr>
              <td colspan="2" class="summary-title">Итого без НДС:</td>
              <td class="right">{format_money(vat['subtotal_without_vat'])}</td>
            </tr>
            <tr>
              <td colspan="2" class="summary-title">{html_text(vat['vat_label'])}:</td>
              <td class="right">{format_money(vat['vat_amount'])}</td>
            </tr>
            <tr>
              <td colspan="2" class="summary-title">Всего с НДС:</td>
              <td class="right">{format_money(vat['total_with_vat'])}</td>
            </tr>
          </tbody>
        </table>

        <div class="totals-note">Всего наименований {len(line_items)}, на сумму {format_money(vat['total_with_vat'])}</div>
        <div class="totals-note"><b>Всего к оплате:</b> {amount_to_words_ru(vat['total_with_vat'])}</div>

        <table class="sign-table">
          <tr>
            <td><b>Руководитель предприятия</b><br /><br />____________ {html_text(organization.director_name)}</td>
            <td><b>Главный бухгалтер</b><br /><br />____________ {html_text(organization.accountant_name)}</td>
          </tr>
        </table>
        """,
    )


def render_act_html(context: dict[str, Any]) -> str:
    organization = context["organization"]
    client = context["client"]
    line_items = context["line_items"]
    vat = context["vat"]
    document_number = context["document_number"]
    scope_note = context.get("scope_note")
    heading = context.get("document_heading") or (
        f"Акт выполненных работ (оказанных услуг) № {html_text(document_number)} от {format_date_ru(context['document_date'])}"
    )
    rows = "".join(
        f"""
        <tr>
          <td>{html_text(item['description'])}</td>
          <td class="center">{item['quantity']}</td>
          <td class="right">{format_money(item['unit_price'])}</td>
          <td class="right">{format_money(item['total'])}</td>
        </tr>
        """
        for item in line_items
    )

    return _document_shell(
        title=heading,
        body=f"""
        <div><b>Исполнитель:</b> {html_text(organization.legal_name)}, ИНН {html_text(organization.inn)}, {html_text(organization.legal_address)}, тел.: {html_text(organization.phone)}</div>
        <div class="spacer-sm"></div>
        <div><b>Заказчик:</b> {html_text(client.legal_name or client.name)}, ИНН {html_text(client.inn)}, КПП {html_text(client.kpp)}, {html_text(client.legal_address or client.address)}, тел.: {html_text(client.phone)}</div>
        <div class="spacer-sm"></div>
        <div><b>Договор:</b> №{html_text(client.contract_number)} от {format_date_ru(client.contract_date)}</div>
        {_render_scope_note(scope_note)}

        <table class="items-table">
          <thead>
            <tr>
              <th>Наименование услуги</th>
              <th class="narrow">Количество</th>
              <th class="money">Цена</th>
              <th class="money">Сумма</th>
            </tr>
          </thead>
          <tbody>
            {rows}
            <tr>
              <td colspan="3" class="summary-title">Итого без НДС:</td>
              <td class="right">{format_money(vat['subtotal_without_vat'])}</td>
            </tr>
            <tr>
              <td colspan="3" class="summary-title">{html_text(vat['vat_label'])}</td>
              <td class="right">{format_money(vat['vat_amount'])}</td>
            </tr>
            <tr>
              <td colspan="3" class="summary-title">Всего с НДС:</td>
              <td class="right">{format_money(vat['total_with_vat'])}</td>
            </tr>
          </tbody>
        </table>

        <div class="totals-note">Всего оказано услуг: {len(line_items)}, на сумму: {format_money(vat['total_with_vat'])} руб.</div>
        <div class="totals-note"><b>Всего к оплате:</b> {amount_to_words_ru(vat['total_with_vat'])}</div>
        <div class="paragraph">
          Вышеперечисленные услуги выполнены полностью и в срок. Заказчик претензий по объему, качеству и срокам оказания услуг не имеет.
        </div>

        <table class="sign-table">
          <tr>
            <td><b>Исполнитель:</b><br /><br />____________ {html_text(organization.director_name)}</td>
            <td><b>Заказчик:</b><br /><br />____________ {html_text(client.signer_name or client.contact_person)}</td>
          </tr>
        </table>
        """,
    )


def render_job_order_html(context: dict[str, Any]) -> str:
    narad = context["narad"]
    work = context["primary_work"]
    client = context["client"]
    job_order_items = context.get("job_order_items") or []
    patient_name = _resolve_narad_or_work_value(work, "patient_name")
    patient_age = _resolve_narad_or_work_value(work, "patient_age")
    patient_gender = _resolve_narad_or_work_value(work, "patient_gender")
    face_shape = _resolve_narad_or_work_value(work, "face_shape") or ""
    selected_teeth = _resolve_narad_or_work_value(work, "tooth_selection") or []
    require_color_photo = _resolve_narad_or_work_value(work, "require_color_photo")
    implant_system = _resolve_narad_or_work_value(work, "implant_system")
    metal_type = _resolve_narad_or_work_value(work, "metal_type")
    shade_color = _resolve_narad_or_work_value(work, "shade_color")
    tooth_formula = _resolve_narad_or_work_value(work, "tooth_formula")
    selected_rows = "".join(
        f"""
        <tr>
          <td>{html_text(item.get('tooth_code'))}</td>
          <td>{html_text(item.get('state'))}</td>
          <td>{html_text(', '.join(item.get('surfaces') or []))}</td>
        </tr>
        """
        for item in selected_teeth
    ) or '<tr><td colspan="3">Зубы на схеме не отмечены.</td></tr>'

    job_rows = "".join(
        f"""
        <tr>
          <td>{index}</td>
          <td>{html_text(item['order_number'])}</td>
          <td>{html_text(item['work_type'])}</td>
          <td>{html_text(item['description'])}</td>
        </tr>
        """
        for index, item in enumerate(job_order_items, start=1)
    ) or '<tr><td colspan="4">Строки заказа не сформированы.</td></tr>'

    return _document_shell(
        title=f"Наряд № {html_text(narad.narad_number)}",
        body=f"""
        <div class="headline">{html_text(context['organization'].display_name)}</div>

        <table class="job-table">
          <tr>
            <td><b>Заказчик</b><br />{html_text(client.name)}</td>
            <td><b>ФИО врача</b><br />{html_text(getattr(narad, 'doctor_name', None) or work.doctor_name)}</td>
          </tr>
          <tr>
            <td><b>раб/тел</b><br />{html_text(client.phone)}</td>
            <td><b>моб/тел</b><br />{html_text(getattr(narad, 'doctor_phone', None) or work.doctor_phone)}</td>
          </tr>
          <tr>
            <td><b>Пациент</b><br />{html_text(patient_name)}</td>
            <td><b>Возраст / Пол</b><br />{html_text(patient_age)} &nbsp;&nbsp; М {checkbox(patient_gender == 'male')} &nbsp; Ж {checkbox(patient_gender == 'female')}</td>
          </tr>
          <tr>
            <td><b>Предоставить фотоаппарат для определения цвета</b><br />{checkbox(bool(require_color_photo))}</td>
            <td><b>Форма лица</b><br />□ {checkbox(face_shape == 'square')} &nbsp; ○ {checkbox(face_shape == 'oval')} &nbsp; △ {checkbox(face_shape == 'triangle')}</td>
          </tr>
        </table>

        <div class="job-meta-grid">
          <div><b>Система имплантов</b><br />{html_text(implant_system)}</div>
          <div><b>Металл</b><br />{html_text(metal_type)}</div>
          <div><b>Цвет</b><br />{html_text(shade_color)}</div>
        </div>

        <div class="section-title">Описание наряда</div>
        <div class="paragraph">{html_multiline(narad.description or work.description)}</div>

        <table class="items-table">
          <thead>
            <tr>
              <th class="narrow">#</th>
              <th>Работа</th>
              <th>Тип</th>
              <th>Описание</th>
            </tr>
          </thead>
          <tbody>
            {job_rows}
          </tbody>
        </table>

        <div class="section-title">Сводка по зубной формуле</div>
        <div class="formula-box">{html_text(tooth_formula)}</div>

        <table class="items-table">
          <thead>
            <tr>
              <th class="narrow">Зуб</th>
              <th>Состояние</th>
              <th>Поверхности</th>
            </tr>
          </thead>
          <tbody>
            {selected_rows}
          </tbody>
        </table>

        <div class="sign-line">Подпись врача ________________________________</div>
        """,
    )


def build_work_line_items(work: Any) -> list[dict[str, Any]]:
    patient_name = _resolve_narad_or_work_value(work, "patient_name")
    tooth_formula = _resolve_narad_or_work_value(work, "tooth_formula")
    work_items = list(getattr(work, "work_items", []) or [])
    if work_items:
        line_items: list[dict[str, Any]] = []
        for index, item in enumerate(work_items, start=1):
            description_parts = [item.work_type]
            if item.description and item.description.strip() and item.description.strip() != item.work_type.strip():
                description_parts.append(item.description.strip())
            if index == 1 and patient_name:
                description_parts.append(f"Пациент: {patient_name}")
            if index == 1 and tooth_formula:
                description_parts.append(f"Формула: {tooth_formula}")

            line_items.append(
                {
                    "description": " · ".join(description_parts),
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "total": item.total_price,
                }
            )
        return line_items

    return build_single_work_line_items(work)


def build_narad_line_items(narad: Any) -> list[dict[str, Any]]:
    line_items: list[dict[str, Any]] = []
    works = list(getattr(narad, "works", []) or [])
    for work in works:
        work_lines = build_work_line_items(work)
        for item in work_lines:
            line_items.append(
                {
                    **item,
                    "description": f"{work.order_number} · {item['description']}",
                }
            )

    if line_items:
        return line_items

    primary_work = works[0] if works else None
    return build_single_work_line_items(primary_work) if primary_work else []


def build_narad_job_order_items(narad: Any) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for work in list(getattr(narad, "works", []) or []):
        work_items = list(getattr(work, "work_items", []) or [])
        if work_items:
            for item in work_items:
                items.append(
                    {
                        "order_number": work.order_number,
                        "work_type": item.work_type,
                        "description": item.description or item.work_type,
                    }
                )
            continue

        items.append(
            {
                "order_number": work.order_number,
                "work_type": work.work_type,
                "description": work.description or work.work_type,
            }
        )

    return items


def build_client_line_items(narads: list[Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for narad in narads:
        for work in list(getattr(narad, "works", []) or []):
            work_lines = build_work_line_items(work)
            for item in work_lines:
                description_parts = [narad.narad_number, work.order_number, item["description"]]
                items.append(
                    {
                        **item,
                        "description": " · ".join(part for part in description_parts if part),
                    }
                )
    return items


def build_single_work_line_items(work: Any) -> list[dict[str, Any]]:
    patient_name = _resolve_narad_or_work_value(work, "patient_name")
    tooth_formula = _resolve_narad_or_work_value(work, "tooth_formula")
    description_parts = [work.work_type]
    if patient_name:
        description_parts.append(f"Пациент: {patient_name}")
    if tooth_formula:
        description_parts.append(f"Формула: {tooth_formula}")

    description = " · ".join(description_parts)
    return [
        {
            "description": description,
            "quantity": Decimal("1.00"),
            "unit_price": work.price_for_client,
            "total": work.price_for_client,
        }
    ]


def _document_shell(*, title: str, body: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="ru">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{title}</title>
        <style>
          :root {{
            color-scheme: light;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          }}
          body {{
            margin: 0;
            padding: 32px;
            background: #f4f6f8;
            color: #111827;
          }}
          .page {{
            max-width: 980px;
            margin: 0 auto;
            background: #fff;
            padding: 48px 56px;
            box-shadow: 0 24px 60px rgba(15, 23, 42, 0.12);
          }}
          .headline {{
            font-size: 28px;
            font-weight: 800;
            text-align: center;
            margin-bottom: 8px;
          }}
          .subline {{
            text-align: center;
            margin-bottom: 24px;
          }}
          .section-title {{
            font-size: 18px;
            font-weight: 800;
            margin: 24px 0 12px;
          }}
          .spacer-sm {{
            height: 8px;
          }}
          .paragraph {{
            margin-top: 12px;
            line-height: 1.5;
          }}
          table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
          }}
          td, th {{
            border: 1px solid #111827;
            padding: 10px 12px;
            vertical-align: top;
          }}
          .bank-table td {{
            width: 25%;
          }}
          .items-table th {{
            text-align: left;
          }}
          .narrow {{
            width: 64px;
          }}
          .money {{
            width: 180px;
          }}
          .right {{
            text-align: right;
          }}
          .center {{
            text-align: center;
          }}
          .summary-title {{
            font-weight: 700;
            text-align: right;
          }}
          .sign-table td {{
            height: 92px;
            width: 50%;
          }}
          .totals-note {{
            margin-top: 18px;
            font-size: 18px;
          }}
          .job-table td {{
            width: 50%;
          }}
          .job-meta-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-top: 20px;
          }}
          .job-meta-grid > div, .formula-box {{
            border: 1px solid #111827;
            padding: 12px;
            min-height: 54px;
          }}
          .sign-line {{
            margin-top: 32px;
            text-align: right;
            font-weight: 700;
          }}
          @media print {{
            body {{
              background: #fff;
              padding: 0;
            }}
            .page {{
              box-shadow: none;
              max-width: none;
              padding: 24px 32px;
            }}
          }}
        </style>
      </head>
      <body>
        <main class="page">
          <h1 style="margin:0 0 20px;text-align:center;font-size:24px;">{title}</h1>
          {body}
        </main>
      </body>
    </html>
    """


def _resolve_narad_or_work_value(work: Any, attr_name: str) -> Any:
    narad = getattr(work, "narad", None)
    if narad is not None:
        narad_value = getattr(narad, attr_name, None)
        if narad_value is not None:
            return narad_value
    return getattr(work, attr_name, None)


def _render_scope_note(value: Any) -> str:
    if not value:
        return ""
    return f'<div class="paragraph"><b>Основание:</b> {html_text(value)}</div>'
