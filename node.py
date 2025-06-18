from astral.sun import elevation
from track_reader import get_elevation, get_track_edge
import datetime
import math
import constants
import numpy as np

# Every node is responsable for 5% of the track distance.
class Node:
	def __init__(self, target_v, t, vi, pi, bi, location, section_duration, section_percent):
		self.target_v = target_v
		self.start_velocity   = vi # m/s
		self.end_velocity     = 0  # m/s
		self.average_velocity = 0  # m/s
		self.start_position   = pi # m
		self.end_position     = pi # m
		self.section_time     = 0  # s
		self.start_percentage = bi
		self.end_percentage   = 0
		self.time = t             # DATE
		self.location = location  # OBJECT

		# How much time and percent each section can use
		self.t   = section_duration / constants.SECTIONS
		self.sp  = section_percent  / constants.SECTIONS
		
		self.elevation_dict = get_track_edge("side_l.csv")

		self.calc()

	def calc(self):
		vi = self.start_velocity
		a = constants.MAX_ACCELERATION
		vf = vi
		pos = self.start_position
		times = []
		vis = []
		vfs = []
		poss = []
		x = 1
		# Iterate through each meter of the designated section
		for i in range(math.ceil(constants.TRACK_LENGTH / constants.SECTIONS)):
			a = self.calculate_acceleration(vf, vi, x)
			vf = math.sqrt(vi * vi + 2 * a * x)
			t = ((2 * x) / (vi + vf))
			poss.append(pos)
			vis.append(vi)
			vfs.append(vf)
			times.append(t)
			pos += x
			vi = vf

		self.end_position = poss[-1]

		sum_work = self.calculate_work(vfs, vis, poss, x)
		t = np.array(times)
		# W * s
		total_energy = np.sum((sum_work / t + constants.PARASITIC_FACTOR * 30) * t)

		self.calculate_energy(total_energy, times)

		self.end_velocity = vf
		self.average_velocity = sum(vfs) / len(vfs)
		self.section_time = sum(times)
	
	def calculate_energy(self, total_energy, times):
		total_energy_out = total_energy
		# W * hrs
		total_energy_out = total_energy_out / 3600
		# kW * hrs
		total_energy_out = total_energy_out / 1000
		self.section_power_out = total_energy_out / constants.MOTOR_EFFICIENCY
		self.end_percentage =  (
			self.start_percentage * constants.BATTERY_CAPACITY - (total_energy_out / constants.MOTOR_EFFICIENCY) + self.power_in(times)
			) / constants.BATTERY_CAPACITY

	def calculate_work(self, vf_array, vi_array, pos_array, x):
		# Convert inputs to numpy arrays
		vf  = np.array(vf_array)
		vi  = np.array(vi_array)
		pos = np.array(pos_array)

		# Change in gravity (vectorized)
		gravity_work = constants.MASS * constants.GRAVITY * (
			np.array(list(map(lambda p: get_elevation(p / constants.TRACK_LENGTH, self.elevation_dict), (pos + x) / constants.TRACK_LENGTH))) -
			np.array(list(map(lambda p: get_elevation(p / constants.TRACK_LENGTH, self.elevation_dict), pos / constants.TRACK_LENGTH)))
		)

		self.gravity_power = gravity_work # FIX THIS LATER COLIN

		delta_work = (0.5 * constants.MASS * vf ** 2) - (0.5 * constants.MASS * vi ** 2)

		sum_work = delta_work + (crr_force(vf) + drag_force(vf)) * x + gravity_work

		return sum_work

	def calculate_acceleration(self, vf, vi, x):
		if (vf >= constants.MAX_VELOCITY):
			a = 0
		else:
			a = (self.target_v ** 2 - vi ** 2) / (2 * x)
			if (a <= constants.MIN_ACCELERATION):
				a = constants.MIN_ACCELERATION
			elif (a >= constants.MAX_ACCELERATION):
				a = constants.MAX_ACCELERATION
		return a

	def power_in(self, times):
		# Adjust this for different efficiency values
		city = self.location
		time_now = self.time
		power_in = 0
		for t in times:
			solar_altitude = elevation(city.observer, time_now)
			time_now = time_now + datetime.timedelta(seconds=t)
			# kW
			power = constants.MAX_PANEL_POWER * math.cos(math.radians(solar_altitude))
			# kW * s
			power_in += power * t

		# kW * hrs
		# print (f"POWER  IN: {power / 3600:.4f}")
		self.section_power_in = power_in / 3600
		return power_in / 3600

def crr_force(v):
	return constants.COEFFICIENT_ROLLING_RESISTANCE * (1 + (v * 3.6) / 161) * constants.WEIGHT

def drag_force(v):
	return (0.0451) * ((v * 3.6) ** 2) * constants.FRONTAL_AREA * constants.COEFFICIENT_DRAG
