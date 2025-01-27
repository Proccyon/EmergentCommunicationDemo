
#-----Imports-----#
import numpy as np
from BaseClasses import Component

class Condition(Component):

    def __init__(self):
        Component.__init__(self)
        self.conditionType = ""
        self.type = "condition"

    def getDescendants(self, parent=(None,0), descendantList=None):
        if descendantList is None:
            descendantList = []
        descendantList.append((self, parent))
        return descendantList

    def getRemoveables(self, parent=(None,0), removableList=None):
        if removableList is None:
            removableList = []
        return removableList

    def isOperator(self):
        return self.conditionType == "BinaryOperator" or self.conditionType == "UnaryOperator"

    def copy(self):
        return Condition()

    def size(self) -> int:
        return 1


class Expression:

    def __init__(self):
        self.exprType = ""

    def evaluate(self, sim, agent) -> float:
        return 0

    def toString(self) -> str:
        return ""

    def copy(self):
        return Expression()

#---Operators---#

class BinaryOperator(Condition):

    def __init__(self, cond: Condition, cond2: Condition):
        Condition.__init__(self)
        self.cond, self.cond2 = cond, cond2
        self.conditionType = "BinaryOperator"

    def getDescendants(self, parent=(None,0), descendantList=None):
        if descendantList is None:
            descendantList = []
        Condition.getDescendants(self, parent, descendantList)
        self.cond.getDescendants((self, 0), descendantList)
        self.cond2.getDescendants((self, 1), descendantList)
        return descendantList

    def getRemoveables(self, parent=(None, 0), removeableList=None):
        if removeableList is None:
            removeableList = []

        if self.cond.isOperator():
            self.cond.getRemoveables((self, 0), removeableList)
        else:
            removeableList.append((self.cond2, parent))
        if self.cond2.isOperator():
            self.cond2.getRemoveables((self, 1), removeableList)
        else:
            removeableList.append((self.cond, parent))

        return removeableList

    def size(self) -> int:
        return 1 + self.cond.size() + self.cond2.size()


class AND(BinaryOperator):

    def run(self, sim, agent) -> bool:
        return self.cond.run(sim, agent) and self.cond2.run(sim, agent)

    def toString(self) -> str:
        return f"({self.cond.toString()} AND {self.cond2.toString()})"

    def copy(self):
        return AND(self.cond.copy(), self.cond2.copy())


class OR(BinaryOperator):

    def run(self, sim, agent) -> bool:
        return self.cond.run(sim, agent) or self.cond2.run(sim, agent)

    def toString(self) -> str:
        return f"({self.cond.toString()} OR {self.cond2.toString()})"

    def copy(self):
        return OR(self.cond.copy(), self.cond2.copy())

class NOT(Condition):

    def __init__(self, cond):
        Condition.__init__(self)
        self.cond = cond
        self.conditionType = "UnaryOperator"

    def run(self, sim, agent) -> bool:
        return not self.cond.run(sim, agent)

    def toString(self) -> str:
        return f"NOT {self.cond.toString()}"

    def getDescendants(self, parent=(None,0), descendantList=None):
        if descendantList is None:
            descendantList = []
        Condition.getDescendants(self, parent, descendantList)
        self.cond.getDescendants((self, 0), descendantList)
        return descendantList

    def getRemoveables(self, parent=(None,0), removeableList=None):
        if removeableList is None:
            removeableList = []

        if self.cond.isOperator():
            self.cond.getRemoveables((self, 0), removeableList)
        else:
            removeableList.append((self.cond, parent))

        return removeableList

    def copy(self):
        return NOT(self.cond.copy())

    def size(self) -> int:
        return 1 + self.cond.size()


class BinaryExpression(Expression):

    def __init__(self, expr1: Expression, expr2: Expression):
        Expression.__init__(self)
        self.expr1, self.expr2 = expr1, expr2
        self.exprType = "BinaryExpr"
        self.symbol = ""

    def calculate(self, x1: float, x2: float):
        return 0

    def evaluate(self, sim, agent) -> float:
        return self.calculate(self.expr1.evaluate(sim, agent), self.expr2.evaluate(sim, agent))

    def toString(self) -> str:
        return f"{self.expr1.toString()} {self.symbol} {self.expr2.toString()}"

