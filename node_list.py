from node import Node
import constants
import datetime

class Node_List:
	def __init__(self, target_v, velocity_i, start_percent, time_of_day, location, elevation_list):
		self.velocity_i = velocity_i
		self.start_percent = start_percent
		self.time_of_day = time_of_day
		self.location = location
		self.target_v = target_v
		self.e_list = elevation_list
		self.generate_list()

	def generate_list(self):
		nodes = []
		nodes.append(
			Node(
			self.target_v,
			self.time_of_day,
			self.velocity_i,
			0,
			self.start_percent,
			self.location,
			self.e_list
			)
		)
		for i in range(int((constants.TRACK_LENGTH - 1) / constants.TRACK_SECTION_LENGTH)):
			new_node = Node(
				nodes[-1].target_v,
				self.time_of_day + datetime.timedelta(seconds=nodes[-1].section_time),
				nodes[-1].end_velocity,
				nodes[-1].end_position,
				nodes[-1].end_percentage,
				self.location,
				self.e_list
			)
			nodes.append(new_node)
		self.nodes = nodes

	def get_battery_used(self):
		total_battery_used = 0
		for node in self.nodes:
			total_battery_used += (node.start_percentage - node.end_percentage)
		return total_battery_used

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
		i = 1
		for node in self.nodes:
			print(f"""
			===========================================
			Iteration:         {i}
			Battery:          {node.start_percentage * constants.BATTERY_CAPACITY:.2f}, {node.end_percentage * constants.BATTERY_CAPACITY:.2f}
			Power_Used:       {self.get_battery_used() * 1000:.2f} W * hrs
			Gravity_Power:    {node.gravity_power:.4f} W * hrs
			Section_Time:     {node.section_time:.2f} seconds
			Start_Velocity:   {node.start_velocity:.2f} m/s {node.start_velocity * 2.237:.2f} mph
			End_Velocity:     {node.end_velocity:.2f} m/s {node.end_velocity * 2.237:.2f} mph
			Average_Velocity: {node.average_velocity:.2f} m/s
			Distance_Traveled:{node.end_position - node.start_position:.2f} m
			===========================================
			""")
			i += 1

	def print_lap_stats(self):
		track_time = 0
		power_in   = 0
		power_out  = 0
		average_velocity = []
		for node in self.nodes:
			track_time += node.section_time / 60
			power_in   += node.section_power_in
			power_out  += node.section_power_out
			average_velocity.append(node.end_velocity)
		average_velocity = sum(average_velocity) / len(average_velocity)
		print(f"""
		===========================================
		Total_Lap_Time:   {track_time:.2f} minutes
		Start_Percentage: {self.nodes[0].start_percentage:.2%}
		Average_Velocity: {average_velocity:.2f} m/s {average_velocity * 2.237:.2f} mph
		End_Percentage:   {self.get_b_f():.2%}
		Total_Power_In:   {power_in:.4f} kW * hrs
		Total_Power_Out:  {power_out:.4f} kW * hrs
		===========================================
		""")

