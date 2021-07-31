import tkinter as tk
import math
from aStar import *
import time as time


# lab code
class Counter:
    def __init__(self, canvas):
        self.dirt_collected = 0
        self.canvas = canvas
        self.canvas.create_text(70, 50, text="Dirt collected: " + str(self.dirt_collected), tags="counter")

    def itemCollected(self, canvas):
        self.dirt_collected += 1
        self.canvas.itemconfigure("counter", text="Dirt collected: " + str(self.dirt_collected))


class Bot:
    # some added parameters for certain eexperiments
    def __init__(self, namep, canvasp, battery_usage, dirt_bin_usage, xx, yy, angle):
        # initialise bot-parameters and connect the bot to the canvas
        self.x = xx  # x-coordinate (position) on screen
        self.y = yy  # y-coordinate (position) on screen
        self.theta = angle  # bot's orientation
        self.name = namep
        self.ll = 60  # axle width
        self.vl = 0.0  # left motor velocity
        self.vr = 0.0  # right motor velocity
        if battery_usage:
            self.battery = 1000  # battery capacity (if used)
            self.percentage = True
        else:
            self.battery = 10000  # battery capacity (if not used: high enough to not affect the bot's behaviour)
            self.percentage = False
        if dirt_bin_usage:
            self.storage = 10  # storage (if used: amount of available storage for dirt collection)
            self.label = True
        else:
            self.storage = 5000  # storage (if not used: high enough to not affect the bot's behaviour)
            self.label = False
        self.turning = 0
        self.moving = random.randrange(50, 100)
        self.currently_turning = False
        self.canvas = canvasp

    # added label for storage
    # draw bot onto canvas
    def draw(self, canvas):
        points = [(self.x + 30 * math.sin(self.theta)) - 30 * math.sin((math.pi / 2.0) - self.theta), \
                  (self.y - 30 * math.cos(self.theta)) - 30 * math.cos((math.pi / 2.0) - self.theta), \
                  (self.x - 30 * math.sin(self.theta)) - 30 * math.sin((math.pi / 2.0) - self.theta), \
                  (self.y + 30 * math.cos(self.theta)) - 30 * math.cos((math.pi / 2.0) - self.theta), \
                  (self.x - 30 * math.sin(self.theta)) + 30 * math.sin((math.pi / 2.0) - self.theta), \
                  (self.y + 30 * math.cos(self.theta)) + 30 * math.cos((math.pi / 2.0) - self.theta), \
                  (self.x + 30 * math.sin(self.theta)) + 30 * math.sin((math.pi / 2.0) - self.theta), \
                  (self.y - 30 * math.cos(self.theta)) + 30 * math.cos((math.pi / 2.0) - self.theta) \
                  ]
        canvas.create_polygon(points, fill="blue", tags=self.name)

        self.sensorPositions = [(self.x + 20 * math.sin(self.theta)) + 30 * math.sin((math.pi / 2.0) - self.theta), \
                                (self.y - 20 * math.cos(self.theta)) + 30 * math.cos((math.pi / 2.0) - self.theta), \
                                (self.x - 20 * math.sin(self.theta)) + 30 * math.sin((math.pi / 2.0) - self.theta), \
                                (self.y + 20 * math.cos(self.theta)) + 30 * math.cos((math.pi / 2.0) - self.theta) \
                                ]

        centre1PosX = self.x
        centre1PosY = self.y

        if self.percentage:  # print battery level inside bot
            canvas.create_oval(centre1PosX - 15, centre1PosY - 15, \
                               centre1PosX + 15, centre1PosY + 15, \
                               fill="gold", tags=self.name)
            canvas.create_text(self.x, self.y, text=str(self.battery), tags=self.name)

        if self.label:  # print storage available inside bot if bins are used
            canvas.create_oval(centre1PosX + 25, centre1PosY + 25, \
                               centre1PosX + 55, centre1PosY + 55, \
                               fill="lightgray", tags=self.name)
            canvas.create_text(self.x + 40, self.y + 40, text=str(self.storage), tags=self.name)

        wheel1PosX = self.x - 30 * math.sin(self.theta)
        wheel1PosY = self.y + 30 * math.cos(self.theta)
        canvas.create_oval(wheel1PosX - 3, wheel1PosY - 3, \
                           wheel1PosX + 3, wheel1PosY + 3, \
                           fill="red", tags=self.name)

        wheel2PosX = self.x + 30 * math.sin(self.theta)
        wheel2PosY = self.y - 30 * math.cos(self.theta)
        canvas.create_oval(wheel2PosX - 3, wheel2PosY - 3, \
                           wheel2PosX + 3, wheel2PosY + 3, \
                           fill="green", tags=self.name)

        sensor1PosX = self.sensorPositions[0]
        sensor1PosY = self.sensorPositions[1]
        sensor2PosX = self.sensorPositions[2]
        sensor2PosY = self.sensorPositions[3]
        canvas.create_oval(sensor1PosX - 3, sensor1PosY - 3, \
                           sensor1PosX + 3, sensor1PosY + 3, \
                           fill="yellow", tags=self.name)
        canvas.create_oval(sensor2PosX - 3, sensor2PosY - 3, \
                           sensor2PosX + 3, sensor2PosY + 3, \
                           fill="yellow", tags=self.name)

    # cf. Dudek and Jenkin, Computational Principles of Mobile Robotics
    def move(self, canvas, registry_passives, dt):
        # decrement battery by 1 for each move and stop the bot if it has run out of battery completely
        if self.battery > 0:
            self.battery -= 1
        if self.battery == 0:
            self.vl = 0
            self.vr = 0

        # stop the bot if there is not enough storage available and display warning to user
        # if self.storage == 4:
        #     canvas.create_text(self.x + 40, self.y + 75, text='Not enough\nstorage!', fill='red', tags=self.name)
        #     return

        # charge the bot's battery if it is near a charger
        for rr in registry_passives:
            if isinstance(rr, Charger) and self.distanceTo(rr) < 80:
                self.battery += 10

        # unload the bot's collected dirt if it is near a bin to free up storage
        for rr in registry_passives:
            if isinstance(rr, DirtBin) and self.distanceTo(rr) < 80:
                self.storage += 1

        if self.vl == self.vr:
            R = 0
        else:
            R = (self.ll / 2.0) * ((self.vr + self.vl) / (self.vl - self.vr))
        omega = (self.vl - self.vr) / self.ll
        ICCx = self.x - R * math.sin(self.theta)  # instantaneous centre of curvature
        ICCy = self.y + R * math.cos(self.theta)
        m = np.matrix([[math.cos(omega * dt), -math.sin(omega * dt), 0], \
                       [math.sin(omega * dt), math.cos(omega * dt), 0], \
                       [0, 0, 1]])
        v1 = np.matrix([[self.x - ICCx], [self.y - ICCy], [self.theta]])
        v2 = np.matrix([[ICCx], [ICCy], [omega * dt]])
        newv = np.add(np.dot(m, v1), v2)
        newX = newv.item(0)
        newY = newv.item(1)
        newTheta = newv.item(2)
        newTheta = newTheta % (2.0 * math.pi)  # make sure angle doesn't go outside [0.0,2*pi)
        self.x = newX
        self.y = newY
        self.theta = newTheta
        if self.vl == self.vr:  # straight line movement
            self.x += self.vr * math.cos(self.theta)  # vr wlog
            self.y += self.vr * math.sin(self.theta)

        # run off one edge, rejoin on the other
        if self.x < 0.0:
            self.x = 999.0
        if self.x > 1000.0:
            self.x = 0.0
        if self.y < 0.0:
            self.y = 1000.0
        if self.y > 999.0:
            self.y = 0.0

        # delete and re-draw bot in new position after movement
        canvas.delete(self.name)
        self.draw(canvas)

    # lab code
    def sense_charger(self, registry_passives):
        lightL = 0.0
        lightR = 0.0
        for pp in registry_passives:
            if isinstance(pp, Charger):
                lx, ly = pp.getLocation()
                distanceL = math.sqrt((lx - self.sensorPositions[0]) * (lx - self.sensorPositions[0]) + \
                                      (ly - self.sensorPositions[1]) * (ly - self.sensorPositions[1]))
                distanceR = math.sqrt((lx - self.sensorPositions[2]) * (lx - self.sensorPositions[2]) + \
                                      (ly - self.sensorPositions[3]) * (ly - self.sensorPositions[3]))
                lightL += 200000 / (distanceL * distanceL)
                lightR += 200000 / (distanceR * distanceR)
        return lightL, lightR

    # new function for bin, based on charger function above
    def sense_dirt_bin(self, registry_passives):
        lightL = 0.0
        lightR = 0.0
        for pp in registry_passives:
            if isinstance(pp, DirtBin):
                lx, ly = pp.getLocation()
                distanceL = math.sqrt((lx - self.sensorPositions[0]) * (lx - self.sensorPositions[0]) + \
                                      (ly - self.sensorPositions[1]) * (ly - self.sensorPositions[1]))
                distanceR = math.sqrt((lx - self.sensorPositions[2]) * (lx - self.sensorPositions[2]) + \
                                      (ly - self.sensorPositions[3]) * (ly - self.sensorPositions[3]))
                lightL += 200000 / (distanceL * distanceL)
                lightR += 200000 / (distanceR * distanceR)
        return lightL, lightR

    # following 3 functions used from lab code
    def distanceTo(self, obj):
        xx, yy = obj.getLocation()
        return math.sqrt(math.pow(self.x - xx, 2) + math.pow(self.y - yy, 2))

    # calculate distance to right sensor of bot from given coordinates (in parameters)
    def distanceToRightSensor(self, lx, ly):
        return math.sqrt((lx - self.sensorPositions[0]) * (lx - self.sensorPositions[0]) + \
                         (ly - self.sensorPositions[1]) * (ly - self.sensorPositions[1]))

    # calculate distance to left sensor of bot from given coordinates (in parameters)
    def distanceToLeftSensor(self, lx, ly):
        return math.sqrt((lx - self.sensorPositions[2]) * (lx - self.sensorPositions[2]) + \
                         (ly - self.sensorPositions[3]) * (ly - self.sensorPositions[3]))

    # code predominantly developed from lab code (with some changes to decrement the storage) and added comments
    # collect dirt by removing it from the canvas if the bot is close to it and incrementing the dirt collection counter
    # and decrementing the storage counter
    def collect_dirt(self, canvas, registry_passives, count):
        if self.storage > 0:  # only collect dirt if there is available storage
            to_delete = []
            for idx, rr in enumerate(registry_passives):
                if isinstance(rr, Dirt):
                    if self.distanceTo(rr) < 30:
                        canvas.delete(rr.name)
                        # decrement the bot's storage as dirt is collected and less storage becomes available
                        self.storage -= 1
                        to_delete.append(idx)
                        count.itemCollected(canvas)
            for ii in sorted(to_delete, reverse=True):
                del registry_passives[ii]

        return registry_passives

    # some code reused from lab code with changes to parameters, added section for the bin and added comments
    def transfer_function(self, path, strategy, charger_l, charger_r, dirt_bin_l, dirt_bin_r):
        if strategy == "planning":  # count number of moves
            target = path[0]
            # print(target)
            target = (target[0] * 100 + 50, target[1] * 100 + 50)

            distL = self.distanceToLeftSensor(target[0], target[1])
            distR = self.distanceToRightSensor(target[0], target[1])

            if distR > distL:
                self.vl = 2.0
                self.vr = -2.0
            elif distR < distL:
                self.vl = -2.0
                self.vr = 2.0
            if abs(distR - distL) < distL * 0.1:  # approximately the same
                self.vl = 5.0
                self.vr = 5.0

            # print(distL, distR)
            # check if the bot is near the target
            if distL < 50.0 or distR < 50.0:
                # print("close")
                path.pop(0)
                # print("popped")

            if not path:
                return "finished"
        elif strategy == "wandering":  # wander, move a pre-set amount in random directions
            if self.currently_turning:
                self.vl = -2.0
                self.vr = 2.0
                self.turning -= 1
            else:
                self.vl = 5.0
                self.vr = 5.0
                self.moving -= 1
            if self.moving == 0 and not self.currently_turning:
                self.turning = random.randrange(20, 40)
                self.currently_turning = True
            if self.turning == 0 and self.currently_turning:
                self.moving = random.randrange(50, 100)
                self.currently_turning = False

        # dirt disposal - this section is later so it has priority (lower priority than battery)
        if self.storage < 35:  # seek bin if remaining dirt storage is below a certain amount
            if dirt_bin_r > dirt_bin_l:
                self.vl = 2.0
                self.vr = -2.0
            elif dirt_bin_r < dirt_bin_l:
                self.vl = -2.0
                self.vr = 2.0
            if abs(dirt_bin_r - dirt_bin_l) < dirt_bin_l * 0.1:  # approximately the same
                self.vl = 5.0
                self.vr = 5.0
        # stop and unload if near bin and remaining storage is below a certain amount
        if dirt_bin_l + dirt_bin_r > 200 and self.storage < 35:
            self.vl = 0.0
            self.vr = 0.0

        # battery - this section is latest so it has the highest priority
        if self.battery < 600:  # seek charger if battery is below a certain amount
            if charger_r > charger_l:
                self.vl = 2.0
                self.vr = -2.0
            elif charger_r < charger_l:
                self.vl = -2.0
                self.vr = 2.0
            if abs(charger_r - charger_l) < charger_l * 0.1:  # approximately the same
                self.vl = 5.0
                self.vr = 5.0
        # stop and charge if near charger and battery is below 600
        if charger_l + charger_r > 200 and self.battery < 600:
            self.vl = 0.0
            self.vr = 0.0


