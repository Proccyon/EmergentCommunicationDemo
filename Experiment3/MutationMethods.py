
#-----Imports-----#
import numpy as np

import Conditions
from Conditions import Condition, GreaterThan, Constant, getBooleanFactories, getValueFactories, NOT, AND, OR
from Optimizer import OptimizationParameters

def generateRandomCondition(op: OptimizationParameters):

    booleanFactories, valueFactories = Conditions.getBooleanFactories(), Conditions.getValueFactories()
    pBool = len(booleanFactories) / (len(booleanFactories) + len(valueFactories))

    # Randomly decide if we want to use one of the atomic booleans as extra condition
    if np.random.random() < pBool:
        return generateRandomBoolean(op.pTargetSelf)
    else:
        # If not we use an inequality
        # First decide if the inequality contains a constant
        if np.random.random() < op.pConst:

            constValue = np.random.randint(op.constMin, op.constMax)
            constant = Constant(constValue)
            value = generateRandomValue(op.pTargetSelf)

            if np.random.random() < 0.5:
                leftValue = constant
                rightValue = value
            else:
                leftValue = value
                rightValue = constant
        else:

            i1, i2 = np.random.choice(len(valueFactories), size=2, replace=False)
            leftValue, rightValue = valueFactories[i1](), valueFactories[i2]()

        return GreaterThan(leftValue, rightValue)


# Increase the size of the condition by 1 by randomly adding an operator
def ExpandCondition(condition: Condition, op: OptimizationParameters):

    # Randomly select where to mutate
    descendants = condition.getDescendants()
    child, parentInfo = descendants[np.random.randint(len(descendants))]

    # Randomly decide if we add a NOT operator
    if np.random.random() < op.pNOT:
        operator = NOT(child)
    else:

        #Generate a random atomic condition
        newCond = generateRandomCondition()

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
def reduceCondition(condition: Condition):

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


def generateRandomBoolean(op: OptimizationParameters):
    booleanFactories = Conditions.getBooleanFactories()
    if np.random.random() < op.pTargetSelf:
        target = "self"
    else:
        target = "saved"
    return booleanFactories[np.random.randint(len(booleanFactories))](target)

def generateRandomValue(op: OptimizationParameters):
    valueFactories = Conditions.getValueFactories()
    if np.random.random() < op.pTargetSelf:
        target = "self"
    else:
        target = "saved"
    return valueFactories[np.random.randint(len(valueFactories))](target)