
#-----Imports-----#
import numpy as np
from Parallelizer import runAsync
import matplotlib.pyplot as plt
from BehaviourTree import *
from Map import *
from Simulation import runSimHidden, SimSettings
from Saver import *


class Parameters:

    def __init__(self, pMutate, mutateStdCoefficient):
        self.valueDict = {}
        self.typeDict = {}
        self.yMinDict = {}
        self.yMaxDict = {}
        self.pMutate = pMutate
        self.mutateStdCoefficient = mutateStdCoefficient

    def generate(self):

        for key in self.valueDict.keys():
            yMin, yMax = self.yMinDict[key], self.yMaxDict[key]
            self.valueDict[key] = np.random.uniform(yMin, yMax)

        return self

    def add(self, name, type, yMin, yMax):
        self.valueDict[name] = 0
        self.typeDict[name] = type
        self.yMinDict[name] = yMin
        self.yMaxDict[name] = yMax

    def get(self, name):

        y = self.valueDict[name]
        if self.typeDict[name] == "int":
            dy = y - int(y)
            if np.random.random() < dy:
                y = int(y) + 1
            else:
                y = int(y)

        return y

    def set(self, name, value):
        self.valueDict[name] = value

    def copy(self):
        child = Parameters(self.pMutate, self.mutateStdCoefficient)
        child.valueDict = self.valueDict.copy()
        child.typeDict = self.typeDict.copy()
        child.yMinDict = self.yMinDict.copy()
        child.yMaxDict = self.yMaxDict.copy()
        return child

    def mutate(self):

        for key in self.valueDict.keys():
            if not np.random.random() < self.pMutate:
                continue

            yMin, yMax = self.yMinDict[key], self.yMaxDict[key]
            dy = np.random.normal(0, self.mutateStdCoefficient * (yMax - yMin))
            yNew = self.valueDict[key] + dy

            if yNew > yMax:
                yNew = yMax
            if yNew < yMin:
                yNew = yMin

            self.set(key, yNew)

        return self

    def crossover(self, partner):

        childParameters = Parameters(self.pMutate, self.mutateStdCoefficient)
        for key in self.valueDict.keys():
            childParameters.add(key, self.typeDict[key], self.yMinDict[key], self.yMaxDict[key])

            newValue = 0.5 * (self.valueDict[key] + partner.valueDict[key])
            # if self.typeDict[key] == "int":
            #     newValue = int(np.round(newValue))

            childParameters.set(key, newValue)

        return childParameters

    def __str__(self):
        text = "Parameters(\n"
        for key in self.valueDict.keys():
            text += f"{key}={self.valueDict[key]}\n"
        text += ")"
        return text



class ParameterOptimizer:

    def __init__(self, parameterSettings, fitnessFunction, fitnessArgs):
        self.parameterSettings = parameterSettings
        self.fitnessFunction = fitnessFunction
        self.fitnessArgs = fitnessArgs

    def run(self, nSteps, nRunsPerStep, popSize):

        parameterList = [self.parameterSettings.copy().generate() for _ in range(popSize)]
        parameterArray = [parameterList]
        for step in range(nSteps):

            print(f"step {step+1}/{nSteps}")
            fitnessList = self.calculateFitnessList(parameterList, nRunsPerStep)

            newParameterList = []
            for i in range(popSize):
                parent1 = self.tournamentSelection(parameterList, fitnessList)
                parent2 = self.tournamentSelection(parameterList, fitnessList)
                newParameterList.append(parent1.crossover(parent2))

            parameterArray.append(newParameterList)
            parameterList = [parameter.mutate() for parameter in newParameterList]




        return parameterArray

    def calculateFitnessList(self, parameterList, nRunsPerStep):

        fitnessList = []
        for i in range(len(parameterList)):
            print(f"Evaluating parameters {i}")
            args = self.fitnessArgs + [parameterList[i]]
            fitness = np.average(runAsync(self.fitnessFunction, nRunsPerStep, args))
            fitnessList.append(fitness)

        return fitnessList

    def tournamentSelection(self, parameterList, fitnessList, k=3):
        selectedIndices = np.random.choice(range(len(parameterList)), replace=False, size=k)
        fitnesses = [fitnessList[i] for i in selectedIndices]
        iBest = selectedIndices[np.argmax(fitnesses)]
        return parameterList[iBest]


class ParameterOptimizerSettings:

    def __init__(self, mapSettings, simSettings, brain, parameterSettings, nSteps, nRunsPerStep, popSize):
        self.mapSettings = mapSettings
        self.simSettings = simSettings
        self.brain = brain
        self.parameterSettings = parameterSettings
        self.nSteps = nSteps
        self.nRunsPerStep = nRunsPerStep
        self.popSize = popSize

    def toString(self):
        text = f"#---Map---#\n"
        text += f"{self.mapSettings.toString()}\n"
        text += f"#---SimSettings---#\n"
        text += f"{self.simSettings.toString()}\n"
        text += f"#---brain----#\n"
        text += self.brain.toString() + "\n"
        text += "#---Optimizer---#\n"
        text += f"nSteps = {self.nSteps}\n"
        text += f"popSize = {self.popSize}\n"
        text += f"nRunsPerStep = {self.nRunsPerStep}\n"
        return text

class ParameterOptimizerResults:

    def __init__(self, parameterArray):
        self.parameterArray = parameterArray


def commRangeFitness(id, map, brain, simSettings, tMax, parameters):
    commRange = parameters.get("commRange")
    simSettings.commRange = commRange
    id, results = runSimHidden(id, map, brain, simSettings, tMax)
    score = results[0]
    return id, score



def runCommRangeOptimizer(map, simSettings, brain, parameterSettings, nSteps, nRunsPerStep, popSize, tMax):

    optimizer = ParameterOptimizer(parameterSettings, commRangeFitness, [map, brain, simSettings, tMax])
    parameterArray = optimizer.run(nSteps, nRunsPerStep, popSize)
    results = ParameterOptimizerResults(parameterArray)
    return results

# def f(x):
#     return 4 * (x - x**2) + 0.25 * np.random.random()
#
# def fitFunc(i, arg1, arg2, parameters):
#     return i, f(parameters.get("x0"))


if __name__ == "__main__":

    nSteps = 15
    nRunsPerStep = 16
    tMax = 1000
    parameterPopulationCount = 10

    brain = BehaviourTree().initCommunicatingAgent(30)

    simSettings = SimSettings(5, 5)

    #RList = [6, 10, 14, 18, 22]
    RList = [6, 10, 14, 18, 22]
    popSizeList = [5, 10, 20, 30]

    for R in RList:
        for popSize in popSizeList:
            parameterSettings = Parameters(1, 0.025)
            parameterSettings.add("commRange", "int", 0, R)

            mapSettings = FourRoomsMapSettings(R, 6, 6, 1, popSize, 10 * popSize, 1, 2, 4, 8)
            map = FourRoomsMap(mapSettings).init()

            settings = ParameterOptimizerSettings(mapSettings, simSettings, brain, parameterSettings, nSteps, nRunsPerStep, parameterPopulationCount)
            results = runCommRangeOptimizer(map, simSettings, brain, parameterSettings, nSteps, nRunsPerStep, parameterPopulationCount, tMax)

            save(settings, results, "CommRangeOptimizer")

















