"""
JIM protocol processing
"""
from functools import partial
import json
from time import time
from .log.staff import logged


# field names
FIELD_ACTION = 'action'
FIELD_CODE = 'response'
FIELD_TIME = 'time'
FIELD_ALERT = 'alert'
FIELD_ERROR = 'error'
FIELD_USER = 'user'
FIELD_TYPE = 'type'
FIELD_RCPNT = 'recipient'
FIELD_SNDR = 'sender'
FIELD_ENC = 'encoding'
FIELD_MSG = 'message'
FIELD_ROOM = 'room'
FIELD_ACC = 'account_name'
FIELD_STATUS = 'status'
FIELD_PWD = 'password'


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


# templates for specific actions
ACTION_TPLS = {
    ACT_PRESENCE: lambda time_fn, acc_name, *status: ({
                        FIELD_ACTION: ACT_PRESENCE,
                        FIELD_TIME: time_fn(),
                        FIELD_TYPE: 'status',
                        FIELD_USER: {
                            FIELD_ACC: acc_name,
                            FIELD_STATUS: ' '.join(status),
                        }, 
                    }, None),
    ACT_MSG: lambda time_fn, to_acc, from_acc, enc, *msg: ({
                        FIELD_ACTION: ACT_MSG,
                        FIELD_TIME: time_fn(),
                        FIELD_RCPNT: to_acc,
                        FIELD_SNDR: from_acc,
                        FIELD_ENC: enc or 'ascii',
                        FIELD_MSG: ' '.join(msg),
                    }, None),
    ACT_AUTH: lambda time_fn, acc_name, pwd, *args: ({
                        FIELD_ACTION: ACT_AUTH,
                        FIELD_TIME: time_fn(),
                        FIELD_USER: {
                            FIELD_ACC: acc_name,
                            FIELD_PWD: pwd,
                        },
                    }, None),
    ACT_JOIN: lambda time_fn, *room_name: ({
                        FIELD_ACTION: ACT_JOIN,
                        FIELD_TIME: time_fn(),
                        FIELD_ROOM: ' '.join(room_name),
                    }, None),
    ACT_LEAVE: lambda time_fn, *room_name: ({
                        FIELD_ACTION: ACT_LEAVE,
                        FIELD_TIME: time_fn(),
                        FIELD_ROOM: ' '.join(room_name),
                    }, None),
    ACT_PROBE: lambda time_fn, *args: ({
                        FIELD_ACTION: ACT_PROBE,
                        FIELD_TIME: time_fn()
                    }, None),
    ACT_QUIT:  lambda time_fn, *args: ({
                        FIELD_ACTION: ACT_QUIT,
                        FIELD_TIME: time_fn()
                    }, None),
}


# fieldsets for specific actions
ACTION_FIELDSET = {
    ACT_PRESENCE: lambda keys: set(keys) == {
                                FIELD_ACTION,
                                FIELD_TIME,
                                FIELD_TYPE,
                                FIELD_USER
                            },
    ACT_MSG: lambda keys: set(keys) == {
                                FIELD_ACTION,
                                FIELD_TIME,
                                FIELD_RCPNT,
                                FIELD_SNDR,
                                FIELD_ENC,
                                FIELD_MSG
                            },
    ACT_AUTH: lambda keys: set(keys) == {
                                FIELD_ACTION,
                                FIELD_TIME,
                                FIELD_USER
                            },
    ACT_JOIN: lambda keys: set(keys) == {
                                FIELD_ACTION,
                                FIELD_TIME,
                                FIELD_ROOM,
                            },
    ACT_LEAVE: lambda keys: set(keys) == {
                                FIELD_ACTION,
                                FIELD_TIME,
                                FIELD_ROOM
                            },
    ACT_QUIT: lambda keys: set(keys) == {
                                FIELD_ACTION,
                                FIELD_TIME
                            },
    ACT_PROBE: lambda keys: set(keys) == {
                                FIELD_ACTION,
                                FIELD_TIME
                            }
}


# templates for specific response code
RESPONSE_TPLS = {
    CODE_NOTE_BASE: lambda time_fn, *args: ({
                        FIELD_CODE: CODE_NOTE_BASE,
                        FIELD_TIME: time_fn(),
                        FIELD_ALERT: ' '.join(args),
                    }, None),
    CODE_NOTE_URGENT: lambda time_fn, *args: ({
                        FIELD_CODE: CODE_NOTE_URGENT,
                        FIELD_TIME: time_fn(),
                        FIELD_ALERT: ' '.join(args),
                    }, None),
    CODE_RESP_OK: lambda time_fn, *args: ({
                        FIELD_CODE: CODE_RESP_OK,
                        FIELD_TIME: time_fn(),
                    }, {FIELD_ALERT: ' '.join(args)} if args else None),
    CODE_RESP_CREATED: lambda time_fn, *args: ({
                        FIELD_CODE: CODE_RESP_CREATED,
                        FIELD_TIME: time_fn(),
                    }, {FIELD_ALERT: ' '.join(args)} if args else None),
    CODE_RESP_ACCEPTED: lambda time_fn, *args: ({
                        FIELD_CODE: CODE_RESP_ACCEPTED,
                        FIELD_TIME: time_fn(),
                    }, {FIELD_ALERT: ' '.join(args)} if args else None),
    CODE_ERR_WRONG_DATA: lambda time_fn, *args: ({
                        FIELD_CODE: CODE_ERR_WRONG_DATA,
                        FIELD_TIME: time_fn(),
                    }, {FIELD_ERROR: ' '.join(args)} if args else None),
    CODE_ERR_NOT_AUTH: lambda time_fn, *args: ({
                        FIELD_CODE: CODE_ERR_NOT_AUTH,
                        FIELD_TIME: time_fn(),
                    }, {FIELD_ERROR: ' '.join(args)} if args else None),
    CODE_ERR_WRONG_AUTH: lambda time_fn, *args: ({
                        FIELD_CODE: CODE_ERR_WRONG_AUTH,
                        FIELD_TIME: time_fn(),
                    }, {FIELD_ERROR: ' '.join(args)} if args else None),
    CODE_ERR_FORBID: lambda time_fn, *args: ({
                        FIELD_CODE: CODE_ERR_FORBID,
                        FIELD_TIME: time_fn(),
                    }, {FIELD_ERROR: ' '.join(args)} if args else None),
    CODE_ERR_NOT_FND: lambda time_fn, *args: ({
                        FIELD_CODE: CODE_ERR_NOT_FND,
                        FIELD_TIME: time_fn(),
                    }, {FIELD_ERROR: ' '.join(args)} if args else None),
    CODE_ERR_CONFLICT: lambda time_fn, *args: ({
                        FIELD_CODE: CODE_ERR_CONFLICT,
                        FIELD_TIME: time_fn(),
                    }, {FIELD_ERROR: ' '.join(args)} if args else None),
    CODE_ERR_UNREACH: lambda time_fn, *args: ({
                        FIELD_CODE: CODE_ERR_UNREACH,
                        FIELD_TIME: time_fn(),
                    }, {FIELD_ERROR: ' '.join(args)} if args else None),
    CODE_ERR_SERVER: lambda time_fn, *args: ({
                        FIELD_CODE: CODE_ERR_SERVER,
                        FIELD_TIME: time_fn(),
                    }, {FIELD_ERROR: ' '.join(args)} if args else None),
}


