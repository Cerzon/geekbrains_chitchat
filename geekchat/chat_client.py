from contextlib import closing
from socket import socket
from threading import Thread
from queue import Queue

from .protocol import compose_request, ACTION_TPLS, ACT_MSG, ACT_PRESENCE
from .transport import chat_socket, send_data, receive_data
from .log.client_log_config import start_logger
from .log.staff import logged


start_logger()


@logged
def start_client(addr: str, port: int):

    client = chat_socket(addr, port)
    user_input_queue = Queue()
    received_data_queue = Queue()

    with closing(client):

        account_name = ''

        while not account_name:
            account_name = input('login: ')

        Thread(target=user_input_loop, args=(user_input_queue,)).start()
        Thread(target=receive_data_loop, args=(client, received_data_queue)).start()

        # main loop
        while True:
            if not user_input_queue.empty():
                user_input = user_input_queue.get()
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
                
                user_input_queue.task_done()

                if rqst:
                    send_data(client, rqst)

            if not received_data_queue.empty():
                resp = received_data_queue.get()
                print(resp)
                received_data_queue.task_done()


@logged
def user_input_loop(user_input_queue: Queue):
    while True:
        user_input = input()
        if user_input:
            user_input_queue.put_nowait(user_input)


@logged
def receive_data_loop(src_sock: socket, received_data_queue: Queue):
    while True:
        received_data_queue.put_nowait(receive_data(src_sock))
