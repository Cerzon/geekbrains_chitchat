from contextlib import closing

from .protocol import compose_request, ACTION_TPLS, ACT_MSG, ACT_PRESENCE
from .transport import chat_socket, send_data, receive_data
from log.client_log_config import clt_logger


def start_client(addr: str, port: int):
    try:
        client = chat_socket(addr, port)
    except Exception as e:
        clt_logger.critical('Ошибка при создании сокета')
        raise e

    with closing(client):

        account_name = ''
        while not account_name:
            account_name = input('login: ')
        status = input('status: ')

        # initial request-response session
        rqst = compose_request(ACT_PRESENCE, account_name, status)
        try:
            send_data(client, rqst)
            resp = receive_data(client)
        except Exception as e:
            clt_logger.critical('Случилось страшное')
            raise e
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
                try:
                    send_data(client, rqst)
                    resp = receive_data(client)
                except Exception as e:
                    clt_logger.critical('Произошло нечто непоправимое')
                    raise e
                print(resp)
                if 'Bye' in resp:
                    break
