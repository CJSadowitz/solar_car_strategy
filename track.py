from node_list import Node_List
import constants
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
        # Some laps will be more constant, currently starting from stop for every lap
        laps = []
        time_driven = 0
        battery_used = 0
        battery_i = self.b_i
        velocity_i = 0
        target_v = constants.MAX_VELOCITY - 2
        driver_time = 0
        while True:
            if (battery_used >= self.b_i - self.b_f or time_driven >= self.duration):
                break
            if math.floor(driver_time >= self.duration / constants.DRIVER_COUNT):
                time_driven += 300 # Add 5 minutes for a driver change
                driver_time = 0
            lap = None
            while True:
                lap = self.generate_lap(target_v, velocity_i, battery_i)
                ratio = abs((lap.get_battery_used() / (self.b_i - self.b_f)) / (lap.get_time() / self.duration))
                target_v, test = self.check_time_charge_ratio(ratio, target_v)
                if (test):
                    break
                    
            velocity_i    = lap.get_v_f()
            battery_used  = self.b_i - lap.get_b_f()
            battery_i     = lap.get_b_f()
            time_driven  += lap.get_time()
            driver_time  += lap.get_time()
            # lap.print_nodes()
            if (battery_used >= self.b_i - self.b_f or time_driven >= self.duration):
                break
            # lap.print_lap_stats()
            laps.append(lap)

        self.battery_used = self.b_i - battery_i
        self.laps = laps

        print (f"{time_driven / 3600:.2f} hours")
        print (f"{battery_used * constants.BATTERY_CAPACITY:.4}")

    def check_time_charge_ratio(self, ratio, target_v):
        if (ratio < 1 + constants.BATTERY_TIME_TOLERANCE and ratio > 1 - constants.BATTERY_TIME_TOLERANCE):
            # print ("good:", ratio, target_v)
            return target_v, True
        if (ratio > 1 + constants.BATTERY_TIME_TOLERANCE):
            # Battery Ratio is bigger than time ratio (battery is the problem)
            if (target_v != 0):
                target_v -= 0.01
                # print (f"battery, {target_v:.2f}, {ratio:.5f}")
            else:
                # Don't go negative speed
                return target_v, True
        else:
            # Time Ratio is bigger than battery ratio (time is the problem)
            if (target_v != constants.MAX_VELOCITY):
                target_v += 0.01
                # print (f"time, {target_v:.2f}, {ratio:.5f}")
            else:
                # Don't go beyond max velocity
                return target_v, True
        return target_v, False

    def generate_lap(self, target_v, velocity_i, battery_i):
        lap = Node_List(
            target_v,
            velocity_i,
            battery_i,
            self.duration,
            (self.b_i - self.b_f),
            self.day,
            self.loc,
            )
        return lap

    def get_battery_final(self):
        return self.b_i - self.battery_used

    def get_laps(self):
        return len(self.laps)