# possible fields in response
RESP_NOTE_FIELD_CHECK = lambda keys: set(keys) == {
                                        FIELD_CODE,
                                        FIELD_TIME,
                                        FIELD_ALERT
                                    }

RESP_STD_FIELD_CHECK = lambda keys: set(keys) == {
                                        FIELD_CODE,
                                        FIELD_TIME,
                                        FIELD_ALERT
                                    } or set(keys) == {
                                            FIELD_CODE,
                                            FIELD_TIME,
                                        }

RESP_ERR_FIELD_CHECK = lambda keys: set(keys) == {
                                        FIELD_CODE,
                                        FIELD_TIME,
                                        FIELD_ERROR
                                    } or set(keys) == {
                                            FIELD_CODE,
                                            FIELD_TIME,
                                        }


# fieldsets for specific response code
RESPONSE_FIELDSET = {
    CODE_NOTE_BASE: RESP_NOTE_FIELD_CHECK,
    CODE_NOTE_URGENT: RESP_NOTE_FIELD_CHECK,
    CODE_RESP_OK: RESP_STD_FIELD_CHECK,
    CODE_RESP_CREATED: RESP_STD_FIELD_CHECK,
    CODE_RESP_ACCEPTED: RESP_STD_FIELD_CHECK,
    CODE_ERR_WRONG_DATA: RESP_ERR_FIELD_CHECK,
    CODE_ERR_NOT_AUTH: RESP_ERR_FIELD_CHECK,
    CODE_ERR_WRONG_AUTH: RESP_ERR_FIELD_CHECK,
    CODE_ERR_FORBID: RESP_ERR_FIELD_CHECK,
    CODE_ERR_NOT_FND: RESP_ERR_FIELD_CHECK,
    CODE_ERR_CONFLICT: RESP_ERR_FIELD_CHECK,
    CODE_ERR_UNREACH: RESP_ERR_FIELD_CHECK,
    CODE_ERR_SERVER: RESP_ERR_FIELD_CHECK
}


@logged
def compose_data(def_val, *args, time_fn=time, data_tpls: dict=None) -> str:
    """
    Return string with dictionary, formed with JIM protocol template and
    dumped as JSON

    Arguments:
    - def_val   - str or int: defining field value;
    - args      - positional arguments to fill template fields;
    - data_tpls - dict: dictionary with protocol templates.
    """
    if data_tpls is None:
        raise TypeError('Unexpected named argument value')

    base, addition = data_tpls[def_val](time_fn, *args)
    if addition:
        base.update(addition)
    return json.dumps(base, ensure_ascii=False)


compose_request = partial(compose_data, data_tpls=ACTION_TPLS)

compose_response = partial(compose_data, data_tpls=RESPONSE_TPLS)


@logged
def check_protocol(data: dict, def_field: str=None,
                    fieldset: dict=None, data_name: str=None) -> tuple:
    """
    Return (True, None) if data match protocol structure,
    otherwise return (False, <error description>)

    Arguments:
    - data      - dict: data to check;
    - def_field - str: field name with defining value;
    - fieldset  - dict: dictionary with reference structures;
    - data_name - str: name of data to check ('request'/'response').
    """
    if any(arg is None for arg in (def_field, fieldset, data_name)):
        raise TypeError('Unexpected named argument value')

    def_val = data.get(def_field, None)

    if def_val is None:
        return False, f'protocol not followed: field "{def_field}" is absent'

    if def_val not in fieldset:
        return False, f'protocol not followed: unknown {def_field} '\
                                                        f'code in {data_name}'

    if not fieldset[def_val](data.keys()):
        return False, f'protocol not followed: wrong {data_name} fieldset'
        
    return True, None


check_request = partial(check_protocol,
                        def_field = FIELD_ACTION,
                        fieldset = ACTION_FIELDSET,
                        data_name = 'request')

check_response = partial(check_protocol,
                        def_field = FIELD_CODE,
                        fieldset = RESPONSE_FIELDSET,
                        data_name = 'response')
