#PyQLab Instrument and Qubit Control Software
This is a python package for simulating and experimentally implementing control of superconducting qubit systems.  It complements and sometimes overlaps with the [Qlab](https://github.com/BBN-Q/Qlab) repository.

Contents:
* Quantum Gate Language (QGL) for specifying pulse sequences
* Instrument settings GUIs

##Setup instructions

The most straightforward way to get up and running is to use the [Anaconda Python distribution](http://continuum.io/downloads). This includes all the dependencies (although you may have to `conda update`) except for watchdog which can be installed with `pip install watchdog`.  Until an issue is fixed upstream you need to either use PyQt (set environment variable `QT_API=pyqt`) or install a patched version of enaml (`pip install git+git://github.com/caryan/enaml-nucleic.git@fix/pyside-dialogs`). 

Use of the `QGL` module requires the PyQLab folder to be included in `PYTHONPATH`. On windows machines, you add/modify this environment variable by going to System -> Advanced Settings -> Environment variables. On Mac/Linux machines add the following line to your .bashrc or .bash_profile:
```
export PYTHONPATH=/path/to/PyQlab:$PYTHONPATH
```

The PyQLab config file will be created the first time you run `startup.py` or `config.py`.

##Dependencies
* Python 2.7
* Numpy/Scipy
* Nucleic enaml/atom
* Matplotlib
* PySide
* h5py
* watchdog 