# lab code
class Charger:
    def __init__(self, namep):
        self.centreX = random.randint(100, 900)
        self.centreY = random.randint(100, 900)
        self.name = namep

    def draw(self, canvas):
        body = canvas.create_oval(self.centreX - 10, self.centreY - 10, \
                                  self.centreX + 10, self.centreY + 10, \
                                  fill="gold", tags=self.name)

    def getLocation(self):
        return self.centreX, self.centreY


class DirtBin:
    def __init__(self, namep):
        self.centreX = random.randint(100, 900)
        self.centreY = random.randint(100, 900)
        self.name = namep

    def draw(self, canvas):
        body = canvas.create_oval(self.centreX - 10, self.centreY - 10, \
                                  self.centreX + 10, self.centreY + 10, \
                                  fill="lightgray", tags=self.name)

    def getLocation(self):
        return self.centreX, self.centreY


# lab code with added comments
class Dirt:
    def __init__(self, namep, xx, yy):
        self.centreX = xx
        self.centreY = yy
        self.name = namep

    def draw(self, canvas):
        body = canvas.create_oval(self.centreX - 1, self.centreY - 1, \
                                  self.centreX + 1, self.centreY + 1, \
                                  fill="grey", tags=self.name)

    def getLocation(self):
        return self.centreX, self.centreY


