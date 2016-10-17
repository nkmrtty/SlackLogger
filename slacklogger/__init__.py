# coding: utf-8
import re
import time
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
        ntf_chname = config.get('logger', 'ntf_chname')
        addr = config.get('logger', 'addr')
        passwd = config.get('logger', 'passwd')
        return token, ntf_chname, addr, passwd
    else:
        configure(fpath)
        return read_config(fpath)


def configure(fpath):
    token = raw_input('[API token] > ').decode('utf-8')
    ntf_chname = raw_input(
        '[Channel name for notification] > ').decode('utf-8')
    addr = raw_input('[Gmail address] > ')
    passwd = raw_input('[Gmail passwd] > ')

    config = ConfigParser.RawConfigParser()
    config.add_section('logger')
    config.set('logger', 'token', token)
    config.set('logger', 'ntf_chname', ntf_chname)
    config.set('logger', 'addr', addr)
    config.set('logger', 'passwd', passwd)

    with open(fpath, 'wb') as fp:
        config.write(fp)


class SlackLogger(object):
    # regexps
    mention_user = re.compile(ur"<@(?P<uid>[^@>|]+)(\|[^>\|]+)?>", re.U)
    mention_channel = re.compile(ur"<!channel>", re.U)
    mention_everyone = re.compile(ur"<!everyone>", re.U)

    def __init__(self, config_fpath=None):
        config_fpath = config_fpath or './config.ini'
        TOKEN, NTF_CHNAME, ADDR, PASSWD = read_config(config_fpath)

        self.slack = SlackClient(TOKEN)
        self.mail = MailClient(ADDR, PASSWD)

        # prefetch
        self.members = self.fetch_members()
        self.channels, self.ntf_chid = self.fetch_channels(NTF_CHNAME)

    def fetch_members(self):
        response = self.slack.api_call('users.list')
        members = {}
        for m in response['members']:
            members[m['id']] = m['name']
        return members

    def fetch_channels(self, ntf_chname):
        response = self.slack.api_call('channels.list')
        channels = {}
        ntf_chid = None
        for c in response['channels']:
            channels[c['id']] = c['name']
            if c['name'] == ntf_chname:
                ntf_chid = c['id']
        return channels, ntf_chid

    def fetch_channel_history(self, channel, oldest, latest):
        def repl_userid(obj):
            uid = obj.group("uid")
            uname = u"@{}".format(self.members[uid])
            return uname

        response = self.slack.api_call(
            'channels.history', channel=channel, oldest=oldest,
            latest=latest, inclusive=1, count=1000)

        history = []
        for msg in response['messages']:
            ts = time.strftime(
                "%H:%M", time.localtime(int(float(msg["ts"]))))
            text = msg['text']
            text = self.mention_user.sub(repl_userid, text)
            text = self.mention_channel.sub('@channel', text)
            text = self.mention_everyone.sub('@everyone', text)

            if 'user' in msg:
                user = self.members[msg['user']]
            else:
                user = 'SYSTEM'

            history.append((ts, user, text))
        if response['has_more']:
            time.sleep(0.5)
            next_latest = response['messages'][-1]['ts']
            history.extend(self.fetch_channel_history(
                channel, oldest, next_latest))

        return history


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
