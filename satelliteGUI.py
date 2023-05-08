# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""PySide6 port of the qt3d/simple-cpp example from Qt v5.x"""

import PySide6
from PySide6 import QtGui
from PySide6.QtCore import (Property, QObject, QPropertyAnimation, Signal)
from PySide6.QtGui import (QGuiApplication, QMatrix4x4, QQuaternion, QVector3D, QImage)
from PySide6.Qt3DCore import (Qt3DCore)
from PySide6.Qt3DExtras import (Qt3DExtras)
from astropy.time import Time
from sgp4.model import Satrec
import sys
import parallelization
import functools
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QLabel,
    QMainWindow,
    QStatusBar,
    QToolBar,
    QMenu,
    QMenuBar
)
#from PySide6.Qt3DExtras import QTextureMaterial
from PySide6.QtGui import QImage
import math

positions = parallelization.serial_get_position()
names = parallelization.get_names()

satellite_dict = {}

for i in range(len(names)):
    name = names[i][0]
    position = positions[i]
    satellite_dict[name] = position

class Window(Qt3DExtras.Qt3DWindow):
    global position1
    global position2
    global position3
    global midpoint

    sat1 = Satrec.twoline2rv('1 00694U 63047A   23086.63310702  .00006056  00000-0  77329-3 0  9998',
                             '2 00694  30.3574  67.0321 0576541 352.0257   7.1496 14.04852726979511')
    e1, position1, velocity1 = sat1.sgp4(Time.now().jd1, Time.now().jd2)
    print(position1)

    sat2 = Satrec.twoline2rv('1 00727U 64001A   23086.87476495  .00000074  00000-0  93905-4 0  9997',
                             '2 00727  69.9052 297.1518 0011340 127.4544 232.7594 13.95483532 12882')
    e2, position2, velocity2 = sat2.sgp4(Time.now().jd1, Time.now().jd2)
    print(position2)

    sat3 = Satrec.twoline2rv('1 00877U 64053B   23086.81598043  .00000569  00000-0  13986-3 0  9997',
                             '2 00877  65.0766 247.1473 0067602 347.4504  12.4908 14.59775579109373')
    e3, position3, velocity3 = sat3.sgp4(Time.now().jd1, Time.now().jd2)
    print(position3)

    midpoint = [(position1[i] + position3[i]) / 2 for i in range(3)]
    # print(midpoint)

    position1 = [position1[i] / 1000 for i in range(3)]
    position2 = [position2[i] / 1000 for i in range(3)]
    position3 = [position3[i] / 1000 for i in range(3)]

    def __init__(self):
        super().__init__()

        # Camera
        self.camera().lens().setPerspectiveProjection(60, 16 / 9, 0.1, 1000)
        camera_pos = QVector3D(*midpoint)
        camera_pos.setZ(camera_pos.z() + 30000)
        camera_target = QVector3D(*midpoint)
        self.camera().setPosition(camera_pos)
        self.camera().setViewCenter(camera_target)
        self.camera().setViewCenter(QVector3D(0, 0, 0))
        self.camera().setPosition(QVector3D(*position3))

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

        # Material
        self.material1 = Qt3DExtras.QPhongMaterial(self.rootEntity)
        self.material1.setDiffuse(QtGui.QColor(0, 255, 0, 255))  # green

        self.material2 = Qt3DExtras.QPhongMaterial(self.rootEntity)
        self.material2.setDiffuse(QtGui.QColor(0, 0, 255, 255))  # blue

        self.material3 = Qt3DExtras.QPhongMaterial(self.rootEntity)
        self.material3.setDiffuse(QtGui.QColor(255, 0, 0, 255))  # red

        # Create a texture object
        #texture = PySide6.Qt3DRender.QTextureImage()
        #texture.setImage(PySide6.QtGui.QImage("earth.png"))
        #texture.setSource(PySide6.QtCore.QUrl.fromLocalFile("earth.png"))



        #self.earthmaterial = Qt3DExtras.QDiffuseMapMaterial(self.rootEntity)
        #self.earthmaterial.setTexture(texture)


        def addSphere1():
            # Sphere
            self.sphereEntity1 = Qt3DCore.QEntity(self.rootEntity)
            self.sphereMesh1 = Qt3DExtras.QSphereMesh()
            self.sphereMesh1.setRadius(0.3)

            self.sphereTransform1 = Qt3DCore.QTransform()
            self.sphereTransform1.setTranslation(QVector3D(position1[0], position1[1], position1[2]))
            # self.sphereTransform.setTranslation(QVector3D(1,1,1))

            self.sphereEntity1.addComponent(self.sphereMesh1)
            self.sphereEntity1.addComponent(self.sphereTransform1)
            self.sphereEntity1.addComponent(self.material1)

        def addSphere2():
            # Sphere
            self.sphereEntity2 = Qt3DCore.QEntity(self.rootEntity)
            self.sphereMesh2 = Qt3DExtras.QSphereMesh()
            self.sphereMesh2.setRadius(0.3)

            self.sphereTransform2 = Qt3DCore.QTransform()
            self.sphereTransform2.setTranslation(QVector3D(0, 0, 0))
            self.sphereTransform2.setTranslation(QVector3D(position2[0], position2[1], position2[2]))

            self.sphereEntity2.addComponent(self.sphereMesh2)
            self.sphereEntity2.addComponent(self.sphereTransform2)
            self.sphereEntity2.addComponent(self.material2)

        def addSphere3():
            # Sphere
            self.sphereEntity3 = Qt3DCore.QEntity(self.rootEntity)
            self.sphereMesh3 = Qt3DExtras.QSphereMesh()
            self.sphereMesh3.setRadius(1)

            self.sphereTransform3 = Qt3DCore.QTransform()
            #self.sphereTransform3.setTranslation(QVector3D(0, 0, 0))
            self.sphereTransform3.setTranslation(QVector3D(position3[0], position3[1], position3[2]))


            self.sphereEntity3.addComponent(self.sphereMesh3)
            self.sphereEntity3.addComponent(self.sphereTransform3)
            self.sphereEntity3.addComponent(self.material3)
            #self.sphereEntity3.addComponent(self.earthmaterial)

        addSphere1()
        addSphere2()
        addSphere3()


if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    view = Window()
    view.show()
    sys.exit(app.exec())
