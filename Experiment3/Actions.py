
#-----Imports-----#
import numpy as np
from Pathfinder import Pathfinder
from Conditions import OptimizationParameters, Expression
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
        agent.waypointCoords = [agent.x, agent.y]
        return True

    def copy(self):
        return SetWaypoint()

# Reset the saved waypoint
class ResetWaypoint(Action):

    def __init__(self, index=0):
        Action.__init__(self)
        self.index = index
        self.name = "ResetWaypoint"

    def run(self, sim, agent) -> bool:
        agent.coordsArray[self.index, :] = [-1, -1]
        return True

    def copy(self):
        return ResetWaypoint(self.index)

# Select and save a nearby agent that matches given condition
class SelectTargetAgent(Action):

    def __init__(self, condition=None):
        Action.__init__(self)
        self.name = "SelectAgent"
        self.condition = condition

    def run(self, sim, agent) -> bool:
        nearbyAgents = agent.getNearbyAgents(sim)
        agentList = []
        for queriedAgent in nearbyAgents:
            agent.queriedAgent = queriedAgent
            if self.condition is None or self.condition.run(sim, agent):
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
            agent.waypointCoords = agent.targetAgent.waypointCoords
            return True
        return False

    def copy(self):
        return CopyWaypoint()

class SetInternalBool(Action):

    def __init__(self, index: int, value: bool):
        Action.__init__(self)
        self.index = index
        self.value = value
        self.name = f"Bool{index}={value}"

    def run(self, sim, agent) -> bool:
        agent.boolArray[self.index] = self.value
        return True

    def copy(self):
        return SetInternalBool(self.index, self.value)


class SetInternalCoord(Action):

    def __init__(self, index: int, value: Expression):
        Action.__init__(self)
        self.index = index
        self.value = value
        self.name = f"Coord{index}={value.toString()}"

    def run(self, sim, agent) -> bool:
        agent.coordsArray[self.index, :] = self.value.evaluate(sim, agent)
        return True

    def copy(self):
        return SetInternalCoord(self.index, self.value)

class SetInternalCounter(Action):

    def __init__(self, index: int, value: int):
        Action.__init__(self)
        self.index = index
        self.value = value
        self.name = f"Counter{index}={value}"

    def run(self, sim, agent) -> bool:
        agent.counterArray[self.index] = self.value
        return True

    def copy(self):
        return SetInternalCounter(self.index, self.value)

class SetInternalFloat(Action):

    def __init__(self, index: int, value: Expression):
        Action.__init__(self)
        self.index = index
        self.value = value
        self.name = f"Float{index}={value}"

    def run(self, sim, agent) -> bool:
        agent.floatArray[self.index] = self.value.evaluate(sim, agent)
        return True

    def copy(self):
        return SetInternalFloat(self.index, self.value)

    def toString(self):
        return f"Float{self.index}={self.value.toString()}"

class IncrementCounter(Action):

    def __init__(self, index: int):
        Action.__init__(self)
        self.index = index
        self.name = f"Counter{index}+=1"

    def run(self, sim, agent) -> bool:
        agent.counterArray[self.index] += 1
        return True

    def copy(self):
        return IncrementCounter(self.index)



def getActionFactories():
    return [SetWaypoint, ResetWaypoint, SelectTargetAgent, CopyWaypoint]

def getActionFactories():
    return [SetWaypoint, ResetWaypoint, SelectTargetAgent, CopyWaypoint]


