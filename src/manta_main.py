import vrep
import time
import sys
import numpy as np
import signal
import math

from class_Manta import Manta
from NeuralNet import DNN

time_step = 0.4
sim_time = 20
steps = int(sim_time/time_step)

nb_sims = 5 # number of simulations were data is recolected before retraining the DNN

nb_dnn_retrains = 500 # number of set of simulations, i.e. number of time the DNN is going to be retrained


dnn = DNN()
clientID=vrep.simxStart('127.0.0.1',19999,True,True,5000,5)

def signal_handler(signal, frame):
	print('You pressed ctrl C. Stopping the simulation...')
	dnn.save()
	return_code = vrep.simxStopSimulation(clientID,vrep.simx_opmode_oneshot)
	time.sleep(1)
	vrep.simxFinish(clientID)
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def firstConnection():
	vrep.simxFinish(-1) #Terminar todas las conexiones
	clientID=vrep.simxStart('127.0.0.1',19999,True,True,5000,5)
	if clientID!=-1:
		print ('Conexion establecida')
		return clientID
	else:
		sys.exit("Error: no se puede conectar")

def reward_simple(history):
	luzera = len(history)
	v = 0
	for i in range(luzera):
		v += history[i][1][1]
	return v/luzera if luzera > 0 else 0

def ruido(entrada, num, rango = 0.05):
	imagen = entrada[0]
	sensores = entrada[1]
	lista = [(imagen, sensores)]
	for i in range(num-1):
		a = np.random.rand(imagen.shape)
		im = np.copy(imagen)+(a*rango)-(rango/2)
		a = np.random.rand(sensores.shape)
		se = np.copy(sensores)+(a*rango)-(rango/2)
		lista.append((im,se))
	return lista


# def reward_penalizar_choque(history,crashed):
# 	luzera = len(history)
# 	v = 0
# 	for i in range(luzera):
# 		v += history[i][1][1]
# 	rew = v/luzera


# 	penalizacion = 0.25 if min(s_prox) < 0.07 else 1
# 	return rew * penalizacion


def choose_action(dnn_out):
	# dnn_out es un np.array, que represneta dos distribuciones de probabilidad
	p_turn = dnn_out[0:7] # coger las probabilidades que tienen que ver con la direccion
	p_accel = dnn_out[7:14] # coger las probabilidades que tienen que ver con la accel/break

	for i in range(len(p_turn)):
		p_turn[i] = math.e**p_turn[i]
	for i in range(len(p_accel)):
		p_accel[i] = math.e**p_accel[i]


	turn_ind = np.random.choice(7,1,p=p_turn/np.sum(p_turn))
	accel_ind = np.random.choice(7,1,p=p_accel/np.sum(p_accel))

	turn_act = [0]*7
	accel_act = [0]*7

	turn_act[turn_ind] = 1
	accel_act[accel_ind] = 1

	return turn_act, accel_act


def new_label(reward, accion, a=0.3, b=0.5, c=0.8, d=1.2):

	sigma_0 = 0.1
	sigma_a = 0.3
	sigma_b = 10

	idxPos = -1
	for index in range(0, 7):
		if accion[index] == 1:
			idxPos = index
			break
	
	v_probs = [0]*7
	
	# Define probabilties regarding range
	if reward <= a:
		#sigma = reward/b * (sigma_a - sigma_0)/b + sigma_0
		sigma = (reward - a)/ (b-a) * (sigma_b - sigma_a)/b + sigma_a
		for i in range(0, 7):
			v_probs[i] = math.exp(-(i - idxPos)**2 / (2 * sigma**2) )
		maximum = max(v_probs)
		for i in range(0, 7):
			v_probs[i] = maximum - v_probs[i]

	elif reward > a and reward <= b: 
		#sigma = (reward - a)/ (b-a) * (sigma_b - sigma_a)/b + sigma_a
		sigma = reward/b * (sigma_a - sigma_0)/b + sigma_0
		for i in range(0, 7):
			v_probs[i] = math.exp(-(i - idxPos)**2 / (2 * sigma**2) )
		maximum = max(v_probs)
		for i in range(0, 7):
			v_probs[i] = maximum - v_probs[i]

	elif reward > b and reward <= c:
		sigma = (reward-b)/ (c-b) * (sigma_a - sigma_b) + sigma_b
		for i in range(0, 7):
			v_probs[i] = math.exp(-(i - idxPos)**2 / (2 * sigma**2) )

	else:
		sigma = (reward-c) / (d-c) * (sigma_0 - sigma_a) + sigma_a
		for i in range(0, 7):
			v_probs[i] = math.exp(-(i - idxPos)**2 / (2 * sigma**2) )

	suma = sum(v_probs)
	
	# Normalise
	for i in range(0, 7):
			v_probs[i] = v_probs[i]/suma

	# print(reward)
	# print(sigma)
	return v_probs


