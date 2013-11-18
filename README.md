#PyQLab Instrument and Qubit Control Software
This is a python package for simulating and experimentally implementing control of superconducting qubit systems.  It complements and sometimes overlaps with the [Qlab](https://github.com/BBN-Q/Qlab) repository.

Contents:
* Quantum Gate Language (QGL) for specifying pulse sequences
* Instrument settings GUIs

##Dependencies
* Python 2.7
* Numpy/Scipy
* Enthought traits
* Matplotlib
* PySide
* h5py
* watchdog 
* enaml - N.b. does not yet work with Nucleic fork (versions 0.7+). For now, use Colm's fork (`pip install git+git://github.com/caryan/enaml.git@list_control_rows`)

##Setup instructions

Use of the `QGL` module requires the PyQLab folder to be included in `PYTHONPATH`. On windows machines, you add/modify this environment variable by going to System -> Advanced Settings -> Environment variables. On Mac/Linux machines add the following line to your .bashrc or .bash_profile:
```
export PYTHONPATH=/path/to/PyQlab:$PYTHONPATH
```

The PyQLab config file will be created the first time you run `startup.py` or `config.py`.
