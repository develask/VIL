import numpy as np

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten, Merge
from keras.layers import Convolution2D, MaxPooling2D

from keras.models import load_model

from keras.optimizers import SGD

from keras import backend as K

import glob

import time

nombre_modelo = "model_DNN1"

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
		image_net = Sequential()
		image_net.add(Convolution2D(4, kernel_size[0], kernel_size[1],
		                        border_mode='valid',
		                        input_shape=input_shape))
		print("Output shape of 1st convolution:", image_net.output_shape)
		image_net.add(Activation('relu'))
		image_net.add(MaxPooling2D(pool_size=pool_size))
		print("Output shape of 1st max-pooling:", image_net.output_shape)
		image_net.add(Convolution2D(5, kernel_size[0], kernel_size[1]))
		print("Output shape of 2nd convolution:", image_net.output_shape)
		image_net.add(Activation('relu'))
		image_net.add(MaxPooling2D(pool_size=pool_size))
		print("Output shape of 2nd max-pooling:", image_net.output_shape)
		image_net.add(Convolution2D(6, kernel_size[0], kernel_size[1]))
		print("Output shape of 3th convolution:", image_net.output_shape)
		image_net.add(Activation('relu'))
		image_net.add(MaxPooling2D(pool_size=pool_size))
		print("Output shape of 3th max-pooling:", image_net.output_shape)
		image_net.add(Convolution2D(7, kernel_size[0], kernel_size[1]))
		print("Output shape of 4th convolution:", image_net.output_shape)
		image_net.add(Activation('relu'))
		image_net.add(MaxPooling2D(pool_size=pool_size))
		print("Output shape of 4th max-pooling:", image_net.output_shape)
		image_net.add(Flatten())
		print("Output shape Total:", image_net.output_shape)

		sensors_net = Sequential()
		sensors_net.add(Dense(other_parameters, input_shape=(other_parameters,)))
		sensors_net.add(Dense(image_net.output_shape[1]))
		sensors_net.add(Activation('relu'))
		print("Output shape Total:", sensors_net.output_shape)

		model = Sequential()

		model.add(Merge([image_net, sensors_net], mode='concat'))
		print("Output shape merge:", model.output_shape)

		
		model.add(Dense(64))
		model.add(Activation('relu'))
		print("Output shape Dense:", model.output_shape)

		model.add(Dense(nb_classes))
		model.add(Activation('sigmoid'))
		print("Output shape Net:", model.output_shape)

	return model

def entrenar(model, imagen, sensores, acciones, batch_size, nb_epoch):
	model.fit([np.asarray(imagen), np.asarray(sensores)], np.asarray(acciones), batch_size=batch_size, nb_epoch=nb_epoch, verbose=0)

def predecir(model, imagen, sensores):
	return model.predict([np.asarray(imagen), np.asarray(sensores)])

def save(model):
	s = "../models/"+nombre_modelo+time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime())+".h5"
	model.save(s)
	print("Model saved:\n\t",s)
