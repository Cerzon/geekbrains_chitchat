import logging


_format = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
_handler = logging.FileHandler('log/chat_client.log', encoding='utf-8')
_handler.setFormatter(_format)
clt_logger = logging.getLogger('chat_client')
clt_logger.addHandler(_handler)
clt_logger.setLevel(logging.INFO)
