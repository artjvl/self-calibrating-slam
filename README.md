# Self-Calibrating SLAM

MSc-Thesis '**Pose-parameter graph optimisation**'  of [Art van Liere](mailto:artvanliere@gmail.com)

# Table of Contents

- [Self-Calibrating SLAM](#self-calibrating-slam)
- [Getting Started](#getting-started)
- [Contact Info](#contact-info)

# Getting Started

## Requirements

Pose-parameter graph simulation and analysis Python framework:
- Python 3.8+
- **[pip3](https://pypi.org/project/pip/)** (with ```apt install python3-pip```)
- **[numpy](https://numpy.org/)** (with ```pip3 install numpy```)
- **[scipy](https://scipy.org/)** (with ```pip3 install scipy```)
- **[matplotlib](https://matplotlib.org/)** (with ```pip3 install matplotlib```)
- **[pyqt5](https://pypi.org/project/PyQt5/)** (with ```pip3 install pyqt5```)
- **[pyqtgraph](http://www.pyqtgraph.org/)** (with  ```pip3 install pyqtgraph```)
- **[pyopengl](https://pypi.org/project/PyOpenGL/)** (with ```pip3 install pyopengl```)

g2o:
- **[cmake](https://cmake.org/)** (with ```apt install cmake```)
- **[eigen3](http://eigen.tuxfamily.org)** (with ```apt install libeigen3-dev```)
- _optional (for g2o gui)_: **[suitesparse](http://faculty.cse.tamu.edu/davis/suitesparse.html)** (with ```apt install libsuitesparse-dev```)
- _optional (for g2o gui)_: **[Qt5](http://qt-project.org)** (with ```apt install qtdeclarative5-dev``` and ```apt install qt5-qmake```)
- _optional (for g2o gui)_: **[libQGLViewer](http://libqglviewer.com/)** (with ```apt install libqglviewer-dev-qt5```)

## Installation

Self-Calibrating SLAM Python framework:
- in root folder: ```pip3 install -e .``` (i.e., ```pip3 install -e path/to/self-calibrating-slam/```)
- if encountering 'xcb platform plugin error' (could occur in VirtualBox), try: **[```sudo apt-get install --reinstall libxcb-xinerama0```](https://askubuntu.com/questions/308128/failed-to-load-platform-plugin-xcb-while-launching-qt5-app-on-linux-without)**

g2o:
- in ```g2o/``` directory (```cd g2o```): ```mkdir build```
- in ```build/``` directory (```cd build```): ```cmake ../```
- in ```build/``` directory: ```make```

# Framework

## GUI

![](doc/gif/peek_20210309.gif)

The GUI intuitively allows for graph creation, optimisation and analysis.
- in ```src/``` directory: ```python3 main.py``` or ```python3 gui/gui.py```

# Contact Info

Art van Liere\
[artvanliere@gmail.com](mailto:artvanliere@gmail.com)\
+31 6 51 66 18 75