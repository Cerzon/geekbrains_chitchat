import click
from contextlib import closing
import json

from geekchat import messages as gcm
from geekchat.transport import chat_socket, send_msg, receive_msg
from geekchat.settings import HOST_IP, PORT

@click.command()
@click.option('-a', 'addr', default=HOST_IP, type=str)
@click.option('-p', 'port', default=PORT, type=int)
def main(addr: str, port: int):
    with closing(chat_socket(addr, port, server=True)) as srv:

        with closing(srv.accept()[0]) as convo:
            keep_connection = True
            while keep_connection:
                response, keep_connection = process_request(receive_msg(convo))
                send_msg(convo, response)


def response_presence(user: dict):
    info = 'Hello {account_name}!'.format(**user)
    return gcm.create_response(gcm.CODE_RESP_OK, info), True


def response_msg(recipient: str, sender: str, encoding: str, message: str):
    info = f'Your message sent to {recipient}'
    return gcm.create_response(gcm.CODE_RESP_ACCEPTED, info), True


def response_wrong_data(description: str=None):
    return gcm.create_response(gcm.CODE_ERR_WRONG_DATA, description), True


def response_quit():
    return gcm.create_response(gcm.CODE_RESP_OK, 'Bye'), False


def process_request(rqst: str):
    try:
        request = json.loads(rqst)
    except json.JSONDecodeError:
        return response_wrong_data('JIM protocol not followed')
    action = request.pop(gcm.FIELD_ACTION, None)
    rq_time = request.pop(gcm.FIELD_TIME, None)
    print(rq_time)
    dispatcher = {
        gcm.ACT_PRESENCE: response_presence,
        gcm.ACT_MSG: response_msg,
        gcm.ACT_QUIT: response_quit,
    }
    if action:
        return dispatcher[action](**request)
    return response_wrong_data('protocol not followed: field "action" is absent')


if __name__ == '__main__':
    main()
