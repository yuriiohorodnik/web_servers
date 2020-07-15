# Серверная часть

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

    # Слушаем подключение 1 клиента
    print("IP: {}. Жду подключения...".format(get_ip_address()))
    sock.bind(("", 9090))
    sock.listen(1)  # Макс. кол-во соединений - 1

    conn, addr = sock.accept()
    # 'addr' в конечном итоге содержит отличный от указанного в bind()
    # порт за счет того, что ОС назначает его самостоятельно
    try:
        print("Соединение установлено:", addr)

        # Отправляем/получаем данные пока клиент не напишет "Выход"
        while True:
            # 'client_mes' перестает приходить при закрытии соединения
            # со стороны клиента
            client_mes = conn.recv(1024).decode()
            if not client_mes:
                break

            print("Клиент:", client_mes)
            if client_mes == "Выход":
                break

            conn.send(input("Сервер: ").encode())
        print("Соединение закрыто.")
    except Exception as err:
        print("Ошибка: ", err)
    finally:
        conn.close()