#PyQLab Instrument and Qubit Control Software
This is a python package for simulating and experimentally implementing control of superconducting qubit systems.  It complements and sometimes overlaps with the [Qlab](https://github.com/BBN-Q/Qlab) repository.

Contents:
* Quantum Gate Language (QGL) for specifying pulse sequences
* Instrument settings GUIs

See example usage in this ipython [notebook](http://nbviewer.ipython.org/github/BBN-Q/PyQLab/blob/develop/doc/QGL-demo.ipynb).

##Setup instructions

The most straightforward way to get up and running is to use the [Anaconda Python distribution](http://continuum.io/downloads). This includes all the dependencies except for watchdog which can be installed with `pip install watchdog`.  You may have to update Bokeh using ``conda update bokeh``. 

There is a known issue on Windows and Linux Anaconda distributions which causes h5py to throw errors.  The errors are benign but they can be avoided using an updated version of h5py from ``binstar/caryan``

```bash
conda remove h5py
conda install -c caryan h5py
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


