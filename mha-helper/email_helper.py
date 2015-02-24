# (c) 2013, Ovais Tariq <ovaistariq@gmail.com>
#
# This file is part of mha-helper
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
