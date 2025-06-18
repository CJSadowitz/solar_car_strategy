from astral.sun import elevation
import datetime
import math
import constants
import numpy as np

# Every node is responsable for 5% of the track distance.
class Node:
	def __init__(self, target_v, t, vi, pi, bi, location, section_duration, section_percent, elevation_list):
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
		
		self.e_list = elevation_list

		self.calc()

	def calc(self):
		vi = self.start_velocity
		a = constants.MAX_ACCELERATION
		vf = vi
		pos = self.start_position

		x = 1
		# Iterate through each meter of the designated section
		a = self.calculate_acceleration(vf, vi, x)
		vf = math.sqrt(vi * vi + 2 * a * x)
		t = ((2 * x) / (vi + vf))
		pos += x
		vi = vf

		sum_work = self.calculate_work(vf, vi, pos, x)

		self.gravity_power  = self.gravity_work * t

		# W * s
		total_energy = np.sum((sum_work / t + constants.PARASITIC_FACTOR * 30) * t)
		self.calculate_energy(total_energy, t)

		self.end_velocity = vf
		self.end_position = pos
		self.section_time = t
	
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

	def calculate_work(self, vf, vi, pos, x):
		# Convert inputs to numpy arrays
		elv = self.e_list

		# Change in gravity (vectorized)
		p_f = (pos - 1 + x) % constants.TRACK_LENGTH
		p_i = pos - 1
		gravity_work = constants.MASS * constants.GRAVITY * (
			elv[p_f] - elv[p_i]
		)

		self.gravity_work = np.sum(gravity_work)

		delta_work = (0.5 * constants.MASS * vf * vf) - (0.5 * constants.MASS * vi * vi)

		sum_work = delta_work + (crr_force(vf) + drag_force(vf)) * x + gravity_work

		return sum_work

	def calculate_acceleration(self, vf, vi, x):
		if (vf >= constants.MAX_VELOCITY):
			return 0
		else:
			a = (self.target_v ** 2 - vi ** 2) / (2 * x)
			if (a <= constants.MIN_ACCELERATION):
				a = constants.MIN_ACCELERATION
			elif (a >= constants.MAX_ACCELERATION):
				a = constants.MAX_ACCELERATION
		return a

	def power_in(self, t):
		# Adjust this for different efficiency values
		city = self.location
		time_now = self.time
		
		solar_altitude = elevation(city.observer, time_now)
		time_now = time_now + datetime.timedelta(seconds=t)
		# kW
		power = constants.MAX_PANEL_POWER * math.cos(math.radians(solar_altitude))
		# kW * s
		power_in = power * t

		# kW * hrs
		self.section_power_in = power_in / 3600
		return power_in / 3600

def crr_force(v):
	return constants.COEFFICIENT_ROLLING_RESISTANCE * (1 + (v * 3.6) / 161) * constants.WEIGHT

def drag_force(v):
	return (0.0451) * ((v * 3.6) ** 2) * constants.FRONTAL_AREA * constants.COEFFICIENT_DRAG
