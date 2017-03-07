import vrep
import time
import sys
import numpy as np
import signal

from class_Manta import Manta
from NeuralNet import DNN

time_step = 0.5
sim_time = 20
steps = int(sim_time/time_step)

nb_sims = 5 # number of simulations were data is recolected before retraining the DNN

nb_dnn_retrains = 10 # number of set of simulations, i.e. number of time the DNN is going to be retrained




def signal_handler(signal, frame):
	print('You pressed ctrl C. Stopping the simulation...')
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
	return v/luzera


def choose_action(dnn_out):
	# dnn_out es un np.array, que represneta dos distribuciones de probabilidad
	p_turn = dnn_out[0:7] # coger las probabilidades que tienen que ver con la direccion
	p_accel = dnn_out[7:14] # coger las probabilidades que tienen que ver con la accel/break

	turn_ind = np.random.choice(7,1,p=p_turn/np.sum(p_turn))
	accel_ind = np.random.choice(7,1,p=p_accel/np.sum(p_accel))

	turn_act = [0]*7
	accel_act = [0]*7

	turn_act[turn_ind] = 1
	accel_act[accel_ind] = 1

	return turn_act, accel_act

dnn = DNN()
clientID=vrep.simxStart('127.0.0.1',19999,True,True,5000,5)



for retrain in range(nb_dnn_retrains): # until convergence in reward, o otro criterio de parada
	
	for sim in range(nb_sims):


		
		return_code = vrep.simxStartSimulation(clientID,vrep.simx_opmode_oneshot)
		manta = Manta(clientID)
		sensors = manta.getSensors()


		history_sensors = []
		history_actions = []

		for step in range(steps):

			sensors = manta.getSensors()
			print(type(sensors))
			
			dnn_out = dnn.evaluar(sensors) # get probability of each action

			action = choose_action(dnn_out) # randomly choose with the previously gotten probabilities
			print(action)

			history_sensors.append(sensors)
			history_actions.append(action)

			manta.act(*action)

			time.sleep(time_step) # asegurarse de que es correcto hacer esto, de que no estamos peridendo
								  # la mayoria del tiempo en computar la DNN y historias

		reward = reward_simple(history_sensors)

		## new_training_labels = getLabels(history, reward)

		## save(new_training_labels)
			
		# finish the current simulation
		return_code = vrep.simxStopSimulation(clientID,vrep.simx_opmode_oneshot)
		time.sleep(1)
		print("simulation", sim, "out of", nb_sims, "finished.")
		#vrep.simxFinish(clientID)


	## retrain_DNN(training_labels)
	print("ahora deberia de estar parado")
	time.sleep(5)
	print("Ya no")




# def getLabels(history,reward,a,b,c,d):
# 	labels = [] [sensors,]



# 	return labels






# def reward_curvatura(history):
# 	luzera = len(history)
# 	v = 0
# 	for i in range(luzera):
# 		v += history[i][0]["velocity"]
	

# 	## computar parte de la curvatura

# 	return(f(v/luzera, zailtasuna))













