from geekchat.protocol import (compose_request, compose_response,
                                check_request, check_response)


def test_compose_request_presence():
    sut = ('account', 'status info',)
    assert compose_request('presence', *sut, time_fn=lambda: 12345) == \
        '{"action": "presence", "time": 12345, "type": "status", '\
            '"user": {"account_name": "account", "status": "status info"}}'
            
    sut = ('account', 'status', 'splited', 'in', 'few', 'words',)
    assert compose_request('presence', *sut, time_fn=lambda: 12345) == \
        '{"action": "presence", "time": 12345, "type": "status", '\
            '"user": {"account_name": "account", "status": '\
                '"status splited in few words"}}'


def test_compose_request_msg():
    sut = ('msg recipient', 'msg sender', 'msg encoding', 'message text',)
    assert compose_request('msg', *sut, time_fn=lambda: 12345) == \
        '{"action": "msg", "time": 12345, "recipient": "msg recipient", '\
            '"sender": "msg sender", "encoding": "msg encoding", "message": '\
                '"message text"}'

    sut = ('msg recipient', 'msg sender', '', 'separated', 'message', 'text',)
    assert compose_request('msg', *sut, time_fn=lambda: 12345) == \
        '{"action": "msg", "time": 12345, "recipient": "msg recipient", '\
            '"sender": "msg sender", "encoding": "ascii", "message": '\
                '"separated message text"}'


def test_compose_request_authenticate():
    sut = ('account', 'user_pass',)
    assert compose_request('authenticate', *sut, time_fn=lambda: 12345) == \
        '{"action": "authenticate", "time": 12345, '\
            '"user": {"account_name": "account", "password": "user_pass"}}'


def test_compose_request_join():
    sut = ('room name',)
    assert compose_request('join', *sut, time_fn=lambda: 12345) == \
        '{"action": "join", "time": 12345, "room": "room name"}'

    sut = ('splited', 'room', 'name',)
    assert compose_request('join', *sut, time_fn=lambda: 12345) == \
        '{"action": "join", "time": 12345, "room": "splited room name"}'


def test_compose_request_leave():
    sut = ('room name',)
    assert compose_request('leave', *sut, time_fn=lambda: 12345) == \
        '{"action": "leave", "time": 12345, "room": "room name"}'

    sut = ('splited', 'room', 'name',)
    assert compose_request('leave', *sut, time_fn=lambda: 12345) == \
        '{"action": "leave", "time": 12345, "room": "splited room name"}'


def test_compose_request_probe():
    assert compose_request('probe', time_fn=lambda: 12345) == \
        '{"action": "probe", "time": 12345}'

    sut = ('some', 'piece', 'of', 'garbage', 4)
    assert compose_request('probe', *sut, time_fn=lambda: 12345) == \
        '{"action": "probe", "time": 12345}'


def test_compose_request_quit():
    assert compose_request('quit', time_fn=lambda: 12345) == \
        '{"action": "quit", "time": 12345}'

    sut = (False, None, 'ash',)
    assert compose_request('quit', *sut, time_fn=lambda: 12345) == \
        '{"action": "quit", "time": 12345}'


def test_compose_response_note_base():
    assert compose_response(100, time_fn=lambda: 12345) == \
        '{"response": 100, "time": 12345, "alert": ""}'

    sut = ('one note',)
    assert compose_response(100, *sut, time_fn=lambda: 12345) == \
        '{"response": 100, "time": 12345, "alert": "one note"}'

    sut = ('couple of', 'notes',)
    assert compose_response(100, *sut, time_fn=lambda: 12345) == \
        '{"response": 100, "time": 12345, "alert": "couple of notes"}'


def test_compose_response_note_urgent():
    assert compose_response(101, time_fn=lambda: 12345) == \
        '{"response": 101, "time": 12345, "alert": ""}'

    sut = ('one note',)
    assert compose_response(101, *sut, time_fn=lambda: 12345) == \
        '{"response": 101, "time": 12345, "alert": "one note"}'

    sut = ('couple of', 'notes',)
    assert compose_response(101, *sut, time_fn=lambda: 12345) == \
        '{"response": 101, "time": 12345, "alert": "couple of notes"}'


