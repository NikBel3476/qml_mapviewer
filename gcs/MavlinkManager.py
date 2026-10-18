from PySide6.QtCore import QObject, Slot, Signal
from PySide6 import QtPositioning
import mavlink
from gcs.Uav import Uav
from gcs.MissionItem import MissionItem

class MavlinkManager(QObject):
    __uv: Uav

    send_message = Signal(mavlink.MAVLink_message, arguments=['msg'])

    def __init__(self, uv: Uav):
        super().__init__()
        self.__uv = uv

    @Slot(mavlink.MAVLink_message)
    def handle_message_receive(self, msg: mavlink.MAVLink_message):
        # print(f'MSG: id = {msg.get_msgId()} SYS_ID = {msg.get_srcSystem()} COMP_ID = {msg.get_srcComponent()}')
        match msg.get_msgId():
            case mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT:
                pos_int: mavlink.MAVLink_global_position_int_message = msg
                self.__uv.setPos(QtPositioning.QGeoCoordinate(pos_int.lat / 10e7, pos_int.lon / 10e7, pos_int.alt / 1000))

    def send_mission(self, mission_items: list[MissionItem]):
        pass