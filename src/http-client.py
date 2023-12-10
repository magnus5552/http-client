import socket
from urllib.parse import urlparse

from cmd_parser import configure_parser, HTTPArgs


def make_request(args: HTTPArgs):
    url, method, headers, body, timeout, output_file = (
        args.url, args.method, args.headers, args.body, args.timeout,
        args.output)

    hostname, port, path = process_url(url)

    headers = process_headers(headers)
    headers['Host'] = f'{hostname}:{port}'
    #headers['Connection'] = 'close'

    body = process_body(body)

    request = build_request(body, headers, method, path)
    print(request)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        sock.connect((hostname, port))
        sock.sendall(request.encode())
        response = recieve_respone(sock).decode()

    if output_file is not None:
        with open(output_file, 'w') as file:
            file.write(response)
    else:
        print(response)


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
    return dict([x.strip(" '") for x in header.split(':', 1)]
                for header in headers)


def process_body(body):
    if body.startswith('@'):
        with open(body[1:], 'r') as file:
            body = file.read()
    return body


def recieve_respone(sock: socket.socket):
    response = b""
    while True:
        chunk = sock.recv(4096)
        if len(chunk) == 0:
            break
        response = response + chunk
    return response


def custom_index(it, f, default=-1):
    return next((i for i, e in enumerate(it) if f(e)), default)


if __name__ == '__main__':
    parser = configure_parser()
    args = parser.parse_args()
    make_request(args)
