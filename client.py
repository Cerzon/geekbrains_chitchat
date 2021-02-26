""" Внезапно решил точно последовать букве задания и реализовать параметры
    командной строки именно в том виде, что описан в тексте ДЗ
"""

from contextlib import closing
import sys

from geekchat.messages import create_request, ACTIONS, ACT_MSG, ACT_PRESENCE
from geekchat.transport import chat_socket, send_msg, receive_msg
from geekchat.settings import PORT


def main(addr, port):
    with closing(chat_socket(addr, port)) as client:

        account_name = ''
        while not account_name:
            account_name = input('login: ')
        status = input('status: ')

        # initial request-response session
        kwargs = ACTIONS[ACT_PRESENCE](account_name, status)
        rqst = create_request(ACT_PRESENCE, **kwargs)
        send_msg(client, rqst)
        resp = receive_msg(client)
        print(resp)

        # main loop
        while True:
            print('type /quit for quit')
            user_input = input('Message: ')
            rqst = None

            # parse user input
            if user_input.startswith('/'):
                action, *args = user_input[1:].split()
                kwargs = ACTIONS.get(action.lower(), None)
                if callable(kwargs):
                    try:
                        kwargs = kwargs(*args)
                    except TypeError:
                        kwargs = None
                if kwargs is not None:
                    rqst = create_request(action.lower(), **kwargs)
            else:
                kwargs = ACTIONS[ACT_MSG]('somebody', account_name, '', user_input)
                rqst = create_request(ACT_MSG, **kwargs)

            if rqst:
                send_msg(client, rqst)
                resp = receive_msg(client)
                print(resp)
                if 'Bye' in resp:
                    break


if __name__ == '__main__':
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
        main(addr, port)