class Addition(BinaryExpression):

    def __init__(self, expr1: Expression, expr2: Expression):
        BinaryExpression.__init__(self, expr1, expr2)
        self.symbol = "+"

    def calculate(self, x1, x2) -> float:
        return x1 + x2

    def copy(self):
        return Addition(self.expr1.copy(), self.expr2.copy())


class Subtraction(BinaryExpression):

    def __init__(self, expr1: Expression, expr2: Expression):
        BinaryExpression.__init__(self, expr1, expr2)
        self.symbol = "-"

    def calculate(self, x1, x2) -> float:
        return x1 - x2

    def copy(self):
        return Subtraction(self.expr1.copy(), self.expr2.copy())

class Multiplication(BinaryExpression):

    def __init__(self, expr1: Expression, expr2: Expression):
        BinaryExpression.__init__(self, expr1, expr2)
        self.symbol = "*"

    def calculate(self, x1, x2) -> float:
        return x1 * x2

    def copy(self):
        return Multiplication(self.expr1.copy(), self.expr2.copy())

class Division(BinaryExpression):

    def __init__(self, expr1: Expression, expr2: Expression):
        BinaryExpression.__init__(self, expr1, expr2)
        self.symbol = "/"

    def calculate(self, x1, x2) -> float:
        if x1 == 0:
            return 0
        if x2 == 0:
            return 999
        return x1 / x2

    def copy(self):
        return Division(self.expr1.copy(), self.expr2.copy())

class Constant(Expression):

    def __init__(self, value):
        Expression.__init__(self)
        self.value = value
        self.exprType = "Const"

    def evaluate(self, sim, agent) -> float:
        return self.value

    def toString(self) -> str:
        return str(self.value)

    def copy(self):
        return Constant(self.value)


class Boltzmann(Expression):

    def __init__(self, expr1: Expression, expr2: Expression, temperature: Constant, pMax: float = 1):
        Expression.__init__(self)
        self.expr1, self.expr2 = expr1, expr2
        self.temperature = temperature
        self.pMax = pMax
        self.exprType = "value"

    def evaluate(self, sim, agent) -> float:
        E1, E2 = self.expr1.evaluate(sim, agent), self.expr2.evaluate(sim, agent)
        T = self.temperature.evaluate(sim, agent)
        frac = np.exp((E1 - E2) / T)
        return self.pMax / (1 + frac)

    def toString(self) -> str:
        return f"Boltz({self.expr1.toString()}, {self.expr2.toString()}, {self.temperature.toString()})"

    def copy(self):
        return Boltzmann(self.expr1.copy(), self.expr2.copy(), self.temperature.copy(), self.pMax)

class DynamicValue(Expression):

    def __init__(self, target: str):
        Expression.__init__(self)
        self.exprType = "Value"
        self.target = target

    def evaluate(self, sim, agent) -> float:
        if self.target == "self":
            return self.sense(sim, agent)
        elif self.target == "saved":
            if agent.targetAgent is not None:
                return self.sense(sim, agent.targetAgent)
            else:
                return 0
        elif self.target == "queried":

            if agent.queriedAgent is not None:
                return self.sense(sim, agent.queriedAgent)
            else:
                return 0

    def sense(self, sim, agent) -> float:
        return 0

    def toString(self) -> str:
        return f"{self.target}.{self.varName()}"

    def varName(self) -> str:
        return ""


#---InequalityBase---#

class GreaterThan(Condition):

    def __init__(self, expr1: Expression, expr2: Expression, andEqual=False):
        Condition.__init__(self)

        self.expr1, self.expr2 = expr1, expr2
        self.andEqual = andEqual

        self.conditionType = "Inequality"

    def run(self, sim, agent) -> bool:
        if self.andEqual:
            return self.expr1.evaluate(sim, agent) >= self.expr2.evaluate(sim, agent)
        else:
            return self.expr1.evaluate(sim, agent) > self.expr2.evaluate(sim, agent)

    def toString(self) -> str:
        return f"{self.expr1.toString()} > {self.expr2.toString()}"

    def getLeaves(self, parent=(None,0), leafList=None):
        if leafList is None:
            leafList = []
        leafList.append((self, parent))
        return leafList

    def copy(self):
        return GreaterThan(self.expr1.copy(), self.expr2.copy())


