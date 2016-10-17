# SlackLogger
A tool for logging messages on your Slack term.

## Requirements
* Python 2.7.x
* pip
* GMail account (Logged messages are sent to the account)

## Installation

```bash
$ git clone https://github.com/nkmrtty/SlackLogger.git
$ cd SlackLogger
$ python setup.py install
```

## Example

```python
>>> from slacklogger import SlackLogger
>>> sl = SlackLogger()
[API token] > `Put your API token`
[Target channel names] > `Put channel names that you want to log (nullable)`
[Ignore channel names] > `Put channel names that you do not want to log (nullable)`
[Channel name for notification] > `Put a channel name that you want to nofity the complication (nullable).`
[Gmail address] > `Put your Gmail address`
[Gmail passwd] > `Put your Gmail password`
>>> sl.logging()  # Logging all messages posted on yesterday(2016/10/16)
> Logging on 2016/10/16
>> general done
>> random done
Finished
>>> sl.logging(start='2016/10/01') # Logging all messages posted from 2016/10/01 to yesterday(2016/10/16)
> Logging on 2016/10/01
>> general done
>> random done
> Logging on 2016/10/02
>> general done
>> random done
...
> Logging on 2016/10/16
>> general done
>> random done
Finished
>>>
```

## Milestones
* Support messages in group
* Support direct messages
