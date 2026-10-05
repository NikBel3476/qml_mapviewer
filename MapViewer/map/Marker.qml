// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtLocation

MapQuickItem {
    id: marker
    property string text: ''

    anchorPoint.x: image.width/4
    anchorPoint.y: image.height

    HoverHandler {
        id: hoverHandler
    }

    // TapHandler {
    //     id: tapHandler
    //     acceptedButtons: Qt.RightButton
    //     gesturePolicy: TapHandler.WithinBounds
    //     onTapped: {
    //         mapview.currentMarker = -1
    //         for (var i = 0; i< mapview.markers.length; i++){
    //             if (marker == mapview.markers[i]){
    //                 mapview.currentMarker = i
    //                 break
    //             }
    //         }
    //         mapview.showMarkerMenu(marker.coordinate)
    //     }
    // }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        acceptedButtons: Qt.RightButton
        // hoverEnabled: true

        onClicked: event => {
            switch (event.button) {
                case Qt.RightButton: {
                    mapview.currentMarker = -1
                    for (var i = 0; i < mapview.markers.length; i++){
                        if (marker == mapview.markers[i]){
                            mapview.currentMarker = i
                            break
                        }
                    }
                    mapview.showMarkerMenu(marker.coordinate)
                    break;
                }
            }
        }
    }

    DragHandler {
        id: dragHandler
        grabPermissions: PointerHandler.CanTakeOverFromItems | PointerHandler.CanTakeOverFromHandlersOfDifferentType
    }

    sourceItem: Image {
        id: image
        source: "../resources/marker.png"
        opacity: hoverHandler.hovered ? 0.6 : 1.0

        Text {
            id: number
            y: image.height/10
            width: image.width
            color: "white"
            font.bold: true
            font.pixelSize: 14
            horizontalAlignment: Text.AlignHCenter
            Component.onCompleted: {
                text = marker.text === '' ? mapview.markerCounter : marker.text
            }
        }
    }
}