# class InequalityAtomFactory():
#
#     def __init__(self, lower, upper):
#         self.lower, self.upper = lower, upper
#
#     def create(self):
#         threshold = np.random.uniform(self.lower, self.upper)
#         greater = np.random.random() < 0.5
#         atom = self.createAtom(threshold, greater)
#         atom.lower = self.lower
#         atom.upper = self.upper
#         return atom
#
#     def createAtom(self, threshold, greater):
#         pass


#----BooleanImplementations-----#

class AtomicBoolean(Condition):

    def __init__(self, target: str):
        Condition.__init__(self)
        self.target = target

    def getLeaves(self, parent=(None,0), leafList=None):
        if leafList is None:
            leafList = []
        leafList.append((self, parent))
        return leafList

    def run(self, sim, agent) -> bool:
        if self.target == "self":
            return self.sense(sim, agent)
        elif self.target == "saved":
            if agent.targetAgent is not None:
                return self.sense(sim, agent.targetAgent)
            else:
                return False
        elif self.target == "queried":
            if agent.queriedAgent is not None:
                return self.sense(sim, agent.queriedAgent)
            else:
                return False

    def sense(self, sim, agent) -> bool:
        pass

    def toString(self) -> str:
        return f"{self.target}.{self.varName()}"

    def varName(self) -> str:
        return ""

class IsHoldingFood(AtomicBoolean):

    def sense(self, sim, agent) -> bool:
        return agent.isHoldingFood

    def varName(self) -> str:
        return "IsHoldingFood"

    def copy(self):
        return IsHoldingFood(self.target)

class IsWaypointSet(AtomicBoolean):

    def __init__(self, target: str, index: int = 0):
        AtomicBoolean.__init__(self, target)
        self.index = index

    def sense(self, sim, agent) -> bool:
        return agent.coordsArray[self.index, 0] >= 0 and agent.coordsArray[self.index, 1] >= 0

    def varName(self) -> str:
        return "IsWaypointSet"

    def copy(self):
        return IsWaypointSet(self.target, self.index)

class IsTargetAgentSet(AtomicBoolean):

    def sense(self, sim, agent) -> bool:
        return agent.targetAgent is not None

    def varName(self) -> str:
        return "TargetAgentSet"

    def copy(self):
        return IsTargetAgentSet(self.target)

class RandomChance(AtomicBoolean):

    def __init__(self, target: str, p: Expression):
        AtomicBoolean.__init__(self, target)
        self.p = p

    def sense(self, sim, agent) -> bool:
        return np.random.random() < self.p.evaluate(sim, agent)

    def varName(self) -> str:
        return f"random(p={self.p.toString()})"

    def copy(self):
        return RandomChance(self.target, self.p.copy())


class CheckInternalBool(AtomicBoolean):

    def __init__(self, target, index):
        AtomicBoolean.__init__(self, target)
        self.index = index

    def sense(self, sim, agent) -> bool:
        return agent.boolArray[self.index]

    def varName(self) -> str:
        return f"Bool{self.index}"

    def copy(self):
        return CheckInternalBool(self.target, self.index)


class HasNearbyFood(AtomicBoolean):

    def sense(self, sim, agent) -> bool:

        for x, y in sim.foodChunkManager.getNeighbours(agent.x, agent.y):
            distance = sim.getDistance(agent.x, agent.y, x, y)
            if distance <= sim.smellRange:
                return True

        return False

    def varName(self) -> str:
        return "HasNearbyFood"

    def copy(self):
        return HasNearbyFood(self.target)


#---InequalityImplementations---#

class GetCurrentCoord(DynamicValue):

    def sense(self, sim, agent):
        return [agent.x, agent.y]

    def varName(self) -> str:
        return "CurrentCoord"

    def copy(self):
        return GetCurrentCoord(self.target)

