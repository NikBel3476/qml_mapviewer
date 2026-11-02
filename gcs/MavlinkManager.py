from PySide6.QtCore import QObject, Slot, Signal, QTimer
from PySide6 import QtPositioning
import mavlink
from gcs.Uav import Uav
from gcs.MissionItem import MissionItem

MISSION_UPLOAD_TIMER_TIMEOUT_MS = 5000

class MavlinkManager(QObject):
    __uv: Uav
    __mission_items_to_upload: list[tuple[int, float, float, float]] = []
    __mission_is_uploading = False
    __target_sys_id = 1
    __target_comp_id = mavlink.MAV_COMP_ID_AUTOPILOT1
    __mission_upload_timer: QTimer = QTimer(singleShot=True, interval=MISSION_UPLOAD_TIMER_TIMEOUT_MS)

    send_message = Signal(mavlink.MAVLink_message, arguments=['msg'])

    def __init__(self, uv: Uav):
        super().__init__()
        self.__uv = uv
        self.__mission_upload_timer.timeout.connect(self.mission_upload_finish)

    @Slot(mavlink.MAVLink_message)
    def handle_message_receive(self, msg: mavlink.MAVLink_message):
        # print(f'MSG: id = {msg.get_msgId()} SYS_ID = {msg.get_srcSystem()} COMP_ID = {msg.get_srcComponent()}')
        match msg.get_msgId():
            case mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT:
                pos_int: mavlink.MAVLink_global_position_int_message = msg
                self.__uv.setPos(QtPositioning.QGeoCoordinate(pos_int.lat / 1e7, pos_int.lon / 1e7, pos_int.alt / 1000))
            case mavlink.MAVLINK_MSG_ID_MISSION_ACK:
                mission_ack: mavlink.MAVLink_mission_ack_message = msg
                if mission_ack.type != mavlink.MAV_MISSION_ACCEPTED:
                    raise RuntimeError(f'Mission rejected, ACK type={mission_ack.type}, mission_type={mission_ack.mission_type}, mission_id={mission_ack.opaque_id}')
                self.mission_upload_finish()
                print(f'Mission uploaded')
            case mavlink.MAVLink_mission_request_int_message:
                mission_request: mavlink.MAVLink_mission_request_message = msg
                if not 0 <= mission_request.seq < len(self.__mission_items_to_upload):
                    print(f"Vehicle requested invalid mission item {mission_request.seq}")
                    self.mission_upload_finish()
                elif self.__mission_is_uploading:
                    command, lat, lon, alt = self.__mission_items_to_upload[mission_request.seq]
                    self.send_message.emit(mavlink.MAVLink_mission_item_int_message(
                        target_system=self.__target_sys_id,
                        target_component=self.__target_comp_id,
                        seq=mission_request.seq,
                        frame=mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                        command=command,
                        current=0,
                        autocontinue=1,
                        param1=0,
                        param2=0,
                        param3=0,
                        param4=0,
                        x=int(lat * 1e7),
                        y=int(lon * 1e7),
                        z=float(alt)
                    ))
                    print(f'Sent item {mission_request.seq}: command={command}')


    def send_mission(self, mission_items: list[MissionItem]):
        if not mission_items:
            return

        self.__mission_items_to_upload = [(
            mavlink.MAV_CMD_NAV_WAYPOINT,
            mission_item.coordinates().latitude(),
            mission_item.coordinates().longitude(),
            mission_item.coordinates().altitude()
            )
            for mission_item in mission_items]
        self.__mission_items_to_upload.append((mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0))

        self.__mission_is_uploading = True
        self.send_message.emit(mavlink.MAVLink_mission_count_message(
            target_system=1,
            target_component=mavlink.MAV_COMP_ID_AUTOPILOT1,
            count=len(self.__mission_items_to_upload),
            mission_type=mavlink.MAV_MISSION_TYPE_MISSION,
            opaque_id=0
        ))
        self.__mission_upload_timer.start()


    def mission_upload_finish(self):
        self.__mission_is_uploading = False
        self.__mission_items_to_upload.clear()
