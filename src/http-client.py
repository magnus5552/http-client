import socket
import sys
from urllib.parse import urlparse
import pickle
import os
from cmd_parser import configure_parser, HTTPArgs

path = os.path.dirname(os.path.realpath(__file__))
cookies_path = os.path.join(path, 'cookies.pickle')


def make_request(args: HTTPArgs):
    url, method, headers, body, timeout, output_file = (
        args.url, args.method, args.headers, args.body, args.timeout,
        args.output)

    if method not in ["GET", 'PUT', 'POST', 'OPTIONS', "HEAD", "PATCH", "DELETE", "TRACE", "CONNECT"]:
        raise ValueError("Incorrect method")

    hostname, port, path = process_url(url)

    headers = process_headers(headers)
    add_cookie(headers, hostname)
    headers['Host'] = f'{hostname}:{port}'
    headers['Connection'] = 'close'

    body = process_body(body)

    request = build_request(body, headers, method, path)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((hostname, port))
            sock.sendall(request.encode())
            response = receive_response(sock).decode()
    except TimeoutError:
        print("Problems with connection, timeout")
        sys.exit()
    except OSError:
        print("Exception appeared when making request")

    set_cookie(response, hostname)

    try:
        if output_file is not None:
            with open(output_file, 'w') as file:
                file.write(response)
        else:
            print(response)
    except PermissionError:
        print("Not enough permissions to open this file")
        sys.exit()
    except IsADirectoryError:
        print("Can't open directory, i need file")
        sys.exit()
    except IOError:
        print("An error occurred while recording, please, try again")
        sys.exit()
    except MemoryError:
        print("Not enough memory to write to file")
        sys.exit()


def build_request(body, headers, method, path):
    method = method.upper()
    headers = ''.join([': '.join(header) + '\n' for header in headers.items()])
    return f'{method} {path} HTTP/1.1\n' + headers + body + '\r\n\r\n'


def process_url(url):
    if not url.startswith('http://'):
        url = 'http://' + url
    url = urlparse(url)

    hostname = url.hostname

    port = url.port if url.port else 80

    path = url.path if url.path else '/'
    path = path + '?' + url.query if url.query else path

    return hostname, port, path


def process_headers(headers):
    if not headers:
        return {}

    return dict([x.strip(" '") for x in header.split(':', 1)]
                for header in headers)


def process_body(body):
    if body.startswith('@'):
        with open(body[1:], 'r') as file:
            body = file.read()
    return body


def receive_response(sock: socket.socket):
    response = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        response = response + chunk
    return response


def set_cookie(response: str, host: str) -> None:
    lines = response.split('\n')
    cookie_headers = list(filter(lambda x: x.startswith('Set-Cookie:'), lines))
    values = {}
    for cookie in cookie_headers:
        name, value = cookie.split(': ', 1)[1].split('=', 1)
        if name.startswith("__Secure-"):
            name = name[9:]
        elif name.startswith('__Host-'):
            name = name[7:]
        values[name] = value
    cookies = get_cookies_from_file()
    cookies[host] = values
    with open(cookies_path, "wb") as file:
        pickle.dump(cookies, file)


def get_cookies_from_file() -> dict:
    cookies = {}
    if os.path.exists(cookies_path):
        with open(cookies_path, "rb") as file:
            cookies = pickle.load(file)
            if cookies is not dict:
                os.remove(cookies_path)
    return cookies


def add_cookie(headers: dict, host: str) -> None:
    cookies = get_cookies_from_file()
    if not cookies or host not in cookies:
        return
    for name, value in cookies[host].items():
        headers["Cookies"] = f"{name}={value}"


if __name__ == '__main__':
    parser = configure_parser()
    args = parser.parse_args()
    make_request(args)
