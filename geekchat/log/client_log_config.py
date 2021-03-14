import logging

def start_logger():
    _format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    _handler = logging.FileHandler('geekchat/log/chat_client.log', encoding='utf-8')
    _handler.setFormatter(_format)
    _logger = logging.getLogger()
    _logger.addHandler(_handler)
    _logger.setLevel(logging.DEBUG)
    return _logger
