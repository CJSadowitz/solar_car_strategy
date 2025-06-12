from node import Node
import constants
import datetime
import math

class Node_List:
	def __init__(self, start_percent, duration, time_of_day, location, sections):
		self.start_percent = start_percent
		self.time_of_day = time_of_day
		self.location = location
		self.head = self.generate_list(sections)

	def generate_list(self, sections):
		head = Node(sections, self.time_of_day, constants.MAX_ACCELERATION, 0, 0, self.start_percent, self.location)
		prev_node = head
		for i in range(sections - 1):
			acceleration = constants.MAX_ACCELERATION * 0.2
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

	def get_time(self):
		head = self.head
		lap_time = 0
		while head != None:
			lap_time += head.section_time
			head = head.next_node
		return lap_time

	def get_b_f(self):
		head = self.head
		used = 0
		while head != None:
			if (head.next_node == None):
				used = head.end_percentage
			head = head.next_node
		return used

	def print_nodes(self):
		head = self.head
		while head != None:
			print(f"""
Section_Time:      {head.section_time / 60:.2f} minutes
Battery:           {head.start_percentage * constants.BATTERY_CAPACITY:.2f}, {head.end_percentage * constants.BATTERY_CAPACITY:.2f}
Power_Used:        {(1 - head.end_percentage / head.start_percentage) * constants.BATTERY_CAPACITY:.2f} W
End_Velocity:      {head.end_velocity:.2f} m/s
Average_Velocity:  {head.average_velocity:.2f} m/s
Distance_Traveled: {head.end_position - head.start_position:.2f} m
            """)
			head = head.next_node

	def print_lap_stats(self):
		track_time = 0
		distance   = 0
		power_in   = 0
		power_out  = 0
		head = self.head
		final_percentage = 0
		while head != None:
			track_time += head.section_time / 60
			distance   += head.end_position - head.start_position
			power_in   += head.section_power_in
			power_out  += head.section_power_out
			if (head.next_node == None):
				final_percentage = head.end_percentage
			head = head.next_node
		print ("===========================================")
		print (f"Total_Lap_Time:   {track_time:.2f} minutes")
		print (f"Start_Percentage: {self.head.start_percentage:.2%}")
		print (f"End_Percentage:   {final_percentage:.2%}")
		print (f"Total_Distance:   {distance:.2f} m")
		print (f"Total_Power_In:   {power_in:.4f} kW")
		print (f"Total_Power_Out:  {power_out:.4f} kW")
		print ("===========================================")
