import socket
import sys
import time
import base64



SECRET_CREDENTIALS = b"root:password"



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
            data = conn.recv(PACKET_SIZE).decode()
            if not data:
                break

            request_method = data.split(' ')[0]
            print(f"Method: {request_method}")
            print(f"Request: {data}")
            if request_method == "GET" and "Authorization" in data:
                for line in data.split('\r\n'):
                    if "Authorization:" in line:
                        password = line.split(' ')[2]
                        print(f"Recieved password: {password}")
                        if self.do_auth(password):
                            request_path = data.split(' ')[1]

                            if request_path == "/":
                                request_path = "/index.html"

                            filepath_to_serve = self.content_folder + request_path
                            print(f"Serving web page {filepath_to_serve}")

                            try:
                                f = open(filepath_to_serve, 'rb')
                                if request_method == "GET":
                                    response_data = f.read()
                                f.close()
                                response_header = self.generate_headers(200)
                            except Exception:
                                print("File not found. Serving 404 page.")
                                response_header = self.generate_headers(404)

                                if request_method == "GET":
                                    response_data = (b"<html><body><center><h1>Error 404:"
                                                    b"File not found</h1></center><p>Head"
                                                    b' back to <a href="/">dry land</a>.'
                                                    b"</p></body></html>")

                            response = response_header.encode()
                            if request_method == "GET":
                                response += response_data
                            conn.sendall(response)
                            print("Sent!")
                            break
                        else:
                            print("Wrong credentials entered")
            elif request_method == "GET" and "Authorization" not in data:
                response_header = self.generate_headers(401)
                print(f"401 Header: {response_header}")
                conn.sendall(response_header.encode())
                print("Sent!")
                break
            else:
                print("Unknown HTTP request method: {method}".format(
                    method=request_method))
        conn.close()

    def do_auth(self, password):
        if base64.standard_b64decode(password.encode()) == SECRET_CREDENTIALS:
            return True
        return False

if __name__ == "__main__":
    server = WebServer()
    server.start()
