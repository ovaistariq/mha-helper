# (c) 2015, Ovais Tariq <ovaistariq@gmail.com>
#
# This file is part of mha_helper
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

from __future__ import print_function
import socket
import smtplib
from email.mime.text import MIMEText
from mha_helper.config_helper import ConfigHelper


class EmailHelper(object):
    def __init__(self, host):
        config_helper = ConfigHelper(host)
        self._smtp_host = config_helper.get_smtp_host()
        self._sender = "mha_helper@%s" % socket.getfqdn()
        self._receiver = config_helper.get_report_email()

    def send_email(self, subject, msg):
        try:
            smtp = smtplib.SMTP(self._smtp_host)

            email_msg = MIMEText(msg)
            email_msg['Subject'] = subject
            email_msg['From'] = self._sender
            email_msg['To'] = self._receiver

            print("Sending email to %s via %s with the subject '%s'" % (self._receiver, self._smtp_host, subject))
            smtp.sendmail(self._sender, self._receiver, email_msg.as_string())
            smtp.quit()
        except Exception as e:
            print("Failed to send email From: %s, To: %s" % (self._sender, self._receiver))
            print(str(e))
            return False

        return True
