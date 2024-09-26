
#-----Imports-----#
import numpy as np


class Condition:

    def __init__(self):
        self.conditionType = ""

    def evaluate(self, sim, agent) -> bool:
        return False

    def toString(self) -> str:
        return ""

    def getDescendants(self, parent=(None,0), descendantList=[]):
        descendantList.append((self, parent))
        return descendantList

    def getRemoveables(self, parent=(None,0), removableList=[]):
        return removableList

    def isOperator(self):
        return self.conditionType == "BinaryOperator" or self.conditionType == "UnaryOperator"

    def copy(self):
        return Condition()


class Expression:

    def __init__(self):
        self.exprType = ""

    def evaluate(self, sim, agent) -> int:
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

    def getDescendants(self, parent=(None,0), descendantList=[]):
        Condition.getDescendants(self, parent, descendantList)
        self.cond.getDescendants((self, 0), descendantList)
        self.cond2.getDescendants((self, 1), descendantList)
        return descendantList

    def getRemoveables(self, parent=(None, 0), removeableList=[]):

        if self.cond.isOperator():
            self.cond.getRemoveables((self, 0), removeableList)
        else:
            removeableList.append((self.cond2, parent))
        if self.cond2.isOperator():
            self.cond2.getRemoveables((self, 1), removeableList)
        else:
            removeableList.append((self.cond, parent))

        return removeableList


class AND(BinaryOperator):

    def evaluate(self, sim, agent) -> bool:
        return self.cond.evaluate(sim, agent) and self.cond2.evaluate(sim, agent)

    def toString(self) -> str:
        return f"({self.cond.toString()} AND {self.cond2.toString()})"

    def copy(self):
        return AND(self.cond.copy(), self.cond2.copy())


class OR(BinaryOperator):

    def evaluate(self, sim, agent) -> bool:
        return self.cond.evaluate(sim, agent) or self.cond2.evaluate(sim, agent)

    def toString(self) -> str:
        return f"({self.cond.toString()} OR {self.cond2.toString()})"

    def copy(self):
        return OR(self.cond.copy(), self.cond2.copy())

class NOT(Condition):

    def __init__(self, cond):
        Condition.__init__(self)
        self.cond = cond
        self.conditionType = "UnaryOperator"

    def evaluate(self, sim, agent) -> bool:
        return not self.cond.evaluate(sim, agent)

    def toString(self) -> str:
        return f"NOT {self.cond.toString()}"

    def getDescendants(self, parent=(None,0), descendantList=[]):
        Condition.getDescendants(self, parent, descendantList)
        self.cond.getDescendants((self, 0), descendantList)
        return descendantList

    def getRemoveables(self, parent=(None,0), removeableList=[]):

        if self.cond.isOperator():
            self.cond.getRemoveables((self, 0), removeableList)
        else:
            removeableList.append((self.cond, parent))

        return removeableList

    def copy(self):
        return NOT(self.cond.copy())


class Addition(Expression):

    def __init__(self, expr1, expr2):
        Expression.__init__(self)
        self.expr1, self.expr2 = expr1, expr2
        self.exprType = "BinaryExpr"

    def evaluate(self, sim, agent) -> int:
        return self.expr1.evaluate(sim, agent) + self.expr2.evaluate(sim, agent)

    def toString(self) -> str:
        return f"{self.expr1.toString()} + {self.expr2.toString()}"

    def copy(self):
        return Addition(self.expr1.copy(), self.expr2.copy())


class Subtraction(Expression):

    def __init__(self, expr1, expr2):
        Expression.__init__(self)
        self.expr1, self.expr2 = expr1, expr2
        self.exprType = "BinaryExpr"

    def evaluate(self, sim, agent) -> int:
        return self.expr1.evaluate(sim, agent) - self.expr2.evaluate(sim, agent)

    def toString(self) -> str:
        return f"{self.expr1.toString()} - {self.expr2.toString()}"

    def copy(self):
        return Subtraction(self.expr1.copy(), self.expr2.copy())

class Constant(Expression):

    def __init__(self, value):
        Expression.__init__(self)
        self.value = value
        self.exprType = "Const"

    def evaluate(self, sim, agent) -> int:
        return self.value

    def toString(self) -> str:
        return str(self.value)

    def copy(self):
        return Constant(self.value)



