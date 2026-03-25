from __future__ import annotations

from typing import Any

from app.modules.documents.formatting import format_date_ru, format_money, html_text


def render_delivery_manifest_html(context: dict[str, Any]) -> str:
    organization = context["organization"]
    items = context["items"]
    rows = "".join(
        f"""
        <tr>
          <td>{index}</td>
          <td>{html_text(item.client_name)}</td>
          <td>{html_text(item.narad_number)}</td>
          <td>{html_text(item.title)}</td>
          <td>{html_text(", ".join(item.work_types))}</td>
          <td>{html_text(item.patient_name)}</td>
          <td>{html_text(item.doctor_name)}</td>
          <td>{html_text(item.delivery_address)}</td>
          <td>{html_text(item.delivery_contact)}</td>
          <td>{html_text(item.delivery_phone)}</td>
          <td class="right">{format_money(item.total_price)}</td>
        </tr>
        """
        for index, item in enumerate(items, start=1)
    )

    return f"""
    <!DOCTYPE html>
    <html lang="ru">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Лист доставки</title>
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
            max-width: 1200px;
            margin: 0 auto;
            background: #fff;
            padding: 40px 48px;
            box-shadow: 0 24px 60px rgba(15, 23, 42, 0.12);
          }}
          .headline {{
            font-size: 30px;
            font-weight: 800;
            margin-bottom: 6px;
          }}
          .subline {{
            color: #4b5563;
            margin-bottom: 24px;
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
            text-align: left;
          }}
          th {{
            font-size: 14px;
          }}
          .right {{
            text-align: right;
          }}
          .meta {{
            display: grid;
            gap: 8px;
            margin-bottom: 16px;
          }}
          .footer {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-top: 28px;
          }}
          .sign-box {{
            min-height: 84px;
            border: 1px solid #111827;
            padding: 16px;
          }}
        </style>
      </head>
      <body>
        <div class="page">
          <div class="headline">Лист доставки</div>
          <div class="subline">{html_text(organization.display_name)} · {format_date_ru(context['generated_at'])}</div>
          <div class="meta">
            <div><b>Организация:</b> {html_text(organization.legal_name)}</div>
            <div><b>Телефон:</b> {html_text(organization.phone)} · <b>Адрес:</b> {html_text(organization.mailing_address or organization.legal_address)}</div>
            <div><b>Всего нарядов:</b> {len(items)}</div>
          </div>

          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Клиент</th>
                <th>Наряд</th>
                <th>Заголовок</th>
                <th>Работы</th>
                <th>Пациент</th>
                <th>Врач</th>
                <th>Адрес доставки</th>
                <th>Контакт</th>
                <th>Телефон</th>
                <th>Сумма</th>
              </tr>
            </thead>
            <tbody>
              {rows}
            </tbody>
          </table>

          <div class="footer">
            <div class="sign-box"><b>Курьер</b><br /><br />____________________________</div>
            <div class="sign-box"><b>Принял клиент</b><br /><br />____________________________</div>
          </div>
        </div>
      </body>
    </html>
    """
