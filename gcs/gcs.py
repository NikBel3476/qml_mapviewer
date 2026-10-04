from PySide6.QtGui import QWindow
from PySide6.QtCore import QObject, Signal
from PySide6.QtPositioning import QGeoCoordinate

class GCS(QObject):
    __qml_root_object: QWindow

    def __init__(self, qml_root_object: QWindow):
        super().__init__()
        self.__qml_root_object = qml_root_object
        self.__qml_root_object.mapviewChanged.connect(self.handleMapViewChange)

    def handleMissionPointsChange(self):
        map_view = self.__qml_root_object.property('mapview')
        # if map_view:
            # mission_points = map_view.property('missionPoints')
            # print(f'Mission points changed:')

    def handleMissionPointAdd(self, coordinate: QGeoCoordinate):
        print(f'Add point: ${coordinate}')

    def handleMapViewChange(self):
        map_view = self.__qml_root_object.property('mapview')
        if map_view:
            map_view.missionPointsChanged.connect(self.handleMissionPointsChange)
            map_view.missionPointAdded.connect(self.handleMissionPointAdd)

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
