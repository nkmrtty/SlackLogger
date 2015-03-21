# SlackLogger
Logging all messages of Slack on yesterday using Gmail

## Requirements

* Python 2.7.x
* slackclient (from pip)

## Configuration

### slacklogger.py

* line 11 `token`: Access token
* line 16 `self.channel_notify`: Channel ID for completion notification

### mailclient.py

* line 10 `self.gmail_addr`: your gmail address
* line 11 `self.gmail_pw`: your gmail password
* line 19 `self.to_addr`: To address (Log data is sent to this address)

## How to use

```
python run.py
```