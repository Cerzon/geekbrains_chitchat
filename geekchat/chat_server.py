from contextlib import closing
import json

from .protocol import (compose_response, check_request, ACT_PRESENCE, ACT_MSG,
                        ACT_QUIT, FIELD_ACC, FIELD_ACTION, FIELD_TIME,
                        FIELD_RCPNT, FIELD_USER, CODE_RESP_OK,
                        CODE_RESP_ACCEPTED, CODE_ERR_WRONG_DATA)
from .transport import chat_socket, send_data, receive_data
from .log.server_log_config import start_logger
from .log.staff import logged


start_logger()


@logged
def start_server(addr: str, port: int):
    srv = chat_socket(addr, port, server=True)

    with closing(srv):

        with closing(srv.accept()[0]) as convo:
            keep_connection = True
            while keep_connection:
                incoming = receive_data(convo)
                response, keep_connection = process_request(incoming)
                send_data(convo, response)


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
