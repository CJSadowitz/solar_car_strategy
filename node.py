from astral.sun import elevation
import datetime
import math
import constants

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
		self.t = section_duration / constants.SECTIONS
		self.section_percent  = section_percent / constants.SECTIONS
		
		self.calc()

	def calc(self):
		vi = self.start_velocity
		a = constants.MAX_ACCELERATION
		vf = vi
		total_energy = 0
		times = []
		velocities = []
		for i in range(math.ceil(constants.TRACK_LENGTH / constants.SECTIONS)):
			if (vf >= constants.MAX_VELOCITY):
				a = 0
			else:
				a = (self.target_v ** 2 - vi ** 2) / 2 * 1
				if (a <= constants.MIN_ACCELERATION):
					a = constants.MIN_ACCELERATION
			
			try:
				vf = math.sqrt(vi ** 2 + 2 * a * 1)
			except ValueError:
				print (f"A, How:\nB, {vi ** 2 + 2 * a * 1}, {vi}, {a}")

			velocities.append(vf)
			t = ((2 * 1) / (vi + vf))
			times.append(t)
			# N * m
			delta_work = (0.5 * constants.MASS * vf ** 2) - (0.5 * constants.MASS * vi ** 2)
			sum_work = delta_work + (crr_force(vf) + drag_force(vf)) * 1
			# W
			power = sum_work / t + constants.PARASITIC_FACTOR * 30
			# W * s
			total_energy += power * t
			vi = vf


		total_energy_out = total_energy
		# W * hrs
		total_energy_out = total_energy_out / 3600
		# kW * hrs
		total_energy_out = total_energy_out / 1000

		# print (f"Power out: {total_energy_out / constants.MOTOR_EFFICIENCY:.4f}, ", end="")
		# print (f"Power in:  {self.power_in(times):.4f}, {sum(times):.2f}")
		self.end_velocity = vf
		self.average_velocity = sum(velocities) / len(velocities)
		self.section_power_out = total_energy_out / constants.MOTOR_EFFICIENCY
		self.end_percentage =  (self.start_percentage * constants.BATTERY_CAPACITY - (total_energy_out / constants.MOTOR_EFFICIENCY) + self.power_in(times)) / constants.BATTERY_CAPACITY
		self.section_time = sum(times)

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
