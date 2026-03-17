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
    work = context["work"]

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
        title=f"Счет № {html_text(work.order_number)} от {format_date_ru(context['document_date'])}",
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
    work = context["work"]
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
        title=f"Акт выполненных работ (оказанных услуг) № {html_text(work.order_number)} от {format_date_ru(context['document_date'])}",
        body=f"""
        <div><b>Исполнитель:</b> {html_text(organization.legal_name)}, ИНН {html_text(organization.inn)}, {html_text(organization.legal_address)}, тел.: {html_text(organization.phone)}</div>
        <div class="spacer-sm"></div>
        <div><b>Заказчик:</b> {html_text(client.legal_name or client.name)}, ИНН {html_text(client.inn)}, КПП {html_text(client.kpp)}, {html_text(client.legal_address or client.address)}, тел.: {html_text(client.phone)}</div>
        <div class="spacer-sm"></div>
        <div><b>Договор:</b> №{html_text(client.contract_number)} от {format_date_ru(client.contract_date)}</div>

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
    work = context["work"]
    client = context["client"]
    face_shape = work.face_shape or ""
    selected_teeth = work.tooth_selection or []
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

    return _document_shell(
        title=f"Наряд № {html_text(work.order_number)}",
        body=f"""
        <div class="headline">{html_text(context['organization'].display_name)}</div>

        <table class="job-table">
          <tr>
            <td><b>Заказчик</b><br />{html_text(client.name)}</td>
            <td><b>ФИО врача</b><br />{html_text(work.doctor_name)}</td>
          </tr>
          <tr>
            <td><b>раб/тел</b><br />{html_text(client.phone)}</td>
            <td><b>моб/тел</b><br />{html_text(work.doctor_phone)}</td>
          </tr>
          <tr>
            <td><b>Пациент</b><br />{html_text(work.patient_name)}</td>
            <td><b>Возраст / Пол</b><br />{html_text(work.patient_age)} &nbsp;&nbsp; М {checkbox(work.patient_gender == 'male')} &nbsp; Ж {checkbox(work.patient_gender == 'female')}</td>
          </tr>
          <tr>
            <td><b>Предоставить фотоаппарат для определения цвета</b><br />{checkbox(bool(work.require_color_photo))}</td>
            <td><b>Форма лица</b><br />□ {checkbox(face_shape == 'square')} &nbsp; ○ {checkbox(face_shape == 'oval')} &nbsp; △ {checkbox(face_shape == 'triangle')}</td>
          </tr>
        </table>

        <div class="job-meta-grid">
          <div><b>Система имплантов</b><br />{html_text(work.implant_system)}</div>
          <div><b>Металл</b><br />{html_text(work.metal_type)}</div>
          <div><b>Цвет</b><br />{html_text(work.shade_color)}</div>
        </div>

        <div class="section-title">Описание работы</div>
        <div class="paragraph">{html_multiline(work.description)}</div>

        <div class="section-title">Сводка по зубной формуле</div>
        <div class="formula-box">{html_text(work.tooth_formula)}</div>

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
    work_items = list(getattr(work, "work_items", []) or [])
    if work_items:
        line_items: list[dict[str, Any]] = []
        for index, item in enumerate(work_items, start=1):
            description_parts = [item.work_type]
            if item.description and item.description.strip() and item.description.strip() != item.work_type.strip():
                description_parts.append(item.description.strip())
            if index == 1 and work.patient_name:
                description_parts.append(f"Пациент: {work.patient_name}")
            if index == 1 and work.tooth_formula:
                description_parts.append(f"Формула: {work.tooth_formula}")

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


def build_single_work_line_items(work: Any) -> list[dict[str, Any]]:
    description_parts = [work.work_type]
    if work.patient_name:
        description_parts.append(f"Пациент: {work.patient_name}")
    if work.tooth_formula:
        description_parts.append(f"Формула: {work.tooth_formula}")

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
