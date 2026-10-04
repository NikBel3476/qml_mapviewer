// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
import QtQuick
import QtQuick.Controls
import QtLocation
import QtPositioning
import "../helper.js" as Helper
import MissionModel

MapView {
    id: view
    property variant markers
    property variant mapItems
    property int markerCounter: 0 // counter for total amount of markers. Resets to 0 when number of markers = 0
    property int currentMarker
    property bool followme: false
    property variant scaleLengths: [5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000, 1000000, 2000000]
    property alias routeQuery: routeQuery
    property alias routeModel: routeModel
    property alias geocodeModel: geocodeModel
    property alias slidersExpanded: sliders.expanded
    property bool rightButtonPressed: false
    property real lastMousePositionX: 0.0
    property QtObject uav
    property list<QtObject> missionPoints

    signal showGeocodeInfo
    signal geocodeFinished
    signal routeError
    signal coordinatesCaptured(double latitude, double longitude)
    signal showMainMenu(variant coordinate)
    signal showMarkerMenu(variant coordinate)
    signal showRouteMenu(variant coordinate)
    signal showPointMenu(variant coordinate)
    signal showRouteList
    signal missionPointAdded(variant coordinate)

    Connections {
        target: uav

        function onPosChanged(pos) {
            uavMarker.coordinate = pos
        }
    }

    Connections {
        target: missionModel

        function onMissionItemAdded(missionItem) {
            addMissionPoint(missionItem.coordinates())
        }

        function onMissionItemsChanged(missionItems) {
            // console.log(missionItems)
        }
    }

    function setUav(uv) {
        uav = uv
    }

    function geocodeMessage() {
        var street, district, city, county, state, countryCode, country, postalCode, latitude, longitude, text;
        latitude = Math.round(geocodeModel.get(0).coordinate.latitude * 10000) / 10000;
        longitude = Math.round(geocodeModel.get(0).coordinate.longitude * 10000) / 10000;
        street = geocodeModel.get(0).address.street;
        district = geocodeModel.get(0).address.district;
        city = geocodeModel.get(0).address.city;
        county = geocodeModel.get(0).address.county;
        state = geocodeModel.get(0).address.state;
        countryCode = geocodeModel.get(0).address.countryCode;
        country = geocodeModel.get(0).address.country;
        postalCode = geocodeModel.get(0).address.postalCode;

        text = "<b>Latitude:</b> " + latitude + "<br/>";
        text += "<b>Longitude:</b> " + longitude + "<br/>" + "<br/>";
        if (street)
            text += "<b>Street: </b>" + street + " <br/>";
        if (district)
            text += "<b>District: </b>" + district + " <br/>";
        if (city)
            text += "<b>City: </b>" + city + " <br/>";
        if (county)
            text += "<b>County: </b>" + county + " <br/>";
        if (state)
            text += "<b>State: </b>" + state + " <br/>";
        if (countryCode)
            text += "<b>Country code: </b>" + countryCode + " <br/>";
        if (country)
            text += "<b>Country: </b>" + country + " <br/>";
        if (postalCode)
            text += "<b>PostalCode: </b>" + postalCode + " <br/>";
        return text;
    }

    function calculateScale() {
        var coord1, coord2, dist, text, f;
        f = 0;
        coord1 = view.map.toCoordinate(Qt.point(0, scale.y));
        coord2 = view.map.toCoordinate(Qt.point(0 + scaleImage.sourceSize.width, scale.y));
        dist = Math.round(coord1.distanceTo(coord2));

        if (dist === 0) {
            // not visible
        } else {
            for (var i = 0; i < scaleLengths.length - 1; i++) {
                if (dist < (scaleLengths[i] + scaleLengths[i + 1]) / 2) {
                    f = scaleLengths[i] / dist;
                    dist = scaleLengths[i];
                    break;
                }
            }
            if (f === 0) {
                f = dist / scaleLengths[i];
                dist = scaleLengths[i];
            }
        }

        text = Helper.formatDistance(dist);
        scaleImage.width = (scaleImage.sourceSize.width * f) - 2 * scaleImageLeft.sourceSize.width;
        scaleText.text = text;
    }

    function deleteMarkers() {
        var count = view.markers.length;
        for (var i = count - 1; i >= 0; i--) {
            view.map.removeMapItem(view.markers[i]);
        }
        view.markers = [];
    }

    function addMarker() {
        var count = view.markers.length;
        markerCounter++;
        var marker = Qt.createQmlObject('Marker {}', map);
        view.map.addMapItem(marker);
        marker.z = view.map.z + 1;
        marker.coordinate = tapHandler.lastCoordinate;
        markers.push(marker);
    }

    function addMissionPoint(coordinate) {
        const marker = Qt.createQmlObject(`Marker { text: '${view.missionPoints.length}'}`, map);
        view.map.addMapItem(marker);
        marker.coordinate = coordinate;
        view.missionPoints.push(marker);
    }

    function deleteMarker(index) {
        //update list of markers
        var myArray = [];
        var count = view.markers.length;
        for (var i = 0; i < count; i++) {
            if (index !== i)
                myArray.push(view.markers[i]);
        }

        view.map.removeMapItem(view.markers[index]);
        view.markers[index].destroy();
        view.markers = myArray;
        if (markers.length === 0)
            markerCounter = 0;
    }

    function calculateMarkerRoute() {
        routeQuery.clearWaypoints();
        for (var i = currentMarker; i < view.markers.length; i++) {
            routeQuery.addWaypoint(markers[i].coordinate);
        }
        routeQuery.travelModes = RouteQuery.CarTravel;
        routeQuery.routeOptimizations = RouteQuery.ShortestRoute;

        routeModel.update();
    }

    function calculateCoordinateRoute(startCoordinate, endCoordinate) {
        // clear away any old data in the query
        routeQuery.clearWaypoints();
        // add the start and end coords as waypoints on the route
        routeQuery.addWaypoint(startCoordinate);
        routeQuery.addWaypoint(endCoordinate);
        routeQuery.travelModes = RouteQuery.CarTravel;
        routeQuery.routeOptimizations = RouteQuery.FastestRoute;

        routeModel.update();

        // center the map on the start coord
        view.map.center = startCoordinate;
    }

    function geocode(fromAddress) {
        // send the geocode request
        geocodeModel.query = fromAddress;
        geocodeModel.update();
    }

    map.zoomLevel: (maximumZoomLevel - minimumZoomLevel) / 2
    map.center {
        latitude: 0.0
        longitude: 0.0
    }

    focus: true
    map.onCopyrightLinkActivated: Qt.openUrlExternally(link)

    map.onCenterChanged: {
        scaleTimer.restart();
        if (view.followme)
            if (view.map.center != positionSource.position.coordinate)
                view.followme = false;
    }

    map.onZoomLevelChanged: {
        scaleTimer.restart();
        if (view.followme)
            view.map.center = positionSource.position.coordinate;
    }

    onWidthChanged: {
        scaleTimer.restart();
    }

    onHeightChanged: {
        scaleTimer.restart();
    }

    Component.onCompleted: {
        markers = [];
        mapItems = [];
    }

    Keys.onPressed: event => {
        if (event.key === Qt.Key_Plus) {
            view.map.zoomLevel++;
        } else if (event.key === Qt.Key_Minus) {
            view.map.zoomLevel--;
        } else if (event.key === Qt.Key_Left || event.key === Qt.Key_Right || event.key === Qt.Key_Up || event.key === Qt.Key_Down) {
            var dx = 0;
            var dy = 0;

            switch (event.key) {
            case Qt.Key_Left:
                dx = view.map.width / 4;
                break;
            case Qt.Key_Right:
                dx = -view.map.width / 4;
                break;
            case Qt.Key_Up:
                dy = view.map.height / 4;
                break;
            case Qt.Key_Down:
                dy = -view.map.height / 4;
                break;
            }

            var mapCenterPoint = Qt.point(view.map.width / 2.0 - dx, view.map.height / 2.0 - dy);
            view.map.center = view.map.toCoordinate(mapCenterPoint);
        }
    }

    MissionModel {
        id: missionModel
    }

    PositionSource {
        id: positionSource
        active: followme

        onPositionChanged: {
            view.map.center = positionSource.position.coordinate;
        }
    }

    MapQuickItem {
        id: mePoisition
        parent: view.map
        sourceItem: Rectangle {
            width: 14
            height: 14
            color: "#251ee4"
            border.width: 2
            border.color: "white"
            smooth: true
            radius: 7
        }
        coordinate: positionSource.position.coordinate
        opacity: 1.0
        anchorPoint: Qt.point(sourceItem.width / 2, sourceItem.height / 2)
        visible: followme
    }

    MapQuickItem {
        parent: view.map
        sourceItem: Text {
            text: qsTr("You're here!")
            color: "#242424"
            font.bold: true
            styleColor: "#ECECEC"
            style: Text.Outline
        }
        coordinate: positionSource.position.coordinate
        anchorPoint: Qt.point(-mePoisition.sourceItem.width * 0.5, mePoisition.sourceItem.height * 1.5)
        visible: followme
    }

    MapQuickItem {
        id: uavMarker
        parent: view.map
        sourceItem: Rectangle {
            width: 14
            height: 14
            color: "#e41e25"
            border.width: 2
            border.color: "white"
            smooth: true
            radius: 7
        }
        coordinate {
            latitude: 0.0
            longitude: 0.0
        }
        opacity: 1.0
        anchorPoint: Qt.point(sourceItem.width / 2, sourceItem.height / 2)
    }

    MapQuickItem {
        id: uavMarkerLabel
        parent: view.map
        sourceItem: Text {
            text: "uav"
            color: "#242424"
            font.bold: true
            styleColor: "#ECECEC"
            style: Text.Outline
        }
        coordinate: uavMarker.coordinate
        anchorPoint: Qt.point(-uavMarker.sourceItem.width * 0.5, uavMarker.sourceItem.height * 1.5)
    }

    MapSliders {
        id: sliders
        z: view.map.z + 3
        mapSource: map
        edge: Qt.LeftEdge
    }

    Item {
        id: scale
        z: view.map.z + 3
        visible: scaleText.text !== "0 m"
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        anchors.margins: 20
        height: scaleText.height * 2
        width: scaleImage.width

        Image {
            id: scaleImageLeft
            source: "../resources/scale_end.png"
            anchors.bottom: parent.bottom
            anchors.right: scaleImage.left
        }
        Image {
            id: scaleImage
            source: "../resources/scale.png"
            anchors.bottom: parent.bottom
            anchors.right: scaleImageRight.left
        }
        Image {
            id: scaleImageRight
            source: "../resources/scale_end.png"
            anchors.bottom: parent.bottom
            anchors.right: parent.right
        }
        Label {
            id: scaleText
            color: "#004EAE"
            anchors.centerIn: parent
            text: "0 m"
        }
        Component.onCompleted: {
            view.calculateScale();
        }
    }

    RouteModel {
        id: routeModel
        plugin: view.map.plugin
        query: RouteQuery {
            id: routeQuery
        }
        onStatusChanged: {
            if (status == RouteModel.Ready) {
                switch (count) {
                case 0:
                    // technically not an error
                    view.routeError();
                    break;
                case 1:
                    view.showRouteList();
                    break;
                }
            } else if (status == RouteModel.Error) {
                view.routeError();
            }
        }
    }

    Component {
        id: routeDelegate

        MapRoute {
            id: route
            route: routeData
            line.color: "#46a2da"
            line.width: 5
            smooth: true
            opacity: 0.8
            TapHandler {
                acceptedButtons: Qt.LeftButton | Qt.RightButton
                onLongPressed: showRouteMenu(view.map.toCoordinate(tapHandler.point.position))
                onSingleTapped: (eventPoint, button) => {
                    if (button === Qt.RightButton)
                        showRouteMenu(view.map.toCoordinate(tapHandler.point.position));
                }
            }
        }
    }

    GeocodeModel {
        id: geocodeModel
        plugin: view.map.plugin
        onStatusChanged: {
            if ((status == GeocodeModel.Ready) || (status == GeocodeModel.Error))
                view.geocodeFinished();
        }
        onLocationsChanged: {
            if (count === 1) {
                view.map.center.latitude = get(0).coordinate.latitude;
                view.map.center.longitude = get(0).coordinate.longitude;
            }
        }
    }

    Component {
        id: pointDelegate

        MapQuickItem {
            id: point
            parent: view.map
            coordinate: locationData.coordinate

            sourceItem: Image {
                id: pointMarker
                source: "../resources/marker_blue.png"

                Text {
                    id: pointText
                    anchors.bottom: pointMarker.top
                    anchors.horizontalCenter: pointMarker.horizontalCenter
                    text: locationData.address.street + ", " + locationData.address.city
                    color: "#242424"
                    font.bold: true
                    styleColor: "#ECECEC"
                    style: Text.Outline
                }
            }
            smooth: true
            autoFadeIn: false
            anchorPoint.x: pointMarker.width / 4
            anchorPoint.y: pointMarker.height

            TapHandler {
                onLongPressed: showPointMenu(point.coordinate)
            }
        }
    }

    MapItemView {
        parent: view.map
        model: routeModel
        delegate: routeDelegate
        autoFitViewport: true
    }

    MapItemView {
        parent: view.map
        model: geocodeModel
        delegate: pointDelegate
    }

    Timer {
        id: scaleTimer
        interval: 100
        running: false
        repeat: false
        onTriggered: view.calculateScale()
    }

    TapHandler {
        id: tapHandler
        property variant lastCoordinate
        acceptedButtons: Qt.LeftButton | Qt.RightButton

        onPressedChanged: (eventPoint, button) => {
            if (pressed) {
                lastCoordinate = view.map.toCoordinate(tapHandler.point.position);
            }
        }

        onSingleTapped: (eventPoint, button) => {
            if (button === Qt.RightButton) {
                showMainMenu(lastCoordinate);
            }
        }

        onDoubleTapped: (eventPoint, button) => {
            var preZoomPoint = view.map.toCoordinate(eventPoint.position);
            if (button === Qt.LeftButton) {
                view.map.zoomLevel = Math.floor(view.map.zoomLevel + 1);
            } else if (button === Qt.RightButton) {
                view.map.zoomLevel = Math.floor(view.map.zoomLevel - 1);
            }
            var postZoomPoint = view.map.toCoordinate(eventPoint.position);
            var dx = postZoomPoint.latitude - preZoomPoint.latitude;
            var dy = postZoomPoint.longitude - preZoomPoint.longitude;

            view.map.center = QtPositioning.coordinate(view.map.center.latitude - dx, view.map.center.longitude - dy);
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        // hoverEnabled: true

        onPressed: event => {
            switch (event.button) {
                case Qt.RightButton: {
                    rightButtonPressed = true
                    lastMousePositionX = event.x
                    break;
                }
            }
        }

        onReleased: event => {
            switch (event.button) {
                case Qt.RightButton: {
                    rightButtonPressed = false
                    break;
                }
            }
        }

        onClicked: event => {
            const coordinate = view.map.toCoordinate(Qt.point(event.x, event.y))
            switch (event.button) {
                case Qt.LeftButton: {
                    if (event.modifiers === Qt.ControlModifier) {
                        // addMissionPoint(coordinate)
                        // missionPointAdded(coordinate)
                        missionModel.addNextPoint(coordinate)
                    }
                    break;
                }
                case Qt.RightButton: {
                    showMainMenu(coordinate);
                    break;
                }
            }
        }

        onPositionChanged: event => {
            if (rightButtonPressed) {
                const delta = (event.x - lastMousePositionX) / 2.0;
                lastMousePositionX = event.x;
                view.map.bearing = (view.map.bearing + delta + 360.0) % 360;
            }
        }
    }
}
