import socket
import time

# Определяем адрес и порт принтера
PRINTER_ADDRESS = '192.168.1.100'
PRINTER_PORT = 9100

# Определяем константы для формирования запросов и ответов
SOH = b'\x01\x01\x01\x01\x01'  # Начало сообщения
STX = b'\x02'  # Начало блока данных
ETX = b'\x03'  # Конец блока данных
EOT = b'\x04'  # Конец сообщения

# Определяем команды для взаимодействия с принтером
CMD_STATUS = b'STATUS'
CMD_COUNTER = b'COUNTER'
CMD_SELECT = b'SELECT'
CMD_PRINT = b'PRINT'
CMD_STOP = b'STOP'


# Функция для отправки запроса к принтеру и получения ответа
def send_receive_data(cmd, data=None):
    # Формируем запрос
    if data:
        request = SOH + cmd + STX + data + ETX + EOT
    else:
        request = SOH + cmd + EOT

    # Отправляем запрос
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((PRINTER_ADDRESS, PRINTER_PORT))
        sock.sendall(request)

        # Получаем ответ
        response = sock.recv(1024)

    # Очищаем ответ от служебных символов
    response = response.replace(SOH, b'').replace(EOT, b'')

    return response


# Пример использования функций
while True:
    # Запрашиваем состояние принтера
    status = send_receive_data(CMD_STATUS)
    print(f"Status: {status.decode('utf-8')}")

    # Запрашиваем количество отпечатков
    counter = send_receive_data(CMD_COUNTER)
    print(f"Counter: {counter.decode('utf-8')}")

    # Выбираем шаблон
    template_id = b'TEMPLATE1'
    select_response = send_receive_data(CMD_SELECT, template_id)
    print(f"Template selected: {select_response.decode('utf-8')}")

    # Печатаем данные
    data_to_print = b"Hello, world!\n"
    print_response = send_receive_data(CMD_PRINT, data_to_print)
    print(f"Print response: {print_response.decode('utf-8')}")

    # Прерываем печать
    stop_response = send_receive_data(CMD_STOP)
    print(f"Stop response: {stop_response.decode('utf-8')}")

    # Ждём 5 секунд перед повторным опросом
    time.sleep(5)