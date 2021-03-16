import inspect
import logging


def logged(func):
    _logger = logging.getLogger()
    def wrapper(*args, **kwargs):
        _logger.debug(
            'Вызов %(fn)s с аргументами %(pa)s %(kwa)s из %(caller)s' % {
                'fn': func.__name__,
                'pa': args,
                'kwa': kwargs,
                'caller': inspect.stack()[1].function
            }
        )
        try:
            result = func(*args, **kwargs)
        except:
            _logger.exception('Мы всё уронили...')
            raise
        return result

    return wrapper
