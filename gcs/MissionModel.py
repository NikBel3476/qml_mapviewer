from PySide6.QtCore import QAbstractListModel, QByteArray, QModelIndex, QPersistentModelIndex, Qt, Slot, QObject, Signal
from PySide6.QtQml import QmlElement
from PySide6.QtPositioning import QGeoCoordinate
from PySide6 import QtPositioning
from typing import Optional, Any
from gcs.MissionItem import MissionItem

QML_IMPORT_NAME = 'MissionModel'
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class MissionModel(QObject):

    # CoordinatesRole = Qt.ItemDataRole.UserRole + 1
    __mission_items: list[MissionItem] = []

    def __init__(self):
        super().__init__()

        self.missionItemAdded.connect(lambda: self.missionItemsChanged.emit(self.__mission_items))

    # def rowCount(self, parent: QModelIndex | QPersistentModelIndex=QModelIndex()) -> int:
    #     return len(self.__mission_points)

    # def roleNames(self) -> dict[int, QByteArray]:
    #     default = super().roleNames()
    #     default[self.CoordinatesRole] = QByteArray(b'coordinates')
    #     # default[Qt.ItemDataRole.BackgroundRole] = QByteArray(b"backgroundColor")
    #     return default

    # def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.UserRole):
    #     ret = None
    #     if self.__mission_points and index.isValid():
    #         item = self.__mission_points[index.row()]
    #         ret = item
    #         match role:
    #             case Qt.ItemDataRole.DisplayRole:
    #                 ret = item.name()
    #             # case Qt.ItemDataRole.BackgroundRole:
    #             #     ret = item["bgColor"]
    #             case self.CoordinatesRole:
    #                 ret = item.coordinates
    #             case _:
    #                 pass
    #     return ret

    # def setData(self, index: QModelIndex | QPersistentModelIndex, value: Any, role: int = Qt.ItemDataRole.UserRole) -> bool:
    #     if not index.isValid():
    #         return False
    #     if role == Qt.ItemDataRole.EditRole:
    #         self.__mission_points[index.row()].setName(value)
    #     return True

    # @Slot(result=bool)
    # def append(self):
    #     """Slot to append a row at the end"""
    #     return self.insertRow(self.rowCount())

    # def insertRow(self, row: int, parent: QModelIndex | QPersistentModelIndex=QModelIndex()) -> bool:
    #     """Insert a single row at row"""
    #     return self.insertRows(row, 0, parent)

    # def insertRows(self, row: int, count: int, parent: QModelIndex | QPersistentModelIndex=QModelIndex()) -> bool:
    #     """Insert n rows (n = 1 + count)  at row"""

    #     self.beginInsertRows(parent, row, row + count)
    #     for _ in range(count):
    #         name = str(0 if self.rowCount() == 0 else self.rowCount() + 1)
    #         self.__mission_points.insert(row, MissionItem(name, QGeoCoordinate()))
    #     self.endInsertRows()
    #     return True

    @Slot(QGeoCoordinate)
    def addNextPoint(self, coordinates: QGeoCoordinate):
        new_mission_item = MissionItem(name=str(len(self.__mission_items) + 1), coordinates=coordinates)
        print(f'Add next point: {new_mission_item}')
        self.__mission_items.append(new_mission_item)
        self.missionItemAdded.emit(new_mission_item)

    # FIXME: if define type as list[MissionItem] qt meta object system breaks
    missionItemsChanged = Signal(list, arguments=['missionItems'])
    missionItemAdded = Signal(MissionItem, arguments=['missionItem'])

    # @Slot(int, int, result=bool)
    # def move(self, source: int, target: int):
    #     """Slot to move a single row from source to target"""
    #     return self.moveRow(QModelIndex(), source, QModelIndex(), target)

    # def moveRow(self, sourceParent, sourceRow, dstParent, dstChild):
    #     """Move a single row"""
    #     return self.moveRows(sourceParent, sourceRow, 0, dstParent, dstChild)

    # def moveRows(self, sourceParent, sourceRow, count, dstParent, dstChild):
    #     """Move n rows (n=1+ count)  from sourceRow to dstChild"""

    #     if sourceRow == dstChild:
    #         return False

    #     elif sourceRow > dstChild:
    #         end = dstChild

    #     else:
    #         end = dstChild + 1

    #     self.beginMoveRows(QModelIndex(), sourceRow, sourceRow + count, QModelIndex(), end)

    #     # start database work
    #     pops = self.db[sourceRow: sourceRow + count + 1]
    #     if sourceRow > dstChild:
    #         self.db = (
    #             self.db[:dstChild]
    #             + pops
    #             + self.db[dstChild:sourceRow]
    #             + self.db[sourceRow + count + 1:]
    #         )
    #     else:
    #         start = self.db[:sourceRow]
    #         middle = self.db[dstChild: dstChild + 1]
    #         endlist = self.db[dstChild + count + 1:]
    #         self.db = start + middle + pops + endlist
    #     # end database work

    #     self.endMoveRows()
    #     return True

    # @Slot(int, result=bool)
    # def remove(self, row: int):
    #     """Slot to remove one row"""
    #     print(f'Remove row: {row}')
    #     return True
    #     # return self.removeRow(row)

    # def removeRow(self, row: int, parent: QModelIndex | QPersistentModelIndex=QModelIndex()) -> bool:
    #     """Remove one row at index row"""
    #     return self.removeRows(row, 0, parent)

    # def removeRows(self, row: int, count: int, parent: QModelIndex | QPersistentModelIndex=QModelIndex()) -> bool:
    #     """Remove n rows (n=1+count) starting at row"""
    #     self.beginRemoveRows(QModelIndex(), row, row + count)
    #     self.__mission_points = self.__mission_points[:row] + self.__mission_points[row + count + 1:]
    #     self.endRemoveRows()
    #     return True

    # @Slot(result=bool)
    # def reset(self) -> bool:
    #     self.beginResetModel()
    #     self.__mission_points.clear()
    #     self.endResetModel()
    #     return True
