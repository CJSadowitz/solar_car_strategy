# Car Values
MAX_VELOCITY                   = 15.0           # m/s 9.1
BATTERY_CAPACITY               = 5.24           # kW * hrs
MAX_PANEL_POWER                = 0.956          # kW
MASS                           = 430            # kg
GRAVITY                        = 9.81           # m/s^2
FRONTAL_AREA                   = 1.2            # m^2
MOTOR_EFFICIENCY               = 0.80
WEIGHT                         = MASS * GRAVITY # N
COEFFICIENT_DRAG               = 0.3
COEFFICIENT_ROLLING_RESISTANCE = 0.0055

# Fudge
MAX_ACCELERATION               =  0.6            # m/s^2
MIN_ACCELERATION               = -0.6           # m/s^2
PARASITIC_FACTOR               = 1.0            # %

# Track Data
TRACK_LENGTH                   = 5069      # m

# Code adjustments
BATTERY_TIME_TOLERANCE         = 0.01          # The smaller the more accurate; the more time required, 0.01 should be accurate enoguh
SECTIONS                       = 5069          # Legacy

DRIVER_COUNT                   = 4
DRIVER_CHANGE_TIME             = 300            # s
