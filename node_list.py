from node import Node
import constants
import datetime

class Node_List:
	def __init__(self, velocity_i, start_percent, total_duration, total_perecent, time_of_day, location):
		self.velocity_i = velocity_i
		self.start_percent = start_percent
		self.time_of_day = time_of_day
		self.location = location
		self.total_duration = total_duration
		self.total_percent = total_perecent
		self.generate_list()

	def generate_list(self):
		self.nodes = []
		self.nodes.append(Node(
			self.time_of_day,
			self.velocity_i,
			0,
			self.start_percent,
			self.location,
			self.total_duration,
			self.total_percent)
			)
		for i in range(constants.SECTIONS - 1):
			self.nodes.append(Node(
				self.time_of_day + datetime.timedelta(seconds=self.nodes[-1].section_time),
				self.nodes[-1].end_velocity,
				self.nodes[-1].end_position,
				self.nodes[-1].end_percentage,
				self.location,
				self.total_duration,
				self.total_percent)
			)

	def get_v_f(self):
		return self.nodes[-1].end_velocity

	def get_b_f(self):
		return self.nodes[-1].end_percentage

	def get_time(self):
		lap_time = 0
		for node in self.nodes:
			lap_time += node.section_time
		return lap_time

	def print_nodes(self):
		for node in self.nodes:
			print (f"Battery:           {node.start_percentage * constants.BATTERY_CAPACITY:.2f}, {node.end_percentage * constants.BATTERY_CAPACITY:.2f}")
			print (f"Power_Used:        {(1 - node.end_percentage / node.start_percentage) * constants.BATTERY_CAPACITY:.2f} W")
			print (f"Section_Time:      {node.section_time / 60:.2f} minutes")
			print (f"End_Velocity:      {node.end_velocity:.2f} m/s")
			print (f"Average_Velocity:  {node.average_velocity:.2f} m/s")
			print (f"Distance_Traveled: {node.end_position - node.start_position:.2f} m")

	def print_lap_stats(self):
		track_time = 0
		power_in   = 0
		power_out  = 0
		average_velocity = []
		for node in self.nodes:
			track_time += node.section_time / 60
			power_in   += node.section_power_in
			power_out  += node.section_power_out
			average_velocity.append(node.average_velocity)
		print ("===========================================")
		print (f"Total_Lap_Time:   {track_time:.2f} minutes")
		print (f"Start_Percentage: {self.nodes[0].start_percentage:.2%}")
		print (f"Average_Velocity: {sum(average_velocity) / len(average_velocity)}")
		print (f"End_Percentage:   {self.get_b_f():.2%}")
		print (f"Total_Power_In:   {power_in:.4f} kW")
		print (f"Total_Power_Out:  {power_out:.4f} kW")
		print ("===========================================")
