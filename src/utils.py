class Singleton(object):
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = object.__new__(cls, *args, **kwargs)
        return cls._instances[cls]


def parse_message(message):
    try:
        args = message.split()
        command = args.pop(0)
    except:
        args = []
        command = message
    print(f'\nArgumentos: {args}')
    print(f'Comando: {command}')
    return command, args