class NearbyFoodAmount(DynamicValue):

    def sense(self, sim, agent):

        foodCount = 0
        for x, y in sim.foodChunkManager.getNeighbours(agent.x, agent.y):
            distance = sim.getDistance(agent.x, agent.y, x, y)
            if distance <= sim.smellRange:
                foodCount += 1

        return foodCount

    def varName(self) -> str:
        return "NearbyFood"

    def copy(self):
        return NearbyFoodAmount(self.target)

class NearbyAgentAmount(DynamicValue):

    def sense(self, sim, agent):
        return len(agent.getNearbyAgents(sim))

    def varName(self) -> str:
        return "NearbyAgentAmount"

    def copy(self):
        return NearbyAgentAmount(self.target)

class AgentFoodDensity(DynamicValue):

    def sense(self, sim, agent):
        return agent.foodDensity

    def varName(self) -> str:
        return "AgentFoodDensity"

    def copy(self):
        return AgentFoodDensity(self.target)

class GroundFoodDensity(DynamicValue):

    def sense(self, sim, agent):
        return sim.foodDensityArray[agent.x, agent.y]

    def varName(self) -> str:
        return "GroundFoodDensity"

    def copy(self):
        return GroundFoodDensity(self.target)

class WaypointFoodDensity(DynamicValue):

    def sense(self, sim, agent):
        if agent.waypointCoords is None:
            return 0

        x0, y0 = agent.waypointCoords
        return sim.foodDensityArray[x0, y0]

    def varName(self) -> str:
        return "WaypointFoodDensity"

    def copy(self):
        return WaypointFoodDensity(self.target)

class WaypointDistance(DynamicValue):

    def sense(self, sim, agent):
        if agent.waypointCoords is None:
            return 999

        xWaypoint, yWaypoint = agent.waypointCoords
        return sim.getDistance(agent.x, agent.y, xWaypoint, yWaypoint)

    def varName(self) -> str:
        return "WaypointDistance"

    def copy(self):
        return WaypointDistance(self.target)


class WaypointColonyDistance(DynamicValue):

    def __init__(self, target: str, index: int):
        DynamicValue.__init__(self, target)
        self.index = index

    def sense(self, sim, agent):
        if agent.coordsArray[self.index, 0] < 0 or agent.coordsArray[self.index, 1] < 0:
            return 999

        xWaypoint, yWaypoint = agent.coordsArray[self.index, :]
        return sim.getDistance(sim.colonyX, sim.colonyY, xWaypoint, yWaypoint)

    def varName(self) -> str:
        return "WaypointColonyDistance"

    def copy(self):
        return WaypointColonyDistance(self.target, self.index)

class WaypointFoodAmount(DynamicValue):

    def sense(self, sim, agent):
        if agent.waypointCoords is None:
            return 0

        xWaypoint, yWaypoint = agent.waypointCoords
        return sim.foodAmountArray[xWaypoint, yWaypoint]

    def varName(self) -> str:
        return "WaypointFoodAmount"

    def copy(self):
        return WaypointFoodAmount(self.target)

class ColonyDistance(DynamicValue):

    def sense(self, sim, agent):
        return sim.getDistance(sim.colonyX, sim.colonyY, agent.x, agent.y)

    def varName(self) -> str:
        return "ColonyDistance"

    def copy(self):
        return ColonyDistance(self.target)

# Calculates the distance between own waypoint and waypoint of set target(queried or saved)
class DistanceBetweenWaypoints(DynamicValue):

    def __init__(self, target, coord1: Expression, coord2: Expression):
        DynamicValue.__init__(self, target)
        self.coord1, self.coord2 = coord1, coord2

    def sense(self, sim, agent):

        x0, y0 = self.coord1.evaluate(sim, agent)
        x1, y1 = self.coord2.evaluate(sim, agent)

        if x0 >= 0 and y0 >= 0 and x1 >= 0 and y1 >= 0:
            return sim.getDistance(x0, y0, x1, y1)
        else:
            return 999

    def varName(self) -> str:
        return "DistanceBetweenWaypoints"

    def copy(self):
        return DistanceBetweenWaypoints(self.target, self.coord1, self.coord2)

