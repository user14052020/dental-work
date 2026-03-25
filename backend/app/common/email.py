from __future__ import annotations

import asyncio
import smtplib
import ssl
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formataddr


@dataclass
class SmtpSettings:
    host: str
    port: int
    username: str | None = None
    password: str | None = None
    from_email: str | None = None
    from_name: str | None = None
    reply_to: str | None = None
    use_tls: bool = True
    use_ssl: bool = False

    @property
    def is_configured(self) -> bool:
        return bool(self.host and self.from_email)


class SmtpEmailSender:
    async def send_html(
        self,
        *,
        settings: SmtpSettings,
        recipient_email: str,
        subject: str,
        html_body: str,
    ) -> None:
        await asyncio.to_thread(
            self._send_sync,
            settings=settings,
            recipient_email=recipient_email,
            subject=subject,
            html_body=html_body,
        )

    @staticmethod
    def _send_sync(
        *,
        settings: SmtpSettings,
        recipient_email: str,
        subject: str,
        html_body: str,
    ) -> None:
        message = EmailMessage()
        message["To"] = recipient_email
        message["Subject"] = subject
        message["From"] = (
            formataddr((settings.from_name, settings.from_email)) if settings.from_name else settings.from_email
        )
        if settings.reply_to:
            message["Reply-To"] = settings.reply_to
        message.set_content("Откройте письмо в HTML-совместимом почтовом клиенте.")
        message.add_alternative(html_body, subtype="html")

        if settings.use_ssl:
            smtp_client = smtplib.SMTP_SSL(settings.host, settings.port, timeout=20)
        else:
            smtp_client = smtplib.SMTP(settings.host, settings.port, timeout=20)

        with smtp_client as client:
            if settings.use_tls and not settings.use_ssl:
                client.starttls(context=ssl.create_default_context())
            if settings.username:
                client.login(settings.username, settings.password or "")
            client.send_message(message)
