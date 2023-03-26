import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import socket
import sqlite3

class PrinterListener(QThread):
    message_signal = pyqtSignal(str)

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('localhost', 12345))
        s.listen()

        while True:
            conn, addr = s.accept()
            data = conn.recv(1024)
            message = data.decode()
            conn.sendall(b'OK')
            conn.close()

            self.message_signal.emit(message)


class PrinterClient(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.initDatabase()

    def initUI(self):
        self.address_label = QLabel('Введите адрес принтера: ', self)
        self.address_label.move(10, 10)

        self.address_edit = QLineEdit(self)
        self.address_edit.move(10, 30)
        self.address_edit.setText('localhost')

        self.port_label = QLabel('Введите порт принтера: ', self)
        self.port_label.move(10, 60)

        self.port_edit = QLineEdit(self)
        self.port_edit.move(10, 80)
        self.port_edit.setText('12345')

        self.command_label = QLabel('Введите команду: ', self)
        self.command_label.move(10, 110)

        self.command_edit = QLineEdit(self)
        self.command_edit.move(10, 130)

        self.data_label = QLabel('Введите данные (если нужно): ', self)
        self.data_label.move(10, 160)

        self.data_edit = QLineEdit(self)
        self.data_edit.move(10, 180)

        self.send_button = QPushButton('Отправить', self)
        self.send_button.move(10, 210)
        self.send_button.clicked.connect(self.send_message)

        self.status_button = QPushButton('STATUS', self)
        self.status_button.move(130, 210)
        self.status_button.clicked.connect(lambda: self.send_command('STATUS'))

        self.counter_button = QPushButton('COUNTER', self)
        self.counter_button.move(210, 210)
        self.counter_button.clicked.connect(lambda: self.send_command('COUNTER'))

        self.select_button = QPushButton('SELECT', self)
        self.select_button.move(290, 210)
        self.select_button.clicked.connect(lambda: self.send_command('SELECT', self.data_edit.text()))

        self.print_button = QPushButton('PRINT', self)
        self.print_button.move(10, 240)
        self.print_button.clicked.connect(lambda: self.send_command('PRINT', self.data_edit.text()))

        self.stop_button = QPushButton('STOP', self)
        self.stop_button.move(130, 240)
        self.stop_button.clicked.connect(self.stop_printing)

        self.log_button = QPushButton('Показать лог', self)
        self.log_button.move(210, 240)
        self.log_button.clicked.connect(self.show_log)

        self.log_table = QTableWidget(self)
        self.log_table.setGeometry(10, 280, 400, 200)
        self.log_table.setColumnCount(3)
        self.log_table.setHorizontalHeaderLabels(['ID', 'Команда', 'Ответ'])

        self.setGeometry(500, 500, 420, 500)
        self.setWindowTitle('Клиент принтера')
        self.show()

    def initDatabase(self):
        self.conn = sqlite3.connect('printer_log.db')
        self.c = self.conn.cursor()

    def send_message(self):
        host = self.address_edit.text()
        port = int(self.port_edit.text())

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))

        message = self.command_edit.text() + '[' + self.data_edit.text() + ']'
        message = chr(1) + message + chr(3)
        s.sendall(message.encode())

        data = s.recv(1024)
        s.close()

        response = data.decode().strip(chr(1)).strip(chr(4))
        self.save_to_database(message, response)
        QMessageBox.information(self, 'Ответ принтера', response)

    def send_command(self, command, data=None):
        self.command_edit.setText(command)
        self.data_edit.setText(data)
        self.send_message()

    def stop_printing(self):
        self.send_command('STOP')

    def save_to_database(self, command, response):
        self.c.execute("INSERT INTO print_log (command, response) VALUES (?, ?)", (command, response))
        self.conn.commit()

    def show_log(self):
        self.log_table.setRowCount(0)
        for row in self.c.execute("SELECT * FROM print_log"):
            self.log_table.insertRow(self.log_table.rowCount())
            for i, value in enumerate(row):
                self.log_table.setItem(self.log_table.rowCount()-1, i, QTableWidgetItem(str(value)))

    def closeEvent(self, event):
        self.conn.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PrinterClient()
    sys.exit(app.exec_())