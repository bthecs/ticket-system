import json
import shlex


class Singleton(object):
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = object.__new__(cls, *args, **kwargs)
        return cls._instances[cls]


def parse_message(message):
    args = shlex.split(message)
    command = args.pop(0)
    return command, args


def make_response(status_code, response):
    return json.dumps({
        'status_code': status_code,
        'response': response,
    })


def parse_request(request):
    request = json.loads(request)
    return request['status_code'], request['response']
