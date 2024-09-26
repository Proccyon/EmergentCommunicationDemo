
#-----Imports-----#
import numpy as np
from TaskNode import initNodes
import Conditions
from Conditions import Condition, AND, OR, NOT, NearbyFoodAmount, GroundFoodDensity, IsWaypointSet, GreaterThan, Constant
from Action import Action, SetWaypoint, ResetWaypoint, getActionFactories


class Automata:

    def __init__(self):
        self.nodes = initNodes()
        self.n = len(self.nodes)
        self.conditionEdgeArray = np.full((self.n, self.n), None, dtype=Condition)
        self.actionArray = np.full((self.n, self.n), None, dtype=Action)

        self.finishEdgeArray = np.zeros(self.n, dtype=int)
        self.finishActionArray = np.full(self.n, None, dtype=Action)

        #self.operators, self.atomFactoryList = getFactoryList()

        self.pNOT = 0.1
        self.pConst = 0.25
        self.pTargetSelf = 0.8
        self.constMin = 0
        self.constMax = 10
        self.conditionAmountMutateRate = 0.1
        self.conditionMutateRate = 0.1
        self.finEdgeMutationRate = 0.1
        self.actionMutationRate = 0.1

        #self.initBaseAutomata()


    def initBaseAutomata(self):

        self.finishEdgeArray[0] = 1
        self.finishEdgeArray[1] = 0
        self.finishEdgeArray[2] = 1
        self.finishEdgeArray[3] = 2

        # self.conditionEdgeArray[0, 2] = NearbyFoodAmount(0, True)
        # self.conditionEdgeArray[2, 2] = GroundFoodDensity(2, True)

        self.conditionEdgeArray[0, 2] = GreaterThan(NearbyFoodAmount(True), Constant(0))
        self.conditionEdgeArray[2, 2] = GreaterThan(GroundFoodDensity(True), Constant(2))

        self.actionArray[2, 2] = SetWaypoint()

        self.conditionEdgeArray[0, 3] = IsWaypointSet(True)
        self.finishActionArray[3] = ResetWaypoint()

        #self.actionArray[0, 2] = SetWaypoint()
        #self.finishActionArray[2] = SetWaypoint()

        #print(self.toString())

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

    def copy(self):

        newCopy = Automata()

        newCopy.finishEdgeArray = self.finishEdgeArray.copy()

        for i in range(self.n):
            newCopy.finishActionArray[i] = self.finishActionArray[i]

        for i in range(self.n):
            for j in range(self.n):
                condition = self.conditionEdgeArray[i, j]
                if condition is None:
                    newCopy.conditionEdgeArray[i, j] = None
                else:
                    newCopy.conditionEdgeArray[i, j] = condition.copy()

                newCopy.actionArray[i, j] = self.actionArray[i, j]

        newCopy.pNOT = self.pNOT
        newCopy.pConst = self.pConst
        newCopy.constMin = self.constMin
        newCopy.constMax = self.constMax
        newCopy.conditionAmountMutateRate = self.conditionAmountMutateRate
        newCopy.conditionMutateRate = self.conditionMutateRate
        newCopy.finEdgeMutationRate = self.finEdgeMutationRate
        newCopy.actionMutationRate = self.actionMutationRate

        return newCopy


    def createOffspring(self):

        child = self.copy()
        #child.mutate()
        return child

    #---MutationMethods---#

    def mutate(self):

        self.booleanFactories = Conditions.getBooleanFactories()
        self.valueFactories = Conditions.getValueFactories()
        self.actionFactories = getActionFactories()

        self.mutateConditionAmount()
        self.mutateConditions()
        self.mutateFinishEdges()
        self.mutateActions()

    # Randomly increases/decreases condition size
    def mutateConditions(self):

        conditions = []
        slots = []
        for i in range(self.n):
            for j in range(self.n):
                condition = self.conditionEdgeArray[i, j]
                if condition is not None:
                    conditions.append(condition)
                    slots.append((i,j))

        expansionAmount = np.random.poisson(self.n * self.conditionMutateRate)
        reductionAmount = np.random.poisson(self.n * self.conditionMutateRate)

        for k in np.random.choice(range(len(conditions)), expansionAmount):
            condition = conditions[k]
            i, j = slots[k]
            self.conditionEdgeArray[i, j] = self.ExpandCondition(condition)

        for k in np.random.choice(range(len(conditions)), reductionAmount):
            condition = conditions[k]
            i, j = slots[k]
            self.conditionEdgeArray[i, j] = self.reduceCondition(condition)


    def generateRandomCondition(self):

        pBool = len(self.booleanFactories) / (len(self.booleanFactories) + len(self.valueFactories))

        # Randomly decide if we want to use one of the atomic booleans as extra condition
        if np.random.random() < pBool:
            return self.generateRandomBoolean(self.pTargetSelf)
        else:
            # If not we use an inequality
            # First decide if the inequality contains a constant
            if np.random.random() < self.pConst:

                constValue = np.random.randint(self.constMin, self.constMax)
                constant = Constant(constValue)
                value = self.generateRandomValue(self.pTargetSelf)

                if np.random.random() < 0.5:
                    leftValue = constant
                    rightValue = value
                else:
                    leftValue = value
                    rightValue = constant
            else:

                i1, i2 = np.random.choice(len(self.valueFactories), size=2, replace=False)
                leftValue, rightValue = self.valueFactories[i1](), self.valueFactories[i2]()

            return GreaterThan(leftValue, rightValue)


    # Increase the size of the condition by 1 by randomly adding an operator
    def ExpandCondition(self, condition: Condition):

        # Randomly select where to mutate
        descendants = condition.getDescendants()
        child, parentInfo = descendants[np.random.randint(len(descendants))]

        # Randomly decide if we add a NOT operator
        if np.random.random() < self.pNOT:
            operator = NOT(child)
        else:

            #Generate a random atomic condition
            newCond = self.generateRandomCondition()

            # Decide whether to use AND or OR
            if np.random.random() < 0.5:
                operator = AND(child, newCond)
            else:
                operator = OR(child, newCond)

        parent, parentIndex = parentInfo

        if parent is None:
            return operator
        else:
            if parentIndex == 0:
                parent.cond = operator
            elif parentIndex == 1:
                parent.cond2 = operator

            return condition

    # Reduce the size of the condition by 1 by randomly removing an operator
    def reduceCondition(self, condition: Condition):

        # Find random leaf to remove
        removeables = condition.getRemoveables()

        if len(removeables) == 0:
            return condition

        child, parentInfo = removeables[np.random.randint(len(removeables))]
        parent, parentIndex = parentInfo

        if parent is None:
            return child

        if parentIndex == 0:
            parent.cond = child
        elif parentIndex == 1:
            parent.cond2 = child

        return condition


    def mutateConditionAmount(self):

        amount = np.random.poisson(self.n * self.conditionAmountMutateRate)

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
                self.conditionEdgeArray[i,j] = self.generateRandomCondition()

        else:
            if len(filledSlots) < amount:
                amount = len(filledSlots)

            selectedSlotIds = np.random.choice(len(filledSlots), size=amount, replace=False)

            for id in selectedSlotIds:
                i, j = filledSlots[id]
                self.conditionEdgeArray[i, j] = None


    def mutateFinishEdges(self):

        mutations = np.random.poisson(self.n * self.finEdgeMutationRate)

        for _ in range(mutations):
            i, j = np.random.choice(self.n, size=2, replace=False)
            self.finishEdgeArray[i] = j


    def mutateActions(self):

        mutations = np.random.poisson(self.n * self.actionMutationRate)

        for _ in range(mutations):
            i = np.random.randint(self.n)
            actionFactory = np.random.choice(self.actionFactories)
            if actionFactory is None:
                newAction = None
            else:
                newAction = actionFactory()
            self.finishActionArray[i] = newAction

        actionSlots = []
        for i in range(self.n):
            for j in range(self.n):
                if self.conditionEdgeArray[i, j] is not None:
                    actionSlots.append((i, j))

        mutations = np.random.poisson(len(actionSlots) * self.actionMutationRate)

        for _ in range(mutations):
            i,j = actionSlots[np.random.randint(len(actionSlots))]
            actionFactory = np.random.choice(self.actionFactories)
            if actionFactory is None:
                newAction = None
            else:
                newAction = actionFactory()
            self.actionArray[i, j] = newAction



    def generateRandomBoolean(self, pTargetSelf):

        if np.random.random() < pTargetSelf:
            target = "self"
        else:
            target = "saved"
        return self.booleanFactories[np.random.randint(len(self.booleanFactories))](target)

    def generateRandomValue(self, pTargetSelf):
        if np.random.random() < pTargetSelf:
            target = "self"
        else:
            target = "saved"
        return self.valueFactories[np.random.randint(len(self.valueFactories))](target)