def test_compose_response_ok():
    assert compose_response(200, time_fn=lambda: 12345) == \
        '{"response": 200, "time": 12345}'

    sut = ('one note',)
    assert compose_response(200, *sut, time_fn=lambda: 12345) == \
        '{"response": 200, "time": 12345, "alert": "one note"}'

    sut = ('couple of', 'notes',)
    assert compose_response(200, *sut, time_fn=lambda: 12345) == \
        '{"response": 200, "time": 12345, "alert": "couple of notes"}'


def test_compose_response_created():
    assert compose_response(201, time_fn=lambda: 12345) == \
        '{"response": 201, "time": 12345}'

    sut = ('one note',)
    assert compose_response(201, *sut, time_fn=lambda: 12345) == \
        '{"response": 201, "time": 12345, "alert": "one note"}'

    sut = ('couple of', 'notes',)
    assert compose_response(201, *sut, time_fn=lambda: 12345) == \
        '{"response": 201, "time": 12345, "alert": "couple of notes"}'


def test_compose_response_accepted():
    assert compose_response(202, time_fn=lambda: 12345) == \
        '{"response": 202, "time": 12345}'

    sut = ('one note',)
    assert compose_response(202, *sut, time_fn=lambda: 12345) == \
        '{"response": 202, "time": 12345, "alert": "one note"}'

    sut = ('couple of', 'notes',)
    assert compose_response(202, *sut, time_fn=lambda: 12345) == \
        '{"response": 202, "time": 12345, "alert": "couple of notes"}'


def test_compose_response_err_wrong_data():
    assert compose_response(400, time_fn=lambda: 12345) == \
        '{"response": 400, "time": 12345}'

    sut = ('error description',)
    assert compose_response(400, *sut, time_fn=lambda: 12345) == \
        '{"response": 400, "time": 12345, "error": "error description"}'

    sut = ('few', 'error', 'descriptions',)
    assert compose_response(400, *sut, time_fn=lambda: 12345) == \
        '{"response": 400, "time": 12345, "error": "few error descriptions"}'


def test_compose_response_err_not_auth():
    assert compose_response(401, time_fn=lambda: 12345) == \
        '{"response": 401, "time": 12345}'

    sut = ('error description',)
    assert compose_response(401, *sut, time_fn=lambda: 12345) == \
        '{"response": 401, "time": 12345, "error": "error description"}'

    sut = ('few', 'error', 'descriptions',)
    assert compose_response(401, *sut, time_fn=lambda: 12345) == \
        '{"response": 401, "time": 12345, "error": "few error descriptions"}'


def test_compose_response_err_wrong_auth():
    assert compose_response(402, time_fn=lambda: 12345) == \
        '{"response": 402, "time": 12345}'

    sut = ('error description',)
    assert compose_response(402, *sut, time_fn=lambda: 12345) == \
        '{"response": 402, "time": 12345, "error": "error description"}'

    sut = ('few', 'error', 'descriptions',)
    assert compose_response(402, *sut, time_fn=lambda: 12345) == \
        '{"response": 402, "time": 12345, "error": "few error descriptions"}'


def test_compose_response_err_forbidden():
    assert compose_response(403, time_fn=lambda: 12345) == \
        '{"response": 403, "time": 12345}'

    sut = ('error description',)
    assert compose_response(403, *sut, time_fn=lambda: 12345) == \
        '{"response": 403, "time": 12345, "error": "error description"}'

    sut = ('few', 'error', 'descriptions',)
    assert compose_response(403, *sut, time_fn=lambda: 12345) == \
        '{"response": 403, "time": 12345, "error": "few error descriptions"}'


def test_compose_response_err_not_found():
    assert compose_response(404, time_fn=lambda: 12345) == \
        '{"response": 404, "time": 12345}'

    sut = ('error description',)
    assert compose_response(404, *sut, time_fn=lambda: 12345) == \
        '{"response": 404, "time": 12345, "error": "error description"}'

    sut = ('few', 'error', 'descriptions',)
    assert compose_response(404, *sut, time_fn=lambda: 12345) == \
        '{"response": 404, "time": 12345, "error": "few error descriptions"}'


def test_compose_response_err_conflict():
    assert compose_response(409, time_fn=lambda: 12345) == \
        '{"response": 409, "time": 12345}'

    sut = ('error description',)
    assert compose_response(409, *sut, time_fn=lambda: 12345) == \
        '{"response": 409, "time": 12345, "error": "error description"}'

    sut = ('few', 'error', 'descriptions',)
    assert compose_response(409, *sut, time_fn=lambda: 12345) == \
        '{"response": 409, "time": 12345, "error": "few error descriptions"}'


