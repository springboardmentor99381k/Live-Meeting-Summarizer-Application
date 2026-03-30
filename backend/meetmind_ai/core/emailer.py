import os
import re
import smtplib
import socket
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional


class Emailer:
    """Send meeting summaries via SMTP over SSL."""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = os.getenv("SMTP_PORT")
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")

    def send(
        self,
        recipient_email: str,
        subject: Optional[str],
        body: str,
        attachment_path: Optional[str] = None,
    ) -> bool:
        """Send a plain-text email with optional file attachment."""
        smtp_connection: Optional[smtplib.SMTP_SSL] = None

        final_subject = (subject or "").strip() or "MeetMind AI - Meeting Summary"

        try:
            self._validate_config()
            self._validate_email(recipient_email)

            message = MIMEMultipart()
            message["From"] = self.smtp_user
            message["To"] = recipient_email
            message["Subject"] = final_subject
            message.attach(MIMEText(body or "", "plain", "utf-8"))

            if attachment_path:
                self._attach_file(message, attachment_path)

            smtp_connection = smtplib.SMTP_SSL(
                host=self.smtp_host,
                port=int(self.smtp_port),
                timeout=15,
            )
            smtp_connection.login(self.smtp_user, self.smtp_password)
            smtp_connection.sendmail(
                self.smtp_user,
                [recipient_email],
                message.as_string(),
            )
            return True

        except ValueError as exc:
            print(f"[Emailer] Validation error: {exc}")
            return False
        except smtplib.SMTPAuthenticationError:
            print("[Emailer] SMTP authentication failed. Check SMTP_USER and SMTP_PASSWORD.")
            return False
        except smtplib.SMTPRecipientsRefused:
            print(f"[Emailer] Recipient address was refused by the server: {recipient_email}")
            return False
        except (socket.timeout, TimeoutError):
            print("[Emailer] SMTP connection timed out. Check SMTP_HOST/SMTP_PORT and network access.")
            return False
        except smtplib.SMTPConnectError as exc:
            print(f"[Emailer] Could not connect to SMTP server: {exc}")
            return False
        except (smtplib.SMTPException, OSError) as exc:
            print(f"[Emailer] Failed to send email: {exc}")
            return False
        finally:
            if smtp_connection is not None:
                try:
                    smtp_connection.quit()
                except Exception:
                    pass

    def _validate_config(self) -> None:
        missing = []
        if not self.smtp_host:
            missing.append("SMTP_HOST")
        if not self.smtp_port:
            missing.append("SMTP_PORT")
        if not self.smtp_user:
            missing.append("SMTP_USER")
        if not self.smtp_password:
            missing.append("SMTP_PASSWORD")

        if missing:
            raise ValueError(f"Missing SMTP environment variables: {', '.join(missing)}")

        try:
            port = int(self.smtp_port)
            if port <= 0:
                raise ValueError
        except ValueError as exc:
            raise ValueError("SMTP_PORT must be a valid positive integer.") from exc

    def _validate_email(self, email: str) -> None:
        candidate = (email or "").strip()
        pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        if not re.match(pattern, candidate):
            raise ValueError(f"Invalid recipient email address: {email}")

    def _attach_file(self, message: MIMEMultipart, attachment_path: str) -> None:
        if not os.path.isfile(attachment_path):
            raise ValueError(f"Attachment file not found: {attachment_path}")

        filename = os.path.basename(attachment_path)
        try:
            with open(attachment_path, "rb") as attachment_file:
                attachment_part = MIMEApplication(attachment_file.read(), Name=filename)
            attachment_part["Content-Disposition"] = f'attachment; filename="{filename}"'
            message.attach(attachment_part)
        except PermissionError as exc:
            raise ValueError(f"Permission denied while reading attachment: {attachment_path}") from exc
        except OSError as exc:
            raise ValueError(f"Could not read attachment file '{attachment_path}': {exc}") from exc
