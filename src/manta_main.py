import vrep
import time
import sys
import numpy as np
import signal
from class_Manta import Manta

time_step = 0.5
sim_time = 10
steps = int(sim_time/time_step)
nb_sims = 5

def signal_handler(signal, frame):
	print('you pressed ctrl c')
	return_code = vrep.simxStopSimulation(clientID,vrep.simx_opmode_oneshot)
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



#clientID = firstConnection()


for sim in range(nb_sims):
	clientID=vrep.simxStart('127.0.0.1',19999,True,True,5000,5)
	return_code = vrep.simxStartSimulation(clientID,vrep.simx_opmode_oneshot)
	manta = Manta(clientID)


	for i in range(steps):
		manta.act("front", "slight_accel")
		
		print("\n\nread sensors")
		sensors = manta.getSensors()
		for key in sensors:
			print(key, ":", sensors[key])
		time.sleep(time_step)


	return_code = vrep.simxStopSimulation(clientID,vrep.simx_opmode_oneshot)
	time.sleep(1)
	print("simulation", sim, "out of", nb_sims, "finished.")
	vrep.simxFinish(clientID)












