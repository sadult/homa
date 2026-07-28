"""Mail plugin: check inbox (IMAP) and send mail (SMTP, confirmation-gated)."""
import email
import imaplib
import smtplib
from email.header import decode_header
from email.message import EmailMessage

from config import settings
from tools.registry import Tool, ToolRegistry


def _decode(value):
    if not value:
        return ""
    out = ""
    for text, enc in decode_header(value):
        out += text.decode(enc or "utf-8", errors="ignore") if isinstance(text, bytes) else text
    return out


async def check_mail(from_contains: str = "", subject_contains: str = "", limit: int = 10):
    if not settings.IMAP_HOST:
        return {"error": "IMAP not configured."}
    m = imaplib.IMAP4_SSL(settings.IMAP_HOST)
    m.login(settings.IMAP_USER, settings.IMAP_PASSWORD)
    m.select("INBOX")
    criteria = []
    if from_contains:
        criteria += ["FROM", from_contains]
    if subject_contains:
        criteria += ["SUBJECT", subject_contains]
    _typ, data = m.search(None, *(criteria or ["ALL"]))
    ids = data[0].split()[-limit:]
    results = []
    for i in reversed(ids):
        _typ, msg_data = m.fetch(i, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])
        results.append({"from": _decode(msg.get("From")),
                        "subject": _decode(msg.get("Subject")), "date": msg.get("Date")})
    m.logout()
    return {"count": len(results), "emails": results}


async def send_mail(to: str, subject: str, body: str):
    if not settings.SMTP_HOST:
        return {"error": "SMTP not configured."}
    msg = EmailMessage()
    msg["From"] = settings.IMAP_USER
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as s:
        s.starttls()
        s.login(settings.IMAP_USER, settings.IMAP_PASSWORD)
        s.send_message(msg)
    return {"sent_to": to, "subject": subject}


def register(r: ToolRegistry) -> None:
    C = "mail"
    r.register(Tool("mail.check", "Check recent emails filtered by sender/subject (IMAP).",
        {"type": "object", "properties": {"from_contains": {"type": "string"},
         "subject_contains": {"type": "string"}, "limit": {"type": "integer", "default": 10}}},
        check_mail, category=C))
    r.register(Tool("mail.send", "Send an email (SMTP). Requires confirmation.",
        {"type": "object", "properties": {"to": {"type": "string"}, "subject": {"type": "string"},
         "body": {"type": "string"}}, "required": ["to", "subject", "body"]},
        send_mail, dangerous=True, category=C))
