import socket


class WebClient:
    def __init__(self, port):
        self.host = socket.gethostname()
        self.port = port

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.host, self.port))
        except Exception as exc:
            print(f"Connection failed: {exc}")
            self.sock.close()

    def send_and_recieve(self, request):
        BUFFER_SIZE = 1024
        b_request = request.encode()
        try:
            self.sock.send(b_request)
            print("Sent!")
            while True:
                message = self.sock.recv(BUFFER_SIZE).decode()
                if not message:
                    break
                print(f"Server: {message}")
        except Exception as exc:
            print(f"Was not send. {exc}")


if __name__ == "__main__":
    client = WebClient(8888)
    client.connect()
    req = "HTTP/1.1 / GET"
    client.send_and_recieve(req)
