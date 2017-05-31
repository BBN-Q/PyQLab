# PyQLab Instrument and Qubit Control Software

[![Build Status](https://travis-ci.org/BBN-Q/PyQLab.svg?branch=develop)](https://travis-ci.org/BBN-Q/PyQLab) [![Coverage Status](https://coveralls.io/repos/BBN-Q/PyQLab/badge.svg?branch=develop)](https://coveralls.io/r/BBN-Q/PyQLab)

This is a python package for managing instruments and control parameters for
superconducting qubit systems. It complements the
[Qlab](https://github.com/BBN-Q/Qlab) repository by providing simple GUIs for
creating the JSON settings structures used by Qlab.

## Setup instructions

The most straightforward way to get up and running is to use the [Anaconda
Python distribution](http://continuum.io/downloads). This includes nearly all the
dependencies. The few remaining can be installed from the termminal or Anaconda
Command Prompt on Windows. On Windows you may also need to ensure that either
the already installed `git` is on the path or `conda install git`.

### Python 2

```shell
conda install atom enaml future
pip install watchdog
pip install git+https://github.com/BBN-Q/QGL.git
```

### Python 3

PyQLab depends on enaml/atom which have only recently become Python 3 compatible
via a fork. You may wan to run PyQlab from its own environment to segregate its
dependencies from your standard environment.

```shell
conda create --name pyqlab python=3.6 scipy networkx h5py bokeh
source activate pyqlab
conda install -c ecpy enaml watchdog
pip install git+https://github.com/BBN-Q/QGL.git
```

The PyQLab config file will be created the first time you run `ExpSettingsGUI.py`.

## Dependencies
* Python 2.7/3.5
* Numpy/Scipy
* Nucleic enaml/atom
* h5py
* future
* watchdog
* Bokeh 0.7
* iPython 3.0 (only for Jupyter notebooks)
* QGL
