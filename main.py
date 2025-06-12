from node_list import Node_List
from track import Track
from datetime import datetime
from astral import LocationInfo


def main():
	location = LocationInfo("Bowling Green", "USA", "America/Chicago", 36.97, -86.43)

	# July 3, 2025, 10:00 AM CT
	start_time = datetime(2025, 7, 3, 10, 0)
	battery_initial = 1.00
	battery_final   = 0.66
	day_1 = Track(location, start_time, 4, battery_initial, battery_final, 28800)
	day_1.get_day_info()
	print (day_1.get_laps(), "laps")

	# July 3, 2025, 10:00 AM CT
	start_time = datetime(2025, 7, 4, 10, 0)
	battery_initial = day_1.get_battery_final()
	battery_final   = 0.33
	day_2 = Track(location, start_time, 4, battery_initial, battery_final, 28800)
	day_2.get_day_info()
	print (day_2.get_laps(), "laps")

	 # July 3, 2025, 10:00 AM CT
	start_time = datetime(2025, 7, 5, 10, 0)
	battery_initial = day_2.get_battery_final()
	battery_final   = 0.00
	day_3 = Track(location, start_time, 4, battery_initial, battery_final, 28800)
	day_3.get_day_info()
	print (day_3.get_laps(), "laps")

if __name__ == "__main__":
	main()
