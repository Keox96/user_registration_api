import logging

from app.utils.smtp import EmailClient


class EmailConsoleClient(EmailClient):
    async def send_verification_email(self, email: str, code: str):
        logging.info(f"[EMAIL CREATION SERVICE] To={email} Code={code}")
