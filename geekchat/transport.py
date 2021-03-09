"""
Transport
"""
from socket import socket, AF_INET, SOCK_STREAM
from .settings import LEN_SZ, ENCODING, LISTEN_QUEUE


def chat_socket(addr: str, port: int, server: bool=False) -> socket:
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


def send_data(sock: socket, data: str):
    """ Convert string message to bytes and send it thru the socket
    """
    payload = data.encode(encoding=ENCODING)
    pl_len = len(payload)
    len_hdr = pl_len.to_bytes(LEN_SZ, byteorder='big')
    package = b''.join((len_hdr, payload))
    sock.sendall(package)


def receive_data(sock: socket) -> str:
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

    msg_len = int.from_bytes(_cycle_recv(LEN_SZ), byteorder='big')
    return _cycle_recv(msg_len).decode(encoding=ENCODING)

