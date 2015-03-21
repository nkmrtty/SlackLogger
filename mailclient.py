import smtplib
from email.MIMEText import MIMEText
from email.Utils import formatdate
from email.Header import Header


class MailClient:
    def __init__(self):
        # Gmail account
        self.gmail_addr = "address@sample.com"
        self.gmail_pw = "password"

        # Gmail server
        self.gmail_smtp_addr = "smtp.gmail.com"
        self.gmail_smtp_port = 587

        # header
        self.from_addr = self.gmail_addr
        self.to_addr = "to_address@sample.com"

    def send(self, date, channel, text):
        subject = u"[SlackLogger] {} #{}".format(date, channel)
        body = text

        # generate message
        msg = MIMEText(body.encode("utf-8"), "plain", "utf-8")
        msg["From"] = self.from_addr
        msg["To"] = self.to_addr
        msg["Date"] = formatdate()
        msg["Subject"] = Header(subject.encode("utf-8"), "utf-8")

        # connect & send
        smtpobj = smtplib.SMTP(self.gmail_smtp_addr, self.gmail_smtp_port)
        smtpobj.ehlo()
        smtpobj.starttls()
        smtpobj.ehlo()
        smtpobj.login(self.gmail_addr, self.gmail_pw)
        smtpobj.sendmail(
            self.from_addr, self.to_addr, msg.as_string()
        )
        smtpobj.close()
