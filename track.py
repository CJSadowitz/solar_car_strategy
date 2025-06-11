import constants
from node_list import Node_List

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
        battery_used = 0
        # Some laps will be more constant, currently starting from stop for every lap
        while time_driven < self.duration and battery_used < self.b_i - self.b_f:
            lap = Node_List(self.b_i, 0, self.day, self.loc, 10)
            time_driven  += lap.get_time()
            battery_used += lap.get_b_f()
            lap.print_lap_stats()
            laps.append(lap)
        
        self.battery_used = battery_used
        self.laps = laps

        print (f"{time_driven / 60:.2f} minutes")
        print (f"{battery_used:.2%}")

    def get_battery_final(self):
        return self.b_i - self.battery_used
    
    def get_laps(self):
        return len(self.laps)
