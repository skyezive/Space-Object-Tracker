from sgp4 import exporter
import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsRectItem, \
    QGraphicsSimpleTextItem, QLineEdit, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QGraphicsEllipseItem, \
    QInputDialog, QListWidget, QToolTip, QWidget
from PySide6.QtGui import QColor, QPen, QBrush, QPainter, QPixmap, QFont, QPalette
from datetime import datetime, timedelta
import TimeHandlingFunctions
import CelestrakAPI
import math
from PySide6 import QtGui, QtCore
from PySide6.QtCore import (Property, QObject, QPropertyAnimation, Signal)
from PySide6.QtGui import (QGuiApplication, QMatrix4x4, QQuaternion, QVector3D, QImage)
from PySide6.Qt3DCore import (Qt3DCore)
from PySide6.Qt3DExtras import (Qt3DExtras)
from astropy.time import Time
from sgp4.model import Satrec
import sys
import re
import functools
from PySide6.QtCore import QSize, Qt, QTimer
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

class SphereItem(QGraphicsEllipseItem):
    def __init__(self, x, y,z, radius, sphereIndex):
        super().__init__(x - radius, y - radius, radius * 2, radius * 2)
        self.si = sphereIndex

    def openNewWindow(self):
        # Create a new window to display additional information
        self.att_window = DisplayWindow(sIndex=self.si)
        self.att_window.show()
    def mousePressEvent(self, event):
        # Handle mouse press event
        if event.button() == Qt.LeftButton:
            self.openNewWindow()

class DisplayWindow(QMainWindow):
    def __init__(self, sIndex):
        super().__init__()
        self.setFixedSize(300, 200)
        self.setWindowTitle("Space Object Attributes")
        self.sIndex = sIndex

        window_color = QColor(0, 0, 15)
        window_palette = self.palette()
        window_palette.setColor(QPalette.Window, window_color)
        self.setPalette(window_palette)

        # Retrieve the necessary information for the object at the specified sIndex
        if sIndex >= 0 and sIndex < len(name_array):
            name = name_array[sIndex][0]
            position = position_array[sIndex]
            position[0] = position[0]-700
            position = [position[i]*300 for i in range(3)]
            velocity = velocity_array[sIndex]
            tle = tle_array[sIndex]
            label_color = QColor(255,255,255)

            # Display Object Name
            self.name_val = QLabel(self)
            self.name_val.setGeometry(10, 0, 220, 20)
            self.name_val.setText('Object Name: ' + str(name))
            self.name_val.setStyleSheet(f"color: {label_color.name()};")

            # Display Position
            self.pos_val = QLabel(self)
            self.pos_val.setGeometry(10, 19, 400, 20)
            self.pos_val.setText('Position: ' + str(round(position[0]/10,2)) + ', ' + str(round(-position[1]/10,2)) + ', ' + str(round(position[2]/10,2)))
            self.pos_val.setStyleSheet(f"color: {label_color.name()};")

            # Display Velocity
            self.vel_val = QLabel(self)
            self.vel_val.setGeometry(10, 38, 400, 20)
            self.vel_val.setText('Velocity: '+ str(round(velocity[0],2)) + ', ' + str(round(velocity[1],2)) + ', ' + str(round(velocity[2],2)))
            self.vel_val.setStyleSheet(f"color: {label_color.name()};")

            # Display Eccentricity
            self.eccentricity = QLabel(self)
            self.eccentricity.setGeometry(10, 57, 200, 20)
            self.eccentricity.setText('Eccentricity: ' + str(tle[1][26:33].strip()))
            self.eccentricity.setStyleSheet(f"color: {label_color.name()};")

            # Display Inclination
            self.inclination = QLabel(self)
            self.inclination.setGeometry(10, 76, 200, 20)
            self.inclination.setText('Inclination: ' + str(tle[1][8:16].strip()))
            self.inclination.setStyleSheet(f"color: {label_color.name()};")

            # Display RAAN
            self.raan = QLabel(self)
            self.raan.setGeometry(10, 95, 200, 20)
            self.raan.setText('RAAN: ' + str(tle[1][17:25].strip()))
            self.raan.setStyleSheet(f"color: {label_color.name()};")

            # Display Argument of Perigee
            self.arg_perigee = QLabel(self)
            self.arg_perigee.setGeometry(10, 114, 210, 20)
            self.arg_perigee.setText('Argument of Perigee: ' + str(tle[1][34:42].strip()))
            self.arg_perigee.setStyleSheet(f"color: {label_color.name()};")

            # Display Mean Anomaly
            self.mean_anomaly = QLabel(self)
            self.mean_anomaly.setGeometry(10, 133, 200, 20)
            self.mean_anomaly.setText('Mean Anomaly: ' + str(tle[1][43:51].strip()))
            self.mean_anomaly.setStyleSheet(f"color: {label_color.name()};")

            # Export TLE Button
            self.export_button = QPushButton(QIcon('blue-document--arrow.png'),"Export TLE", self)
            self.export_button.setGeometry(40, 160, 100, 30)
            self.export_button.clicked.connect(self.export_TLE(name))

            # Print TLE Button
            self.print_button = QPushButton(QIcon('monitor--pencil.png'), "Print TLE", self)
            self.print_button.setGeometry(160, 160, 100, 30)
            self.print_button.clicked.connect(self.print_TLE(name))

    def export_TLE(self, name):
        fn = re.sub(r'[\\/:"*?<>|]', '', name) + '_TLE'
        with open(fn, 'w') as file:
            file.write(name + '\n')
            file.write(str(tle_dict[name][0]) + '\n')
            file.write(str(tle_dict[name][1]) + '\n')

    def print_TLE(self, name):
        print(name)
        print(str(tle_dict[name][0]))
        print(str(tle_dict[name][1]))