def getLabels(history_sensors, history_actions, reward):
	## precariamente
	new_history_actions = []
	for action in history_actions:
		act1 = action[:7]
		act2 = action[7:]
		new_act1 = new_label(reward, act1)
		new_act2 = new_label(reward, act2)
		new_history_actions.append(new_act1+new_act2)

	return history_sensors, new_history_actions







manta = Manta(clientID)

for retrain in range(nb_dnn_retrains): # until convergence in reward, o otro criterio de parada

	x_training_labels = []
	y_training_labels = []
	
	for sim in range(nb_sims):

		manta.setRandomPosition()

		return_code = vrep.simxStartSimulation(clientID,vrep.simx_opmode_oneshot)
		
		sensors = manta.getSensors()


		history_sensors = []
		history_actions = []

		crashed = False
		for step in range(steps):

			try:
				sensors = manta.getSensors()
				
				print("SENSORS:",sensors[1])
				dnn_out = dnn.evaluar(sensors) # get probability of each action
				print("DNN_OUT",dnn_out)

				action = choose_action(dnn_out) # randomly choose with the previously gotten probabilities
				

				history_sensors.append(sensors)
				history_actions.append(action[0]+action[1])

				## si se choca -> acabar la simulacion
				if sensors[1][3] < 0.07 or sensors[1][8] < 0.07 or sensors[1][13] < 0.07 or sensors[1][18] < 0.07 or sensors[1][23] < 0.07:
					crashed = True
					break
					

				manta.act(*action)

				time.sleep(time_step) # asegurarse de que es correcto hacer esto, de que no estamos peridendo
									  # la mayoria del tiempo en computar la DNN y historias
			except Exception as e:
				print(e)
				pass
			

		
		
		if crashed == False:
			reward = reward_simple(history_sensors)
			print("REWARD (not crashed)", reward)
			if reward > 0: #siempre
				new_training_labels = getLabels(history_sensors, history_actions, reward)
				x_training_labels += new_training_labels[0]
				y_training_labels += new_training_labels[1]

		else:

			reward = reward_simple(history_sensors[:-int(2/time_step)])
			print("REWARD (not crashed part)", reward)
			if reward > 0: #siempre
				new_training_labels = getLabels(history_sensors[:-int(2/time_step)], history_actions[:-int(2/time_step)], reward)
				x_training_labels += new_training_labels[0]
				y_training_labels += new_training_labels[1]

			reward = reward_simple(history_sensors[-int(2/time_step):])/4
			print("REWARD (crashed part)", reward)
			if reward > 0.4: # never
				new_training_labels = getLabels(history_sensors[-int(2/time_step):], history_actions[-int(2/time_step):], reward)
				x_training_labels += new_training_labels[0]
				y_training_labels += new_training_labels[1]







		## save(new_training_labels)
			
		# finish the current simulation
		return_code = vrep.simxStopSimulation(clientID,vrep.simx_opmode_oneshot)
		time.sleep(1)
		print("simulation", sim, "out of", nb_sims, "finished.")
		#vrep.simxFinish(clientID)

	print("Vamos a reentrenar la red con", len(x_training_labels), "ejemplos nuevos...")
	dnn.entrenar((x_training_labels,y_training_labels))
	dnn.save()



















