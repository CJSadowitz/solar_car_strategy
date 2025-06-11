from astral.sun import elevation
import datetime
import math

# Definitions
MAX_ACCELERATION =  0.2 # m/s^2
MIN_ACCELERATION = -0.2 # m/s^2
MAX_VELOCITY = 10.6 # m/s 9.1
BATTERY_CAPACITY = 5.1  # kW * hrs
MAX_PANEL_POWER  = 0.976  # kW
COEFFICIENT_DRAG = 0.22
COEFFICIENT_ROLLING_RESISTANCE = 0.0055
MASS = 320 # kg
GRAVITY = 9.81 # m/s^2
WEIGHT = MASS * GRAVITY
FRONTAL_AREA = 1.2 # m^2
TRACK_LENGTH = 5069.434 # m
PARASITIC_FACTOR = 1.0 # %

class Node_Tree:
	def __init__(self, start_percent, end_percent, duration, time_of_day, location):
		self.start_percent = start_percent
		self.end_percent = end_percent
		self.duration = duration
		self.time_of_day = time_of_day
		self.location = location

		head = self.generate_tree(100)
		self.print_nodes(head)
		self.print_track_stats(head)

	def generate_tree(self, sections):
		head = Node(sections, self.time_of_day, MAX_ACCELERATION, 0, 0, self.start_percent, self.location)
		prev_node = head
		for i in range(sections - 1):
			acceleration = MAX_ACCELERATION * 0.2
			cur = Node(
				sections,
				self.time_of_day + datetime.timedelta(seconds=prev_node.section_time),
				acceleration,
				prev_node.end_velocity,
				prev_node.end_position,
				prev_node.end_percentage,
				self.location)
			prev_node.next_node = cur
			prev_node = cur
		return head

	def print_nodes(self, head):
		while head != None:
			print(f"""
Section_Time:      {head.section_time / 60:.2f} minutes
Battery:           {head.start_percentage * BATTERY_CAPACITY:.2f}, {head.end_percentage * BATTERY_CAPACITY:.2f}
Power_Used:        {1 - head.end_percentage / head.start_percentage:.2%}
End_Velocity:      {head.end_velocity:.2f} m/s
Average_Velocity:  {head.average_velocity:.2f} m/s
Distance_Traveled: {head.end_position - head.start_position:.2f} m
			""")
			head = head.next_node

	def print_track_stats(self, head):
		track_time = 0
		power_used = 0
		distance   = 0
		while head != None:
			track_time += head.section_time / 60
			power_used += 1 - head.end_percentage / head.start_percentage
			distance   += head.end_position - head.start_position
			head = head.next_node
		print ("===========================================")
		print (f"Total_Lap_Time:   {track_time:.2f} minutes")
		print (f"Laps_Time:        {math.floor((self.duration / 60) / track_time):.2f}")
		print (f"Total_Power_Used: {power_used:.2%}")
		print (f"Laps_Power:       {math.floor((self.start_percent - self.end_percent) / power_used):.2f}")
		print (f"Total_Distance:   {distance:.2f} m")
		print ("===========================================")

# Every node is responsable for 5% of the track distance.
class Node:
	def __init__(self, sections, t, a, vi, pi, bi, location):
		self.track_section    = sections
		self.acceleration     = a  # m/s^2
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
		self.calc(bi)
		self.next_node = None

	def calc(self, start_p):
		velocities = []
		accelerations = []
		times = []

		vi = self.start_velocity
		a = self.acceleration
		vf = vi
		for i in range(math.ceil(TRACK_LENGTH / self.track_section)):
			if (vf >= MAX_VELOCITY):
				a = 0

			vf = math.sqrt(math.pow(vi, 2) + 2 * a * 1)
			velocities.append(vf)
			accelerations.append(a)
			times.append((2 * 1) / (vi + vf))

			vi = vf
		
		self.section_time = sum(times)

		self.end_position = TRACK_LENGTH / self.track_section + self.start_position

		if len(velocities) != 0:
			self.average_velocity = sum(velocities) / len(velocities)
			self.end_velocity = velocities[-1]
		else:
			self.average_velocity = self.start_velocity
			self.end_velocity = self.start_velocity

		self.end_percentage = (BATTERY_CAPACITY * start_p +
			self.power_in(times) -
			(self.power_out(accelerations, velocities, times))
			) / BATTERY_CAPACITY

	def power_in(self, times):
		# SUN CALCULATIONS OVER A GIVEN PERIOD OF TIME
		city = self.location
		time_now = self.time
		power_in = 0
		for t in times:
			solar_altitude = elevation(city.observer, time_now)
			time_now = time_now + datetime.timedelta(seconds=t)
			power = MAX_PANEL_POWER * math.cos(math.radians(solar_altitude))
			# kW * s
			power_in = power * t
			
		# GRAVITY
		gravity = 0
		# REGEN
		regen = 0

		# kW * hrs
		# print (f"POWER  IN: {power / 3600:.4f}")
		return power / 3600 

	# RETURNS Kw * hrs
	def power_out(self, a, v, t):
		# USING SPEED DETERMINE POWER COST
		power = 0
		for i in range(len(v)):
			drag_f = (0.0451) * math.pow(v[i] * 3.6, 2) * FRONTAL_AREA * COEFFICIENT_DRAG
			crr_f = COEFFICIENT_ROLLING_RESISTANCE * (1 + (v[i] * 3.6) / 161) * WEIGHT
			forces = a[i] * MASS + drag_f + crr_f
			# W * s
			power += forces * v[i] * t[i]
			# PARASITIC LOSSES

			power += PARASITIC_FACTOR * 30 * t[i]

		# GRAVITY


		# W * hrs
		power = power / 3600

		# kW * hrs
		# print (f"POWER OUT: {power / 1000:.4f}")
		return power / 1000
