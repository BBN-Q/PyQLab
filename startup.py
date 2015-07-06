import h5py # hack until anaconda fixes h5py/pytables conflict
from Libraries import instrumentLib, channelLib
import numpy as np
from QGL import *
import QGL
import config as PQconfig

QGL.Compiler.channelLib = channelLib
QGL.Compiler.instrumentLib = instrumentLib
