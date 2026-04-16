"""
Email Tool for sending emails via SMTP with retry logic and error handling.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

@dataclass
class EmailConfig:
    """Email configuration settings."""
    smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    use_tls: bool = True
    from_email: str = os.getenv("SMTP_USERNAME", "")
    from_name: str = "Cold Outreach System"

@dataclass
class EmailResult:
    """Result of email sending operation."""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    attempts: int = 0

class EmailTool:
    """Tool for sending emails with retry logic and error handling."""

    def __init__(self, config: Optional[EmailConfig] = None):
        self.config = config or EmailConfig()
        self.max_retries = 3
        self.retry_delay = 2  # seconds

        # Validate configuration
        if not self.config.smtp_username or not self.config.smtp_password:
            logger.warning("SMTP credentials not configured. Email sending will fail.")

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool = False,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> EmailResult:
        """
        Send an email with retry logic.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            is_html: Whether body is HTML
            cc: CC recipients
            bcc: BCC recipients
            attachments: List of attachments (dict with filename, content, content_type)

        Returns:
            EmailResult object
        """
        if not self._is_valid_email(to_email):
            return EmailResult(
                success=False,
                error=f"Invalid email address: {to_email}",
                attempts=0
            )

        # Validate all email addresses
        all_emails = [to_email]
        if cc:
            all_emails.extend(cc)
        if bcc:
            all_emails.extend(bcc)

        for email in all_emails:
            if not self._is_valid_email(email):
                return EmailResult(
                    success=False,
                    error=f"Invalid email address: {email}",
                    attempts=0
                )

        # Attempt sending with retries
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Attempt {attempt}/{self.max_retries}: Sending email to {to_email}")
                result = self._send_email_attempt(
                    to_email, subject, body, is_html, cc, bcc, attachments
                )
                if result.success:
                    logger.info(f"Email sent successfully to {to_email}")
                    return result
                else:
                    logger.warning(f"Attempt {attempt} failed: {result.error}")
                    if attempt < self.max_retries:
                        logger.info(f"Retrying in {self.retry_delay} seconds...")
                        time.sleep(self.retry_delay)
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt}: {str(e)}")
                if attempt == self.max_retries:
                    return EmailResult(
                        success=False,
                        error=f"Failed after {self.max_retries} attempts: {str(e)}",
                        attempts=attempt
                    )
                time.sleep(self.retry_delay)

        return EmailResult(
            success=False,
            error=f"Failed to send email after {self.max_retries} attempts",
            attempts=self.max_retries
        )

    def _send_email_attempt(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool,
        cc: Optional[List[str]],
        bcc: Optional[List[str]],
        attachments: Optional[List[Dict[str, Any]]]
    ) -> EmailResult:
        """Single email sending attempt."""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.config.from_name} <{self.config.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)

            # Add body
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            # Add attachments
            if attachments:
                for attachment in attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment['content'])
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {attachment["filename"]}'
                    )
                    msg.attach(part)

            # Create secure connection and send email
            context = ssl.create_default_context()

            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls(context=context)
                server.login(self.config.smtp_username, self.config.smtp_password)
                text = msg.as_string()
                recipients = [to_email]
                if cc:
                    recipients.extend(cc)
                if bcc:
                    recipients.extend(bcc)
                server.sendmail(self.config.from_email, recipients, text)

            return EmailResult(
                success=True,
                message_id=f"<{int(time.time())}.{hash(to_email + subject)}@cold-email-system>",
                attempts=1
            )

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication error: {str(e)}")
            return EmailResult(
                success=False,
                error="SMTP authentication failed. Check username and password.",
                attempts=1
            )
        except smtplib.SMTPRecipientsRefused as e:
            logger.error(f"SMTP recipients refused: {str(e)}")
            return EmailResult(
                success=False,
                error=f"Recipient email refused: {to_email}",
                attempts=1
            )
        except smtplib.SMTPServerDisconnected as e:
            logger.error(f"SMTP server disconnected: {str(e)}")
            return EmailResult(
                success=False,
                error="SMTP server disconnected",
                attempts=1
            )
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            return EmailResult(
                success=False,
                error=f"Failed to send email: {str(e)}",
                attempts=1
            )

    def _is_valid_email(self, email: str) -> bool:
        """Basic email validation."""
        if not email or '@' not in email:
            return False
        parts = email.split('@')
        if len(parts) != 2:
            return False
        if not parts[0] or not parts[1]:
            return False
        if '.' not in parts[1]:
            return False
        return True

    def send_bulk_emails(
        self,
        emails: List[Dict[str, Any]],
        delay_between_emails: float = 1.0
    ) -> List[EmailResult]:
        """
        Send multiple emails with delay between each.

        Args:
            emails: List of email dictionaries with keys: to_email, subject, body, etc.
            delay_between_emails: Delay in seconds between each email

        Returns:
            List of EmailResult objects
        """
        results = []
        for i, email_data in enumerate(emails):
            logger.info(f"Sending email {i+1}/{len(emails)}")
            result = self.send_email(**email_data)
            results.append(result)

            # Delay between emails (except for the last one)
            if i < len(emails) - 1:
                time.sleep(delay_between_emails)

        return results


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    tool = EmailTool()

    # Test email sending (will fail without valid SMTP credentials)
    result = tool.send_email(
        to_email="test@example.com",
        subject="Test Email from Cold Email System",
        body="This is a test email from the AI Cold Email Outreach System.",
        is_html=False
    )

    print(f"Email send result: {result}")