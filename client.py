""" Запуск "одностороннего" клиента:
    с флагом --sender - только отправка данных на сервер;
    без флага --sender - только получение данных от сервера.
"""
import click

from geekchat.chat_client import start_client
from geekchat.settings import HOST_IP, PORT


@click.command()
@click.option('-a', 'addr', default=HOST_IP, type=str)
@click.option('-p', 'port', default=PORT, type=int)
@click.option('--sender', is_flag=True)
def main(addr: str, port: int, sender):
    start_client(addr, port, sender)


main()
