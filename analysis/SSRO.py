import numpy as np
from scipy.signal import butter, lfilter
from scipy.io import loadmat

from sklearn import decomposition, preprocessing, cross_validation
from sklearn import svm, grid_search

import pywt
import h5py

import matplotlib.pyplot as plt

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


def load_exp_data(fileName):
	"""
	Helper function to load data dumped from matlab
	"""
	f = h5py.File(fileName, 'r')
	gData = np.fromstring(f['groundData'].value, dtype=np.complex).reshape(f['groundData'].shape)
	eData = np.fromstring(f['excitedData'].value, dtype=np.complex).reshape(f['excitedData'].shape)

	return gData, eData
def wavelet_transform(measRecords, wavelet):
	"""
	Take and array of measurment records, wavelet transform and return the most significant components.
	"""
	out = []
	for record in measRecords:
		cA3, cD3, cD2, cD1 = pywt.wavedec(record, wavelet, level=3)
		out.append(np.hstack((cA3, cD3)))
	return np.array(out)

def credible_interval(outcomes, c=0.95):
	"""
	Calculate the credible interval for a fidelity estimate.
	"""
	from scipy.special import betaincinv
	N = outcomes.size
	S = np.count_nonzero(outcomes)
	xlo = betaincinv(S+1,N-S+1,(1-c)/2.)
	xup = betaincinv(S+1,N-S+1,(1+c)/2.)

	return xlo, xup

for ct in range(90,120):
	testSignals[::2] = np.sum((weights*gUnWound.real)[:,:ct], axis=1)
	testSignals[1::2] = np.sum((weights*eUnWound.real)[:,:ct], axis=1)
	print(fidelity_est(testSignals))

if __name__ == '__main__':
	pass

	# SNR = 1e4
	# fakeData = create_fake_data(SNR, 1e-3, 1, 4000)


	# # trainData = pca.transform(fakeData)
	# # validateData =  pca.transform(create_fake_dpata(SNR, 1e-2, 1, 2000))

	# trueStates = np.tile([0,1], 2000).flatten()

	# # trueStates = np.hstack((np.zeros(1000), np.ones(1000)))
	# # testData = wavelet_transform(fakeData, 'db4')
	# testData = pca.transform(fakeData)
	# # scaler = preprocessing.Scaler().fit(testData)
	# # testData = scaler.transform(testData)


	# # fakeData = create_fake_data(SNR, 1e-2, 1, 5000)
	# validateData = scaler.transform(validateData)


	gData, eData = load_exp_data('/home/cryan/Desktop/SSData.mat')

	# #Use PCA to extract fewer, more useful features
	# allData = np.vstack((np.hstack((gData.real, gData.imag)), np.hstack((eData.real, eData.imag))))
	# pca = decomposition.PCA()
	# pca.n_components = 20
	# reducedData = pca.fit_transform(allData)


	# #Assing the assumed states
	# states = np.repeat([0,1], 10000)

	# X_train, X_test, y_train, y_test = cross_validation.train_test_split(reducedData, states, test_size=0.2, random_state=0)

	# # searchParams = {'gamma':(1.0/100)*np.logspace(-3, 0, 10), 'nu':np.arange(0.01, 0.2, 0.02)}
	# # clf = grid_search.GridSearchCV(svm.NuSVC(cache_size=2000), searchParams, n_jobs=2)
	# searchParams = {'C':np.linspace(0.1,4,20)}
	# clf = grid_search.GridSearchCV(svm.SVC(cache_size=2000), searchParams)
	# # clf = svm.SVC()

	# clf.fit(X_train, y_train)

	# print clf.score(X_test, y_test)

	# gridScores =  np.reshape([x[1] for x in clf.grid_scores_], (clf.param_grid['nu'].size, clf.param_grid['gamma'].size))

	# x_min, x_max = reducedData[:, 0].min() - 0.1, reducedData[:, 0].max() + 0.1
	# y_min, y_max = reducedData[:, 1].min() - 0.1, reducedData[:, 1].max() + 0.1

	# xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.005), np.arange(y_min, y_max, 0.005))
	# Z = clf.predict(np.c_[xx.ravel(), yy.ravel(), np.zeros(xx.size), np.zeros(xx.size)])
	# Z = Z.reshape(xx.shape)
	# plt.contourf(xx, yy, Z, cmap=plt.cm.Paired)
	# plt.scatter(reducedData[:10000,0], reducedData[:10000,1], s=1, c='b', edgecolors='none')
	# plt.scatter(reducedData[10000:,0], reducedData[10000:,1], s=1, c='r', edgecolors='none')
	# plt.xlim((x_min, x_max))
	# plt.ylim((y_min, y_max))
	# plt.xlabel('Principal Component 1', fontsize=16)
	# plt.ylabel('Principal Component 2', fontsize=16)
	# plt.show()


