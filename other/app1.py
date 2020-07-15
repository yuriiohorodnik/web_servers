import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', 9090))
sock.listen()

conn, addr = sock.accept()

try:
    print(f"Connection established: {addr}")
    while True:
        message = conn.recv(1024).decode()
        if not message:
            break

        print(f"Client: {message}")
        if message == "Exit":
            break

        conn.send(input("Server: ").encode())
    print("Connection refused")
except Exception as exc:
    print(f"Error: {exc}")
finally:
    conn.close()