class DynamicValue(Expression):

    def __init__(self, target: str):
        Expression.__init__(self)
        self.exprType = "Value"
        self.target = target

    def evaluate(self, sim, agent) -> int:
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

    def sense(self, sim, agent) -> int:
        return 0


#---InequalityBase---#

class GreaterThan(Condition):

    def __init__(self, expr1, expr2):
        Condition.__init__(self)

        self.expr1, self.expr2 = expr1, expr2

        self.conditionType = "Inequality"

    def evaluate(self, sim, agent) -> bool:
        return self.expr1.evaluate(sim, agent) > self.expr2.evaluate(sim, agent)

    def toString(self) -> str:
        return f"{self.expr1.toString()} > {self.expr2.toString()}"

    def getLeaves(self, parent=(None,0), leafList=[]):
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

    def getLeaves(self, parent=(None,0), leafList=[]):
        leafList.append((self, parent))
        return leafList

    def evaluate(self, sim, agent) -> bool:
        if self.target == "self":
            return self.sense(sim, agent)
        elif self.target == "saved":
            if agent.targetAgent is not None:
                return self.sense(sim, agent.targetAgent)
            else:
                return False
        elif self.target == "queried":
            if agent.queriedAgent is not None:
                return self.sense(sim, agent.queriedAgent )
            else:
                return False

    def sense(self, sim, agent) -> bool:
        pass

class IsHoldingFood(AtomicBoolean):

    def sense(self, sim, agent) -> bool:
        return agent.isHoldingFood

    def toString(self) -> str:
        return "IsHoldingFood"

    def copy(self):
        return IsHoldingFood(self.target)

class IsWaypointSet(AtomicBoolean):

    def sense(self, sim, agent) -> bool:
        return agent.waypointPathfinder is not None

    def toString(self) -> str:
        return "IsWaypointSet"

    def copy(self):
        return IsWaypointSet(self.target)

class IsTargetAgentSet(AtomicBoolean):

    def sense(self, sim, agent) -> bool:
        return agent.targetAgent is not None

    def toString(self) -> str:
        return "TargetAgentSet"

    def copy(self):
        return IsTargetAgentSet(self.target)

#---InequalityImplementations---#

class NearbyFoodAmount(DynamicValue):

    def sense(self, sim, agent):

        foodCount = 0
        for x, y in sim.foodPosList:
            pathfinder = sim.getPathfinder(x, y)
            distance = pathfinder.getDistance(agent.x, agent.y)
            if distance <= sim.smellRange:
                foodCount += 1
        return foodCount

    def toString(self) -> str:
        return "NearbyFood"

    def copy(self):
        return NearbyFoodAmount(self.target)

class AgentFoodDensity(DynamicValue):

    def sense(self, sim, agent):
        return agent.foodDensity

    def toString(self) -> str:
        return "AgentFoodDensity"

    def copy(self):
        return AgentFoodDensity(self.target)

class GroundFoodDensity(DynamicValue):

    def sense(self, sim, agent):
        return sim.foodDensityArray[agent.x, agent.y]

    def toString(self) -> str:
        return "GroundFoodDensity"

    def copy(self):
        return GroundFoodDensity(self.target)


#---FactoryList---#

# def getFactoryList():
#     operatorList = ["AND","OR","!"]
#     atomList = [NearbyFoodAmountFactory(0, 10)]
#
#     return operatorList, atomList


def getBooleanFactories():
    factoryList = []
    factoryList.append(lambda targetSelf: IsHoldingFood(targetSelf))
    factoryList.append(lambda targetSelf: IsWaypointSet(targetSelf))
    factoryList.append(lambda targetSelf: IsTargetAgentSet(targetSelf))
    return factoryList

def getValueFactories():
    factoryList = []
    factoryList.append(lambda targetSelf: NearbyFoodAmount(targetSelf))
    factoryList.append(lambda targetSelf: AgentFoodDensity(targetSelf))
    factoryList.append(lambda targetSelf: GroundFoodDensity(targetSelf))
    return factoryList








