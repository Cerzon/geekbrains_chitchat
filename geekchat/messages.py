"""
Message processing
"""
import json
from time import time


# field names
FIELD_ACTION = 'action'
FIELD_CODE = 'response'
FIELD_TIME = 'time'
FIELD_ALERT = 'alert'
FIELD_ERROR = 'error'


# response codes
CODE_NOTE_BASE = 100
CODE_NOTE_URGENT = 101

CODE_RESP_OK = 200
CODE_RESP_CREATED = 201
CODE_RESP_ACCEPTED = 202

CODE_ERR_WRONG_DATA = 400
CODE_ERR_NOT_AUTH = 401
CODE_ERR_WRONG_AUTH = 402
CODE_ERR_FORBID = 403
CODE_ERR_NOT_FND = 404
CODE_ERR_CONFLICT = 409
CODE_ERR_UNREACH = 410

CODE_ERR_SERVER = 500


# available actions
ACT_PRESENCE = 'presence'
ACT_PROBE = 'probe'
ACT_MSG = 'msg'
ACT_QUIT = 'quit'
ACT_AUTH = 'authenticate'
ACT_JOIN = 'join'
ACT_LEAVE = 'leave'

# kwargs templates for specific actions
ACTIONS = {
    ACT_PRESENCE: lambda acc_name, *status: {
                        'user': {
                            'account_name': acc_name,
                            'status': ' '.join(status),
                        }
                    },
    ACT_MSG: lambda to_acc, from_acc, enc, *msg: {
                        'recipient': to_acc,
                        'sender': from_acc,
                        'encoding': enc or 'ascii',
                        'message': ' '.join(msg),
                    },
    ACT_PROBE: {},
    ACT_QUIT: {},
}


def create_request(action: str, **kwargs) -> str:
    """
    Return string with client request object
    """
    msg = {
        FIELD_ACTION: action,
        FIELD_TIME: time(),
    }
    if kwargs:
        msg.update(kwargs)
    return json.dumps(msg, ensure_ascii=False)


def create_response(code: int, info: str=None) -> str:
    """
    Return string with server response object
    """
    msg = {
        FIELD_CODE: code,
        FIELD_TIME: time(),
    }
    if info:
        info_field = FIELD_ALERT if code < 400 else FIELD_ERROR
        msg.update({info_field: info})
    return json.dumps(msg, ensure_ascii=False)
