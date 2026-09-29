# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the location/mapviewer example from Qt v6.x"""

import os
import sys
import socket
import mavlink
import threading
from pathlib import Path
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtGui import QGuiApplication
from PySide6.QtNetwork import QSslSocket
from PySide6.QtCore import QCoreApplication, QMetaObject, Q_ARG
import uav

HELP = """Usage:
plugin.<parameter_name> <parameter_value> - Sets parameter = value for plugin"""
HOST = '127.0.0.1'
PORT = 5760
BUFFER_SIZE = 1024
SYS_ID = 255

def run_tcp_client(host: str, port: int, uv: uav.Uav):
    mav = mavlink.MAVLink(None, SYS_ID, mavlink.MAV_COMP_ID_MISSIONPLANNER)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((host, port))
            print(f"Connected to {host}:{port}. Reading data continuously...")
            while True:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    print("Server closed the connection.")
                    break
                # print(f"Received: {data}")

                msg = mav.parse_char(data)
                if msg:
                    print(f'MSG: id = {msg.get_msgId()} SYS_ID = {msg.get_srcSystem()} COMP_ID = {msg.get_srcComponent()}')

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
    return parameters


if __name__ == "__main__":
    additionalLibraryPaths = os.environ.get("QTLOCATION_EXTRA_LIBRARY_PATH")
    if additionalLibraryPaths:
        for p in additionalLibraryPaths.split(':'):
            QCoreApplication.addLibraryPath(p)

    application = QGuiApplication(sys.argv)
    name = "QtLocation Mapviewer example"
    QCoreApplication.setApplicationName(name)
    QGuiApplication.setDesktopFileName(QCoreApplication.applicationName())

    args = sys.argv[1:]
    if "--help" in args:
        print(f"{name}\n\n{HELP}")
        sys.exit(0)

    parameters = parseArgs(args)
    if not parameters.get("osm.useragent"):
        parameters["osm.useragent"] = name

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

    thread = threading.Thread(target=run_tcp_client, args=(HOST, PORT, uv))

    thread.start()
    exit_code = application.exec()
    del engine
    thread.join()
    sys.exit(exit_code)
