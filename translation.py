from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsEllipseItem, QGraphicsView
from PySide6.QtCore import QTimer
import sys
import time

app = QApplication(sys.argv)

# Create the main window and 2D view
window = QMainWindow()
view = QGraphicsView(window)
scene = QGraphicsScene()
view.setScene(scene)

# Define the circle properties
circle_radius = 50
circle_spacing = 100

# Create three circles
circles = []
for i in range(3):
    x = (i + 1) * circle_spacing
    y = 100

    # Create a QGraphicsEllipseItem
    circle = QGraphicsEllipseItem(x - circle_radius, y - circle_radius, circle_radius * 2, circle_radius * 2)
    circles.append(circle)
    scene.addItem(circle)

# Set up the main window and show it
window.setCentralWidget(view)
window.show()

# Function to translate the circles' positions
def translate_circles():
    for circle in circles:
        # Translate the circle's position
        circle.setPos(circle.x() + 500, circle.y())

# Use QTimer to delay the translation by 5 seconds
timer = QTimer()
timer.timeout.connect(translate_circles)
timer.setSingleShot(True)
timer.start(5000)  # Delay in milliseconds (5 seconds = 5000 milliseconds)

sys.exit(app.exec())