# change the bots' location to be the location of where a click-event occurred
def button_clicked(x, y, registry_actives):
    for rr in registry_actives:
        if isinstance(rr, Bot):
            rr.x = x
            rr.y = y


# lab code with added comments
def initialise(window):
    window.resizable(False, False)
    canvas = tk.Canvas(window, width=1000, height=1000)  # enable drawing and adding graphic objects to window
    canvas.pack()  # fit canvas onto window
    return canvas  # return canvas to later add graphics to


# # code predominantly developed from lab code (with changes to randomise the distribution) and added comments
# places dirt in a specific configuration
def place_dirt(registry_passives, canvas):
    # initialise an array of zeros representing a 10x10 map of the environment which dirt can be added to
    map_of_dirt = np.zeros((10, 10), dtype=np.int16)

    # nested loop to iterate through all 100 sections of the 2d-map and flip the 0 (representing no dirt) of
    # each section to a random number between 1 and 3 (adding a small a mount of dirt randomly to each section)
    for xx in range(10):
        for yy in range(10):
            map_of_dirt[xx][yy] = random.randrange(1, 3)

    # accessing elements of numpy.ndarray: [row][col]

    # # add a lot of dirt (10) in the 8th row
    # # (flipped due to graphics-mechanisms so added at the top of the interface instead of bottom)
    # for yy in range(10):
    #     map_of_dirt[8][yy] = 10
    #
    # # add a lot of dirt (10) in the 0th (first) column
    # # (flipped due to graphics-mechanisms so added at the right of the interface instead of left)
    # for xx in range(1, 8):
    #     map_of_dirt[xx][0] = 10

    # iterate over all 100 sections of the map and randomly add a lot of dirt to a random 20% of the sections
    for xx in range(10):
        for yy in range(10):
            if random.randint(0, 4) == 4:  # 20% chance
                map_of_dirt[xx][yy] = random.randrange(8, 12)

    map_of_dirt[0][0] = 1
    map_of_dirt[9][9] = 0

    # create dirt objects and place on map according to random configurations set up above
    i = 0
    for xx in range(10):
        for yy in range(10):
            for _ in range(map_of_dirt[xx][yy]):
                dirtX = xx * 100 + random.randrange(0, 99)
                dirtY = yy * 100 + random.randrange(0, 99)
                dirt = Dirt("Dirt" + str(i), dirtX, dirtY)
                registry_passives.append(dirt)
                dirt.draw(canvas)
                i += 1

    print(np.transpose(map_of_dirt))

    return map_of_dirt


