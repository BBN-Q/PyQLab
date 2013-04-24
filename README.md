#PyQLab Instrument and Qubit Control Software
This is a python package for simulating and experimentally implementing control of superconducting qubit systems.  It complements and sometimes overlaps with the [Qlab](https://github.com/BBN-Q/Qlab) repository.

Contents:
* Quantum Gate Language (QGL) for specifying pulse sequences
* Instrument settings GUIs

##Dependencies
### General
* Python 2.7
* Numpy/Scipy
* Matplotlib
* PySide
* h5py
* watchdog 

### ExpSettings GUI
* enaml - Until updated upstream use Colm's fork (`pip install git+git://github.com/caryan/enaml.git@list_control_rows`)

##Setup instructions

Use of the `QGL` module requires the presence of two environment variables and two configuration files (one for PyQlab configuration info, the other for pulse/instrument info). Set `PYTHONPATH` to include the PyQlab folder. You must also set `PYQLAB_CFGFILE` to the full path of the config file. On windows machines, you add the environment variables by going to System -> Advanced Settings -> Environment variables. On Mac/Linux machines add the following lines to your .bashrc or .bash_profile:
```
export PYTHONPATH=/path/to/PyQlab:$PYTHONPATH
export PYQLAB_CFGFILE=/path/to/config.json
```

The PyQlab config and pulse params files can be created by running install.sh [TODO].
