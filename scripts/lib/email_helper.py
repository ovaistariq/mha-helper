import socket
import smtplib
from email.mime.text import MIMEText

class Email_helper(object):
    SMTP_HOST = "localhost"
    SENDER = "mha_helper@%s" % socket.getfqdn()

    def __init__(self):
        self._email_sender = smtplib.SMTP(Email_helper.SMTP_HOST)

    def send_email(self, subject, msg, to_email_list):
        if len(to_email_list) < 1:
            return False

        email_sender = smtplib.SMTP(Email_helper.SMTP_HOST)

        email_msg = MIMEText(msg)
        email_msg['Subject'] = subject
        email_msg['From'] = Email_helper.SENDER
        email_msg['To'] = ', '.join(to_email_list)

        email_sender.sendmail(Email_helper.SENDER, to_email_list,
                                email_msg.as_string())
        email_sender.quit()

        return True
