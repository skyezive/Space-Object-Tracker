import updateOrbits;
from astropy.time import Time
import sys
from PySide6 import QtGui
from PySide6.QtCore import (Property, QObject, QPropertyAnimation, Signal)
from PySide6.QtGui import (QGuiApplication, QMatrix4x4, QQuaternion, QVector3D, QImage)
from PySide6.Qt3DCore import (Qt3DCore)
from PySide6.Qt3DExtras import (Qt3DExtras)
from astropy.time import Time
from sgp4.model import Satrec
import parallelization


class Window(Qt3DExtras.Qt3DWindow):
    global positionDictionary
    positions = parallelization.serial_get_position()
    names = parallelization.get_names()

    positionDictionary = {}

    for i in range(len(names)):
        name = names[i][0]
        position = positions[i]
        positionDictionary[name] = position
    #print(positionDictionary)

    positionDictionary = {
        "Satellite1": [-110, 20, 30],
        "Satellite2": [40, 50, 60],
        "Satellite3": [70, 80, 90],
        "Satellite4": [100, 110, 120],
        "Satellite5": [130, 140, 150]
    }

    def __init__(self):
        super().__init__()

        # Camera
        self.camera().lens().setPerspectiveProjection(60, 16 / 9, 0.1, 1000)
        self.camera().setViewCenter(QVector3D(0, 0, 0))
        self.camera().setPosition(QVector3D(-1, -1, -1))
        #self.camera().setPosition(QVector3D(*positionDictionary['THOR AGENA D R/B']))

        # For camera controls
        self.createScene()
        self.camController = Qt3DExtras.QOrbitCameraController(self.rootEntity)
        self.camController.setLinearSpeed(50)
        self.camController.setLookSpeed(180)
        self.camController.setCamera(self.camera())

        self.setRootEntity(self.rootEntity)


    def createScene(self):
        # Root entity
        self.rootEntity = Qt3DCore.QEntity()

        def addSphere(name, position, index):
            #print(position)
            # Material
            self.material = Qt3DExtras.QPhongMaterial(self.rootEntity)
            if name.startswith('SURCAL 150B'):
                self.material.setDiffuse(QtGui.QColor(0, 255, 0, 255))  # green
            elif name.startswith('LCS'):
                self.material.setDiffuse(QtGui.QColor(0, 0, 255, 255))  # blue
            else:
                self.material.setDiffuse(QtGui.QColor(255, 0, 0, 255))  # red

            # Sphere
            self.sphereEntity = Qt3DCore.QEntity(self.rootEntity)
            self.sphereMesh = Qt3DExtras.QSphereMesh()
            self.sphereMesh.setRadius(3)

            self.sphereTransform = Qt3DCore.QTransform()
            #print(position)
            #print(position[0])
            self.sphereTransform.setTranslation(QVector3D(position[0], position[1], position[2]))
            #print(position)

            self.sphereEntity.addComponent(self.sphereMesh)
            self.sphereEntity.addComponent(self.sphereTransform)
            self.sphereEntity.addComponent(self.material)

            # Append index to variable names
            self.sphereEntity.setObjectName(f"sphereEntity_{index}")
            self.sphereMesh.setObjectName(f"sphereMesh_{index}")
            self.sphereTransform.setObjectName(f"sphereTransform_{index}")
            self.material.setObjectName(f"material_{index}")

        index = 0
        #print(positionDictionary)
        for name, pos in positionDictionary.items():
            #print(name)
            print(pos[0])
            addSphere(name, pos, index)  # name, position, index
            index += 1


if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    view = Window()
    view.show()
    sys.exit(app.exec())
