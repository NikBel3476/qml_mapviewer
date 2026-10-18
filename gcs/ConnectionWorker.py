from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtNetwork import QTcpSocket
# import socket
import mavlink

HOST = '127.0.0.1'
PORT = 5760
# BUFFER_SIZE = 1024
SYS_ID = 255

class ConnectionWorker(QObject):
    __mav: mavlink.MAVLink = mavlink.MAVLink(None, SYS_ID, mavlink.MAV_COMP_ID_MISSIONPLANNER)
    __client_socket = QTcpSocket()

    message_received = Signal(mavlink.MAVLink_message)

    def __init__(self):
        super().__init__()

    def run_tcp_client(self, host: str = HOST, port: int = PORT):
        self.__client_socket = QTcpSocket()
        self.__client_socket.readyRead.connect(self.handle_ready_read)
        self.__client_socket.connectToHost(host, port)
        print(f"Connected to {host}:{port}. Reading data continuously...")

    @Slot()
    def handle_ready_read(self):
        msg = self.__mav.parse_char(self.__client_socket.readAll().data())
        if msg:
            self.message_received.emit(msg)

    @Slot(mavlink.MAVLink_message)
    def send_message(self, msg: mavlink.MAVLink_message):
        self.__client_socket.write(msg.pack(self.__mav))
