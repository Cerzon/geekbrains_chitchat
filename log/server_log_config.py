import logging


_format = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
_handler = logging.FileHandler('log/chat_server.log', encoding='utf-8')
_handler.setFormatter(_format)
srv_logger = logging.getLogger('chat_server')
srv_logger.addHandler(_handler)
srv_logger.setLevel(logging.INFO)
