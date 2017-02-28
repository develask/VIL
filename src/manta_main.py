import vrep
import time
import numpy as np


vrep.simxFinish(-1) #Terminar todas las conexiones
clientID=vrep.simxStart('127.0.0.1',19999,True,True,5000,5)

if clientID!=-1:
    print ('Conexion establecida')
 
else:
    sys.exit("Error: no se puede conectar")



#ACTUADORES

#importar

# direccion, ángulo de giro
_, steer_handle = vrep.simxGetObjectHandle(clientID, 'steer_joint', vrep.simx_opmode_oneshot_wait)
# motor: se puede fijar tanto el par como la velocidad-> mismo actuador, dos actuaciones...
_, motor_handle = vrep.simxGetObjectHandle(clientID, 'motor_joint', vrep.simx_opmode_oneshot_wait)
# fuerza de freno
_, fl_brake_handle = vrep.simxGetObjectHandle(clientID, 'fl_brake_joint', vrep.simx_opmode_oneshot_wait)
_, fr_brake_handle = vrep.simxGetObjectHandle(clientID, 'fr_brake_joint', vrep.simx_opmode_oneshot_wait)
_, bl_brake_handle = vrep.simxGetObjectHandle(clientID, 'bl_brake_joint', vrep.simx_opmode_oneshot_wait)
_, br_brake_handle = vrep.simxGetObjectHandle(clientID, 'br_brake_joint', vrep.simx_opmode_oneshot_wait)

#wheel radius:         0.09
#wheel base:             0.6
#wheel track:             0.35
#maximum steering rate:     70 deg/sec

#the maximum steer angle 30 degree
steer_angle = 0
max_steer_angle=0.5235987
#the maximum torque of the motor
motor_torque=60

motor_velocity = 30


brake_force = 0 # >= 0
#### if brake_force> 0 => motor_torque = 0 !!!


#SENSORES:

#importar
#propios del manta
#current steer pos
_, steer_pos=vrep.simxGetJointPosition(clientID,steer_handle,vrep.simx_opmode_oneshot_wait);
#current angular velocity of back left wheel
_, bl_wheel_velocity=vrep.simxGetObjectFloatParameter(clientID, bl_brake_handle,2012,vrep.simx_opmode_oneshot_wait)
#current angular velocity of back right wheel
_, br_wheel_velocity=vrep.simxGetObjectFloatParameter(clientID, br_brake_handle,2012,vrep.simx_opmode_oneshot_wait)
#average angular velocity of the back wheels
rear_wheel_velocity=(bl_wheel_velocity+br_wheel_velocity)/2
#linear velocity
linear_velocity=rear_wheel_velocity*0.09 # el radio es 0.09


# sensor de visión
_, camhandle = vrep.simxGetObjectHandle(clientID, 'Vision_sensor', vrep.simx_opmode_oneshot_wait)
_, resolution, image = vrep.simxGetVisionSensorImage(clientID, camhandle, 0, vrep.simx_opmode_oneshot_wait)
img = np.array(image, dtype = np.uint8)
img.resize([resolution[0], resolution[1], 3]) # 2 dimensiones, RGB, 256 x 128


# sensor de proximidad en disco
_, proximityhandle = vrep.simxGetObjectHandle(clientID, 'Proximity_sensor0', vrep.simx_opmode_oneshot_wait)
_, state, point, handle, vector = vrep.simxReadProximitySensor(clientID, proximityhandle, vrep.simx_opmode_oneshot_wait)





# LÓGICA

print(linear_velocity)

vrep.simxSetJointTargetPosition(clientID, steer_handle, steer_angle, vrep.simx_opmode_streaming)

vrep.simxSetJointForce(clientID, motor_handle, motor_torque, vrep.simx_opmode_streaming)
vrep.simxSetJointTargetVelocity(clientID, motor_handle, motor_velocity, vrep.simx_opmode_streaming)

vrep.simxSetJointForce(clientID, fr_brake_handle, brake_force, vrep.simx_opmode_streaming)
vrep.simxSetJointForce(clientID, fl_brake_handle, brake_force, vrep.simx_opmode_streaming)
vrep.simxSetJointForce(clientID, bl_brake_handle, brake_force, vrep.simx_opmode_streaming)
vrep.simxSetJointForce(clientID, br_brake_handle, brake_force, vrep.simx_opmode_streaming)

while True:
	time.sleep(0.5)
	#read sensors
	_, steer_pos=vrep.simxGetJointPosition(clientID,steer_handle,vrep.simx_opmode_oneshot_wait);
	#current angular velocity of back left wheel
	_, bl_wheel_velocity=vrep.simxGetObjectFloatParameter(clientID, bl_brake_handle,2012,vrep.simx_opmode_oneshot_wait)
	#current angular velocity of back right wheel
	_, br_wheel_velocity=vrep.simxGetObjectFloatParameter(clientID, br_brake_handle,2012,vrep.simx_opmode_oneshot_wait)
	#average angular velocity of the back wheels
	rear_wheel_velocity=(bl_wheel_velocity+br_wheel_velocity)/2
	#linear velocity
	linear_velocity=rear_wheel_velocity*0.09 
	# print("linear_velocity", linear_velocity)
	# print("angulo_direccion", steer_pos)
	_, state, point, handle, vector = vrep.simxReadProximitySensor(clientID, proximityhandle, vrep.simx_opmode_streaming)
	print("state", state)
	print("point", point)
	print("vector", vector)
	if state==True and abs(vector[2])>0.4: # hay algo, más o menos delante, y más o menos perpendicular
		if point[0] < 0: # hay algo a la izauierda

			steer_angle += 0.04 # gira a la derecha

		else: # hay algo a la derecha
			steer_angle -= 0.04 # gira a la izquierda
	else:
		if steer_angle < 0:
			steer_angle += 0.02
		elif steer_angle>0:
			steer_angle-= 0.02
			



	print("steer_angle", steer_angle)
	vrep.simxSetJointTargetPosition(clientID, steer_handle, steer_angle, vrep.simx_opmode_streaming)

	vrep.simxSetJointForce(clientID, motor_handle, motor_torque, vrep.simx_opmode_streaming)
	vrep.simxSetJointTargetVelocity(clientID, motor_handle, motor_velocity, vrep.simx_opmode_streaming)

	vrep.simxSetJointForce(clientID, fr_brake_handle, brake_force, vrep.simx_opmode_streaming)
	vrep.simxSetJointForce(clientID, fl_brake_handle, brake_force, vrep.simx_opmode_streaming)
	vrep.simxSetJointForce(clientID, bl_brake_handle, brake_force, vrep.simx_opmode_streaming)
	vrep.simxSetJointForce(clientID, br_brake_handle, brake_force, vrep.simx_opmode_streaming)






