# Space-Object-Tracker

## Background to the Study
The Soviet Union’s launch of Sputnik 1 began the Space Age in 1957. \cite{1, 2} Over the past 66 years, approximately 6400 rockets have been launched, deploying 15070 satellites into Earth's orbit. When a spacecraft is abandoned, its rocket stages remain in orbit, and if a collision or explosion occurs between these stages or with other satellites or objects, the result is termed a fragmentation event. This is an occurrence in which a larger object breaks apart into smaller pieces or fragments which remain in the Earth's orbit. The population of man-made objects in space that have lost their functionality or purpose, is otherwise known as space debris. The accumulation of space debris is leading to the formation of a belt of debris around Earth \cite{4}, increasing the potential for collisions and endangering operational satellites and spacecraft. To mitigate these risks associated with the growing space population, it is crucial to enhance Space Situational Awareness (SSA). This involves a more thorough mapping of the space environment, by accurately tracking and predicting the precise positions of all space objects. A visual software interface serves as a valuable tool for representing the space environment, enabling astronomers, researchers, and space enthusiasts to assess the space population more effectively and make informed decisions.

## Objectives
This study aims to develop and optimise a software tool capable of modelling space objects, predicting their orbit propagation, and providing a symbolic visualisation of the space environment. The investigation endeavours to research and determine the most appropriate orbit propagation model to predict the trajectories of space objects in the Low Earth Orbit.   This chosen model will be employed to predict the position of a space object at a given date and time, and the developed application will enable simultaneous tracking of multiple space objects. The final objective of the project is to develop a graphical user interface (GUI) which provides a visual representation of the space population. This will enable users to interact with the application and utilise its diverse functionalities. The application must have the capability to present the orbital data associated with each space object. Moreover, the application aims to incorporate a functionality that facilitates the export of Two-Line Elements for selected space objects.

## Scope and Limitations
This study aims to develop an application that tracks and visualises satellites, focusing on their movement and spatial representation. The application is limited to the position estimation of satellites and space debris which are in Earth’s low orbit, and which have publicly available TLE data on Celestrak. It is important to note that the application is not intended for use in scenarios where precise position accuracy is of critical importance. The application will import Two-Line Element (TLE) data from a third-party satellite tracker and extract the necessary control data. The tracking of object positions will occur at regular time intervals, but it should be noted that the data displayed will not be real-time information.

The scope of this study introduces two important limitations. Firstly, satellites with classified information or objects in unconventional orbits may not be trackable through this application. Secondly, the application's functionality is contingent upon a stable internet connection as it relies on retrieving up-to-date TLE data from Celestrak. Furthermore, it is important to note that this application does not provide real-time position tracking data from the space objects themselves, but instead relies on estimated positions which have been calculated using TLE data and SGP4. The accuracy of satellite position estimation is thus dependent on the precision of the TLE data and the inclusion of perturbations within the environmental model. Finally, the performance of the application may be influenced by the processing speed and graphical capabilities of the user's computer. Older or low-powered machines might experience limitations in efficiently running the GUI application.

## Installation Instructions
1. Install Python: Make sure you have Python installed on your system. You can download the latest version of Python from the official website (https://www.python.org) and follow the installation instructions for your operating system.
2. Install Required Packages: Open a terminal or command prompt and execute the following commands to install the required packages:

```
pip install sgp4
pip install numpy
pip install PySide6
pip install astropy
```
3. Verify Installation: After the installation process is complete, you can verify if the packages are installed correctly. Run the following commands in the terminal:

```
python -c "import sgp4; print(sgp4.__version__)"
python -c "import numpy; print(numpy.__version__)"
python -c "import PySide6; print(PySide6.__version__)"
python -c "import astropy; print(astropy.__version__)"
```

If the packages are installed correctly, you should see the respective package versions printed without any errors.
## Usage Guide
The `updating2dgui` project is a graphical user interface (GUI) application that allows users to interact with the system easily. It requires the `CelestrakAPI` dependency file to be present.
### Prerequisites

Before running the updating2dgui application, make sure you have the following:

1. **IDE (Integrated Development Environment):**
   - Ensure you have an IDE installed on your machine.
   - Choose an IDE that suits your preferences, such as Visual Studio Code, PyCharm, or Eclipse.

2. **CelestrakAPI Dependency File:**
   - Obtain the CelestrakAPI dependency file required for interacting with the Celestrak satellite database.
   - Make sure you have the dependency file available before running the application.

3. **TLE Textile:**
   - You will need a TLE (Two-Line Elements) file that contains orbital data for the satellites.
   - There are two options for obtaining the TLE file:
     - Download it directly from Celestrak, a popular source for satellite information.
     - Find the TLE file included in the repository where the updating2dgui application is located.

4. **GUI Images:**
   - The updating2dgui application relies on several PNG images for proper functioning.
   - Download the required images from the repository and ensure they are available in the appropriate locations for the GUI to display correctly.


### Running the Application

To run the `updating2dgui` application, follow these steps:

1. Open your preferred IDE.

2. Import the `CelestrakAPI` dependency file into your project.

3. Locate the `updating2dgui` file in your project.

4. Run the `updating2dgui` file in the IDE.

5. The GUI will open up, providing clear and concise controls for navigating and interacting with the system.

## Application Features

The project incorporates the following features that address the system requirements:

### TLE Data Management

- Import TLE data for multiple satellites.
- Efficiently store the TLE data in a database or data structure.
- Automatically update the system and replace out-of-date TLE data.

### Orbit Propagation

- Implement an orbit propagation algorithm to determine the trajectories of the satellites.
- Re-calibrate the satellite positions at frequent regular intervals.

### Graphical User Interface (GUI)

- Visualise the movement of satellites around the Earth.
- Switch between a 2D view and a 3D view of the space environment.
- Interact with satellite objects by clicking on them.
- Display relevant information about the selected satellite.
- Print or export the TLE data of specified satellites.
- Easily dismiss the displayed information.
- Select an orbit propagation interval.

These features provide a comprehensive tool for space object modeling, orbit propagation prediction, and symbolic visualisation of the space environment.



