# Клиентская часть

# recv() и send() работают с типом bytes, который требует
# преобразования из/в строку при помощи encode()/decode() соответственно

import socket


def get_ip_address():
    """Вернуть IP-адрес компьютера.

    Фиктивное UDP-подключение к google's DNS,
    после подключения getsockname() вернет локальный IP.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


if __name__ == "__main__":

    sock = socket.socket()
    try:
        print("IP: {}.".format(get_ip_address()))
        # Подключаемся к серверу
        server_ip = input("Введите IP-адрес сервера (например, 192.168.0.3): ")
        print("Подключаюсь к серверу...")
        sock.connect((server_ip, 9090))
        print("Соединение установлено!")

        # Отправляем/получаем данные пока не напишем "Выход"
        while True:
            client_mes = input("Клиент: ")
            sock.send(client_mes.encode())
            if client_mes == "Выход":
                break

            server_mes = sock.recv(1024).decode()
            print("Сервер:", server_mes)
    except Exception as err:
        print("Ошибка: ", err)
    finally:
        sock.close()