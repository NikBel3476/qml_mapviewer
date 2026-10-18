# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""PySide6 port of the location/mapviewer example from Qt v6.x"""

import os
import sys
from pathlib import Path
from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent
from PySide6.QtGui import QGuiApplication
from PySide6.QtNetwork import QSslSocket
from PySide6.QtCore import QCoreApplication, QMetaObject, Q_ARG
from gcs.GCS import GCS

IS_TEST = False
APP_NAME = 'GCS'
HELP = '''Usage:
plugin.<parameter_name> <parameter_value> - Sets parameter = value for plugin'''

def parseArgs(args: list[str]) -> dict[str, bool | str]:
    parameters: dict[str, bool | str] = {}
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
    # IS_TEST = '--test' in parameters

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("supportsSsl",
                                            QSslSocket.supportsSsl())
    engine.addImportPath(Path(__file__).parent)
    qml_component = QQmlComponent(engine)
    qml_component.loadFromModule("MapViewer", "Main")
    engine.quit.connect(QCoreApplication.quit)

    qml_main = qml_component.create()
    gcs = GCS(qml_main)
    QMetaObject.invokeMethod(qml_main, "initializeProviders",
                             Q_ARG("QVariant", parameters))

    # if IS_TEST:
    #     def updatePos():
    #         currPos = uv.pos()
    #         uv.setPos(
    #             QtPositioning.QGeoCoordinate(
    #                 currPos.latitude() + random.uniform(-0.0001, 0.0001),
    #                 currPos.longitude() + random.uniform(-0.0001, 0.0001),
    #                 currPos.altitude() + random.uniform(-2, 2)
    #             )
    #         )

    #     pos_update_timer = QTimer()
    #     pos_update_timer.setInterval(1000)
    #     pos_update_timer.timeout.connect(updatePos)
    #     pos_update_timer.start()

    exit_code = application.exec()
    del gcs
    del engine
    sys.exit(exit_code)
