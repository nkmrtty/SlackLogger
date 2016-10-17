# coding: utf-8
import ConfigParser
from slackclient import SlackClient

import smtplib
from email.MIMEText import MIMEText
from email.Utils import formatdate
from email.Header import Header


def read_config(fpath):
    config = ConfigParser.ConfigParser()
    if config.read(fpath):
        token = config.get('logger', 'token')
        ntf_chname = config.get('logger', 'token')
        addr = config.get('logger', 'token')
        passwd = config.get('logger', 'token')
        return token, ntf_chname, addr, passwd
    else:
        configure(fpath)
        return read_config(fpath)


def configure(fpath):
    token = raw_input('[API token] >').decode('utf-8')
    ntf_chname = raw_input('[Channel name for notification] >').decode('utf-8')
    addr = raw_input('[Gmail address] >')
    passwd = raw_input('[Gmail passwd] >')

    config = ConfigParser.RawConfigParser()
    config.add_section('logger')
    config.set('logger', 'token', token)
    config.set('logger', 'ntf_chname', ntf_chname)
    config.set('logger', 'addr', addr)
    config.set('logger', 'passwd', passwd)

    with open(fpath, 'wb') as fp:
        config.write(fp)


class SlackLogger(object):
    def __init__(self, config_fpath=None):
        config_fpath = config_fpath or './config.ini'
        TOKEN, NTF_CHNAME, ADDR, PASSWD = read_config(config_fpath)

        self.slack = SlackClient(TOKEN)
        self.mail = MailClient(ADDR, PASSWD)


class MailClient:
    def __init__(self, addr, passwd):
        # Gmail account
        self.gmail_addr = addr
        self.gmail_pw = passwd

        # Gmail server
        self.gmail_smtp_addr = "smtp.gmail.com"
        self.gmail_smtp_port = 587

        # header
        self.from_addr = self.gmail_addr
        self.to_addr = self.gmail_addr

    def send(self, subject, body):
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