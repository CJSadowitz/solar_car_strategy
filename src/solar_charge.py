from astral.sun import elevation
import datetime
import math
import src.constants

def charge_off_hour(location, start_time, duration):
    # Adjust this for different efficiency values
    time_now = start_time
    power_in = 0
    for i in range(duration):
        solar_altitude = elevation(location.observer, time_now)
        time_now = time_now + datetime.timedelta(seconds=1)
        # kW
        power = src.constants.MAX_PANEL_POWER * math.cos(math.radians(solar_altitude))
        # kW * s
        power_in += power * 1

    # kW * hrs
    # print (f"POWER  IN: {power / 3600:.4f}")
    return (power_in / 3600) / src.constants.BATTERY_CAPACITY