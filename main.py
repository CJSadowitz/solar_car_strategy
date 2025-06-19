from src.track import Track
from datetime import datetime
from astral import LocationInfo
from src.solar_charge import charge_off_hour
from src.track_reader import get_track_edge, get_elevation
import src.constants
import numpy as np
import requests
from pathlib import Path

def main():
	# api_key = "af05721584dfa815538ec3376e61af4a" # MAKE THIS A FILE OR SOMETHING
	# city = "Bowling%20Green,US"
	# url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}"
	# response = requests.get(url)
	# data = response.json()

	# for entry in data["list"]:
	# 	dt = entry["dt"]
	# 	cloud_coverage = entry["clouds"]["all"]
	# 	readable_time = datetime.utcfromtimestamp(dt).strftime('%Y-%m-%d %H:%M:%S UTC')
		
	# 	print(f"{readable_time} — Cloud Coverage: {cloud_coverage}%")

	location = LocationInfo("Bowling Green", "USA", "America/Chicago", 36.97, -86.43)

	laps = 0

	# Precomute Elevation data
	e_dict = None
	if src.constants.TRACK_BOWLING_GREEN:
		file_path = Path("track_data") / "side_l.csv"
		e_dict = get_track_edge(file_path)
	else:
		e_dict = {0: 0}
	
	pos = list(range(0, src.constants.TRACK_LENGTH))  # Creates a list from 0 to 5068
	elevation_list = np.array(list(map(lambda p: get_elevation(p / src.constants.TRACK_LENGTH, e_dict), pos)))

	# July 3, 2025, 10:00 AM CT
	start_time = datetime(2025, 7, 3, 10, 0)
	battery_initial = 1.00
	battery_final   = 0.66
	day_1 = Track(location, start_time, src.constants.DRIVER_COUNT, battery_initial, battery_final, 28800, elevation_list)
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
	day_2 = Track(location, start_time, src.constants.DRIVER_COUNT, battery_initial, battery_final, 28800, elevation_list)
	day_2.get_day_info()
	laps += day_2.get_laps()
	print (day_2.get_laps(), "laps")

	# Add in battery power here
	start_time = datetime(2025, 7, 4, 18, 0)
	duration = 3600 # 1 hr
	battery_final += charge_off_hour(location, start_time, duration)

	# July 5, 2025, 10:00 AM CT
	start_time = datetime(2025, 7, 5, 9, 0)
	battery_final += charge_off_hour(location, start_time, duration)

	start_time = datetime(2025, 7, 5, 10, 0)
	battery_initial = battery_final
	battery_final   = 0.00
	day_3 = Track(location, start_time, src.constants.DRIVER_COUNT, battery_initial, battery_final, 28800, elevation_list)
	day_3.get_day_info()
	laps += day_3.get_laps()
	print (day_3.get_laps(), "laps")

	print ("Total Laps:", laps)

if __name__ == "__main__":
	main()