def register(canvas, battery_usage, dirt_bin_usage):
    registry_actives = []  # initialise list of active elements in the system
    registry_passives = []  # initialise list of passive elements in the system

    for i in range(0, 1):  # create required number of bots (noOfBots) and draw onto canvas
        bot = Bot("Bot" + str(i), canvas, battery_usage, dirt_bin_usage,  950, 950, -3.0 * math.pi / 4.0)
        registry_actives.append(bot)
        bot.draw(canvas)

    # lab code
    if battery_usage:
        charger = Charger("Charger")  # create charger object and add to list of passives
        registry_passives.append(charger)
        charger.draw(canvas)  # draw charger on canvas

    if dirt_bin_usage:  # only create the bin if they're used in the current test
        dirt_bin = DirtBin("DirtBin")  # create bin object and add to list of passives
        registry_passives.append(dirt_bin)
        dirt_bin.draw(canvas)  # draw bin on canvas

    map_of_dirt = place_dirt(registry_passives, canvas)  # distribute dirt

    count = Counter(canvas)  # initialise a counter for dirt-collection

    # continuously check the canvas to see if a button has been clicked
    # and if so, update the bots' location to the location of the event
    canvas.bind("<Button-1>", lambda event: button_clicked(event.x, event.y, registry_actives))

    return registry_actives, registry_passives, count, map_of_dirt


