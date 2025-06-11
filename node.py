from astral.sun import elevation
import datetime
import math

# Definitions
MAX_ACCELERATION =  0.2 # m/s^2
MIN_ACCELERATION = -0.2 # m/s^2
MAX_VELOCITY = 12 # m/s 9.1
BATTERY_CAPACITY = 971  # kW * hrs
MAX_PANEL_POWER  = 0.976  # kW
COEFFICIENT_DRAG = 0.22
COEFFICIENT_ROLLING_RESISTANCE = 0.0055
WEIGHT = 320 # kgs
GRAVITY = 9.8 # m/s^2
FRONTAL_AREA = 1.2 # m^2
TRACK_LENGTH = 5069.434 # m

class Node_Tree:
	def __init__(self, start_percent, end_percent, duration, time_of_day, location):
		self.start_percent = start_percent
		self.end_percent = end_percent
		self.duration = duration
		self.time_of_day = time_of_day
		self.location = location

		head = self.generate_tree()
		self.print_nodes(head)
		self.print_track_stats(head)

	# ADJUST THIS TO BEWARE OF GOING OVER TRACK DISTANCE LOOK AT TOTAL DISTANCE DRIVEN VS TRACK_LENGTH IMPLEMENT DISTANCE CLIPPING OR SOMETHING
	def generate_tree(self):
		total_position = 0
		head = Node(self.time_of_day, MAX_ACCELERATION, 0, 0, self.start_percent, self.location)
		total_position += head.end_position - head.start_position
		prev_node = head
		while total_position < TRACK_LENGTH:
			acceleration = MAX_ACCELERATION * 0.2
			cur = Node(
				self.time_of_day + datetime.timedelta(seconds=prev_node.section_time),
				acceleration,
				prev_node.end_velocity,
				prev_node.end_position,
				prev_node.end_percentage,
				self.location)
			total_position += cur.end_position - cur.start_position
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
		print (f"Total_Track_Time: {track_time:.2f} minutes")
		print (f"Laps_Time: {math.floor((self.duration / 60) / track_time):.2f}")
		print (f"Total_Power_Used: {power_used:.2%}")
		print (f"Laps_Power: {math.floor((self.start_percent - self.end_percent) / power_used):.2f}")
		print (f"Total_Distance:   {distance:.2f} m")

# Every node is responseable for 5% of the track distance.
class Node:
	def __init__(self, time, acceleration, start_v, start_d, start_p, location):
		self.acceleration     = acceleration # m/s^2
		self.start_velocity   = start_v      # m/s
		self.end_velocity     = 0            # m/s
		self.average_velocity = 0            # m/s
		self.start_position   = start_d      # m
		self.end_position     = start_d            # m
		self.section_time     = 0            # s
		self.start_percentage = start_p
		self.end_percentage   = None
		self.time = time # DATE
		self.location = location # OBJECT
		self.calc(start_p)
		self.next_node = None

	def calc(self, start_p):
		velocities = []
		accelerations = []

		velocity = self.start_velocity
		while self.end_position < TRACK_LENGTH * 0.05 + self.start_position:
			velocity = velocity + self.acceleration
			if (velocity > MAX_VELOCITY):
				velocities.append(MAX_VELOCITY)
				accelerations.append(0)
			else:
				velocities.append(velocity)
				accelerations.append(self.acceleration)
			self.section_time += 1
			self.end_position += velocities[-1]

		if len(velocities) != 0:
			self.average_velocity = sum(velocities) / len(velocities)
			self.end_velocity = velocities[-1]
		else:
			self.average_velocity = 0
			self.end_velocity = self.start_velocity

		self.end_percentage = (BATTERY_CAPACITY * start_p + self.power_in(self.section_time) - self.power_out(accelerations)) / BATTERY_CAPACITY

	def power_in(self, interval):
		# SUN CALCULATIONS OVER A GIVEN PERIOD OF TIME
		city = self.location
		time_now = self.time
		power = 0
		for i in range(math.ceil(interval)):
			solar_altitude = elevation(city.observer, time_now)
			power += MAX_PANEL_POWER * math.cos(math.radians(solar_altitude))
			time_now = time_now + datetime.timedelta(seconds=1)
		# GRAVITY
		gravity = 0
		# REGEN
		regen = 0
		return power / 3600 

	def power_out(self, accelerations):
		# USING SPEED DETERMINE POWER COST
		drag_f = (0.0) * math.pow(self.average_velocity, 2) * FRONTAL_AREA * COEFFICIENT_DRAG
		# ROLLING RESISTANCE
		crr_f = COEFFICIENT_ROLLING_RESISTANCE * (1 + self.average_velocity / 161) * WEIGHT # NEWTONS
		# GRAVITY

		# Power Calc
		forces = []
		for acceleration in accelerations:
			forces.append(acceleration * WEIGHT + (drag_f + crr_f))

		power = sum(forces) * self.average_velocity
		return power / 3600
