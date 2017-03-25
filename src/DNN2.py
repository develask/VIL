import numpy as np

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten, Merge
from keras.layers import Convolution2D, MaxPooling2D

from keras.models import load_model

from keras.optimizers import SGD

from keras import backend as K

import glob

import time

nombre_modelo = "model_DNN2"

def loadModel(path):
	try:
		if not path:
			path = "../models/"
			files = glob.glob("../models/"+nombre_modelo+"*.h5")
			files = sorted(files)
			path = files[-1]
		m = load_model(path)
		print("Model loaded:\n\t",path)
		return m
	except Exception as e:
		print(e)
		return None


def getModel(img_dim = (128, 64, 3), other_parameters = 27, nb_classes = 14, model = None):

	# size of pooling area for max pooling
	pool_size = (2, 2)
	# convolution kernel size
	kernel_size = (3, 3)

	input_shape = img_dim

	model = loadModel(model)

	if not model:
		print("Building new model...\n")

		model = Sequential()
		model.add(Dense(other_parameters, input_shape=(other_parameters,)))
		model.add(Dense(30))
		model.add(Activation('relu'))
		print("Output shape Total:", model.output_shape)
		
		model.add(Dense(30))
		model.add(Activation('relu'))
		print("Output shape Dense:", model.output_shape)

		model.add(Dense(nb_classes))
		model.add(Activation('sigmoid'))
		print("Output shape Net:", model.output_shape)

	return model

def entrenar(model, imagen, sensores, acciones, batch_size, nb_epoch):
	model.fit(np.asarray(sensores), np.asarray(acciones), batch_size=batch_size, nb_epoch=nb_epoch, verbose=0)

def predecir(model, imagen, sensores):
	return model.predict(np.asarray(sensores))

def save(model):
	s = "../models/"+nombre_modelo+time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime())+".h5"
	model.save(s)
	print("Model saved:\n\t",s)
