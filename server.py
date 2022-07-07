# -*- coding: utf-8 -*-

"""
Echo-сервер, адрес: 127.0.0.1:9090
Принимает: стартовую строку и набор HTTP-заголовков HTTP-запроса от клиента
Возвращает: информацию о HTTP-запросе клиента в формате
Request Method: GET | POST | PUT | HEAD| DELETE | OPTIONS | CONNECT
Request Source: <IP-address>:<PORT>
Response Status: <CODE> <Name>
header-name:header-value
...

Код ответа можно передать в параметре запроса status=[CODE]
    Пример:
    http://127.0.0.1:9090/?status=200

В случае, если параметр запроса status отсутствует, имеет пустое или иное невалидное значение,
код ответа устанавливается равным 200

"""

import socket
import re
from collections import defaultdict
from http import HTTPStatus

SERVER_IP = 'localhost'
PORT = 9090
# Зададим максимальное количество соединений в очереди
QUEUED_CONNECTIONS = 1
# Регулярные выражения для поиска нужных значений в HTTP-запросе клиента
METHOD = re.compile(r"(GET|POST|PUT|HEAD|DELETE|OPTIONS|CONNECT)")
STATUS = re.compile(r"\?status=([1-5][0-9]{2})")
STATUS_CODE = 200
HEADERS = defaultdict(str)
method_string = ''

# Создаём словарь с ключами Код статуса HTTP и значениями "Пояснение кода"
statuses = defaultdict(str)
for i in list(HTTPStatus):
    statuses[int(i.value)] = i.phrase

# Создаём объект сокета
sock = socket.socket()
# Осуществляем привязку IP-адреса и порта к сокету
sock.bind((SERVER_IP, PORT))
# Зададим размер очереди клиентов, ожидающих соединения
sock.listen(QUEUED_CONNECTIONS)
# Зададим тайм-аут работы сокета
sock.settimeout(60)
# Принимаем подключение
conn, client_address = sock.accept()      # метод возвращает кортеж (новый_сокет, адрес_клиента)
request_source = f"Request source: {client_address[0]}:{client_address[1]}\n"

while True:
    data = conn.recv(1024)
    if not data:
        break
    else:
        request = data.decode().split("\r\n")
        general = request[0]
        headers = request[1:]
        method = METHOD.search(general)
        if method is not None:
            request_method = method.group()
            method_string = f"Request method: {request_method}\n"

        if general.find('status=') != -1:
            status_value = STATUS.search(general)
            # Проверка кода статуса и присваивание ему значения
            if status_value is not None:
                received_code = int(status_value.group(1))
                if received_code in statuses.keys():
                    STATUS_CODE = received_code
                else:
                    print(f"Incorrect status code!\nsubstituded value is {STATUS_CODE}\n")
            else:
                print(f"No status value was passed.\nsubstituded value is {STATUS_CODE}\n")
        else:
            print(f"Parameter \"status\" wasn\'t sent, substituded value is {STATUS_CODE}\n")

        status_string = f"Response Status: {STATUS_CODE}  {statuses[STATUS_CODE]}\n"

    rep_str = method_string + request_source + status_string + '\n'.join(headers)
    conn.send(rep_str.encode())

conn.close()
