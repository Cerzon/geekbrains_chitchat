from contextlib import closing

from .protocol import compose_request, ACTION_TPLS, ACT_MSG, ACT_PRESENCE
from .transport import chat_socket, send_data, receive_data
from .log.client_log_config import start_logger
from .log.staff import logged


start_logger()


@logged
def start_client(addr: str, port: int, sender: bool=False):
    """ If sender is True - only sends data to server,
        otherwise listen only
    """
    client = chat_socket(addr, port)

    with closing(client):

        account_name = ''

        if sender:
            while not account_name:
                account_name = input('login: ')
            status = input('status: ')

            # initial request-response session
            rqst = compose_request(ACT_PRESENCE, account_name, status)
            send_data(client, rqst)

        # main loop
        while True:
            if sender:
                print('type /quit for quit')
                user_input = input('Message: ')
                rqst = None

                # parse user input
                if user_input.startswith('/'):
                    action, *args = user_input[1:].split()
                    action = action.lower()
                    if action in ACTION_TPLS:
                        rqst = compose_request(action, *args)
                elif user_input:
                    rqst = compose_request(ACT_MSG, 'somebody',
                                            account_name, '', user_input)

                if rqst:
                    send_data(client, rqst)
            else:
                resp = receive_data(client)
                print(resp)
