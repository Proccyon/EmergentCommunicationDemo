
#-----Imports-----#
import numpy as np
from Pathfinder import Pathfinder

class Action:

    def __init__(self):
        self.name = ""

    def run(self, sim, agent):
        pass

# Save the current position as the waypoint
class SetWaypoint(Action):

    def __init__(self):
        Action.__init__(self)
        self.name = "Set waypoint"

    def run(self, sim, agent):
        agent.waypointPathfinder = sim.getPathfinder(agent.x, agent.y)

# Reset the saved waypoint
class ResetWaypoint(Action):

    def __init__(self):
        Action.__init__(self)
        self.name = "Reset waypoint"

    def run(self, sim, agent):
        agent.waypointPathfinder = None

# Select and save a nearby agent that matches given condition
class SelectTargetAgent(Action):

    def __init__(self, condition):
        Action.__init__(self)
        self.name = "Select Agent"
        self.condition = condition

    def run(self, sim, agent):
        pathfinder = sim.map.pathfinderArray[agent.x, agent.y]
        agentList = []
        for queriedAgent in sim.creatureList:
            distance = pathfinder.distanceArray[queriedAgent.x, queriedAgent.y]
            agent.queriedAgent = queriedAgent
            if distance <= sim.smellRange and self.condition.evaluate(sim, agent):
                agentList.append(queriedAgent)

        if len(agentList) > 0:
            agent.targetAgent = np.random.choice(agentList)








def getActionFactories():
    factoryList = []
    factoryList.append(None)
    factoryList.append(lambda: SetWaypoint())
    factoryList.append(lambda: ResetWaypoint())
    factoryList.append(lambda condition: SelectTargetAgent(condition))
    return factoryList