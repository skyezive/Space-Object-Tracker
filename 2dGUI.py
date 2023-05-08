from sgp4.model import Satrec
from astropy.time import Time
import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsRectItem, \
    QGraphicsSimpleTextItem
from PySide6.QtGui import QColor, QPen, QBrush, QPainter, QPixmap, QFont
import sys
import parallelization
import re
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
filename = '100.txt'

with open(filename, "r") as file:
    num_lines = sum(1 for line in file)
    num_tles = round(num_lines/3)
    print(num_tles)

tle_array = np.empty([num_tles, 2], dtype='U70') #numtles in .txt, 2 elements per tle
name_array = np.empty([num_tles, 1], dtype='U30')
position_array = np.empty([num_tles, 3])
#print(position_array)

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

print(TLEcounter)
for i in range(num_tles):
    if tle_array[i][0] != "":
        satelliteObj = Satrec.twoline2rv(tle_array[i][0], tle_array[i][1])  # convert tle to satrec object
        e, r, v = satelliteObj.sgp4(Time.now().jd1, Time.now().jd2)
        r = [r[i] / 200 for i in range(3)]
        position_array[i] = r


position_dict = {}
tle_dict = {}

for i in range(len(name_array)):
    tle = tle_array[i]
    tle_dict[name_array[i][0]] = tle
    position_dict[name_array[i][0]] = position_array[i]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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
        self.resize(1000, 700)

        num_colors = 8
        start_color = QColor(0, 0, 255)  # Blue (for negative values)
        end_color = QColor(255, 0, 0)  # Red (for positive values)

        colors = []
        for i in range(num_colors):
            # Calculate the interpolation factor between start_color and end_color
            gradient_position = i / (num_colors - 1)

            # Interpolate the RGB components based on gradient position
            r = int((1 - gradient_position) * start_color.red() + gradient_position * end_color.red())
            g = int((1 - gradient_position) * start_color.green() + gradient_position * end_color.green())
            b = int((1 - gradient_position) * start_color.blue() + gradient_position * end_color.blue())

            # Create the color and add it to the list
            color = QColor(r, g, b)
            colors.append(color)

        # Create multiple spheres at specified positions with different colors
        earth_radius = 50
        radius = 5
        # Load the Earth image as a QPixmap
        earth_image_path = "earth2.png"  # Replace with the path to your Earth image file
        earth_pixmap = QPixmap(earth_image_path)

        # Create a QGraphicsPixmapItem and set the Earth image as its pixmap
        earth_item = self.scene.addPixmap(earth_pixmap)

        # Set the position and size of the Earth item
        earth_radius = 100  # Adjust the radius as needed
        earth_item.setPos(-earth_radius, -earth_radius)
        earth_item.setScale(2 * earth_radius / earth_pixmap.width())
        earth_item.setToolTip("This is the Earth.")
        #num_spheres = len(colors)
        num_tles = 100
        min_z = -476
        max_z = 343
        circles = []
        for i in range(num_tles):
            x, y, z = position_array[i][0], position_array[i][1], position_array[i][2]
            #print(z)
            index = int((z - min_z) / (max_z - min_z) * (num_colors - 1))
            index %= num_colors
            sphere = self.scene.addEllipse(x - radius, y - radius, radius * 2, radius * 2)
            sphere.setPen(QPen(QColor("black")))
            sphere.setBrush(QBrush(colors[index]))


        # Set the scene dimensions
        legend_width = 20
        legend_height = 200

        min_height = -200
        max_height = 200

        # Calculate the height increment for each color band
        height_increment = (max_height - min_height) / len(colors)

        # Create a rectangle and label for each color band in the legend
        labels = ['1500km','1000km', '500km', '0','-500km', '-1000km', '-1500km', '-2000km']
        for i, color in enumerate(reversed(colors)):
            # Calculate the height range for the current color band
            start_height = min_height + i * height_increment
            end_height = start_height + height_increment

            # Create a QGraphicsRectItem for the current color band
            rect = QGraphicsRectItem(400, start_height, legend_width, end_height - start_height)
            rect.setBrush(QBrush(color))

            # Add the rectangle to the scene
            self.scene.addItem(rect)

            # Create a QGraphicsSimpleTextItem for the height label
            label = QGraphicsSimpleTextItem()
            label.setFont(QFont("Arial", 10))
            label.setText(labels[i])
            label.setPos(legend_width + 410, start_height+40)

            # Add the label to the scene
            self.scene.addItem(label)
        label1 = QGraphicsSimpleTextItem()
        label1.setFont(QFont("Arial", 10))
        label1.setText("2000km")
        label1.setPos(legend_width + 410, start_height- 360)

        # Add the label to the scene
        self.scene.addItem(label1)

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


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