# code predominantly developed from lab code (with some added functions, parameters and conditions) and added comments
def move_it(canvas, registry_actives, registry_passives, count, moves, window, path, strategy, start_time):
    moves += 1  # increment count of moves for each move

    for rr in registry_actives:
        charger_intensity_l, charger_intensity_r = rr.sense_charger(registry_passives)  # calculate distance to charger

        dirt_bin_intensity_l, dirt_bin_intensity_r = rr.sense_dirt_bin(registry_passives)  # calculate distance to bin

        # transfer inputs into motor movement output for the bot
        # return a variable that says if its A* path has been completed
        finished = rr.transfer_function(path, strategy, charger_intensity_l, charger_intensity_r,
                                        dirt_bin_intensity_l, dirt_bin_intensity_r)

        rr.move(canvas, registry_passives, 1.0)

        registry_passives = rr.collect_dirt(canvas, registry_passives, count)

        max_no_of_moves = 10000
        # close the system if done
        if time.time() > (start_time + 10) or moves > max_no_of_moves or finished == "finished":
            print("total dirt collected in", moves, "moves is",
                  count.dirt_collected)
            window.destroy()  # close the window when done
            return

    # recursively call the current function with a time delay
    # so the bot(s) are always moving until the system has finished
    canvas.after(30, move_it, canvas, registry_actives, registry_passives,
                 count, moves, window, path, strategy, start_time)


# code predominantly developed from lab code (with some changes to parameters) and added comments
def run_one_experiment(strategy, battery_usage, dirt_bin_usage, my_seed):
    random.seed(my_seed)  # seed the randomness to make results reproducible
    window = tk.Tk()  # create window
    canvas = initialise(window)  # initialise a canvas on the window to add graphics to
    # register all objects and subjects in the system
    registry_actives, registry_passives, count, map_of_dirt = register(canvas, battery_usage, dirt_bin_usage)
    moves = 0  # initialise counter for number of moves (system-limitation)
    path = aStarSearch(map_of_dirt)  # find A* path
    # print(path)
    start_time = time.time()  # initialise start time
    # start the system
    move_it(canvas, registry_actives, registry_passives, count, moves, window, path, strategy, start_time)
    window.mainloop()  # check window iteratively in an endless loop to monitor it for updates

    # return amount of dirt collected by the agents in the current system for statistical purposes
    return count.dirt_collected


# running one test:
# pass the following parameters:
# - strategy (wandering or planning)
# - battery_usage (true or false)
# - dirt_bin_usage (true or false)
# - seed: determines dirt distribution, wandering movement, etc.
# run_one_experiment("planning", True, True, 54)
