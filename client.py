import sys

from geekchat.chat_client import start_client
from geekchat.settings import PORT


err_flag = False
addr = ''
port = 0
args = sys.argv[1:]
if 1 <= len(args) <=2:
    addr, *port = args
    if port:
        try:
            port = int(port[0])
        except ValueError:
            err_flag = True
    else:
        port = PORT
else:
    err_flag = True

if err_flag:
    print('Usage: client.py <addr> [<port>]\n\n'\
        'addr\t\t- server ip or host name\n'\
        'port (optional)\t- port number; must be integer (default = %d)' % PORT)
else:
    start_client(addr, port)
