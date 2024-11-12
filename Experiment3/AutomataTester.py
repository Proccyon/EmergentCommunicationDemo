
#-----Imports-----#
import numpy as np
from Simulation import runSimHidden, SimSettings
from Parallelizer import runAsync
from Map import FourRoomsMap, FourRoomsMapSettings
from Automata import Automata
from BehaviourTree import *
from Conditions import OptimizationParameters
from Saver import save
import time
from Pathfinder import *

def run(i, map, automata, simSettings, tMax):
    return runSimHidden(i, map, automata, simSettings, tMax)

class PopExpSettings:

    def __init__(self, mapSettings, simSettings, automataList, populationRange, runsPerPop, op):
        self.mapSettings = mapSettings
        self.simSettings = simSettings
        self.automataList = automataList
        self.populationRange = populationRange
        self.runsPerPop = runsPerPop
        self.op = op

    def toString(self):
        text =  f"#---OptimizationParameters---#\n"
        text += f"{self.op.toString()}\n"
        text += f"#---Map---#\n"
        text += f"{self.mapSettings.toString()}\n"
        text += f"#---SimSettings---#\n"
        text += f"{self.simSettings.toString()}\n"
        for i, automata in enumerate(self.automataList):
            text += f"#---Automata-{i+1}---#\n"
            text += automata.toString() + "\n"
        text += "#---PopulationRange---#\n"
        text += f"populationRange = {str(self.populationRange)}\n"
        text += "#---PopulationRange---#\n"
        text += f"runsPerPop = {str(self.runsPerPop)}"
        return text

class PopExpResults:

    def __init__(self, scoreArray, maxScoreList, aucArray, maxAUCList, bestFoodDensityArray, foodCollectedArray):
        self.scoreArray = scoreArray
        self.maxScoreList = maxScoreList
        self.uacArray = aucArray
        self.maxAUCList = maxAUCList
        self.bestFoodDensityArray = bestFoodDensityArray
        self.foodCollectedArray = foodCollectedArray

class CommRangeExpSettings:

    def __init__(self, mapSettings, simSettings, automataList, commRangeList, runsPerComm, op):
        self.mapSettings = mapSettings
        self.simSettings = simSettings
        self.automataList = automataList
        self.commRangeList = commRangeList
        self.runsPerComm = runsPerComm
        self.op = op

    def toString(self):
        text =  f"#---OptimizationParameters---#\n"
        text += f"{self.op.toString()}\n"
        text += f"#---Map---#\n"
        text += f"{self.mapSettings.toString()}\n"
        text += f"#---SimSettings---#\n"
        text += f"{self.simSettings.toString()}\n"
        for i, automata in enumerate(self.automataList):
            text += f"#---Automata-{i+1}---#\n"
            text += automata.toString() + "\n"
        text += "#---commRangeList---#\n"
        text += f"commRangeList = {str(self.commRangeList)}\n"
        text += "#---runsPerComm---#\n"
        text += f"runsPerComm = {str(self.runsPerComm)}"
        return text

class CommRangeExpResults:

    def __init__(self, scoreArray, maxScore, uacArray, maxAUC, bestFoodDensityArray, foodCollectedArray):
        self.scoreArray = scoreArray
        self.maxScore = maxScore
        self.uacArray = uacArray
        self.maxUAC = maxAUC
        self.bestFoodDensityArray = bestFoodDensityArray
        self.foodCollectedArray = foodCollectedArray


def runPopExperiment(map, simSettings, brainList, populationRange, runsPerPop, op):

    pathfinder = Pathfinder(map).init()
    scoreArray = np.zeros((len(brainList), len(populationRange), runsPerPop))
    aucArray = np.zeros((len(brainList), len(populationRange), runsPerPop))
    bestFoodDensityArray = np.zeros((len(brainList), len(populationRange), runsPerPop))
    foodCollectedArray = np.zeros((len(brainList), len(populationRange), runsPerPop))
    baseFoodAmount = map.foodAmount
    maxScoreList = []
    maxAUCList = []

    for i, populationSize in enumerate(populationRange):
        print(f"Running for population size {populationSize}...")
        map.creatureCount = populationSize
        map.foodAmount = populationSize * baseFoodAmount
        map.generateCreatures()
        map.generateFood()
        maxScore = map.calculateMaxScore(op.tMax, populationSize, pathfinder)
        maxScoreList.append(maxScore)
        maxUAC = map.calculateMaxAUC(op.tMax, populationSize, pathfinder)
        maxAUCList.append(maxUAC)
        for j, brain in enumerate(brainList):
            print(f"Running for brain {j+1}...")
            startTime = time.time()
            resultsList = runAsync(run, runsPerPop, [map, brain, simSettings, op.tMax])
            scoreArray[j, i, :] = np.array([results[0] for results in resultsList])
            aucArray[j, i, :] = np.array([results[1] for results in resultsList])
            bestFoodDensityArray[j, i, :] = np.array([results[2] for results in resultsList])
            foodCollectedArray[j, i, :] = np.array([results[3] for results in resultsList])
            dt = int(time.time() - startTime)
            print(f"Run {i + 1}.{j+1}/{len(populationRange)}, minScore={np.amin(scoreArray[j, i, :])}, maxScore={np.amax(scoreArray[j, i, :])}, avgScore={np.average(scoreArray[j, i, :])}, time={dt}s")

    return PopExpResults(scoreArray, maxScoreList, aucArray, maxAUCList, bestFoodDensityArray, foodCollectedArray)


