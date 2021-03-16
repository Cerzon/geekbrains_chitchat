from contextlib import closing
import json
import selectors

from .protocol import (compose_response, check_request, ACT_PRESENCE, ACT_MSG,
                        ACT_QUIT, FIELD_ACC, FIELD_ACTION, FIELD_TIME,
                        FIELD_RCPNT, FIELD_USER, CODE_RESP_OK,
                        CODE_RESP_ACCEPTED, CODE_ERR_WRONG_DATA)
from .transport import chat_socket, send_data, receive_data
from .log.server_log_config import start_logger
from .log.staff import logged


LOGGER = start_logger()


@logged
def accept_connection(sel, subscribers, srv_listen_socket, _):
    convo_socket, addr = srv_listen_socket.accept()
    LOGGER.info(f'Соединение с адресом {addr}')
    convo_socket.setblocking(False)
    sel.register(
        convo_socket,
        selectors.EVENT_READ | selectors.EVENT_WRITE,
        process_events
    )
    subscribers[convo_socket] = ''


@logged
def disconnect_subscriber(sel, subscribers, convo_socket):
    LOGGER.info('Соединение %s закрыто' % convo_socket.fileno())
    sel.unregister(convo_socket)
    convo_socket.close()
    del subscribers[convo_socket]


@logged
def process_events(sel, subscribers, convo_socket, mask):
    if mask & selectors.EVENT_READ:
        try:
            incoming = receive_data(convo_socket)
        except:
            disconnect_subscriber(sel, subscribers, convo_socket)
        for sub_socket in subscribers:
            if sub_socket is convo_socket:
                continue
            subscribers[sub_socket] += incoming

    if mask & selectors.EVENT_WRITE:
        outgoing = subscribers[convo_socket]
        if outgoing:
            try:
                send_data(convo_socket, outgoing)
            except:
                disconnect_subscriber(sel, subscribers, convo_socket)


@logged
def start_server(addr: str, port: int):
    srv_listen_socket = chat_socket(addr, port, server=True)
    srv_listen_socket.setblocking(False)

    subscribers = {}

    with closing(srv_listen_socket):
        with selectors.DefaultSelector() as sel:
            sel.register(
                srv_listen_socket,
                selectors.EVENT_READ,
                accept_connection
            )
            while True:
                events = sel.select()
                for key, mask in events:
                    callback = key.data
                    callback(sel, subscribers, key.fileobj, mask)


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
