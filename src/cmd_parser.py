import argparse
from dataclasses import dataclass


@dataclass
class HTTPArgs:
    url: str
    method: str
    headers: list[str]
    body: str
    timeout: float
    output: str


def configure_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='http',
        description='HTTP клиент')

    parser.add_argument('url', type=str,
                        help='Адрес, на который нужно отправить запрос')
    parser.add_argument('-m', '--max-time', default=2.0,
                        type=float, dest='timeout',
                        help='Время ожидания запроса')
    parser.add_argument('-H', action='append', dest='headers',
                        help='Заголовок HTTP запроса')
    parser.add_argument('-X', type=str, default='GET',
                        dest='method',
                        help='Метод HTTP запроса')
    parser.add_argument('-d', type=str, dest='body', default='',
                        help='Тело запроса, если начинается с @, загружает из файла')
    parser.add_argument('-o', type=str, dest='output',
                        help='Файл, в который нужно загрузить ответ')
    return parser