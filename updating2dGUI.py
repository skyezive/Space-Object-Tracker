from sgp4 import exporter
import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsRectItem, \
    QGraphicsSimpleTextItem, QLineEdit, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy
from PySide6.QtGui import QColor, QPen, QBrush, QPainter, QPixmap, QFont
from datetime import datetime, timedelta
import TimeHandlingFunctions
import importTLE
import math
from PySide6 import QtGui
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
filename = '1.txt'

with open(filename, "r") as file:
    num_lines = sum(1 for line in file)
    num_tles = round(num_lines/3)

global tle_array
global name_array
global position_array
global tle_dict
global position_dict


tle_array = np.empty([num_tles, 2], dtype='U70') #numtles in .txt, 2 elements per tle
name_array = np.empty([num_tles, 1], dtype='U30')
position_array = np.empty([num_tles, 3])

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


position_dict = {}
tle_dict = {}

for i in range(len(name_array)):
    tle = tle_array[i]
    tle_dict[name_array[i][0]] = tle
    position_dict[name_array[i][0]] = position_array[i]



class MainWindow(QMainWindow):
    global spheres
    spheres = []
    speedup_counter = 0
    current_time = datetime.now()
    global orbit_speedup #= 1/20#1/60

    def __init__(self):
        global max_z, min_z, index, color, colors, num_colors
        super().__init__()
        #spheres = []
        self.orbit_speedup = 1 / 20  # 1/60
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)
        self.setWindowTitle("Multiple Spheres Example")

        self.setWindowTitle("Satellite Tracker")


        button_action = QAction(QIcon("bug.png"), "&Print All Satellites", self)
        button_action.triggered.connect(self.onMyToolBarButtonClick)
        button_action.setCheckable(True)

        button_action2 = QAction(QIcon("pen.png"), "Print All Positions", self)
        button_action2.triggered.connect(self.func2)
        button_action2.setCheckable(True)

        # Create a menu bar
        menu_bar = self.menuBar()

        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(button_action)
        file_menu.addSeparator()
        file_menu.addAction(button_action2)

        # Create a "Names" menu
        satellites_menu = QMenu("Satellites", self)
        print_positions_menu = QMenu("Print Position", self)
        export_tle_menu = QMenu("Export TLE", self)

        # Add an action for each item in the "names" list
        for satellite_name in name_array:
            name = satellite_name[0]

            action = QAction(name, self)
            partial_func = functools.partial(self.onNameMenuActionTriggered, name)
            action.triggered.connect(partial_func)
            print_positions_menu.addAction(action)

            action = QAction(name, self)
            partial_func = functools.partial(self.onPrintTLE, name)
            action.triggered.connect(partial_func)
            export_tle_menu.addAction(action)

            # Create a submenu for each satellite
            satellite_submenu = QMenu(name, self)

            # Action for printing position
            position_action = QAction("Print Position", self)
            partial_position_func = functools.partial(self.onPrintPosition, name)
            position_action.triggered.connect(partial_position_func)
            satellite_submenu.addAction(position_action)

            # Action for printing TLE
            tle_action = QAction("Export TLE", self)
            partial_tle_func = functools.partial(self.onPrintTLE, name)
            tle_action.triggered.connect(partial_tle_func)
            satellite_submenu.addAction(tle_action)

            # Add the satellite submenu to the Satellites menu
            satellites_menu.addMenu(satellite_submenu)


        # Add the "Names" menu to the menu bar
        menu_bar.addMenu(satellites_menu)
        menu_bar.addMenu(print_positions_menu)
        menu_bar.addMenu(export_tle_menu)

        self.setStatusBar(QStatusBar(self))
        self.resize(1400, 700)

        num_colors = 200
        start_color = QColor(255, 0, 0)  # Red
        mid1_color = QColor(255, 165, 0)  # Orange
        mid2_color = QColor(255, 255, 0)  # Yellow
        mid3_color = QColor(0, 255, 0)  # Green
        mid4_color = QColor(0, 255, 255)  # Turquoise
        end_color = QColor(0, 0, 255)  # Blue

        colors = []
        for i in range(num_colors):
            # Calculate the interpolation factor between colors
            gradient_position = i / (num_colors - 1)

            if gradient_position <= 0.3:
                # Interpolate between start_color and mid1_color
                r = int((1 - gradient_position * 5) * start_color.red() + gradient_position * 5 * mid1_color.red())
                g = int((1 - gradient_position * 5) * start_color.green() + gradient_position * 5 * mid1_color.green())
                b = int((1 - gradient_position * 5) * start_color.blue() + gradient_position * 5 * mid1_color.blue())
            elif gradient_position <= 0.4:
                # Interpolate between mid1_color and mid2_color
                r = int((1 - (gradient_position - 0.3) * 5) * mid1_color.red() + (
                            gradient_position - 0.3) * 5 * mid2_color.red())
                g = int((1 - (gradient_position - 0.3) * 5) * mid1_color.green() + (
                            gradient_position - 0.3) * 5 * mid2_color.green())
                b = int((1 - (gradient_position - 0.3) * 5) * mid1_color.blue() + (
                            gradient_position - 0.3) * 5 * mid2_color.blue())
            elif gradient_position <= 0.6:
                # Interpolate between mid2_color and mid3_color
                r = int((1 - (gradient_position - 0.4) * 5) * mid2_color.red() + (
                            gradient_position - 0.4) * 5 * mid3_color.red())
                g = int((1 - (gradient_position - 0.4) * 5) * mid2_color.green() + (
                            gradient_position - 0.4) * 5 * mid3_color.green())
                b = int((1 - (gradient_position - 0.4) * 5) * mid2_color.blue() + (
                            gradient_position - 0.4) * 5 * mid3_color.blue())
            elif gradient_position <= 0.7:
                # Interpolate between mid3_color and mid4_color
                r = int((1 - (gradient_position - 0.6) * 5) * mid3_color.red() + (
                            gradient_position - 0.6) * 5 * mid4_color.red())
                g = int((1 - (gradient_position - 0.6) * 5) * mid3_color.green() + (
                            gradient_position - 0.6) * 5 * mid4_color.green())
                b = int((1 - (gradient_position - 0.6) * 5) * mid3_color.blue() + (
                            gradient_position - 0.6) * 5 * mid4_color.blue())
            else:
                # Interpolate between mid4_color and end_color
                r = int((1 - (gradient_position - 0.7) * 5) * mid4_color.red() + (
                            gradient_position - 0.7) * 5 * end_color.red())
                g = int((1 - (gradient_position - 0.7) * 5) * mid4_color.green() + (
                            gradient_position - 0.7) * 5 * end_color.green())
                b = int((1 - (gradient_position - 0.7) * 5) * mid4_color.blue() + (
                            gradient_position - 0.7) * 5 * end_color.blue())

            colors.append(QColor(r, g, b))

        # Create multiple spheres at specified positions with different colors
        earth_radius = 50
        radius = 3.5
        # Load the Earth image as a QPixmap
        earth_image_path = "earth2.png"  # Replace with the path to your Earth image file
        earth_pixmap = QPixmap(earth_image_path)

        # Create a QGraphicsPixmapItem and set the Earth image as its pixmap
        earth_item = self.scene.addPixmap(earth_pixmap)

        # Set the position and size of the Earth item
        earth_radius = 100  # Adjust the radius as needed
        earth_item.setPos(-earth_radius+ 500, -earth_radius) #+500 to shift to the right
        earth_item.setScale(2 * earth_radius / earth_pixmap.width())
        min_z = -476
        max_z = 343
        for i in range(num_tles):
            x, y, z = position_array[i][0], position_array[i][1], position_array[i][2]
            index = int((z - min_z) / (max_z - min_z) * (num_colors - 1))
            index %= num_colors
            sphere = self.scene.addEllipse(x - radius, y - radius, radius * 2, radius * 2)
            sphere.setPen(QPen(QColor("black")))
            sphere.setBrush(QBrush(colors[index]))
            spheres.append(sphere)

        # Set the scene dimensions
        legend_width = 20
        legend_height = 200

        min_height = -250
        max_height = 250

        # Calculate the height increment for each color band
        height_increment = (max_height - min_height) / len(colors)

        # Create a rectangle and label for each color band in the legend
        labels = ['1500km','1000km', '500km', '0','-500km', '-1000km', '-1500km', '-2000km']
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
            label.setText(labels[i])
            label.setPos(legend_width + 1310, start_height + 50)


            # Add the label to the scene
            self.scene.addItem(label)
        label1 = QGraphicsSimpleTextItem()
        label1.setFont(QFont("Arial", 10))
        label1.setText("2000km")
        label1.setPos(legend_width + 1310, start_height- 450)

        # Add the label to the scene
        self.scene.addItem(label1)

        # Create a layout for the central widget
        layout = QVBoxLayout()
        self.view.setLayout(layout)

        # Create a label and a line edit widget
        prop_interval_label = QLabel("Enter your desired propagation interval")
        line_edit = QLineEdit()
        line_edit.setFixedWidth(205)

        #layout.addSpacing(40)

        # Add the label and line edit to the layout
        layout.addWidget(line_edit)
        layout.addWidget(prop_interval_label)
        layout.setAlignment(prop_interval_label, Qt.AlignTop)

        layout.setAlignment(line_edit, Qt.AlignLeft)


        # Connect the line edit's textChanged signal to a slot
        line_edit.textChanged.connect(self.onLineEditTextChanged)

        # Create a button
        button = QPushButton("Open 3D View")
        button.setFixedSize(200, 30)
        layout.setAlignment(button, Qt.AlignBottom)

        # Add some spacing above the button to move it upwards
        layout.addSpacing(-600)

        # Add the button to the layout
        layout.addWidget(button)

        # Connect the button's clicked signal to the slot that opens a new window
        button.clicked.connect(self.open3DWindow)

        # Add the button to the layout
        layout.addWidget(button)

        # Keep a reference to the new window
        self.new_window = None

    def open3DWindow(self):
        self.new_window = Window3D()
        self.new_window.show()
    def onLineEditTextChanged(self, text):
        # Retrieve the entered value from the line edit
        try:
            self.orbit_speedup = float(text)
            # Use the entered value in your code
            print("Entered number:", self.orbit_speedup)
        except ValueError:
            print("Invalid number entered")

    def schedule_scene_update(self):
        self.translate_spheres()
        #for sphere in spheres:
        self.translation_timer = QTimer()
        self.translation_timer.timeout.connect(self.translate_spheres)
        self.translation_timer.start(2*1000)  # repetition period in minutes

        self.tle_timer = QTimer()
        self.tle_timer.timeout.connect(self.update_tle_array)
        self.tle_timer.start(8*60*60*1000)  # repetition period in hours - updates 3 times a day

    def update_tle_array(self):
        for i in range(num_tles):
            tle_array[i] = exporter.export_tle(list(importTLE.load_gp_from_celestrak(name=name_array[i][0]))[0])

    def translate_spheres(self):
        #update position array
        #position_array = parallelization.serial_get_position()
        for i in range(num_tles):
            if tle_array[i][0] != "":
                satelliteObj = Satrec.twoline2rv(tle_array[i][0], tle_array[i][1])  # convert tle to satrec object
                # Calculate the target time as 10 minutes later than the previous time
                target_time = self.current_time + timedelta(minutes= self.orbit_speedup)

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
                r = [r[i] / 300 for i in range(3)] #to scale the position to fit onto the screen
                r[0] = r[0]+500 #to shift to the center of the screen
                position_array[i] = r
        print(position_array[0])
        MainWindow.speedup_counter +=1

        # Translate the sphere's position
        for i in range(len(spheres)):
            spheres[i].setPos(position_array[i][0], position_array[i][1])

            # change colour
            z = position_array[i][2]
            index = int((z - min_z) / (max_z - min_z) * (num_colors - 1))
            index %= num_colors
            spheres[i].setBrush(QBrush(colors[index]))


    def onMyToolBarButtonClick(self):
        print(name_array)

    def func2(self, s):
        print(position_array)

    def onNameMenuActionTriggered(self, name):
        print('Position: ' + str(position_dict[name]))

    def onPrintPosition(self, name):
        print('Position:', position_dict[name])

    def onPrintTLE(self, name):
        #print(tle_dict[name])
        filename = re.sub(r'[\\/:"*?<>|]', '', name) + '_TLE'
        with open(filename, 'w') as file:
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
window.show()
sys.exit(app.exec())