def runCommRangeExperiment(map, simSettings, brainList, commRangeList, runsPerComm, op):

    pathfinder = Pathfinder(map).init()
    scoreArray = np.zeros((len(brainList), len(commRangeList), runsPerComm))
    maxScore = map.calculateMaxScore(op.tMax, map.creatureCount, pathfinder)
    aucArray = np.zeros((len(brainList), len(commRangeList), runsPerComm))
    bestFoodDensityArray = np.zeros((len(brainList), len(commRangeList), runsPerComm))
    foodCollectedArray = np.zeros((len(brainList), len(commRangeList), runsPerComm))
    maxAUC = map.calculateMaxAUC(op.tMax, map.creatureCount, pathfinder)

    for i, commRange in enumerate(commRangeList):
        print(f"Running for comm Range {commRange}...")
        for j, brain in enumerate(brainList):
            print(f"Running for brain {j+1}...")
            startTime = time.time()
            simSettings.commRange = commRange
            resultsList = runAsync(runSimHidden, runsPerComm, [map, brain, simSettings, op.tMax])
            scoreArray[j, i, :] = np.array([results[0] for results in resultsList])
            aucArray[j, i, :] = np.array([results[1] for results in resultsList])
            bestFoodDensityArray[j, i, :] = np.array([results[2] for results in resultsList])
            foodCollectedArray[j, i, :] = np.array([results[3] for results in resultsList])
            dt = int(time.time() - startTime)
            print(f"Run {i + 1}.{j+1}/{len(commRangeList)}, minScore={np.amin(scoreArray[j, i, :])}, maxScore={np.amax(scoreArray[j, i, :])}, avgScore={np.average(scoreArray[j, i, :])}, time={dt}s")

    return CommRangeExpResults(scoreArray, maxScore, aucArray, maxAUC, bestFoodDensityArray, foodCollectedArray)


#-----Main-----#


if __name__ == "__main__":

    if False:
        populationRange = [1, 2, 3, 5, 8, 10, 15, 20, 30, 40, 50, 75, 100]
        runsPerPop = 200
        op = OptimizationParameters()
        op.tMax = 1000

        brainList = [Automata().initMemorizingAutomata(), Automata().initCommunicatingAutomata()]

        simSettings = SimSettings(5, 5)
        mapSettings = FourRoomsMapSettings(6, 6, 6, 1, populationRange[0], 10, 1, 2, 4, 8)
        map = FourRoomsMap(mapSettings).generateArrays()

        results = runPopExperiment(map, simSettings, brainList, populationRange, runsPerPop, op)

        settings = PopExpSettings(mapSettings, simSettings, brainList, populationRange, runsPerPop, op)
        save(settings, results, "PopExperiment")

    if True:

        commRangeList = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        runsPerComm = 200
        op = OptimizationParameters()
        op.tMax = 1000
        popSize = 5

        #brainList = [BehaviourTree().initExploringAgent(0, 0.01), BehaviourTree().initExploringAgent(0.0025, 0.01), BehaviourTree().initExploringAgent(0.005, 0.01)]
        brainList = [BehaviourTree().initCommunicatingAgent(30)]

        simSettings = SimSettings(5, commRangeList[0])
        mapSettings = FourRoomsMapSettings(18, 6, 6, 1, popSize, 10*popSize, 1, 2, 4, 8)
        map = FourRoomsMap(mapSettings).init()

        results = runCommRangeExperiment(map, simSettings, brainList, commRangeList, runsPerComm, op)

        settings = CommRangeExpSettings(mapSettings, simSettings, brainList, commRangeList, runsPerComm, op)
        save(settings, results, "CommRangeExperiment")




















