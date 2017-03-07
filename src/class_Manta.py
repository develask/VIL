import vrep
import numpy as np

class Manta():
	def __init__(self, clientID):
		self.clientID = clientID

		# inicializar todos los handlers

		_, self.steer_handle = vrep.simxGetObjectHandle(self.clientID, 'steer_joint', vrep.simx_opmode_oneshot_wait)
		# motor: se puede fijar tanto el par como la velocidad-> mismo actuador, dos actuaciones...
		_, self.motor_handle = vrep.simxGetObjectHandle(self.clientID, 'motor_joint', vrep.simx_opmode_oneshot_wait)
		# fuerza de freno
		_, self.fl_brake_handle = vrep.simxGetObjectHandle(self.clientID, 'fl_brake_joint', vrep.simx_opmode_oneshot_wait)
		_, self.fr_brake_handle = vrep.simxGetObjectHandle(self.clientID, 'fr_brake_joint', vrep.simx_opmode_oneshot_wait)
		_, self.bl_brake_handle = vrep.simxGetObjectHandle(self.clientID, 'bl_brake_joint', vrep.simx_opmode_oneshot_wait)
		_, self.br_brake_handle = vrep.simxGetObjectHandle(self.clientID, 'br_brake_joint', vrep.simx_opmode_oneshot_wait)
		#_, self.steer_pos = vrep.simxGetJointPosition(self.clientID,self.steer_handle,vrep.simx_opmode_oneshot_wait)

		#current angular velocity of back left wheel
		#_, self.bl_wheel_velocity = vrep.simxGetObjectFloatParameter(self.clientID, self.bl_brake_handle,2012,vrep.simx_opmode_oneshot_wait)
		#current angular velocity of back right wheel
		#_, self.br_wheel_velocity = vrep.simxGetObjectFloatParameter(self.clientID, self.br_brake_handle,2012,vrep.simx_opmode_oneshot_wait)



		# inicializar sensor de vision
		_, self.camhandle = vrep.simxGetObjectHandle(self.clientID, 'Vision_sensor', vrep.simx_opmode_oneshot_wait)
		#_, self.resolution, self.image = vrep.simxGetVisionSensorImage(self.clientID, self.camhandle, 0, vrep.simx_opmode_oneshot_wait)
		# img = np.array(image, dtype = np.uint8)
		# img.resize([resolution[0], resolution[1], 3]) # 2 dimensiones, RGB, 256 x 128


		self.max_steer_angle = 0.5235987
		
		self.min_brake = 0
		self.max_brake = 100

		self.max_torque = 60
		self.min_torque =0

		self.max_velocity = 30
		self.min_velocity = 0


		
		# inicializar sensores de proximidad
		_, self.proximityhandle_vl = vrep.simxGetObjectHandle(self.clientID, 'Proximity_sensor_very_left', vrep.simx_opmode_oneshot_wait)
		_, self.proximityhandle_l = vrep.simxGetObjectHandle(self.clientID, 'Proximity_sensor_left', vrep.simx_opmode_oneshot_wait)
		_, self.proximityhandle_f = vrep.simxGetObjectHandle(self.clientID, 'Proximity_sensor_front', vrep.simx_opmode_oneshot_wait)
		_, self.proximityhandle_r = vrep.simxGetObjectHandle(self.clientID, 'Proximity_sensor_right', vrep.simx_opmode_oneshot_wait)
		_, self.proximityhandle_vr = vrep.simxGetObjectHandle(self.clientID, 'Proximity_sensor_very_right', vrep.simx_opmode_oneshot_wait)


	def getSensors(self):
		# leer angulo de la direccion
		_, self.steer_pos = vrep.simxGetJointPosition(self.clientID, self.steer_handle,vrep.simx_opmode_streaming)

		# leer velocidad del manta
		_, self.bl_wheel_velocity = vrep.simxGetObjectFloatParameter(self.clientID, self.bl_brake_handle,2012,vrep.simx_opmode_streaming)
		_, self.br_wheel_velocity = vrep.simxGetObjectFloatParameter(self.clientID, self.br_brake_handle,2012,vrep.simx_opmode_streaming)
		velocity = (self.bl_wheel_velocity+self.br_wheel_velocity)/2*0.09

		# leer los 5 sensores de proximidad
		_, state_vl, point_vl, handle_vl, normal_vl = vrep.simxReadProximitySensor(self.clientID, self.proximityhandle_vl, vrep.simx_opmode_streaming)
		_, state_l, point_l, handle_l, normal_l = vrep.simxReadProximitySensor(self.clientID, self.proximityhandle_l, vrep.simx_opmode_streaming)
		_, state_f, point_f, handle_f, normal_f = vrep.simxReadProximitySensor(self.clientID, self.proximityhandle_f, vrep.simx_opmode_streaming)
		_, state_r, point_r, handle_r, normal_r = vrep.simxReadProximitySensor(self.clientID, self.proximityhandle_r, vrep.simx_opmode_streaming)
		_, state_vr, point_vr, handle_vr, normal_vr = vrep.simxReadProximitySensor(self.clientID, self.proximityhandle_vr, vrep.simx_opmode_streaming)

		# leer sensor de vision

		#_, self.camhandle = vrep.simxGetObjectHandle(self.clientID, 'Vision_sensor', vrep.simx_opmode_oneshot_wait)
		_, self.resolution, self.image = vrep.simxGetVisionSensorImage(self.clientID, self.camhandle, 0, vrep.simx_opmode_oneshot_wait)
		img = np.array(self.image, dtype = np.uint8)
		img.resize([self.resolution[0], self.resolution[1], 3]) # 2 dimensiones, RGB, 256 x 128

		return { # queda pendiente normalizar (linealmente, entre 0 y 1) todos los sensores
			"steer_pos": self.norm(self.steer_pos, -self.max_steer_angle, self.max_steer_angle),
			"velocity": self.norm(velocity, self.min_velocity, self.max_velocity),

			"state_vl": 1 if state_vl else 0,
			"point_vl": point_vl[2]/5 if state_vl else 1,
			#"handle_vl": handle_vl,
			"normal_vl": normal_vl,

			"state_l": 1 if state_l else 0,
			"point_l": point_l[2]/5 if state_l else 1,
			#"handle_l": handle_l,
			"normal_l": normal_l,

			"state_f": 1 if state_f else 0,
			"point_f": point_f[2]/5 if state_f else 1,
			#"handle_f": handle_f,
			"normal_f": normal_f,

			"state_r": 1 if state_r else 0,
			"point_r": point_r[2]/5 if state_r else 1,
			#"handle_r": handle_r,
			"normal_r": normal_r,

			"state_vr": 1 if state_vr else 0,
			"point_vr": point_vr[2]/5 if state_vr else 1,
			#"handle_vr": handle_vr,
			"normal_vr": normal_vr,

			"camera": img/255
		}

	def act(self, turn_discr, accel_discr): # entradas discretas, que hay que pasar a salidas continuas y no normalizadas

		# turn_discr: string con estas posibilidades:  {"very_left", "left", "slight_left", "front", "slight_right", "right", "very_right"}
		# accel_discr: string con estas posibilidades:  {"hard_break", "medium_break", "slight_break", "inertia", "slight_accel", "medium_accel", "full_gas"}

		turn_dict = {
			"very_left": 0, 
			"left": 0.2,
			"slight_left": 0.35,
			"front": 0.5,
			"slight_right": 0.65,
			"right": 0.8,
			"very_right": 1
		}

		steer_denorm = self.denorm(turn_dict[turn_discr],-self.max_steer_angle,self.max_steer_angle)

		vrep.simxSetJointTargetPosition(self.clientID, self.steer_handle, steer_denorm, vrep.simx_opmode_streaming)

		if accel_discr == "hard_break":
			brake_force = 1
			motor_torque = 0
			motor_velocity = 0

		accel_dict = { # (brake_force,motor_torque,motor_velocity)
			"hard_break": 	(1,		0,		0),
			"medium_break": (0.5,	0,		0),
			"slight_break": (0.25,	0,		0),
			"inertia": 		(0,		0,		0),
			"slight_accel": (0,		1,		0.25),
			"medium_accel": (0,		1,		0.5),
			"full_gas": 	(0,		1,		1)
		}

		brake_force_norm, motor_torque_norm, motor_velocity_norm = accel_dict[accel_discr]
		brake_force = self.denorm(brake_force_norm, self.min_brake, self.max_brake)
		motor_torque = self.denorm(motor_torque_norm, self.min_torque, self.max_torque)
		motor_velocity = self.denorm(motor_velocity_norm, self.min_velocity, self.max_velocity)


		vrep.simxSetJointForce(self.clientID, self.motor_handle, motor_torque, vrep.simx_opmode_streaming)
		vrep.simxSetJointTargetVelocity(self.clientID, self.motor_handle, motor_velocity, vrep.simx_opmode_streaming)

		vrep.simxSetJointForce(self.clientID, self.fr_brake_handle, brake_force, vrep.simx_opmode_streaming)
		vrep.simxSetJointForce(self.clientID, self.fl_brake_handle, brake_force, vrep.simx_opmode_streaming)
		vrep.simxSetJointForce(self.clientID, self.bl_brake_handle, brake_force, vrep.simx_opmode_streaming)
		vrep.simxSetJointForce(self.clientID, self.br_brake_handle, brake_force, vrep.simx_opmode_streaming)


	def denorm(self, magnitude, minim, maxim):
		return (maxim-minim)*magnitude+minim

	def norm(self,magnitude, minim, maxim):
		return (magnitude-minim)/(maxim-minim)