from PySide6.QtCore import QObject, Signal, Slot, QThread
from PySide6.QtPositioning import QGeoCoordinate
from gcs.MissionModel import MissionModel
from gcs.MissionItem import MissionItem
from gcs.MavlinkManager import MavlinkManager
from gcs.ConnectionWorker import ConnectionWorker
from gcs.Uav import Uav

class GCS(QObject):
    __qml_root_object: QObject
    __mission_model: MissionModel = MissionModel()
    __uv = Uav()
    __mavlink_manager = MavlinkManager(__uv)
    __connection_worker = ConnectionWorker()
    __connection_worker_thread = QThread()

    def __init__(self, qml_root_object: QObject):
        super().__init__()
        self.__qml_root_object = qml_root_object

        self.__qml_root_object.setProperty('uav', self.__uv)

        self.__qml_root_object.mapviewChanged.connect(self.handleMapViewChange)
        self.__qml_root_object.uploadMission.connect(self.handleUploadMission)

        self.__mission_model.missionItemAdded.connect(self.handleMissionItemAdd)
        self.__mission_model.missionItemsChanged.connect(self.handleMissionItemsChange)

        self.__mavlink_manager.send_message.connect(self.__connection_worker.send_message)

        self.__connection_worker.moveToThread(self.__connection_worker_thread)
        self.__connection_worker.message_received.connect(self.__mavlink_manager.handle_message_receive)

        self.__connection_worker_thread.started.connect(self.__connection_worker.run_tcp_client)
        self.__connection_worker_thread.finished.connect(self.__connection_worker.deleteLater)
        self.__connection_worker_thread.start()

    def __del__(self):
        print('GCS del')
        self.__connection_worker_thread.quit()
        self.__connection_worker_thread.wait()

    @Slot(QGeoCoordinate)
    def handleMissionItemAdd(self, coordinate: QGeoCoordinate):
        print(f'Add point: ${coordinate}')

    def handleMissionItemsChange(self, missionItems: list[MissionItem]):
        print('Mission items changed')

    def handleMapViewChange(self):
        map_view = self.__qml_root_object.property('mapview')
        if map_view:
            map_view.setProperty('missionModel', self.__mission_model)

    def handleUploadMission(self):
        print('Upload mission')

    def missionPoints(self) -> list[QGeoCoordinate]:
        return self.__mission_points

    def setMissionPoints(self, mission_points: list[QGeoCoordinate]):
        if self.__mission_points != mission_points:
            self.__mission_points = mission_points
            self.missionPointsChanged.emit(self.__mission_points)

    def addMissionPoint(self, mission_point: QGeoCoordinate):
        self.__mission_points.append(mission_point)
        self.missionPointsChanged.emit(self.__mission_points)

    missionPointsChanged = Signal(list[QGeoCoordinate], arguments=['mission_points'])
