# HTTP-client

Простой HTTP клиент на python

## Usage

```
http [-h] [-m TIMEOUT] [-H [HEADERS ...]] [-X METHOD] [-d BODY] [-o OUTPUT] url


positional arguments:
  url                   Адрес, на который нужно отправить запрос

options:
  -h, --help            show this help message and exit
  -m TIMEOUT, --max-time TIMEOUT
                        Время ожидания запроса
  -H [HEADERS ...]      Заголовок HTTP запроса
  -X METHOD             Метод HTTP запроса
  -d BODY               Тело запроса, если начинается с @, загружает из файла
  -o OUTPUT             Файл, в который нужно загрузить ответ
```