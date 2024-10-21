
#-----Imports-----#
import numpy as np
from Pathfinder import Pathfinder
from Conditions import OptimizationParameters
from MutationMethods import mutateCondition
from BaseClasses import Component

class Action(Component):

    def __init__(self):
        Component.__init__(self)
        self.name = ""
        self.type = "action"

    def mutate(self, op: OptimizationParameters):
        pass

    def copy(self):
        return Action()

    def toString(self):
        return self.name

# Save the current position as the waypoint
class SetWaypoint(Action):

    def __init__(self):
        Action.__init__(self)
        self.name = "SetWaypoint"

    def run(self, sim, agent) -> bool:
        agent.waypointPathfinder = sim.getPathfinder(agent.x, agent.y)
        return True

    def copy(self):
        return SetWaypoint()

# Reset the saved waypoint
class ResetWaypoint(Action):

    def __init__(self):
        Action.__init__(self)
        self.name = "ResetWaypoint"

    def run(self, sim, agent) -> bool:
        agent.waypointPathfinder = None
        return True

    def copy(self):
        return ResetWaypoint()

# Select and save a nearby agent that matches given condition
class SelectTargetAgent(Action):

    def __init__(self, condition=None):
        Action.__init__(self)
        self.name = "SelectAgent"
        self.condition = condition

    def run(self, sim, agent) -> bool:
        pathfinder = sim.map.pathfinderArray[agent.x, agent.y]
        agentList = []
        for queriedAgent in sim.agentList:
            distance = pathfinder.distanceArray[queriedAgent.x, queriedAgent.y]
            agent.queriedAgent = queriedAgent
            if distance <= sim.commRange and (self.condition is None or self.condition.run(sim, agent)):
                agentList.append(queriedAgent)

        if len(agentList) > 0:
            agent.targetAgent = np.random.choice(agentList)
            return True
        return False

    def mutate(self, op: OptimizationParameters):
        self.condition = mutateCondition(self.condition, op, True)

    def copy(self):
        if self.condition is None:
            copiedCondition = None
        else:
            copiedCondition = self.condition.copy()
        return SelectTargetAgent(copiedCondition)

    def toString(self):
        if self.condition is None:
            return self.name
        else:
            return f"{self.name}({self.condition.toString()})"

class CopyWaypoint(Action):

    def __init__(self):
        Action.__init__(self)
        self.name = "CopyWaypoint"

    def run(self, sim, agent) -> bool:
        if agent.targetAgent is not None:
            agent.waypointPathfinder = agent.targetAgent.waypointPathfinder
            return True
        return False

    def copy(self):
        return CopyWaypoint()

def getActionFactories():
    return [SetWaypoint, ResetWaypoint, SelectTargetAgent, CopyWaypoint]


