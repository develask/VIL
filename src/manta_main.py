import vrep
import time
import sys
import numpy as np
import signal
from class_Manta import Manta

time_step = 0.5
sim_time = 3
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


clientID=vrep.simxStart('127.0.0.1',19999,True,True,5000,5)

for retrain in range(nb_dnn_retrains): # until convergence in reward, o otro criterio de parada
	
	for sim in range(nb_sims):


		
		return_code = vrep.simxStartSimulation(clientID,vrep.simx_opmode_oneshot)
		manta = Manta(clientID)
		sensors = manta.getSensors()


		history = []

		for step in range(steps):

			sensors = manta.getSensors()
			
			## dnn_out = DNN(sensors) # get probability of each action

			## action = choose_action(dnn_out) # randomly choose with the previously gotten probabilities

			#history.append((sensors, action))

			manta.act("front", "slight_accel")#manta.act(*action)

			time.sleep(time_step) # asegurarse de que es correcto hacer esto, de que no estamos peridendo
								  # la mayoria del tiempo en computar la DNN y historias

		## reward = setReward(history)

		## new_training_labels = getLabels(history, reward)

		## save(new_training_labels)
			
		# finish the current simulation
		return_code = vrep.simxStopSimulation(clientID,vrep.simx_opmode_oneshot)
		time.sleep(1)
		print("simulation", sim, "out of", nb_sims, "finished.")
		#vrep.simxFinish(clientID)


	## retrain_DNN(training_labels)
	print("ahora deberia de estar paradao")
	time.sleep(5)
	print("Ya no")














