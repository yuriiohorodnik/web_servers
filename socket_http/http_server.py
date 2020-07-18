import socket
import sys
import time
import base64

SECRET_CREDENTIALS = b"root:password"
METHODS = ["GET", "POST"]


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
            print("Trying to close socket...")
            self.sock.close()
            print("Socket closed")
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
        return header

    def _listen(self):
        self.sock.listen()
        while True:
            conn, addr = self.sock.accept()
            print("Recieved connection from {}".format(addr))
            self._handle_request(conn, addr)

    def _handle_request(self, conn, addr):
        PACKET_SIZE = 1024

        while True:
            all_data = conn.recv(PACKET_SIZE).decode()
            if not all_data:
                break
            print(f"All data: {all_data}")
            print(f"Type of all_data: {type(all_data)}")
            data = all_data.split('\r\n')
            print(f"splitted data: {data}")
            print(data)
            headers = {}
            request_line = data[0].split(" ")
            method, path = request_line[0], request_line[1]
            for line in data:
                if ":" in line:
                    parts = line.split(":")
                    headers[parts[0]] = parts[1].strip()
            print(f"Method: {method}")
            print(f"Headers: {headers}")
            print(f"Request: {data}")
            if method not in METHODS:
                print("Unknown HTTP request method: {method}".format(
                    method=method))
            elif "Authorization" in headers:
                auth_type, password = (
                    headers["Authorization"].split(" ")[0].strip(),
                    headers["Authorization"].split(" ")[1].strip())
                print(f"auth_type: {auth_type}, password: {password}")
                if self.process_auth(auth_type, password):
                    if path == "/":
                        path = "/index.html"

                    filepath_to_serve = self.content_folder + path
                    print(f"Serving web page {filepath_to_serve}")

                    try:
                        if method == "GET":
                            f = open(filepath_to_serve, 'rb')
                            response_data = f.read()
                            response_header = self.generate_headers(200)  # my comments take up more than 88 symbols
                            f.close()
                        elif method == "POST":
                            values = {}
                            passed_data = all_data.split("\r\n\r\n")[1].split("&")
                            for item in passed_data:
                                temp = item.split("=")
                                values[temp[0]] = temp[1]
                            response_header = self.generate_headers(202)
                            response_data = self.create_page_with_data(str(values))
                            print(f"passed data: {values}")
                    except Exception:
                        print("File not found. Serving 404 page.")
                        response_header = self.generate_headers(404)
                        if method == "GET":
                            response_data = (b"<html><body><center><h1>Error 404:"
                                             b"File not found</h1></center><p>Head"
                                             b' back to <a href="/">dry land</a>.'
                                             b"</p></body></html>")
                    response = response_header.encode()
                    print(f"RESPONSE DATA: {response_data}")
                    response += response_data
                    conn.sendall(response)
                    print(f"RESPONSE: {response}")
                    print("Sent!")
                    break
                else:
                    print("Wrong credentials entered")
            elif "Authorization" not in data:
                response_header = self.generate_headers(401)
                print(f"401 Header: {response_header}")
                conn.sendall(response_header.encode())
                print("Sent!")
                break
        conn.close()

    def process_auth(self, auth_type, password):
        if auth_type == "Basic":
            if (base64.standard_b64decode(password.encode()) ==
                    SECRET_CREDENTIALS):
                return True
        return False

    def create_page_with_data(self, data):
        with open("stuff/base.html", "rb") as f:
            text = f.read()
            parts = text.split(b"<body>")
            new_data = parts[0] + data.encode()
            return new_data + parts[1]


if __name__ == "__main__":
    server = WebServer()
    server.start()
