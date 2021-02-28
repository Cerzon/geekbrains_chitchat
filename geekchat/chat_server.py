from contextlib import closing
import json

from .protocol import (compose_response, check_request, ACT_PRESENCE, ACT_MSG,
                        ACT_QUIT, FIELD_ACC, FIELD_ACTION, FIELD_TIME,
                        FIELD_RCPNT, FIELD_USER, CODE_RESP_OK,
                        CODE_RESP_ACCEPTED, CODE_ERR_WRONG_DATA)
from .transport import chat_socket, send_data, receive_data


def start_server(addr: str, port: int):
    with closing(chat_socket(addr, port, server=True)) as srv:

        with closing(srv.accept()[0]) as convo:
            keep_connection = True
            while keep_connection:
                response, keep_connection = process_request(receive_data(convo))
                send_data(convo, response)


def response_presence(**kwargs):
    info = 'Hello {}!'.format(kwargs.get(FIELD_USER, {}).get(FIELD_ACC, None))
    return compose_response(CODE_RESP_OK, info), True


def response_msg(**kwargs):
    info = 'Your message sent to {}'.format(kwargs.get(FIELD_RCPNT, None))
    return compose_response(CODE_RESP_ACCEPTED, info), True


def response_wrong_data(*args):
    return compose_response(CODE_ERR_WRONG_DATA, *args), True


def response_quit():
    return compose_response(CODE_RESP_OK, 'Bye'), False


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
