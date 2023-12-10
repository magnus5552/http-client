from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer


class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        print(self.headers)
        self.send_header("Set-Cookie", "name=value")
        self.end_headers()


def run(server_class=HTTPServer, handler_class=HTTPRequestHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


if __name__ == '__main__':
    run()
