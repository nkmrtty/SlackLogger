from slacklogger import SlackLogger
import sys
import os
import os.path

if __name__ == "__main__":
    pypath = sys.argv[0]
    os.chdir(os.path.dirname(pypath))
    sl = SlackLogger()
    sl.run()
