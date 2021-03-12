import inspect
import logging


def logged(func):
    def wrapper(*args, **kwargs):
        _logger = logging.getLogger()
        _logger.info(
            'Вызов %(fn)s с аргументами %(pa)s %(kwa)s из %(caller)s' % {
                'fn': func.__name__,
                'pa': args,
                'kwa': kwargs,
                'caller': inspect.stack()[1].function
            }
        )
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            _logger.exception('Мы всё уронили...')
            raise e
        return result

    return wrapper
