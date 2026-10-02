from PySide6.QtCore import QObject, Property, Signal
from PySide6 import QtPositioning

class Uav(QObject):
    __pos: QtPositioning.QGeoCoordinate = QtPositioning.QGeoCoordinate(latitude=0.0, longitude=0.0, altitude=0.0)

    def __init__(self):
        super().__init__()

    def pos(self) -> QtPositioning.QGeoCoordinate:
        return self.__pos

    def setPos(self, pos: QtPositioning.QGeoCoordinate):
        if (self.__pos != pos):
            self.__pos = pos
            self.posChanged.emit(self.__pos)

    posChanged = Signal(QtPositioning.QGeoCoordinate, arguments=['pos'])

    value = Property(int, pos, setPos, notify=posChanged)