def test_compose_response_err_unreachable():
    assert compose_response(410, time_fn=lambda: 12345) == \
        '{"response": 410, "time": 12345}'

    sut = ('error description',)
    assert compose_response(410, *sut, time_fn=lambda: 12345) == \
        '{"response": 410, "time": 12345, "error": "error description"}'

    sut = ('few', 'error', 'descriptions',)
    assert compose_response(410, *sut, time_fn=lambda: 12345) == \
        '{"response": 410, "time": 12345, "error": "few error descriptions"}'


def test_compose_response_err_server():
    assert compose_response(500, time_fn=lambda: 12345) == \
        '{"response": 500, "time": 12345}'

    sut = ('error description',)
    assert compose_response(500, *sut, time_fn=lambda: 12345) == \
        '{"response": 500, "time": 12345, "error": "error description"}'

    sut = ('few', 'error', 'descriptions',)
    assert compose_response(500, *sut, time_fn=lambda: 12345) == \
        '{"response": 500, "time": 12345, "error": "few error descriptions"}'


def test_check_request_correct_presence():
    sut = {
        'action': 'presence',
        'time': 123456,
        'type': 'status',
        'user': 'userinfo'
    }
    assert check_request(sut) == (True, None)


def test_check_request_correct_msg():
    sut = {
        'action': 'msg',
        'time': 123456,
        'recipient': 'someone',
        'sender': 'anotherone',
        'encoding': 'ascii',
        'message': 'lorem ipsum dolor sit amet'
    }
    assert check_request(sut) == (True, None)


def test_check_request_correct_auth():
    sut = {
        'action': 'authenticate',
        'time': 123456,
        'user': 'userinfo'
    }
    assert check_request(sut) == (True, None)


def test_check_request_correct_join():
    sut = {
        'action': 'join',
        'time': 123456,
        'room': 'room name'
    }
    assert check_request(sut) == (True, None)


def test_check_request_correct_leave():
    sut = {
        'action': 'leave',
        'time': 123456,
        'room': 'room name'
    }
    assert check_request(sut) == (True, None)


def test_check_request_correct_quit():
    sut = {
        'action': 'quit',
        'time': 123456,
    }
    assert check_request(sut) == (True, None)


def test_check_request_correct_probe():
    sut = {
        'action': 'probe',
        'time': 123456,
    }
    assert check_request(sut) == (True, None)


def test_check_request_wrong_action():
    sut = {
        'action': 'pass',
        'time': 123456,
    }
    assert check_request(sut) == \
        (False, 'protocol not followed: unknown action code in request')


def test_check_request_wrong_fieldset():
    sut = {
        'action': 'presence',
        'time': 123456,
        'user': 'userinfo'
    }
    assert check_request(sut) == \
        (False, 'protocol not followed: wrong request fieldset')


def test_check_request_action_absent():
    sut = {
        'time': 123456,
        'user': 'userinfo'
    }
    assert check_request(sut) == \
        (False, 'protocol not followed: field "action" is absent')


def test_check_response_correct_alert():
    sut = {
        'response': 100,
        'time': 123456,
        'alert': 'text message'
    }
    assert check_response(sut) == (True, None)


def test_check_response_correct_standart():
    sut = {
        'response': 200,
        'time': 123456,
        'alert': 'text message'
    }
    assert check_response(sut) == (True, None)

    sut = {
        'response': 200,
        'time': 123456,
    }
    assert check_response(sut) == (True, None)


def test_check_response_correct_error():
    sut = {
        'response': 404,
        'time': 123456,
        'error': 'error message'
    }
    assert check_response(sut) == (True, None)
    
    sut = {
        'response': 500,
        'time': 123456,
    }
    assert check_response(sut) == (True, None)


def test_check_response_wrong_code():
    sut = {
        'response': 444,
        'time': 123456,
        'error': 'nginx special error'
    }
    assert check_response(sut) == \
        (False, 'protocol not followed: unknown response code in response')


def test_check_response_wrong_fieldset():
    sut = {
        'response': 201,
        'time': 123456,
        'error': 'here must be alert or nothing'
    }
    assert check_response(sut) == \
        (False, 'protocol not followed: wrong response fieldset')


def test_check_response_code_absent():
    sut = {
        'time': 123456
    }
    assert check_response(sut) == \
        (False, 'protocol not followed: field "response" is absent')

