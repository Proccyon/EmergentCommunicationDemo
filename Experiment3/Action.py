
#-----Imports-----#
import numpy as np
from Pathfinder import Pathfinder

class Action:

    def __init__(self):
        self.name = ""

    def run(self, sim, agent):
        pass

class SetWaypoint(Action):

    def __init__(self):
        Action.__init__(self)
        self.name = "Set waypoint"

    def run(self, sim, agent):
        agent.waypointPathfinder = sim.addPathfinder(agent.x, agent.y)

class ResetWaypoint(Action):

    def __init__(self):
        Action.__init__(self)
        self.name = "Reset waypoint"

    def run(self, sim, agent):
        agent.waypointPathfinder = None