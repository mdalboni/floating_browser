import QtQuick 2.0
import QtQuick.Controls 2.3

Item {
    width: 640
    clip: false
    antialiasing: true

    Dial {
        id: dial
        x: 98
        y: 0
    }

    Button {
        id: button
        x: 0
        y: 0
        text: qsTr("Button")
    }

}
