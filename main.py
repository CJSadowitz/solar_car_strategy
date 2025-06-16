from track import Track
from datetime import datetime
from astral import LocationInfo
from solar_charge import charge_off_hour
import constants

def main():
	location = LocationInfo("Bowling Green", "USA", "America/Chicago", 36.97, -86.43)

	laps = 0

	# July 3, 2025, 10:00 AM CT
	start_time = datetime(2025, 7, 3, 10, 0)
	battery_initial = 1.00
	battery_final   = 0.66
	day_1 = Track(location, start_time, 4, battery_initial, battery_final, 28800)
	day_1.get_day_info()
	laps += day_1.get_laps()
	print (day_1.get_laps(), "laps")

	# Add in battery power here
	# July 3, 2025, 6:00 PM CT
	start_time = datetime(2025, 7, 3, 18, 0)
	duration = 3600 # 1 hr
	battery_final += charge_off_hour(location, start_time, duration)

	# July 4, 2025, 10:00 AM CT
	start_time = datetime(2025, 7, 4, 9, 0)
	battery_final += charge_off_hour(location, start_time, duration)

	start_time = datetime(2025, 7, 4, 10, 0)
	battery_initial = battery_final
	battery_final   = 0.33
	day_2 = Track(location, start_time, constants.DRIVER_COUNT, battery_initial, battery_final, 28800)
	day_2.get_day_info()
	laps += day_2.get_laps()
	print (day_2.get_laps(), "laps")

	# Add in battery power here
	start_time = datetime(2025, 7, 4, 18, 0)
	duration = 3600 # 1 hr
	battery_final += charge_off_hour(location, start_time, duration)

	# # July 5, 2025, 10:00 AM CT
	start_time = datetime(2025, 7, 5, 9, 0)
	battery_final += charge_off_hour(location, start_time, duration)

	start_time = datetime(2025, 7, 5, 10, 0)
	battery_initial = battery_final
	battery_final   = 0.00
	day_3 = Track(location, start_time, constants.DRIVER_COUNT, battery_initial, battery_final, 28800)
	day_3.get_day_info()
	laps += day_3.get_laps()
	print (day_3.get_laps(), "laps")

	print ("Total Laps:", laps)

if __name__ == "__main__":
	main()
