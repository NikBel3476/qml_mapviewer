from PySide6.QtCore import QObject, Property, Signal, Slot
from PySide6.QtQml import QmlElement
from PySide6.QtPositioning import QGeoCoordinate

QML_IMPORT_NAME = 'MissionItem'
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class MissionItem(QObject):
    __name: str = ''
    __coordinates: QGeoCoordinate

    def __init__(self, name: str, coordinates: QGeoCoordinate):
        super().__init__()
        self.__name = name
        self.__coordinates = coordinates

    def name(self) -> str:
        return self.__name

    def setName(self, name: str):
        if self.__name != name:
            self.__name = name
            self.nameChanged.emit(self.__name)

    nameChanged = Signal(str, arguments=['name'])
    nameProperty = Property(str, name, setName, notify=nameChanged)

    @Slot(result=QGeoCoordinate)
    def coordinates(self) -> QGeoCoordinate:
        return self.__coordinates

    @Slot(QGeoCoordinate)
    def setCoordinates(self, coordinates: QGeoCoordinate):
        if self.__coordinates != coordinates:
            self.__coordinates = coordinates
            self.coordinatesChanged.emit(self.__coordinates)

    coordinatesChanged = Signal(QGeoCoordinate, arguments=['coordinates'])
    coordinatesProperty = Property(QGeoCoordinate, coordinates, setCoordinates, notify=coordinatesChanged)
