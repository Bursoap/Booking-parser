from scrapy.mail import MailSender
from scrapy.utils.python import to_bytes
import env


class ScrapyMailSender(MailSender):

    def __init__(self):
        super(ScrapyMailSender, self).__init__()
        self.smtphost = "smtp.gmail.com"
        self.smtpport = 587
        self.smtpuser = self._to_bytes_or_none(env.SMTPUSER)
        self.smtppass = self._to_bytes_or_none(env.SMTPPASS)
        self.smtptls = True
        self.mailfrom = "Scrapy"

    def send_email(self, data):
        self.send(to=[f"{env.MAIL_TO}"], subject="Scrapy booking report", body=data)

    @staticmethod
    def _to_bytes_or_none(text):
        if text is None:
            return None
        return to_bytes(text)
