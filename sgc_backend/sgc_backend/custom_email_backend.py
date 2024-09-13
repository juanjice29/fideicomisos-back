import smtplib
from django.core.mail.backends.smtp import EmailBackend
from urllib.parse import urlparse

class ProxyEmailBackend(EmailBackend):
    def __init__(self, *args, **kwargs):
        self.proxy_url = kwargs.pop('proxy_url', None)
        super().__init__(*args, **kwargs)

    def _get_connection(self):
        if self.proxy_url:
            proxy = urlparse(self.proxy_url)
            proxy_host = proxy.hostname
            proxy_port = proxy.port
            proxy_username = proxy.username
            proxy_password = proxy.password

            # Create a connection to the proxy
            connection = smtplib.SMTP(proxy_host, proxy_port)
            if proxy_username and proxy_password:
                connection.login(proxy_username, proxy_password)
            
            # Connect to the actual SMTP server through the proxy
            connection.starttls()
            connection.connect(self.host, self.port)
            if self.username and self.password:
                connection.login(self.username, self.password)
            return connection
        else:
            return super()._get_connection()