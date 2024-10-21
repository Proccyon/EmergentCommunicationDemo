
#-----Imports-----#
import numpy as np
from TaskNode import initNodes
import Conditions
from Conditions import *
from Actions import *
from MutationMethods import *
from BaseClasses import Brain

class Automata(Brain):

    def __init__(self):
        Brain.__init__(self)
        self.nodes = initNodes()
        self.n = len(self.nodes)
        self.conditionEdgeArray = np.full((self.n, self.n), None, dtype=Condition)
        self.actionArray = np.full((self.n, self.n), None, dtype=Action)

        self.finishEdgeArray = np.zeros(self.n, dtype=int)
        self.finishActionArray = np.full(self.n, None, dtype=Action)

    def initBaseAutomata(self):

        self.finishEdgeArray[0] = 1
        self.finishEdgeArray[1] = 0
        self.finishEdgeArray[2] = 1

        self.conditionEdgeArray[0, 2] = GreaterThan(NearbyFoodAmount("self"), Constant(0))

        return self

    def initMemorizingAutomata(self):

        self.finishEdgeArray[0] = 1
        self.finishEdgeArray[1] = 0
        self.finishEdgeArray[2] = 1
        self.finishEdgeArray[3] = 2

        self.conditionEdgeArray[0, 2] = GreaterThan(NearbyFoodAmount("self"), Constant(0))
        self.conditionEdgeArray[2, 2] = GreaterThan(GroundFoodDensity("self"), Constant(0))

        self.actionArray[2, 2] = SetWaypoint()

        self.conditionEdgeArray[0, 3] = IsWaypointSet("self")
        self.finishActionArray[3] = ResetWaypoint()

        return self

    def initCommunicatingAutomata(self):

        self.finishEdgeArray[0] = 1
        self.finishEdgeArray[1] = 0
        self.finishEdgeArray[2] = 1
        self.finishEdgeArray[3] = 2

        self.conditionEdgeArray[0, 0] = OR(NOT(IsHoldingFood("self")), IsHoldingFood("self"))
        self.conditionEdgeArray[1, 1] = OR(NOT(IsHoldingFood("self")), IsHoldingFood("self"))
        self.conditionEdgeArray[0, 2] = GreaterThan(NearbyFoodAmount("self"), Constant(0))
        self.conditionEdgeArray[2, 2] = GreaterThan(GroundFoodDensity("self"), Constant(0))

        self.actionArray[0, 0] = SelectTargetAgent(GreaterThan(WaypointFoodDensity("queried"), WaypointFoodDensity("self")))
        self.actionArray[1, 1] = SelectTargetAgent(GreaterThan(WaypointFoodDensity("queried"), WaypointFoodDensity("self")))
        self.actionArray[2, 2] = SetWaypoint()
        self.actionArray[0, 3] = CopyWaypoint()

        self.conditionEdgeArray[0, 3] = OR(IsWaypointSet("self"), IsTargetAgentSet("self"))

        return self

    # Runs the automata for a single agent
    # 1. Move through the automata using conditional edges if possible
    # 2. Perform the action associated with the current node
    # 3. If task is finished move through the automata using the finish edge
    def run(self, sim, agent):

        # Loop through all conditional edges from this node to other nodes
        nextNodes = []
        for i in range(self.n):
            condition = self.conditionEdgeArray[agent.currentNode, i]
            if condition is None:
                continue

            # Check if condition is met
            if condition.run(sim, agent):
                nextNodes.append(i)

        # If more than one condition is met, select a random edge to follow
        if len(nextNodes) > 0:
            nextNode = np.random.choice(nextNodes)

            action = self.actionArray[agent.currentNode, nextNode]
            if action is not None:
                action.run(sim, agent)

            agent.currentNode = nextNode

        # Perform the task of the node
        isFinished = not self.nodes[agent.currentNode].act(sim, agent)

        # If action could not be performed, go to new node using the finish edge
        if isFinished:

            action = self.finishActionArray[agent.currentNode]
            if action is not None:
                action.run(sim, agent)

            agent.currentNode = self.finishEdgeArray[agent.currentNode]

    def toString(self):

        output = "digraph G {\n"

        for i, node in enumerate(self.nodes):
            output += f'n{i} [label="{node.name}"]\n'

        for i in range(self.n):
            for j in range(self.n):
                condition = self.conditionEdgeArray[i, j]
                if condition is None:
                    continue

                label = condition.toString()
                if self.actionArray[i, j] is not None:
                    label += f"\n{self.actionArray[i,j].toString()}"

                output += f'n{i}->n{j} [label="{label}"]\n'

        for i in range(self.n):
            label = ""
            action = self.finishActionArray[i]
            if action is not None:
                label += f"\n{action.toString()}"

            output += f'n{i}->n{self.finishEdgeArray[i]} [style=dashed,label="{label}"]\n'

        output += "}"

        return output

    def copy(self):

        newCopy = Automata()

        newCopy.finishEdgeArray = self.finishEdgeArray.copy()

        for i in range(self.n):
            action = self.finishActionArray[i]
            if action is None:
                newCopy.finishActionArray[i] = None
            else:
                newCopy.finishActionArray[i] = action.copy()

        for i in range(self.n):
            for j in range(self.n):
                condition = self.conditionEdgeArray[i, j]
                if condition is None:
                    newCopy.conditionEdgeArray[i, j] = None
                else:
                    newCopy.conditionEdgeArray[i, j] = condition.copy()

                action = self.actionArray[i, j]
                if action is None:
                    newCopy.actionArray[i, j] = None
                else:
                    newCopy.actionArray[i, j] = action.copy()

        return newCopy


    # def createOffspring(self, op: OptimizationParameters):
    #
    #     child = self.copy()
    #     child.mutate(op)
    #     return child

    #---MutationMethods---#

    def mutate(self, op: OptimizationParameters):

        self.booleanFactories = Conditions.getBooleanFactories()
        self.valueFactories = Conditions.getValueFactories()
        self.actionFactories = getActionFactories()

        self.mutateConditionAmount(op)
        self.mutateConditions(op)
        self.mutateFinishEdges(op)
        self.mutateActions(op)

    # Randomly increases/decreases condition size
    def mutateConditions(self, op: OptimizationParameters):
        for i in range(self.n):
            for j in range(self.n):
                condition = self.conditionEdgeArray[i, j]
                if condition is not None:
                    self.conditionEdgeArray[i, j] = mutateCondition(condition, op)

    def mutateConditionAmount(self, op: OptimizationParameters):

        amount = np.random.poisson(self.n * (self.n - 1) * op.conditionAmountMutateRate)

        if amount == 0:
            return

        emptySlots = []
        filledSlots = []

        for i in range(self.n):
            for j in range(self.n):
                if self.conditionEdgeArray[i,j] is None:
                    emptySlots.append((i,j))
                else:
                    filledSlots.append((i,j))

        if np.random.random() < 0.5:
            if len(emptySlots) < amount:
                amount = len(emptySlots)

            selectedSlotIds = np.random.choice(len(emptySlots), size=amount, replace=False)

            for id in selectedSlotIds:
                i, j = emptySlots[id]
                self.conditionEdgeArray[i, j] = generateRandomCondition(op)

        else:
            if len(filledSlots) < amount:
                amount = len(filledSlots)

            selectedSlotIds = np.random.choice(len(filledSlots), size=amount, replace=False)

            for id in selectedSlotIds:
                i, j = filledSlots[id]
                self.conditionEdgeArray[i, j] = None

    def mutateFinishEdges(self, op:OptimizationParameters):

        mutations = np.random.poisson(self.n * op.finEdgeMutationRate)

        for _ in range(mutations):
            i, j = np.random.choice(self.n, size=2, replace=False)
            self.finishEdgeArray[i] = j

    def mutateActions(self, op: OptimizationParameters):

        for i in range(self.n):
            action = self.finishActionArray[i]
            if action is not None and np.random.random() < op.actionMutationRate:
                action.mutate(op)
            if np.random.random() < op.actionResetChance:
                self.finishActionArray[i] = generateRandomAction(op)

        for i in range(self.n):
            for j in range(self.n):
                action = self.actionArray[i, j]
                if action is not None and np.random.random() < op.actionMutationRate:
                    action.mutate(op)
                if np.random.random() < op.actionResetChance:
                    self.actionArray[i, j] = generateRandomAction(op)

    def size(self) -> int:

        size = 0
        for i in range(self.n):
            for j in range(self.n):
                condition = self.conditionEdgeArray[i, j]
                if condition is None:
                    continue
                size += condition.size()
        return size










