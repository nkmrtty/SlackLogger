from mailclient import MailClient
from slackclient import SlackClient
from ConfigParser import ConfigParser, NoSectionError
from datetime import date, timedelta
import time
import sys
import json
import re


mention_user = re.compile(ur"<@(?P<uid>[^@>|]+)(\|[^>\|]+)?>", re.U)
mention_channel = re.compile(ur"<!channel>", re.U)
mention_everyone = re.compile(ur"<!everyone>", re.U)


class SlackLogger:
    def __init__(self):
        # read args
        config = ConfigParser()
        if not config.read("config.ini"):
            self.config_error()
        # params
        try:
            token = config.get("slack", "token")
            notification_chname = config.get("slack", "notification_chname")
            addr = config.get("gmail", "addr")
            passwd = config.get("gmail", "passwd")
        except NoSectionError:
            self.config_error("parameters could not read correctly")
        # init
        self.sc = SlackClient(token)
        self.mc = MailClient(addr, passwd)
        # pre-fetch
        self.member_list = self.fetch_members_list()
        self.channel_list, self.notification_chid = \
            self.fetch_channels_list(notification_chname)
        # check
        if not self.notification_chid:
            self.config_error(
                "channel `{}` does not exist".format(notification_chname)
            )
        # date init
        self.today = date.today()
        self.today_timestamp = time.mktime(self.today.timetuple())
        self.yesterday = self.today - timedelta(days=1)
        self.yesterday_timestamp = time.mktime(self.yesterday.timetuple())
        self.yesterday_str = self.yesterday.strftime("%y-%m-%d")

    def config_error(self, reason):
        print "File config.ini is invalid."
        print "REASON: {}".format(reason)
        print "Please run configuration script as follow:"
        print "\t python configure.py"
        sys.exit("exit")

    def repl_userid(self, obj):
        uid = obj.group("uid")
        uname = u"@{}".format(self.member_list[uid])
        print uname
        return uname

    def api_call(self, method, **kw):
        res = self.sc.api_call(method, **kw)
        res = json.loads(res)
        return res

    def fetch_members_list(self):
        res = self.api_call("users.list")
        member_id_name = {}
        for mem in res["members"]:
            member_id_name[mem["id"]] = mem["name"]
        return member_id_name

    def fetch_channels_list(self, notification_chname):
        res = self.api_call("channels.list")
        notification_chid = None
        channel_id_name = {}
        for ch in res["channels"]:
            channel_id_name[ch["id"]] = ch["name"]
            if ch["name"] == notification_chname:
                notification_chid = ch["id"]
        return channel_id_name, notification_chid

    def fetch_channel_history(self, channel, latest=None):
        if latest:
            res = self.api_call(
                "channels.history", channel=channel, latest=latest,
                oldest=self.yesterday_timestamp, inclusive=1, count=1000
            )
        else:
            res = self.api_call(
                "channels.history", channel=channel,
                latest=self.today_timestamp, oldest=self.yesterday_timestamp,
                inclusive=1, count=1000
            )
        log = []
        for msg in res["messages"]:
            ts = int(float(msg["ts"]))
            ts_hm = time.strftime("%H:%M", time.localtime(ts))
            text = msg["text"]
            text = mention_user.sub(self.repl_userid, text)
            text = mention_channel.sub("@channel", text)
            text = mention_everyone.sub("@everyone", text)
            if "user" in msg:
                user = self.member_list[msg["user"]]
            else:
                user = "SYSTEM"
            log.append((ts_hm, user, text))
            if res["has_more"]:
                log.extend(self.fetch_channel_history(channel, ts))
        return log

    def parsing(self, log):
        prev_user = None
        log_text = u""
        for ts, user, text in log:
            if not prev_user == user:
                log_text += u"\n{}\n".format(user)
                prev_user = user
            log_text += u"{}: {}\n".format(ts, text)
        return log_text

    def send_mail(self, channel, log_text):
        subject = u"[SlackLogger] {} #{}".format(self.yesterday_str, channel)
        self.mc.send(subject, log_text)

    def notify_to_slack(self):
        text = "Logging on {} has been completed successfully."\
            .format(self.yesterday_str)
        botname = "SlackLogger"
        self.api_call("chat.postMessage", channel=self.notification_chid,
                      text=text, username=botname)

    def run(self):
        for ch, ch_name in self.channel_list.iteritems():
            print ch, ch_name
            log = self.fetch_channel_history(ch)
            if not log:
                continue
            log_text = self.parsing(reversed(log))
            self.send_mail(ch_name, log_text)
        self.notify_to_slack()
