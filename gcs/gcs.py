from PySide6.QtGui import QWindow
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtPositioning import QGeoCoordinate
from gcs.MissionModel import MissionModel
from gcs.MissionItem import MissionItem
from pprint import pprint

class GCS(QObject):
    __qml_root_object: QWindow
    __mission_model: MissionModel = MissionModel()

    def __init__(self, qml_root_object: QWindow):
        super().__init__()
        self.__qml_root_object = qml_root_object

        self.__qml_root_object.mapviewChanged.connect(self.handleMapViewChange)
        self.__qml_root_object.uploadMission.connect(self.handleUploadMission)

        self.__mission_model.missionItemAdded.connect(self.handleMissionItemAdd)
        self.__mission_model.missionItemsChanged.connect(self.handleMissionItemsChange)

    @Slot(QGeoCoordinate)
    def handleMissionItemAdd(self, coordinate: QGeoCoordinate):
        print(f'Add point: ${coordinate}')

    def handleMissionItemsChange(self, missionItems: list[MissionItem]):
        print('Mission items changed')
        pprint(missionItems)

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
