import time
import json
from datetime import date, timedelta
from slackclient import SlackClient
from mailclient import MailClient


class SlackLogger:
    def __init__(self):
        # Slack API
        token = "XXXXX-0123456789"
        self.sc = SlackClient(token)
        self.members = self.fetch_members_list()
        self.channels = self.fetch_channels_list()
        # channel for notification
        self.channel_notify = "ChannelID"
        # date setting
        self.today = date.today()
        self.today_timestamp = time.mktime(self.today.timetuple())
        self.yesterday = self.today - timedelta(days=1)
        self.yesterday_timestamp = time.mktime(self.yesterday.timetuple())
        self.yesterday_str = self.yesterday.strftime("%y-%m-%d")
        # mail client
        self.mc = MailClient()

    def api_call(self, method, **kw):
        res = self.sc.api_call(method, **kw)
        res = json.loads(res)
        return res

    def fetch_members_list(self):
        res = self.api_call("users.list")
        members = {}
        for mem in res["members"]:
            members[mem["id"]] = mem["name"]
        return members

    def fetch_channels_list(self):
        res = self.api_call("channels.list")
        channels = {}
        for ch in res["channels"]:
            channels[ch["id"]] = ch["name"]
        return channels

    def fetch_channels_history(self, channel, latest=None):
        if latest:
            res = self.api_call(
                "channels.history", channel=channel,
                latest=latest, oldest=self.yesterday_timestamp,
                inclusive=1, count=1000)
        else:
            res = self.api_call(
                "channels.history", channel=channel,
                latest=self.today_timestamp, oldest=self.yesterday_timestamp,
                inclusive=1, count=1000)
        log = []
        for msg in res["messages"]:
            if msg["type"] == "message":
                ts = int(float(msg["ts"]))
                ts_hm = time.strftime("%H:%M", time.localtime(ts))
                text = msg["text"]
                if "comment" in msg:
                    user = self.members[msg["comment"]["user"]]
                else:
                    user = self.members[msg["user"]]
                log.append((ts_hm, user, text))
        if "has_more" in res:
            if res["has_more"]:
                log.extend(self.fetch_channels_history(channel, ts))
        return log

    def parse_log(self, log):
        prev_user = None
        log_text = u""
        for ts, user, text in log:
            if not prev_user == user:
                log_text += u"\n{}\n".format(user)
                prev_user = user
            log_text += u"{}: {}\n".format(ts, text)
        return log_text

    def send_mail(self, channel, log_text):
        self.mc.send(self.yesterday_str, channel, log_text)

    def notify_to_slack(self):
        text = "Logging on {} has been completed successfully."\
            .format(self.yesterday_str)
        botname = "SlackLogger"
        self.api_call("chat.postMessage", channel=self.channel_notify,
            text=text, username=botname)

    def run(self):
        for ch, ch_name in self.channels.iteritems():
            print ch, ch_name
            log = self.fetch_channels_history(ch)
            if not log:
                continue
            log_text = self.parse_log(reversed(log))
            self.send_mail(ch_name, log_text)
        self.notify_to_slack()
