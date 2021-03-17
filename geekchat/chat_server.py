from contextlib import closing
import json
from select import select

from .protocol import (compose_response, check_request, ACT_PRESENCE, ACT_MSG,
                        ACT_QUIT, FIELD_ACC, FIELD_ACTION, FIELD_TIME,
                        FIELD_RCPNT, FIELD_USER, CODE_RESP_OK,
                        CODE_RESP_ACCEPTED, CODE_ERR_WRONG_DATA)
from .transport import chat_socket, send_data, receive_data
from .log.server_log_config import start_logger
from .log.staff import logged


LOGGER = start_logger()


@logged
def read_requests(sockets_to_read, all_connections):
    
    requests = {}
    
    for source in sockets_to_read:
        try:
            data = receive_data(source)
            requests[source] = data
        except:
            LOGGER.info(f'Соединение {source.fileno()} разорвано')
            all_connections.remove(source)
            source.close()
    
    return requests


@logged
def write_responses(requests, sockets_to_write, all_connections):
    
    for source, data in requests.items():
        for destination in sockets_to_write:
            if destination is source:
                continue
            try:
                send_data(destination, data)
            except:
                LOGGER.info(f'Соединение {destination.fileno()} разорвано')
                all_connections.remove(destination)
                destination.close()


@logged
def start_server(addr: str, port: int):
    srv_listen_socket = chat_socket(addr, port, server=True)
    srv_listen_socket.settimeout(0.2)
    wait = 0

    all_connections = []

    with closing(srv_listen_socket):
        while True:
            try:
                connection, c_addr = srv_listen_socket.accept()
            except OSError:
                pass
            else:
                LOGGER.info(f'Соединение {connection.fileno()} с адресом {c_addr}')
                all_connections.append(connection)
            finally:
                r = []
                w = []
                try:
                    r, w, _ = select(all_connections, all_connections, [], wait)
                except:
                    pass

                requests = read_requests(r, all_connections)
                write_responses(requests, w, all_connections)


@logged
def response_presence(**kwargs):
    info = 'Hello {}!'.format(kwargs.get(FIELD_USER, {}).get(FIELD_ACC, None))
    return compose_response(CODE_RESP_OK, info), True


@logged
def response_msg(**kwargs):
    info = 'Your message sent to {}'.format(kwargs.get(FIELD_RCPNT, None))
    return compose_response(CODE_RESP_ACCEPTED, info), True


@logged
def response_wrong_data(*args):
    return compose_response(CODE_ERR_WRONG_DATA, *args), True


@logged
def response_quit():
    return compose_response(CODE_RESP_OK, 'Bye'), False


@logged
def process_request(rqst: str):
    try:
        request = json.loads(rqst)
    except json.JSONDecodeError:
        return response_wrong_data('JIM protocol not followed')

    is_correct, err_desc = check_request(request)
    if not is_correct:
        return response_wrong_data(err_desc)

    action = request.pop(FIELD_ACTION, None)
    rq_time = request.pop(FIELD_TIME, None)
    print(rq_time)
    dispatcher = {
        ACT_PRESENCE: response_presence,
        ACT_MSG: response_msg,
        ACT_QUIT: response_quit,
    }
    if action in dispatcher:
        return dispatcher[action](**request)
    return response_wrong_data('action not implemented')
