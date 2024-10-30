
#-----Imports-----#
import numpy as np
from Pathfinder import selectRandomPosition
from BaseClasses import Component

#---Base---#

# Represents one node of an automata
class TaskNode(Component):

    def __init__(self):
        Component.__init__(self)
        self.name = ""
        self.type = "task"

    # Performs a task, e.g. picking up food
    # Returns False when task is finished, True when task is still ongoing
    def act(self, sim, agent) -> bool:
        return False

    def run(self, sim, agent) -> bool:
        if self.act(sim, agent):
            agent.isDone = True
            return True
        else:
            return False

    def toString(self) -> str:
        return self.name

#---Action-Implementations---#

# Node that makes the agent move away from the colony
class ExploreNode(TaskNode):

    def __init__(self):
        TaskNode.__init__(self)
        self.name = "Explore"

    def act(self, sim, agent):

        pathfinder = sim.getPathfinder(sim.colonyX, sim.colonyY)

        # Find possible next positions we can move to so we move away from the colony
        next = pathfinder.getPrev(agent.x, agent.y)

        # If no next positions exists, e.g. if we are next to a wall, task is finished
        if len(next) == 0:
            return False

        # Select random position to move to from possible positions
        #x, y = selectRandomPosition(sim, agent.x, agent.y, next)
        x, y = selectRandomPosition(sim, agent.x, agent.y, next)

        #Move to new position
        agent.move(x, y, sim)

        return True

# Node that makes the agent move towards the colony
class ReturnHomeNode(TaskNode):

    def __init__(self):
        TaskNode.__init__(self)
        self.name = "Return Home"

    def act(self, sim, agent):

        pathfinder = sim.getPathfinder(sim.colonyX, sim.colonyY)

        # Find possible next positions we can move to so we move towards the colony
        next = pathfinder.getNext(agent.x, agent.y)

        # If no next positions exists, either we are home or are stuck
        if len(next) == 0:
            return False

        # Select random position to move to from possible positions
        x, y = next[np.random.randint(len(next))]

        # Move to new position
        agent.move(x, y, sim)

        # If we reached the colony, drop off food
        if agent.x == sim.colonyX and agent.y == sim.colonyY and agent.isHoldingFood:
            agent.dropOffFood(sim)

        return True


# Node that makes the agent move towards the colony
class GoToWaypoint(TaskNode):

    def __init__(self):
        TaskNode.__init__(self)
        self.name = "Go waypoint"

    def act(self, sim, agent):

        pathfinder = agent.waypointPathfinder

        if pathfinder is None:
            return False

        # Find possible next positions we can move to so we move towards the waypoint
        next = pathfinder.getNext(agent.x, agent.y)

        # If no next positions exists, either we are at waypoint or are stuck
        if len(next) == 0:
            return False

        # Select random position to move to from possible positions
        x, y = next[np.random.randint(len(next))]

        # Move to new position
        agent.move(x, y, sim)

        return True

# Node that makes the agent pick up nearby food
class GatherNode(TaskNode):

    def __init__(self):
        TaskNode.__init__(self)
        self.name = "GatherFood"

    def act(self, sim, agent):

        if agent.isHoldingFood:
            return False

        if not agent.foodPathfinder is None and not sim.hasFoodArray[agent.x, agent.y]:
            agent.foodPathfinder = None

        # If agent has not yet found food to walk towards, locate nearby food
        if agent.foodPathfinder is None:

            minDistance = 999
            minPathfinder = None
            for x, y in sim.foodPosList:
                pathfinder = sim.getPathfinder(x, y)

                distance = pathfinder.getDistance(agent.x, agent.y)
                if distance < minDistance and distance <= sim.smellRange:
                    minDistance = min(minDistance, distance)
                    minPathfinder = pathfinder

            # If no nearby food is found we are done
            if minPathfinder is None:
                return False

            agent.foodPathfinder = minPathfinder

        # Get next positions we can move to in order to move closer to food
        nextPositions = agent.foodPathfinder.getNext(agent.x, agent.y)

        # If there are none we are probably standing on some food
        if len(nextPositions) == 0:
            agent.foodPathfinder = None
            agent.gatherFood(sim)
            return True

        x, y = nextPositions[np.random.randint(len(nextPositions))]
        agent.move(x, y, sim)

        return True


# Node that makes the agent pick up nearby food
class RandomWalkNode(TaskNode):

    def __init__(self):
        TaskNode.__init__(self)
        self.name = "RandomWalk"

    def act(self, sim, agent):

        newPositions = sim.map.neighbourArray[agent.x, agent.y]

        if len(newPositions) == 0:
            return False

        xNew, yNew = newPositions[np.random.randint(len(newPositions))]

        agent.move(xNew, yNew, sim)
        return True

        # newPositions = []
        # for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
        #     xNew, yNew = agent.x + dx, agent.y + dy
        #     if sim.isValidPosition(xNew, yNew):
        #         newPositions.append((xNew, yNew))
        #
        # if len(newPositions) == 0:
        #     return True
        #
        # xNew, yNew = newPositions[np.random.randint(len(newPositions))]
        # agent.move(xNew, yNew, sim)
        #
        # return False


def initNodes():
    return [RandomWalkNode(), ReturnHomeNode(), GatherNode(), GoToWaypoint()]

