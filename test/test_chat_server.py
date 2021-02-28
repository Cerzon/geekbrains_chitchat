import json

from geekchat.chat_server import process_request


def test_process_request_presence():
    sut = '{"action": "presence", "time": 12345, "type": "status", '\
            '"user": {"account_name": "account", "status": "status info"}}'
    response, keep_con = process_request(sut)
    response = json.loads(response)
    response.pop('time', None)
    assert (response, keep_con) == \
        ({'response': 200, 'alert': 'Hello account!'}, True)


def test_process_request_msg():
    sut = '{"action": "msg", "time": 12345, "recipient": "msg recipient", '\
            '"sender": "msg sender", "encoding": "msg encoding", "message": '\
                '"message text"}'
    response, keep_con = process_request(sut)
    response = json.loads(response)
    response.pop('time', None)
    assert (response, keep_con) == \
        ({'response': 202, 'alert': 'Your message sent to msg recipient'}, True)


def test_process_request_quit():
    sut = '{"action": "quit", "time": 12345}'
    response, keep_con = process_request(sut)
    response = json.loads(response)
    response.pop('time', None)
    assert (response, keep_con) == ({'response': 200, 'alert': 'Bye'}, False)


def test_process_request_wrong_data():
    sut = 'pointless letter set'
    response, keep_con = process_request(sut)
    response = json.loads(response)
    response.pop('time', None)
    assert (response, keep_con) == \
        ({'response': 400, 'error': 'JIM protocol not followed'}, True)


def test_process_request_bad_request_format():
    sut = '{"action": "presence", "time": 12345, "type": "status"}'
    response, keep_con = process_request(sut)
    response = json.loads(response)
    response.pop('time', None)
    assert (response, keep_con) == ({'response': 400, \
        'error': 'protocol not followed: wrong request fieldset'}, True)


def test_process_request_action_field_absent():
    sut = '{"time": 12345, "type": "status", '\
            '"user": {"account_name": "account", "status": "status info"}}'
    response, keep_con = process_request(sut)
    response = json.loads(response)
    response.pop('time', None)
    assert (response, keep_con) == ({'response': 400, \
        'error': 'protocol not followed: field "action" is absent'}, True)


def test_process_request_action_wrong_value():
    sut = '{"action": "drive", "time": 12345, "type": "status", '\
            '"user": {"account_name": "account", "status": "status info"}}'
    response, keep_con = process_request(sut)
    response = json.loads(response)
    response.pop('time', None)
    assert (response, keep_con) == ({'response': 400, \
        'error': 'protocol not followed: unknown action code in request'}, True)


def test_process_request_action_not_implemented():
    sut = '{"action": "join", "time": 12345, "room": "room name"}'
    response, keep_con = process_request(sut)
    response = json.loads(response)
    response.pop('time', None)
    assert (response, keep_con) == ({'response': 400, \
        'error': 'action not implemented'}, True)
