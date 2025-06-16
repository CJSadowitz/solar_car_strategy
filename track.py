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
        # Some laps will be more constant, currently starting from stop for every lap
        laps = []
        time_driven = 0
        battery_used = 0
        battery_i = self.b_i
        num_laps = 100
        velocity_i = 0
        while True:
            if ((battery_used) >= self.b_i - self.b_f or time_driven >= self.duration):
                # print (self.b_i - self.b_f)
                # print (self.b_i - battery_used, time_driven / 3600)
                break
            lap = Node_List(
                velocity_i,
                battery_i,
                self.duration / num_laps,
                (self.b_i - self.b_f) / num_laps,
                self.day,
                self.loc,
                )
            velocity_i = lap.get_v_f()
            battery_used = self.b_i - lap.get_b_f()
            battery_i = lap.get_b_f()
            time_driven  += lap.get_time()
            # lap.print_lap_stats()
            laps.append(lap)

        self.battery_used = self.b_i - battery_i
        self.laps = laps

        print (f"{time_driven / 3600:.2f} hours")
        print (f"{battery_used:.4%}")

    def get_battery_final(self):
        return self.b_i - self.battery_used

    def get_laps(self):
        return len(self.laps)
