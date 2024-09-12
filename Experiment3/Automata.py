
#-----Imports-----#
import numpy as np
from TaskNode import initNodes
from Conditions import Expression, getFactoryList, AND, OR, NOT, NearbyFoodAmount, GroundFoodDensity, IsWaypointSet, IsHoldingFood
from Action import Action, SetWaypoint, ResetWaypoint

class Automata:

    def __init__(self):
        self.nodes = initNodes()
        self.n = len(self.nodes)
        self.conditionEdgeArray = np.full((self.n, self.n), None, dtype=Expression)
        self.actionArray = np.full((self.n, self.n), None, dtype=Action)

        self.finishEdgeArray = np.zeros(self.n, dtype=int)
        self.finishActionArray = np.full(self.n, None, dtype=Action)

        self.operators, self.atomFactoryList = getFactoryList()

        self.thresholdMutateRate = 10
        self.operatorAdditionRate = 1
        self.thresholdMutateChance = self.thresholdMutateRate / (self.thresholdMutateRate + self.operatorAdditionRate)

        self.thresholdMutateStd = 0.1

        self.initBaseAutomata()


    def initBaseAutomata(self):

        self.finishEdgeArray[0] = 1
        self.finishEdgeArray[1] = 0
        self.finishEdgeArray[2] = 1
        self.finishEdgeArray[3] = 2

        self.conditionEdgeArray[0, 2] = NearbyFoodAmount(0, True)
        self.conditionEdgeArray[2, 2] = GroundFoodDensity(2, True)
        self.actionArray[2, 2] = SetWaypoint()

        self.conditionEdgeArray[0, 3] = IsWaypointSet()
        self.finishActionArray[3] = ResetWaypoint()

        #self.actionArray[0, 2] = SetWaypoint()
        #self.finishActionArray[2] = SetWaypoint()

        print(self.toString())


    #---MutationMethods---#

    def addEdge(self, indexIn, indexOut, condition):

        if indexIn == indexOut or not self.conditionEdgeArray[indexIn, indexOut] is None:
            return

        self.conditionEdgeArray[indexIn, indexOut] = condition

    def deleteEdge(self, indexIn, indexOut):

        if self.conditionEdgeArray[indexIn, indexOut] is None:
            return

        self.conditionEdgeArray[indexIn, indexOut] = None

    # def addRandomEdge(self):
    #
    #     i = np.random.randint(len(self.filledEdgeList))
    #     indexIn, indexOut = self.filledEdgeList[i]
    #
    #     condition = np.random.choice(self.atomFactoryList).create()
    #
    #     self.addEdge(indexIn, indexOut, condition)

    # def deleteRandomEdge(self):
    #
    #     i = np.random.randint(len(self.emptyEdgeList))
    #     indexIn, indexOut = self.emptyEdgeList[i]
    #
    #     self.deleteEdge(indexIn, indexOut)

    # def mutateRandomEdge(self):
    #
    #     i = np.random.randint(len(self.filledEdgeList))
    #     indexIn, indexOut = self.filledEdgeList[i]
    #     condition = self.edgeArray[indexIn, indexOut]
    #     self.edgeArray[indexIn, indexOut] = self.mutateCondition(condition)

    #Changes a random edge slightly
    def mutateCondition(self, condition):

        if condition.conditionType == "UnaryOperator":
            self.mutateCondition(condition.expr)
            return condition
        elif condition.conditionType == "BinaryOperator":
            self.mutateCondition(condition.expr1)
            self.mutateCondition(condition.expr2)
            return condition

        elif condition.conditionType == "Inequality":

            if self.thresholdMutateChance > np.random.random():
                std = self.thresholdMutateStd * (condition.upper - condition.lower)
                condition.threshold += np.random.normal(0, std)
                if condition.threshold < condition.lower: condition.threshold = condition.lower
                if condition.threshold > condition.upper: condition.threshold = condition.upper
                return condition
            else:
                newOperator = np.random.choice(self.operators)

                if newOperator == "!":
                    return NOT(condition)

                additionalCondition = np.random.choice(self.atomFactoryList).create()

                if newOperator == "AND":
                    return AND(condition, additionalCondition)
                elif newOperator == "OR":
                    return OR(condition, additionalCondition)

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
            if condition.evaluate(sim, agent):
                nextNodes.append(i)

        # If more than one condition is met, select a random edge to follow
        if len(nextNodes) > 0:
            nextNode = np.random.choice(nextNodes)

            action = self.actionArray[agent.currentNode, nextNode]
            if action is not None:
                action.run(sim, agent)

            agent.currentNode = nextNode

        # Perform the task of the node
        isFinished = self.nodes[agent.currentNode].act(sim, agent)

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
                    label += f"\n{self.actionArray[i,j].name}"

                output += f'n{i}->n{j} [label="{label}"]\n'

        for i in range(self.n):
            label = ""
            action = self.finishActionArray[i]
            if action is not None:
                label += f"\n{action.name}"

            output += f'n{i}->n{self.finishEdgeArray[i]} [style=dashed,label="{label}"]\n'

        output += "}"

        return output







