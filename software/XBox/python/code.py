
# Write your code here :-)
import time
import board
import array
from analogio import AnalogIn
from adafruit_hid.gamepad import Gamepad

from settings import *


time.sleep(1.0)
gp = Gamepad()

class RollingAverage:
    def __init__(self, size):
        self.size=size
        self.buffer = array.array('d')
        for i in range(size):
            self.buffer.append(0.0)
        self.pos = 0
    def addValue(self,val):
        self.buffer[self.pos] = val
        self.pos = (self.pos + 1) % self.size
    def average(self):
        return (sum(self.buffer) / self.size)

# this looks to get the analog inputs from the wheelchair joystick 
# plugged into the freedom wing. so this is getting pin A2
base = AnalogIn(board.A2)
# check if swap axes was set in settings.py
if (not swapAxes):
    hor = AnalogIn(board.A3)
    vert = AnalogIn(board.A4)
else:
    hor = AnalogIn(board.A4)
    vert = AnalogIn(board.A3)
# check if swap horizontal axis was set in settings.py
if (not invertHor):
    horDirection=1
else:
    horDirection=-1
# check if swap vertical axis was set in settings.py
if (not invertVert):
    vertDirection=1
else:
    vertDirection=-1
avgCount = smoothingFactor

# create three rolling averages: base, horizontal and vertical
baseAvg = RollingAverage(avgCount)
horAvg = RollingAverage(avgCount)
vertAvg = RollingAverage(avgCount)

# define a range map function, I think. maybe range map means something specific in Python
def range_map(value, in_min, in_max, out_min, out_max):
    return int(max(out_min,min(out_max,(value - in_min) * (out_max - out_min) // (in_max - in_min) + out_min)))

# define function to get the voltage of a pin
def get_voltage(pin):
    return (pin.value)
baseVal = 0

# loop from 0 to 9, range upper bound not inclusive in python
for i in range(0,10,1):
   # base is the AnalogIn structure created above. it is pin A2.
   # get the voltage, divide by 10 and add to running average
   # more efficient way would be just do sum in loop and one
   # divide at the end but not super important as this is just 
   # initialization code the runs once and is not  in the real-time
   # loop affecting gameplay
   baseVal += (get_voltage(base))/10.0
   time.sleep(.1)

lowVal = -(baseVal / 6)
highVal = (baseVal / 6)

center = 128
last_game_x = center
last_game_y = center

game_thresh=1
middleLimit = 10

gp.reset_all()
while True:
#    baseVal = get_voltage(base)
    horVal = get_voltage(hor) - baseVal
    vertVal = get_voltage(vert) - baseVal
    horAvg.addValue(horVal)
    vertAvg.addValue(vertVal)

    game_x = range_map(horDirection * horAvg.average(), lowVal, highVal, 0, 255)
    game_y = range_map(vertDirection * vertAvg.average(), lowVal, highVal, 0, 255)

    if (abs(game_x - center) < middleLimit):
        game_x = center
    if (abs(game_y - center) < middleLimit):
        game_y = center

    if (abs(last_game_x - game_x) > game_thresh):
        last_game_x = game_x
#        print(game_x, game_y)
        gp.move_joysticks(x=game_x)
    if (abs(last_game_y - game_y) > game_thresh):
        last_game_y = game_y
#        print(game_x, game_y)
        gp.move_joysticks(y=game_y)
#    print((horAvg.average(),vertAvg.average(),))

    print((game_x, game_y,))
    time.sleep(0.025)