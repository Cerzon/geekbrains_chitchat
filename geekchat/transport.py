"""
Transport
"""
from socket import socket, AF_INET, SOCK_STREAM
from .settings import MSGLEN_SZ, ENCODING, LISTEN_QUEUE


def chat_socket(addr: str, port: int, server: bool=False):
    """ Return socket binded or connected to address:port
    """
    if 1024 <= port <= 65535:
        sock = socket(family=AF_INET, type=SOCK_STREAM)
        if server:
            sock.bind((addr, port))
            sock.listen(LISTEN_QUEUE)
        else:
            sock.connect((addr, port))
        return sock
    raise ValueError('Port number must be in range 1024-65535')


def send_msg(sock: socket, message: str):
    """ Convert string message to bytes and send it thru the socket
    """
    payload = message.encode(encoding=ENCODING)
    pl_len = len(payload)
    len_hdr = pl_len.to_bytes(MSGLEN_SZ, byteorder='big')
    total_len = MSGLEN_SZ + pl_len
    package = b''.join((len_hdr, payload))
    total_sent = 0
    while total_sent < total_len:
        sent = sock.send(package[total_sent:])
        if sent == 0:
            raise RuntimeError('error occured while sending: socket broken')
        total_sent += sent


def receive_msg(sock: socket) -> str:
    """ Return message recieved thru socket and converted to string
    """
    def _cycle_recv(length: int) -> bytes:
        chunks = []
        rcvd = 0
        while rcvd < length:
            chunk = sock.recv(length - rcvd)
            if chunk == b'':
                raise RuntimeError('error occured while recieving: socket broken')
            chunks.append(chunk)
            rcvd += len(chunk)
        return b''.join(chunks)

    msg_len = int.from_bytes(_cycle_recv(MSGLEN_SZ), byteorder='big')
    return _cycle_recv(msg_len).decode(encoding=ENCODING)

