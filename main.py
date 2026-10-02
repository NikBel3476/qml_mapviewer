# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the location/mapviewer example from Qt v6.x"""

import os
import sys
import socket
import mavlink
import threading
import random
from pathlib import Path
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtGui import QGuiApplication
from PySide6.QtNetwork import QSslSocket
from PySide6.QtCore import QCoreApplication, QMetaObject, Q_ARG, QTimer
from PySide6 import QtPositioning
import uav

IS_TEST = False
HOST = '127.0.0.1'
PORT = 5760
BUFFER_SIZE = 1024
SYS_ID = 255
APP_NAME = 'GCS'
HELP = '''Usage:
plugin.<parameter_name> <parameter_value> - Sets parameter = value for plugin'''

def run_tcp_client(stopEvent: threading.Event, host: str, port: int, uv: uav.Uav):
    mav = mavlink.MAVLink(None, SYS_ID, mavlink.MAV_COMP_ID_MISSIONPLANNER)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((host, port))
            print(f"Connected to {host}:{port}. Reading data continuously...")
            while not stopEvent.is_set():
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    print("Server closed the connection.")
                    break
                # print(f"Received: {data}")

                msg = mav.parse_char(data)
                if msg:
                    # print(f'MSG: id = {msg.get_msgId()} SYS_ID = {msg.get_srcSystem()} COMP_ID = {msg.get_srcComponent()}')
                    match msg.get_msgId():
                        case mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT:
                            uv.setPos(QtPositioning.QGeoCoordinate(msg.lat / 10e7, msg.lon / 10e7, msg.alt / 1000))

        except KeyboardInterrupt:
            print("\nClient stopped by user.")
        except socket.error as e:
            print(f"Socket error occurred: {e}")

def parseArgs(args):
    parameters = {}
    while args:
        param = args[0]
        args = args[1:]
        if param.startswith("--plugin."):
            param = param[9:]
            if not args or args[0].startswith("--"):
                parameters[param] = True
            else:
                value = args[0]
                args = args[1:]
                if value in ("true", "on", "enabled"):
                    parameters[param] = True
                elif value in ("false", "off", "disable"):
                    parameters[param] = False
                else:
                    parameters[param] = value
        parameters[param] = True
    return parameters


if __name__ == "__main__":
    additionalLibraryPaths = os.environ.get("QTLOCATION_EXTRA_LIBRARY_PATH")
    if additionalLibraryPaths:
        for p in additionalLibraryPaths.split(':'):
            QCoreApplication.addLibraryPath(p)

    application = QGuiApplication(sys.argv)
    QCoreApplication.setApplicationName(APP_NAME)
    QGuiApplication.setDesktopFileName(QCoreApplication.applicationName())

    args = sys.argv[1:]
    if "--help" in args:
        print(f"{APP_NAME}\n\n{HELP}")
        sys.exit(0)

    parameters = parseArgs(args)
    if not parameters.get("osm.useragent"):
        parameters["osm.useragent"] = APP_NAME
    IS_TEST = '--test' in parameters

    uv = uav.Uav()

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("supportsSsl",
                                            QSslSocket.supportsSsl())
    engine.addImportPath(Path(__file__).parent)
    engine.loadFromModule("MapViewer", "Main")
    engine.quit.connect(QCoreApplication.quit)

    items = engine.rootObjects()
    if not items:
        sys.exit(-1)

    root_item = items[0]
    QMetaObject.invokeMethod(root_item, "initializeProviders",
                             Q_ARG("QVariant", parameters))
    root_item.setProperty('uav', uv)

    uv.setPos(QtPositioning.QGeoCoordinate(56.852586, 53.182805, 100.0))

    stopEvent = threading.Event()
    thread = threading.Thread(target=run_tcp_client, args=(stopEvent, HOST, PORT, uv))

    thread.start()

    if IS_TEST:
        def updatePos():
            currPos = uv.pos()
            uv.setPos(
                QtPositioning.QGeoCoordinate(
                    currPos.latitude() + random.uniform(-0.0001, 0.0001),
                    currPos.longitude() + random.uniform(-0.0001, 0.0001),
                    currPos.altitude() + random.uniform(-2, 2)
                )
            )

        pos_update_timer = QTimer()
        pos_update_timer.setInterval(1000)
        pos_update_timer.timeout.connect(updatePos)
        pos_update_timer.start()

    exit_code = application.exec()
    del engine
    stopEvent.set()
    thread.join()
    sys.exit(exit_code)