class MainWindow(QMainWindow):
    global tle_array
    global name_array
    global position_array
    global velocity_array
    global tle_dict
    global position_dict
    global e, r, v
    global spheres
    global orbit_speedup

    filename = '100.txt'

    # Read the TLE data from the specified file
    with open(filename, "r") as file:
        num_lines = sum(1 for line in file)
        num_tles = round(num_lines / 3)

    # populate the arrays and dictionaries with the necessary information for each satellite object
    tle_array = np.empty([num_tles, 2], dtype='U70')
    name_array = np.empty([num_tles, 1], dtype='U30')
    position_array = np.empty([num_tles, 3])
    velocity_array = np.empty([num_tles, 3])
    spheres = []
    speedup_counter = 0
    current_time = datetime.now()
    position_dict = {}
    tle_dict = {}
    TLEcounter = 0
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line[0] != '1' and line[0] != '2':
                name_array[TLEcounter] = line
            elif line[0] == '1':
                tle_array[TLEcounter][0] = line
            elif line[0] == '2':
                tle_array[TLEcounter][1] = line
                TLEcounter += 1

    for i in range(num_tles):
        if tle_array[i][0] != "":
            satelliteObj = Satrec.twoline2rv(tle_array[i][0], tle_array[i][1])  # convert tle to satrec object
            e, r, v = satelliteObj.sgp4(Time.now().jd1, Time.now().jd2)
            r = [r[i] / 300 for i in range(3)]
            position_array[i] = r
            velocity_array[i] = v

    for i in range(len(name_array)):
        tle = tle_array[i]
        tle_dict[name_array[i][0]] = tle
        position_dict[name_array[i][0]] = position_array[i]

    def __init__(self):
        global max_z, min_z, index, color, colors, num_colors
        super().__init__()
        self.orbit_speedup = 1 / 20  # 1/60
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)
        self.setWindowTitle("Satellite Tracker")

        # Button Actions for the File menu
        propint = QAction(QIcon("clock-select-remain.png"), "Select Propagation Interval", self)
        propint.triggered.connect(self.propInterval)
        exportAll = QAction(QIcon("allTLEs.png"), "Export All TLEs", self)
        exportAll.triggered.connect(self.exportAllTLEs)
        printAll = QAction(QIcon("application-list.png"), "Print All TLEs", self)
        exportAll.triggered.connect(self.printAllTLEs)

        # Button Action for the Satellites menu
        showSatOptions = QAction( "View Orbital Data", self)
        showSatOptions.triggered.connect(self.satListDisplay)

        #Button Action for the 3D Viewer menu
        openView = QAction("Open 3D View", self)
        openView.triggered.connect(self.open3DWindow)
        self.new_window = None

        # Create a menu bar and add menus to it
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(propint)
        file_menu.addSeparator()
        file_menu.addAction(exportAll)
        file_menu.addSeparator()
        file_menu.addAction(printAll)
        satellites_menu = menu.addMenu("Satellites")
        satellites_menu.addAction(showSatOptions)
        threeD_menu = menu.addMenu("3D Viewer")
        threeD_menu.addAction(openView)

        self.setStatusBar(QStatusBar(self))
        self.resize(1400, 700)

        # Defining colours for the z axis legend
        num_colors = 200
        start_color = QColor(0, 255, 0)  # Green
        mid1_color = QColor(0, 255, 255)  # Turquoise
        mid2_color = QColor(0, 0, 255)  # Blue
        mid3_color = QColor(255, 0, 0)  # Red
        mid4_color = QColor(255, 165, 0)  # Orange
        end_color = QColor(255, 255, 0)  # Yellow

        colors = []
        for i in range(num_colors):
            # Calculate the interpolation factor between colors
            gradient_position = i / (num_colors - 1)

            if gradient_position <= 0.2:
                # Interpolate between start_color and mid1_color
                r = int((1 - gradient_position * 5) * start_color.red() + gradient_position * 5 * mid1_color.red())
                g = int((1 - gradient_position * 5) * start_color.green() + gradient_position * 5 * mid1_color.green())
                b = int((1 - gradient_position * 5) * start_color.blue() + gradient_position * 5 * mid1_color.blue())
            elif gradient_position <= 0.4:
                # Interpolate between mid1_color and mid2_color
                r = int((1 - (gradient_position - 0.2) * 5) * mid1_color.red() + (
                        gradient_position - 0.2) * 5 * mid2_color.red())
                g = int((1 - (gradient_position - 0.2) * 5) * mid1_color.green() + (
                        gradient_position - 0.2) * 5 * mid2_color.green())
                b = int((1 - (gradient_position - 0.2) * 5) * mid1_color.blue() + (
                        gradient_position - 0.2) * 5 * mid2_color.blue())
            elif gradient_position <= 0.6:
                # Interpolate between mid2_color and mid3_color
                r = int((1 - (gradient_position - 0.4) * 5) * mid2_color.red() + (
                        gradient_position - 0.4) * 5 * mid3_color.red())
                g = int((1 - (gradient_position - 0.4) * 5) * mid2_color.green() + (
                        gradient_position - 0.4) * 5 * mid3_color.green())
                b = int((1 - (gradient_position - 0.4) * 5) * mid2_color.blue() + (
                        gradient_position - 0.4) * 5 * mid3_color.blue())
            elif gradient_position <= 0.8:
                # Interpolate between mid3_color and mid4_color
                r = int((1 - (gradient_position - 0.6) * 5) * mid3_color.red() + (
                        gradient_position - 0.6) * 5 * mid4_color.red())
                g = int((1 - (gradient_position - 0.6) * 5) * mid3_color.green() + (
                        gradient_position - 0.6) * 5 * mid4_color.green())
                b = int((1 - (gradient_position - 0.6) * 5) * mid3_color.blue() + (
                        gradient_position - 0.6) * 5 * mid4_color.blue())
            else:
                # Interpolate between mid4_color and end_color
                r = int((1 - (gradient_position - 0.8) * 5) * mid4_color.red() + (
                        gradient_position - 0.8) * 5 * end_color.red())
                g = int((1 - (gradient_position - 0.8) * 5) * mid4_color.green() + (
                        gradient_position - 0.8) * 5 * end_color.green())
                b = int((1 - (gradient_position - 0.8) * 5) * mid4_color.blue() + (
                        gradient_position - 0.8) * 5 * end_color.blue())

            colors.append(QColor(r, g, b))

        # Create multiple spheres at specified positions with different colors
        radius = 3.5
        # Load the Earth image as a QPixmap
        earth_image_path = "earth2.png"
        earth_pixmap = QPixmap(earth_image_path)

        # Create a QGraphicsPixmapItem and set the Earth image as its pixmap
        earth_item = self.scene.addPixmap(earth_pixmap)

        # Set the position and size of the Earth item
        earth_radius = 100
        earth_item.setPos(-earth_radius + 700, -earth_radius)  # +700 to shift to the right
        earth_item.setScale(2 * earth_radius / earth_pixmap.width())

        # Assign a colour to each sphere
        min_z = -476
        max_z = 343
        for i in range(self.num_tles):
            x, y, z = position_array[i][0], position_array[i][1], position_array[i][2]
            index = int((z - min_z) / (max_z - min_z) * (num_colors - 1))
            index %= num_colors
            sphere = SphereItem(x, y, z, radius, i)
            self.scene.addItem(sphere)
            sphere.setPen(QPen(QColor("black")))
            sphere.setToolTip(str(name_array[i][0]))
            sphere.setBrush(QBrush(colors[index]))
            spheres.append(sphere)

        # Set the scene dimensions
        legend_width = 20
        min_height = -250
        max_height = 250
        height_increment = (max_height - min_height) / len(colors)

        # Create a rectangle and label for each color band in the legend
        labels = ['1500km', '1000km', '500km', '0', '-500km', '-1000km', '-1500km', '-2000km']
        for i, color in enumerate(colors):
            # Calculate the height range for the current color band
            start_height = min_height + i * height_increment
            end_height = start_height + height_increment

            # Create a QGraphicsRectItem for the current color band
            rect = QGraphicsRectItem(1300, start_height, legend_width, end_height - start_height)
            rect.setBrush(QBrush(color))
            rect.setPen(Qt.NoPen)

            # Add the rectangle to the scene
            self.scene.addItem(rect)

        for i in range(8):
            # Create a QGraphicsSimpleTextItem for the height label
            start_height = min_height + i * height_increment
            height_increment = (max_height - min_height) / 8
            label = QGraphicsSimpleTextItem()
            label.setFont(QFont("Arial", 10))
            label.setBrush(QtGui.QBrush(QtGui.QColor("white")))
            label.setText(labels[i])
            label.setPos(legend_width + 1310, start_height + 50)

            # Add the label to the scene
            self.scene.addItem(label)
        label1 = QGraphicsSimpleTextItem()
        label1.setFont(QFont("Arial", 10))
        label1.setText("2000km")
        label1.setBrush(QtGui.QBrush(QtGui.QColor("white")))
        label1.setPos(legend_width + 1310, start_height - 450)

        # Add the label to the scene
        self.scene.addItem(label1)

        # Create a layout for the central widget
        layout = QVBoxLayout()
        self.view.setLayout(layout)

    def satListDisplay(self):
        sats = [name_array[i][0] for i in range(len(name_array))]
        selected_satellite, ok = QInputDialog.getItem(self, "Select Satellite", "Choose a satellite to view its orbital data:",
                                                  sats)

        if ok:
            self.DisplayInfo(sats.index(selected_satellite))

    def DisplayInfo(self, index):
        self.att_window = DisplayWindow(sIndex=index)
        self.att_window.show()

    def get_speed_value(self, selected_speed):
        if selected_speed == "Real-Time":
            return 1/30
        elif selected_speed == "1 Minute":
            return 1
        elif selected_speed == "10 Minutes":
            return 10
        elif selected_speed == "1 Hour":
            return 60
        elif selected_speed == "2 Hours":
            return 120
        else:
            return 1  # Default speed value

    def propInterval(self):
        speed_options = ["Real-Time", "1 Minute", "10 Minutes", "1 Hour", "2 Hours"]
        selected_speed, ok = QInputDialog.getItem(self, "Select Interval", "Choose a propagation interval:", speed_options)

        if ok:
            speed = self.get_speed_value(selected_speed)
            self.orbit_speedup = speed

    def open3DWindow(self):
        self.new_window = Window3D()
        self.new_window.show()

    def schedule_scene_update(self):
        self.translate_spheres()
        self.translation_timer = QTimer()
        self.translation_timer.timeout.connect(self.translate_spheres)
        self.translation_timer.start(2 * 1000)  # repetition period in seconds

        self.tle_timer = QTimer()
        self.tle_timer.timeout.connect(self.update_tle_array)
        self.tle_timer.start(8 * 60 * 60 * 1000)  # repetition period in hours - updates 3 times a day

    def update_tle_array(self):
        for i in range(self.num_tles):
            tle_array[i] = exporter.export_tle(list(CelestrakAPI.load_gp_from_celestrak(name=name_array[i][0]))[0])

    def translate_spheres(self):
        # update position array
        for i in range(self.num_tles):
            if tle_array[i][0] != "":
                satelliteObj = Satrec.twoline2rv(tle_array[i][0], tle_array[i][1])  # convert tle to satrec object
                # Calculate the target time as 10 minutes later than the previous time
                target_time = self.current_time + timedelta(minutes=self.orbit_speedup)

                # Convert the target time to the Julian day format
                julianDate = TimeHandlingFunctions.fnJulianDate(
                    target_time.year,
                    target_time.month,
                    target_time.day,
                    target_time.hour,
                    target_time.minute,
                    target_time.second,
                )

                jd = math.floor(julianDate)
                fr = julianDate - jd

                # Call the sgp4 function with the target time in Julian day format
                e, r, v = satelliteObj.sgp4(jd, fr)

                self.current_time = target_time
                r = [r[i] / 300 for i in range(3)]  # to scale the position to fit onto the screen
                r[0] = r[0] + 700  # to shift to the center of the screen
                position_array[i] = r
                velocity_array[i] = v
        MainWindow.speedup_counter += 1

        # Translate the sphere's position
        for i in range(len(spheres)):
            spheres[i].setPos(position_array[i][0], position_array[i][1])

            # change colour
            z = position_array[i][2]
            index = int((z - min_z) / (max_z - min_z) * (num_colors - 1))
            index %= num_colors
            spheres[i].setBrush(QBrush(colors[index]))


    def selectSatelliteFile(self):
        self.filename = '100.txt'

    def exportAllTLEs(self):
        fn = 'TLE_File'
        with open(fn, 'w') as file:
            for i in range(len(name_array)):
                file.write(name_array[i][0] + '\n')
                file.write(tle_array[i][0]+ '\n')
                file.write(tle_array[i][1]+ '\n')

    def printAllTLEs(self):
        for i in range(len(name_array)):
            print(name_array[i][0])
            print(tle_array[i][0])
            print(tle_array[i][1])

    def onNameMenuActionTriggered(self, name):
        print('Position: ' + str(position_dict[name]))

    def onPrintTLE(self, name):
        fn = re.sub(r'[\\/:"*?<>|]', '', name) + '_TLE'
        with open(fn, 'w') as file:
            file.write(name + '\n')
            file.write(str(tle_dict[name][0]) + '\n')
            file.write(str(tle_dict[name][1]) + '\n')


