from contextlib import closing

from .protocol import compose_request, ACTION_TPLS, ACT_MSG, ACT_PRESENCE
from .transport import chat_socket, send_data, receive_data
from .log.client_log_config import start_logger
from .log.staff import logged


start_logger()


@logged
def start_client(addr: str, port: int):
    client = chat_socket(addr, port)

    with closing(client):

        account_name = ''
        while not account_name:
            account_name = input('login: ')
        status = input('status: ')

        # initial request-response session
        rqst = compose_request(ACT_PRESENCE, account_name, status)
        send_data(client, rqst)
        resp = receive_data(client)
        print(resp)

        # main loop
        while True:
            print('type /quit for quit')
            user_input = input('Message: ')
            rqst = None

            # parse user input
            if user_input.startswith('/'):
                action, *args = user_input[1:].split()
                action = action.lower()
                if action in ACTION_TPLS:
                    rqst = compose_request(action, *args)
            else:
                rqst = compose_request(ACT_MSG, 'somebody',
                                        account_name, '', user_input)

            if rqst:
                send_data(client, rqst)
                resp = receive_data(client)
                print(resp)
                if 'Bye' in resp:
                    break
