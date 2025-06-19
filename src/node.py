from astral.sun import elevation
import math
import src.constants

# Every node is responsable for 5% of the track distance.
class Node:
	def __init__(self, target_v, t, vi, pi, bi, location, elevation_list):
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
		
		self.e_list = elevation_list

		self.calc()

	def calc(self):
		vi = self.start_velocity
		vf = vi
		pos = self.start_position

		x = src.constants.TRACK_SECTION_LENGTH
		# Iterate through each meter of the designated section
		a = self.calculate_acceleration(vf, vi, x)
		vf = math.sqrt(vi * vi + 2 * a * x)
		t = ((2 * x) / (vi + vf))
		pos += x
		vi = vf

		sum_work = self.calculate_work(vf, vi, pos, x)

		self.gravity_power  = self.gravity_work * t

		# W * s
		total_energy = (sum_work / t + src.constants.PARASITIC_FACTOR * 30) * t
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
		self.section_power_out = total_energy_out / src.constants.MOTOR_EFFICIENCY
		self.end_percentage =  (
			self.start_percentage * src.constants.BATTERY_CAPACITY - (total_energy_out / src.constants.MOTOR_EFFICIENCY) + self.power_in(times)
			) / src.constants.BATTERY_CAPACITY

	def calculate_work(self, vf, vi, pos, x):
		p_f = (pos - 1 + x) % src.constants.TRACK_LENGTH
		p_i = (pos - 1) % src.constants.TRACK_LENGTH
		gravity_work = src.constants.MASS * src.constants.GRAVITY * (
			self.e_list[p_f] - self.e_list[p_i]
		)

		self.gravity_work = gravity_work
		delta_work = (0.5 * src.constants.MASS * vf * vf) - (0.5 * src.constants.MASS * vi * vi)
		sum_work = delta_work + (crr_force(vf) + drag_force(vf)) * x + gravity_work

		return sum_work

	def calculate_acceleration(self, vf, vi, x):
		if vf >= src.constants.MAX_VELOCITY:
			return 0
		 
		a = (self.target_v ** 2 - vi ** 2) / (2 * x)

		return max(src.constants.MIN_ACCELERATION, min(a, src.constants.MAX_ACCELERATION))


	def power_in(self, t):
		solar_altitude = elevation(self.location.observer, self.time)
		# kW
		power = src.constants.MAX_PANEL_POWER * math.cos(math.radians(solar_altitude))
		# kW * s
		power_in = power * t

		# kW * hrs
		self.section_power_in = power_in / 3600
		return power_in / 3600

def crr_force(v):
	return src.constants.COEFFICIENT_ROLLING_RESISTANCE * (1 + (v * 3.6) / 161) * src.constants.WEIGHT

def drag_force(v):
	return (0.0451) * ((v * 3.6) * (v * 3.6)) * src.constants.FRONTAL_AREA * src.constants.COEFFICIENT_DRAG
