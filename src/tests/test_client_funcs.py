import socket
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

from src.cmd_parser import configure_parser
from src.http_client import (process_url, process_headers,
                             read_headers, find_content_length,
                             build_request, make_request)


def _configure_socket(expected_response):
    mock_socket = MagicMock()
    mock_socket.fileno.return_value = 0
    mock_socket.recv.side_effect = [expected_response, b'']
    mock_socket.__enter__.return_value = mock_socket
    return mock_socket


class MyTestCase(unittest.TestCase):
    def test_process_url(self):
        url = 'http://example.com'
        expected_result = ('example.com', 80, '/')
        self.assertEqual(process_url(url), expected_result)

        url = 'http://example.com:8080/path?query'
        expected_result = ('example.com', 8080, '/path?query')
        self.assertEqual(process_url(url), expected_result)

    def test_process_headers(self):
        headers = ["Content-Type: application/json"]
        expected_result = {'Content-Type': 'application/json'}
        self.assertEqual(process_headers(headers), expected_result)

        headers = ["Content-Type: application/json", "Accept: text/html"]
        expected_result = {'Content-Type': 'application/json',
                           'Accept': 'text/html'}
        self.assertEqual(process_headers(headers), expected_result)

    def test_find_content_length(self):
        headers = b"Content-Length: 100\r\n"
        expected_result = 100
        self.assertEqual(find_content_length(headers), expected_result)
        headers = b""
        expected_result = None
        self.assertEqual(find_content_length(headers), expected_result)

    def test_read_headers(self):
        sock = MagicMock(spec=socket.socket)
        response = (b"HTTP/1.1 200 OK\r\nContent-Length: 100\r\n\r\nSome "
                    b"response body")

        sock.recv = MagicMock(return_value=response)

        expected_headers = b"HTTP/1.1 200 OK\r\nContent-Length: 100"
        expected_response = b"Some response body"
        headers, other = read_headers(sock)
        print(other)

        self.assertEqual(headers, expected_headers)
        self.assertEqual(other, expected_response)

    def test_build_request(self):
        method = "GET"
        path = "/path"
        headers = {"Content-Type": "application/json", "Accept": "text/html"}
        body = "Some body"

        expected_result = ("GET /path HTTP/1.1\r\nContent-Type: "
                           "application/json\r\nAccept: text/html\r\n\r\nSome"
                           " body\r\n\r\n")
        self.assertEqual(build_request(body, headers, method, path),
                         expected_result)

    @patch('sys.stdout', new_callable=StringIO)
    @patch('src.http_client.socket.socket')
    def test_simple_make_request(self, socket, mock_stdout):
        args = ['test.com:8080', '-m', '1']
        expected_request = (b'GET / HTTP/1.1\r\n'
                            b'Host: test.com:8080\r\n'
                            b'Connection: close\r\n'
                            b'\r\n\r\n\r\n')
        mock_socket = _configure_socket(b'HTTP/1.1 200 OK\r\n\r\n\r\n')
        socket.return_value = mock_socket

        parser = configure_parser()
        make_request(parser.parse_args(args))

        mock_socket.settimeout.assert_called_once_with(1.0)
        mock_socket.connect.assert_called_once_with(('test.com', 8080))
        mock_socket.sendall.assert_called_once_with(expected_request)
        self.assertEqual('HTTP/1.1 200 OK\r\n\r\n\n',
                         mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    @patch('src.http_client.socket.socket')
    def test_make_request_with_headers(self, socket, mock_stdout):
        args = ['test.com:8080', '-H', "'Test: 123'"]
        expected_request = (b'GET / HTTP/1.1\r\n'
                            b'Test: 123\r\n'
                            b'Host: test.com:8080\r\n'
                            b'Connection: close\r\n'
                            b'\r\n\r\n\r\n')
        mock_socket = _configure_socket(b'HTTP/1.1 200 OK\r\n\r\n\r\n')
        socket.return_value = mock_socket

        parser = configure_parser()
        make_request(parser.parse_args(args))

        mock_socket.sendall.assert_called_once_with(expected_request)


if __name__ == '__main__':
    unittest.main()
