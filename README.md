#PyQLab Instrument and Qubit Control Software

[![Build Status](https://travis-ci.org/BBN-Q/PyQLab.svg?branch=develop)](https://travis-ci.org/BBN-Q/PyQLab) [![Coverage Status](https://coveralls.io/repos/BBN-Q/PyQLab/badge.svg?branch=develop)](https://coveralls.io/r/BBN-Q/PyQLab)

This is a python package for simulating and experimentally implementing control of superconducting qubit systems.  It complements and sometimes overlaps with the [Qlab](https://github.com/BBN-Q/Qlab) repository.

Contents:
* Quantum Gate Language (QGL) for specifying pulse sequences
* Instrument settings GUIs

See example usage in this [Jupyter notebook](https://github.com/BBN-Q/PyQLab/blob/develop/doc/QGL-demo.ipynb).

##Setup instructions

The most straightforward way to get up and running is to use the [Anaconda Python distribution](http://continuum.io/downloads). This includes nearly the dependencies. The few remaining can be installed from the termminal or Anaconda Command Prompt on Windows

```bash
conda install atom
conda install enaml
pip install watchdog
```

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
* h5py
* watchdog
* Bokeh 0.7
* iPython 3.0 (only for Jupyter notebooks)
