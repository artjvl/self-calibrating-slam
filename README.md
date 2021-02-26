# Self-Calibrating SLAM

MSc-Thesis work  of [Art van Liere](mailto:artvanliere@gmail.com)

# Table of Contents

- [Self-Calibrating SLAM](#self-calibrating-slam)
- [Getting Started](#getting-started)
- [Contact Info](#contact-info)

# Getting Started

## Requirements

Self-Calibrating SLAM Python framework:
- **[pip3](https://pypi.org/project/pip/)** (install package ```python3-pip``` with ```apt```)
- **[pyqt5](https://pypi.org/project/PyQt5/)** (install package ```pyqt5``` with ```pip3```)
- **[pyqtgraph](http://www.pyqtgraph.org/)** (install package ```pyqtgraph``` with ```pip3```)

g2o:
- **[cmake](https://cmake.org/)** (install package ```cmake``` with ```apt```)
- **[eigen3](http://eigen.tuxfamily.org)** (install package ```libeigen3-dev``` with ```apt```)
- **[suitesparse](http://faculty.cse.tamu.edu/davis/suitesparse.html)** (_optional_, install package ```libsuitesparse-dev``` with ```apt```)
- **[Qt5](http://qt-project.org)** (_optional_, install package ```qtdeclarative5-dev``` and ```qt5-qmake``` with ```apt```)
- **[libQGLViewer](http://libqglviewer.com/)** (_optional_, install package ```libqglviewer-dev-qt5``` with ```apt```)

## Installation

Self-Calibrating SLAM Python framework:
- ```pip3 install -e path/to/self-calibrating-slam/src/``` (or ```pip3 install -e .``` when in the ```src/``` directory) to install the package in editable state.

g2o:
- ```mkdir build``` in the ```g2o/``` directory
- ```cd build```
- ```cmake ../```
- ```make```

# Framework

## GUI

The GUI intuitively allows for graph creation, optimisation and analysis.
- ```python3 gui.py``` in ```src/gui/```

# Contact Info

Art van Liere\
[artvanliere@gmail.com](mailto:artvanliere@gmail.com)\
+31 6 51 66 18 75