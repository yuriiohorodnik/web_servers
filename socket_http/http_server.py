import socket
import sys
import time
import base64

SECRET_CREDENTIALS = b"root:password"
METHODS = [b"GET", b"POST"]


class TooMuchMemory:
    pass


class WebServer:
    def __init__(self, port=8888):
        self.host = socket.gethostname()
        self.port = port
        self.content_folder = 'stuff'

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.sock.bind((self.host, self.port))
            print("Connection established on {}:{}".format(self.host,
                                                           self.port))
        except Exception as exc:
            print(f"An error occured while binding: {exc}")
            self.shutdown()
        self._listen()

    def shutdown(self):
        try:
            self.sock.close()
        except Exception:
            print("Socket is already stopped or wasn't started")
            sys.exit(1)

    def generate_headers(self, status_code):
        # 200 and 404 only
        header = None
        if status_code == 200:
            header = "HTTP/1.1 200 OK\r\n"
        elif status_code == 404:
            header = "HTTP/1.1 404 Not found\r\n"
        elif status_code == 401:
            header = "HTTP/1.1 401 Unauthorized\r\n"
            header += 'WWW-Authenticate: Basic realm="Access to the site"\r\n'
        elif status_code == 202:
            header = "HTTP/1.1 202 Accepted\r\n"

        time_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        header += 'Date: {now}\r\n'.format(now=time_now)
        header += 'Server: HTTP-Server\r\n'
        header += 'Connection: close\r\n'
        header += 'Encoding: gzip\r\n'
        header += '\r\n'
        return header.encode()

    def _listen(self):
        self.sock.listen()
        while True:
            conn, addr = self.sock.accept()
            print("Recieved connection from {}".format(addr))
            self._handle_request(conn, addr)

    def _handle_request(self, conn, addr):
        first_line = self.read_until(conn, chars="\r\n")
        method, path = self.parse_request(first_line)
        request_headers = self.read_until(conn, chars="\r\n\r\n")
        headers = self.parse_headers(request_headers)
        if method not in METHODS:
            print(f"Unknown HTTP request method: {method}")
        elif b"Authorization" in headers:
            if self.process_auth(headers[b'Authorization']):
                if path == b"/":
                    path = b"/index.html"
                filepath_to_serve = self.content_folder.encode() + path
                try:
                    if method == b"GET":
                        with open(filepath_to_serve, 'rb') as f:
                            response_data = self.generate_headers(200) + f.read()
                    elif method == b"POST":
                        content_length = headers[b'Content-Length']
                        passed_info = self.read_remaining(conn, content_length)
                        if not passed_info:
                            raise TooMuchMemory()
                        response_data = (self.generate_headers(202) +
                                         self.create_page_with_data(passed_info))
                        print(f"passed data POST: {response_data}")
                except TooMuchMemory:
                    response_data = b"16 mb is too much."
                except Exception:
                    response_data = self.generate_404()
                conn.sendall(response_data)
            else:
                print("Wrong credentials entered")
        elif b"Authorization" not in headers:
            response_header = self.generate_headers(401)
            conn.sendall(response_header)
        conn.close()

    def process_auth(self, auth_data):
        data = auth_data.split(b" ")
        method = data[0]
        if method == b"Basic":
            password = data[1]
            if (base64.standard_b64decode(password) == SECRET_CREDENTIALS):
                return True
        return False

    def generate_404(self, msg=""):
        print("File not found. Serving 404 page.")
        response_header = self.generate_headers(404)
        with open("stuff/404.html", "rb") as f:
            response_data = f.read()
        return response_header + response_data

    def create_page_with_data(self, data):
        with open("stuff/base.html", "rb") as f:
            text = f.read()
            parts = text.split(b"<body>")
            new_data = parts[0] + data
            return new_data + parts[1]

    def parse_request(self, request: str) -> tuple:
        """Return method as first return value and path as second value
        """
        parts = request.split(b" ")
        return parts[0], parts[1]

    @staticmethod
    def parse_headers(headers_payload: str) -> dict:
        delimiter = b":" if type(headers_payload) == bytes else ":"
        items = [i.split(delimiter, 1) for i in headers_payload.splitlines() if delimiter in i]
        return {k.strip(): v.strip() for k, v in items}

    def read_until(self, sock, chars="\r\n") -> str:
        temp = b""
        while True:
            data = sock.recv(1)
            if not data:
                break
            temp += data
            if chars.encode() in temp:
                return temp

    def read_remaining(self, sock, bytes_number) -> str:
        if int(bytes_number) >= 16777216:
            print("Memory exceeded")
            return False
        temp = b""
        while True:
            data = sock.recv(int(bytes_number))
            if not data:
                return temp
            temp += data


if __name__ == "__main__":
    server = WebServer()
    server.start()