# Calculates quality of food at waypoint (food density / distance from colony)
class WaypointFoodEfficiency(DynamicValue):

    def sense(self, sim, agent):

        if agent.waypointCoords is None:
            return 0
        else:
            xWaypoint, yWaypoint = agent.waypointCoords
            distance = sim.getDistance(sim.colonyX, sim.colonyY, xWaypoint, yWaypoint)
            foodDensity = sim.foodDensityArray[xWaypoint, yWaypoint]
            return foodDensity / distance

    def varName(self) -> str:
        return "WaypointFoodEfficiency"

    def copy(self):
        return WaypointFoodEfficiency(self.target)


class CheckInternalCounter(DynamicValue):

    def __init__(self, target: str, index: int):
        DynamicValue.__init__(self, target)
        self.index = index

    def sense(self, sim, agent):
        return agent.counterArray[self.index]

    def varName(self) -> str:
        return f"Counter{self.index}"

    def copy(self):
        return CheckInternalCounter(self.target, self.index)

# Returns the value of a float that is stored in the memory of an agent
class CheckInternalFloat(DynamicValue):

    def __init__(self, target: str, index: int):
        DynamicValue.__init__(self, target)
        self.index = index

    def sense(self, sim, agent):
        value = agent.floatArray[self.index]

        # If checking memory of other agent, sometimes distort the data
        if self.target != "self" and np.random.random() < sim.pDistortFloat:
            distortion = np.random.normal(0, sim.stdDistortFloat)
            value *= 2**distortion
        return value

    def varName(self) -> str:
        return f"InternalFloat{self.index}"

    def copy(self):
        return CheckInternalFloat(self.target, self.index)

# Returns a coordinate that is saved in the internal memory of an agent
class CheckInternalCoord(DynamicValue):

    def __init__(self, target: str, index: int):
        DynamicValue.__init__(self, target)
        self.index = index

    def sense(self, sim, agent):
        xCoord, yCoord = agent.coordsArray[self.index, :]

        # If reading memory of other agent, sometimes distort the coordinate
        if self.target != "self" and np.random.random() < sim.pDistortCoord:
            nDistort = np.random.poisson(sim.stdDistortCoord)
            for _ in range(nDistort):
                nextCoords = sim.pathfinder.getPrev(xCoord, yCoord, xCoord, yCoord)
                xCoord, yCoord = nextCoords[np.random.randint(len(nextCoords))]

        return [xCoord, yCoord]

    def varName(self) -> str:
        return f"InternalCoords{self.index}"

    def copy(self):
        return CheckInternalCoord(self.target, self.index)


#---FactoryList---#

def getBooleanFactories():
    return [IsHoldingFood, IsWaypointSet, IsTargetAgentSet]

def getValueFactories():
    return [NearbyFoodAmount, AgentFoodDensity, GroundFoodDensity, WaypointFoodDensity, WaypointFoodAmount, WaypointDistance, ColonyDistance]


class OptimizationParameters:

    def __init__(self):
        self.pNOT = 0.15
        self.pConst = 0.4
        self.pTargetSelf = 0.9
        self.constMin = 0
        self.constMax = 10
        self.conditionAmountMutateRate = 0.05
        self.conditionMutateRate = 0.05
        self.finEdgeMutationRate = 0.05
        self.actionMutationRate = 1
        self.actionResetChance = 0.05
        self.pQueriedValue = 0.5
        self.elitismChance = 0.1

        self.tMax = 4000
        self.n = 5
        self.runs = 10

    def toString(self):

        parameterDict = {"pNot": self.pNOT,
                         "pConst:": self.pConst,
                         "pTargetSelf": self.pTargetSelf,
                         "constMin": self.constMin,
                         "constMax": self.constMax,
                         "conditionAmountMutateRate": self.conditionAmountMutateRate,
                         "conditionMutateRate": self.conditionMutateRate,
                         "finEdgeMutationRate": self.finEdgeMutationRate,
                         "actionMutationRate": self.actionMutationRate,
                         "actionResetChance": self.actionResetChance,
                         "pQueriedValue": self.pQueriedValue,
                         "tMax": self.tMax,
                         "n": self.n,
                         "runs": self.runs}

        text = ""
        for name, value in parameterDict.items():
            text += f"{name} = {value}\n"
        return text



