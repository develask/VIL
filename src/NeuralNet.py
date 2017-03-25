import numpy as np

from keras.optimizers import SGD

from keras import backend as K

import DNN3 as dnn

import time
import os



class DNN():
	def __init__(self, img_dim = (128, 64, 3), other_parameters = 27, nb_classes = 14, model = None):
		self.batch_size = 8
		self.nb_epoch = 5

		self.model = dnn.getModel(img_dim = img_dim, other_parameters = other_parameters, nb_classes = nb_classes, model = model)

		sgd = SGD(lr=0.04, decay=0, momentum=0.2, nesterov=False)

		self.model.compile(loss='mse',
		              optimizer=sgd,
		              metrics=['accuracy'])

	def entrenar(self,x_and_y):
		x = x_and_y[0]
		y = x_and_y[1]
		x1 = []
		x2 = []
		for ej in x:
			x1.append(ej[0])
			x2.append(ej[1])

		dnn.entrenar(self.model, x1, x2, y, self.batch_size, self.nb_epoch)
		#self.model.fit([np.asarray(), np.asarray(x2)], np.asarray(y), batch_size=self.batch_size, nb_epoch=self.nb_epoch, verbose=0)

	def evaluar(self,numpy_array):
		return dnn.predecir(self.model, [numpy_array[0]], [numpy_array[1]])[0]

	def save(self):
		dnn.save(self.model)




		
		