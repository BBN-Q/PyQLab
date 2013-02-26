import numpy as np
from scipy.io import loadmat
from scipy.signal import butter, lfilter
from scipy.io import loadmat

from sklearn import decomposition, preprocessing
from sklearn import svm, grid_search

import pywt

import glob

# import matplotlib.pyplot as plt

def create_fake_data(SNR, dt, maxTime, numShots, T1=1.0):
	"""
	Helper function to create fake training data.
	"""
	#Create a random set of decay times
	decayTimes = np.random.exponential(scale=T1, size=numShots/2 )

	#Create the noiseless decays
	timePts = np.arange(dt, maxTime, dt)
	fakeData = np.zeros((numShots, timePts.size))

	#Put the ground state runs down to -1
	fakeData[::2, :] = -1.0

	#Put the excited state ones to one before they decay
	for ct, decayTime in enumerate(decayTimes):
		fakeData[2*ct-1] = 2*(decayTime>timePts)-1

	#Now add Gaussian noise
	fakeData += np.random.normal(scale=1.0/np.sqrt(dt*SNR), size=fakeData.shape)

	return fakeData

def extract_meas_data(fileName, numAvgs):
	"""
	Helper function to load, filter and extract pulsed measurment data from single shot records.
	"""

	#Load the matlab data
	rawData = np.mean(loadmat(fileName)['demodSignal'].reshape((3200, 8000/numAvgs, numAvgs), order='F'), axis=2)

	#Decimate by a factor of 8 twice
	b,a = butter(5, 0.5/8)
	filteredData = lfilter(b,a, avgData, axis=0)[::8, :]
	filteredData = lfilter(b,a, filteredData, axis=0)[::8, :]

	#Extract the pulse part
	pulseData = filteredData[10:40,:]

	#Pull out real and imaginary components 
	return np.hstack((pulseData.real.T, pulseData.imag.T))

def fidelity_est(testSignals):
	"""
	Estimate the optimal fidelity by estimating the probability distributions.
	"""
	rangeMin = np.min(testSignals)
	rangeMax = np.max(testSignals)

	groundProb = np.histogram(testSignals[::2], bins=100, range=(rangeMin, rangeMax), density=True)[0]
	excitedProb, binEdges = np.histogram(testSignals[1::2], bins=100, range=(rangeMin, rangeMax), density=True)
	return 0.5*(binEdges[1]-binEdges[0])*np.sum(np.abs(groundProb-excitedProb))

def test_fixed(SNRs):
	"""
	Fixed (infinite T1) qubit.
	"""
	fidelities = []
	numShots = 10000
	dt = 1e-3
	for SNR in SNRs:
		fakeData = create_fake_data(SNR, dt, 1, numShots, T1=1e9)
		signal = dt*np.sum(fakeData, axis=1)
		fidelities.append(fidelity_est(signal))
	return fidelities

def test_boxcar(SNRs, intTimes):
	"""
	Simple box-car integration with finite T1.
	"""
	fidelities = []
	numShots = 10000
	dt = 1e-3
	trueStates = np.tile([False, True], numShots/2)
	for SNR, intTime in zip(SNRs, intTimes):
		fakeData = create_fake_data(SNR, dt, intTime, numShots)
		signal = dt*np.sum(fakeData, axis=1)
		fidelities.append(fidelity_est(signal))
	return fidelities

def test_nn(SNR):
	pass


def load_exp_data(path):
	matFiles = glob.glob(path+'*.mat')
	allRecords = None
	for matFile in matFiles:
		if allRecords is not None:
			allRecords = np.dstack((allRecords, np.squeeze(loadmat(matFile)['demodSignal']) ))
		else:
			allRecords = np.squeeze(loadmat(matFile)['demodSignal'])

	return allRecords[:,0,:], allRecords[:,1,:]

def wavelet_transform(measRecords, wavelet):
	"""
	Take and array of measurment records, wavelet transform and return the most significant components.
	"""
	out = []
	for record in measRecords:
		cA3, cD3, cD2, cD1 = pywt.wavedec(record, wavelet, level=3)
		out.append(np.hstack((cA3, cD3)))
	return np.array(out)

if __name__ == '__main__':
	pass

	SNR = 1e4
	fakeData = create_fake_data(SNR, 1e-3, 1, 4000)

	#Use PCA to extract fewer useful features
	pca = decomposition.PCA()
	pca.n_components = 40
	pca.fit(fakeData)

	# trainData = pca.transform(fakeData)
	# validateData =  pca.transform(create_fake_dpata(SNR, 1e-2, 1, 2000))

	trueStates = np.tile([0,1], 2000).flatten()

	# trueStates = np.hstack((np.zeros(1000), np.ones(1000)))
	# testData = wavelet_transform(fakeData, 'db4')
	testData = pca.transform(fakeData)
	# scaler = preprocessing.Scaler().fit(testData)
	# testData = scaler.transform(testData)

	searchParams = {'gamma':(1.0/100)*np.logspace(-3, 0, 40), 'nu':np.arange(0.01, 0.2, 0.02)}
	clf = grid_search.GridSearchCV(svm.NuSVC(cache_size=500), searchParams, n_jobs=1)
	clf.fit(testData, trueStates)


	# fakeData = create_fake_data(SNR, 1e-2, 1, 5000)
	# validateData = scaler.transform(validateData)


	# numAvgs = 10
	# fileName = '/home/cryan/Desktop/SSResults-2013-01-09-09-51-17.mat'

	# pulseData = extract_meas_data(fileName, numAvgs)




	# #Assumed states alternate between ground and excited.
	# states = np.tile([0,1], (1, 400)).flatten()

	# plt.figure()
	# plt.scatter(np.mean(pulseData[:,:30],1), np.mean(pulseData[:,31:],1), c=states, cmap=plt.cm.Paired)

	# plt.figure()
	# plt.scatter(reducedData[:,0], reducedData[:,1], c=states, cmap=plt.cm.Paired)

	# plt.show()


