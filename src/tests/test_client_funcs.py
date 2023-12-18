import unittest
import socket
from unittest.mock import MagicMock
from src.http_client import (process_url, process_headers,
                             read_headers, find_content_length,
                             build_request)


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
        expected_result = 0
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


if __name__ == '__main__':
    unittest.main()
