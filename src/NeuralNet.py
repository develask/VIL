import numpy as np

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten, Merge
from keras.layers import Convolution2D, MaxPooling2D

from keras.models import load_model

from keras.optimizers import SGD

from keras import backend as K

import time
import os



class DNN():
	def __init__(self, img_dim = (128, 64, 3), other_parameters = 27, nb_classes = 14, model = None):
		self.batch_size = 128
		self.nb_classes = nb_classes
		self.nb_epoch = 12

		# size of pooling area for max pooling
		self.pool_size = (2, 2)
		# convolution kernel size
		self.kernel_size = (3, 3)

		input_shape = img_dim

		self.model = self.loadModel(model)
		if not self.model:
			print("Building new model...\n")
			image_net = Sequential()
			image_net.add(Convolution2D(4, self.kernel_size[0], self.kernel_size[1],
			                        border_mode='valid',
			                        input_shape=input_shape))
			print("Output shape of 1st convolution:", image_net.output_shape)
			image_net.add(Activation('relu'))
			image_net.add(MaxPooling2D(pool_size=self.pool_size))
			print("Output shape of 1st max-pooling:", image_net.output_shape)
			image_net.add(Convolution2D(5, self.kernel_size[0], self.kernel_size[1]))
			print("Output shape of 2nd convolution:", image_net.output_shape)
			image_net.add(Activation('relu'))
			image_net.add(MaxPooling2D(pool_size=self.pool_size))
			print("Output shape of 2nd max-pooling:", image_net.output_shape)
			image_net.add(Convolution2D(6, self.kernel_size[0], self.kernel_size[1]))
			print("Output shape of 3th convolution:", image_net.output_shape)
			image_net.add(Activation('relu'))
			image_net.add(MaxPooling2D(pool_size=self.pool_size))
			print("Output shape of 3th max-pooling:", image_net.output_shape)
			image_net.add(Convolution2D(7, self.kernel_size[0], self.kernel_size[1]))
			print("Output shape of 4th convolution:", image_net.output_shape)
			image_net.add(Activation('relu'))
			image_net.add(MaxPooling2D(pool_size=self.pool_size))
			print("Output shape of 4th max-pooling:", image_net.output_shape)
			image_net.add(Flatten())
			print("Output shape Total:", image_net.output_shape)

			sensors_net = Sequential()
			sensors_net.add(Dense(other_parameters, input_shape=(other_parameters,)))
			sensors_net.add(Dense(image_net.output_shape[1]))
			sensors_net.add(Activation('relu'))
			print("Output shape Total:", sensors_net.output_shape)

			self.model = Sequential()

			self.model.add(Merge([image_net, sensors_net], mode='concat'))
			print("Output shape merge:", self.model.output_shape)

			
			self.model.add(Dense(64))
			self.model.add(Activation('relu'))
			print("Output shape Dense:", self.model.output_shape)

			self.model.add(Dense(nb_classes))
			self.model.add(Activation('sigmoid'))
			print("Output shape Net:", self.model.output_shape)

		sgd = SGD(lr=0.01, decay=0, momentum=0.9, nesterov=False)

		self.model.compile(loss='mse',
		              optimizer=sgd,
		              metrics=['accuracy'])

	def entrenar(self,numpy_array):
		x = numpy_array[0,]
		y = numpy_array[1,]
		self.model.fit(X_train, Y_train, batch_size=self.batch_size, nb_epoch=self.nb_epoch, verbose=1)

	def evaluar(self,numpy_array):
		return self.model.predict([np.asarray([numpy_array[0]]), np.asarray([numpy_array[1]])])[0]

	def save(self):
		s = "../models/model_"+time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime())+".h5"
		self.model.save(s)
		print("Model saved:\n\t",s)

	def loadModel(self, path = None):
		try:
			if not path:
				path = "../models/"
				for root, dirs, files in os.walk("../models/", topdown=False):
					path += files[-1]
					break
			m = load_model(path)
			print("Model loaded:\n\t",path)
			return m
		except Exception as e:
			print(e)
			return None




		
		