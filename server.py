import click

from geekchat.chat_server import start_server
from geekchat.settings import HOST_IP, PORT

@click.command()
@click.option('-a', 'addr', default=HOST_IP, type=str)
@click.option('-p', 'port', default=PORT, type=int)
def main(addr: str, port: int):
    start_server(addr, port)


main()