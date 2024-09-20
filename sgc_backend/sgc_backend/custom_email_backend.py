import smtplib
import ssl
from django.core.mail.backends.smtp import EmailBackend
import logging

logger = logging.getLogger(__name__)

class CustomEmailBackend(EmailBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.local_hostname = kwargs.get('local_hostname', None)
        self.source_address = kwargs.get('source_address', None)  # Initialize source_address

    def _get_ssl_context(self):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context

    def open(self):
        if self.connection:
            return False
        connection_class = smtplib.SMTP_SSL if self.use_ssl else smtplib.SMTP
        self.connection = connection_class(
            self.host,
            self.port,
            local_hostname=self.local_hostname,
            timeout=self.timeout,
            source_address=self.source_address,  # Use source_address
        )
        if self.use_tls:
            try:
                self.connection.starttls(context=self._get_ssl_context())
            except smtplib.SMTPNotSupportedError:
                logger.warning("STARTTLS extension not supported by server.")
        if self.username and self.password:
            try:
                self.connection.login(self.username, self.password)
            except smtplib.SMTPException as e:
                logger.error(f"SMTP login failed: {e}")
                self.close()
                return False
        return True