import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect(("192.168.0.193", 9090))
    print("Connection established")

    while True:
        message = input("Client: ")
        sock.send(message.encode())
        if message == "Exit":
            break

        server_message = sock.recv(1024).decode()
        print("Server: {}".format(server_message))
except Exception as exc:
    print("Something goes wrong: {}".format(exc))
finally:
    sock.close()
