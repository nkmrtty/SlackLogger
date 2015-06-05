import ConfigParser
from codecs import open

if __name__ == "__main__":
    print "Start configulation for SlackLogger"
    token = raw_input("Put Web API token > ").decode("utf-8")
    notification_chname = \
        raw_input("Put channel name to notify the result > ").decode("utf-8")
    addr = raw_input("Put your gmail address > ")
    passwd = raw_input("Put your gmail password > ")

    config = ConfigParser.RawConfigParser()
    config.add_section("slack")
    config.set("slack", "token", token)
    config.set("slack", "notification_chname", notification_chname)
    config.add_section("gmail")
    config.set("gmail", "addr", addr)
    config.set("gmail", "passwd", passwd)

    with open("config.ini", "wb", "utf-8") as fp:
        config.write(fp)