class Window3D(Qt3DExtras.Qt3DWindow):
    global position1
    global position2
    global position3
    global midpoint

    sat1 = Satrec.twoline2rv('1 00694U 63047A   23086.63310702  .00006056  00000-0  77329-3 0  9998',
                             '2 00694  30.3574  67.0321 0576541 352.0257   7.1496 14.04852726979511')
    e1, position1, velocity1 = sat1.sgp4(Time.now().jd1, Time.now().jd2)

    sat2 = Satrec.twoline2rv('1 00727U 64001A   23086.87476495  .00000074  00000-0  93905-4 0  9997',
                             '2 00727  69.9052 297.1518 0011340 127.4544 232.7594 13.95483532 12882')
    e2, position2, velocity2 = sat2.sgp4(Time.now().jd1, Time.now().jd2)

    sat3 = Satrec.twoline2rv('1 00877U 64053B   23086.81598043  .00000569  00000-0  13986-3 0  9997',
                             '2 00877  65.0766 247.1473 0067602 347.4504  12.4908 14.59775579109373')
    e3, position3, velocity3 = sat3.sgp4(Time.now().jd1, Time.now().jd2)

    midpoint = [(position1[i] + position3[i]) / 2 for i in range(3)]
    # print(midpoint)

    position1 = [position1[i] / 1000 for i in range(3)]
    position2 = [position2[i] / 1000 for i in range(3)]
    position3 = [position3[i] / 1000 for i in range(3)]

    def __init__(self):
        super().__init__()
        self.resize(300, 200)


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
        # texture = PySide6.Qt3DRender.QTextureImage()
        # texture.setImage(PySide6.QtGui.QImage("earth.png"))
        # texture.setSource(PySide6.QtCore.QUrl.fromLocalFile("earth.png"))

        # self.earthmaterial = Qt3DExtras.QDiffuseMapMaterial(self.rootEntity)
        # self.earthmaterial.setTexture(texture)

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
            # self.sphereTransform3.setTranslation(QVector3D(0, 0, 0))
            self.sphereTransform3.setTranslation(QVector3D(position3[0], position3[1], position3[2]))

            self.sphereEntity3.addComponent(self.sphereMesh3)
            self.sphereEntity3.addComponent(self.sphereTransform3)
            self.sphereEntity3.addComponent(self.material3)
            # self.sphereEntity3.addComponent(self.earthmaterial)

        addSphere1()
        addSphere2()
        addSphere3()


app = QApplication(sys.argv)
window = MainWindow()
window.schedule_scene_update()
window.setStyleSheet("background-color: rgb(0,0,15); color: white;") #rgb(179, 222, 245)
window.show()
sys.exit(app.exec())
