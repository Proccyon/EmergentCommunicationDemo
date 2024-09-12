
#-----Imports-----#
import numpy as np


class Expression:

    def __init__(self):
        self.conditionType = ""

    def evaluate(self, sim, agent) -> bool:
        return False

    def toString(self) -> str:
        return ""

#---Operators---#

class AND(Expression):

    def __init__(self, expr1, expr2):
        Expression.__init__(self)
        self.expr1, self.expr2 = expr1, expr2
        self.conditionType = "BinaryOperator"

    def evaluate(self, sim, agent) -> bool:
        return self.expr1.evaluate(sim, agent) and self.expr2.evaluate(sim, agent)

    def toString(self) -> str:
        return f"({self.expr1.toString()} AND {self.expr2.toString()})"

class OR(Expression):

    def __init__(self, expr1, expr2):
        Expression.__init__(self)
        self.expr1, self.expr2 = expr1, expr2
        self.conditionType = "BinaryOperator"

    def evaluate(self, sim, agent) -> bool:
        return self.expr1.evaluate(sim, agent) or self.expr2.evaluate(sim, agent)

    def toString(self) -> str:
        return f"({self.expr1.toString()} OR {self.expr2.toString()})"

class NOT(Expression):

    def __init__(self, expr):
        Expression.__init__(self)
        self.expr = expr
        self.conditionType = "UnaryOperator"

    def evaluate(self, sim, agent) -> bool:
        return not self.expr.evaluate(sim, agent)

    def toString(self) -> str:
        return f"NOT {self.expr.toString()}"

#---InequalityBase---#

class InequalityAtom(Expression):

    def __init__(self, threshold, greater):
        Expression.__init__(self)

        self.threshold = threshold
        self.greater = greater

        self.conditionType = "Inequality"

    def evaluate(self, sim, agent) -> bool:
        if self.greater:
            return self.sense(sim, agent) > self.threshold
        else:
            return self.sense(sim, agent) <= self.threshold

    def sense(self, sim, agent):
        return 0

    def variableName(self) -> str:
        return ""

    def toString(self) -> str:
        if self.greater:
            sign = ">"
        else:
            sign = "<="

        return f"{self.variableName()} {sign} {self.threshold}"


class InequalityAtomFactory():

    def __init__(self, lower, upper):
        self.lower, self.upper = lower, upper

    def create(self):
        threshold = np.random.uniform(self.lower, self.upper)
        greater = np.random.random() < 0.5
        atom = self.createAtom(threshold, greater)
        atom.lower = self.lower
        atom.upper = self.upper
        return atom

    def createAtom(self, threshold, greater):
        pass


#----BooleanImplementations-----#

class IsHoldingFood(Expression):

    def evaluate(self, sim, agent) -> bool:
        return agent.isHoldingFood

    def toString(self) -> str:
        return "IsHoldingFood"

class IsWaypointSet(Expression):

    def evaluate(self, sim, agent) -> bool:
        return agent.waypointPathfinder is not None

    def toString(self) -> str:
        return "IsWaypointSet"

#---InequalityImplementations---#

class NearbyFoodAmount(InequalityAtom):

    def sense(self, sim, agent):

        foodCount = 0
        for pathfinder in sim.foodPathfinderList:
            distance = pathfinder.getDistance(agent.x, agent.y)
            if distance <= sim.smellRange:
                foodCount += 1

        return foodCount

    def variableName(self) -> str:
        return "NearbyFood"


class NearbyFoodAmountFactory(InequalityAtomFactory):

    def createAtom(self, threshold, greater):
        return NearbyFoodAmount(threshold, greater)


class AgentFoodDensity(InequalityAtom):

    def sense(self, sim, agent):
        return agent.foodDensity

    def variableName(self) -> str:
        return "AgentFoodDensity"

class GroundFoodDensity(InequalityAtom):

    def sense(self, sim, agent):
        return sim.foodDensityArray[agent.x, agent.y]

    def variableName(self) -> str:
        return "GroundFoodDensity"


#---FactoryList---#

def getFactoryList():
    operatorList = ["AND","OR","!"]
    atomList = [NearbyFoodAmountFactory(0, 10)]

    return operatorList, atomList










