from astral.sun import elevation
import datetime
import math
import constants

# Every node is responsable for 5% of the track distance.
class Node:
	def __init__(self, sections, t, vi, pi, bi, location, section_duration, section_percent):
		self.track_section    = sections
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
		self.t = section_duration
		self.section_percent  = section_percent
		
		self.calc()
		self.next_node = None


	def calc(self):
		velocities = []
		accelerations = []
		times = []

		vi = self.start_velocity
		a = constants.MAX_ACCELERATION # ADJUST THIS TO ATTEMPT TO ACHIEVE DESIRED RATIO
		vf = vi
		# Given desired time used and percentage, I can calc desired velocity
		# desired_vf = vi + a * self.t
		# print (f"{desired_vf:.2f}, {self.t:.2f} sec")
		for i in range(math.ceil(constants.TRACK_LENGTH / self.track_section)):
			if (vf >= constants.MAX_VELOCITY):
				a = 0

			vf = math.sqrt(math.pow(vi, 2) + 2 * a * 1)
			velocities.append(vf)
			accelerations.append(a)
			times.append((2 * 1) / (vi + vf))

			vi = vf
		
		self.section_time = sum(times)

		self.end_position = constants.TRACK_LENGTH / self.track_section + self.start_position

		if len(velocities) != 0:
			self.average_velocity = sum(velocities) / len(velocities)
			self.end_velocity = velocities[-1]
		else:
			self.average_velocity = self.start_velocity
			self.end_velocity = self.start_velocity


		power_used = (self.power_in(times) - self.power_out(accelerations, velocities, times)) / constants.BATTERY_CAPACITY
		print (f"{self.power_in(times):.4f}, {power_used:.4f}, {sum(times):.2f}")

		self.end_percentage = (constants.BATTERY_CAPACITY * self.start_percentage +
			self.power_in(times) -
			(self.power_out(accelerations, velocities, times))
			) / constants.BATTERY_CAPACITY
		

		# if (self.section_time / self.t < 1 and self.section_percent / power_used > 1):
		# 	# THIS TELLS ME THAT BOTH TIME AND POWER CAN HANDLE MORE LAPS OR CAN GO FASTER
		# 	print ("MORE LAPS")
		# 	# print ("USED, ALLOTED")
		# 	# print (f"{self.section_time:.2f}, {self.t:.2f}")
		# 	# print (f"{power_used:.2%}, {self.section_percent:.2%}")

		# if (self.section_time / self.t > 1 or self.section_percent / power_used < 1):
		# 	# THIS TELLS ME THAT I CANNOT HANDLE THIS NUMBER OF LAPS OR NEEDS TO GO SLOWER
		# 	print ("LESS LAPS")
		# 	print ("USED, ALLOTED")
		# 	print (f"{self.section_time:.2f}, {self.t:.2f}")
		# 	print (f"{power_used:.2%}, {self.section_percent:.2%}")

	def power_in(self, times):
		# SUN CALCULATIONS OVER A GIVEN PERIOD OF TIME
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
		# GRAVITY
		gravity = 0
		# REGEN
		regen = 0

		# kW * hrs
		# print (f"POWER  IN: {power / 3600:.4f}")
		self.section_power_in = power_in / 3600
		return power_in / 3600

	def power_out(self, a, v, t):
		# USING SPEED DETERMINE POWER COST
		energy = 0
		for i in range(len(v)):
			drag_f = (0.0451) * math.pow(v[i] * 3.6, 2) * constants.FRONTAL_AREA * constants.COEFFICIENT_DRAG
			crr_f = constants.COEFFICIENT_ROLLING_RESISTANCE * (1 + (v[i] * 3.6) / 161) * constants.WEIGHT
			forces = a[i] * constants.MASS + drag_f + crr_f
			# W
			power = forces * v[i]
			# W * s
			energy = power * t[i]
			# PARASITIC LOSSES
			energy += constants.PARASITIC_FACTOR * 30 * t[i]

		# GRAVITY

		# W * hrs
		energy = energy / 3600
		# kW * hrs
		self.section_power_out = energy / 1000
		return (energy / 1000) / constants.MOTOR_EFFICIENCY
