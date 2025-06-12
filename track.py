import constants
from node_list import Node_List
import math

class Track:
    def __init__(self, location, day, driver_count, b_i, b_f, duration):
        self.loc = location
        self.day = day
        self.count = driver_count
        self.b_i = b_i
        self.b_f = b_f
        self.duration = duration

    def get_day_info(self):
        laps = []
        time_driven = 0
        # Some laps will be more constant, currently starting from stop for every lap
        battery_i = self.b_i
        while time_driven < self.duration and math.floor(battery_i * 100) > self.b_f * 100:
            lap = Node_List(
                battery_i,
                self.duration,
                (self.b_f - self.b_i),
                self.day,
                self.loc,
                constants.SECTIONS
                )
            
            battery_i = lap.get_b_f()
            time_driven  += lap.get_time()
            lap.print_lap_stats()
            laps.append(lap)

        self.battery_used = self.b_i - battery_i
        self.laps = laps

        print (f"{time_driven / 3600:.2f} hours")

    def get_battery_final(self):
        return self.b_i - self.battery_used

    def get_laps(self):
        return len(self.laps)
