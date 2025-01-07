
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


class GeneralExpSettings:


    def __init__(self, mapSettingsArray, simSettingsArray, brainArray, runsPerSetting, op):
        self.mapSettingsArray = mapSettingsArray
        self.simSettingsArray = simSettingsArray
        self.brainArray = brainArray
        self.runsPerSetting = runsPerSetting
        self.op = op

    def toString(self):

        text =  f"#---OptimizationParameters---#\n"
        text += f"{self.op.toString()}\n"
        text += f"runsPerSetting = {str(self.runsPerSetting)}\n"

        if len(self.mapSettingsArray) == 1:
            text += self.mapSettingsArray[0].toString()+"\n"

        for i in range(self.simSettingsArray.size):
            simSettings = np.ndarray.flatten(self.simSettingsArray)[i]
            brain = np.ndarray.flatten(self.brainArray)[i]
            text += f"#---SimSettings-{i+1}---#\n"
            text += f"{simSettings.toString()}\n"
            text += f"#---Automata-{i+1}---#\n"
            text += brain.toString() + "\n"

            if len(self.mapSettingsArray) > 1:
                mapSettings = np.ndarray.flatten(self.mapSettingsArray)[i]
                text += f"#---Map-{i+1}---#\n"
                text += f"{mapSettings.toString()}\n"

        return text

class GeneralExpResults:

    def __init__(self, scoreArray, maxScoreArray, aucArray, maxAUCArray, bestFoodDensityArray, foodCollectedArray, avgAgentCenterDistanceArray, avgWaypointCenterDistanceArray, avgWaypointAgentDistanceArray, scoreOverTimeArray, foodOverTimeArray):
        self.scoreArray = scoreArray
        self.maxScoreArray = maxScoreArray
        self.aucArray = aucArray
        self.maxUACArray = maxAUCArray
        self.bestFoodDensityArray = bestFoodDensityArray
        self.foodCollectedArray = foodCollectedArray
        self.avgAgentCenterDistanceArray = avgAgentCenterDistanceArray
        self.avgWaypointCenterDistanceArray = avgWaypointCenterDistanceArray
        self.avgWaypointAgentDistanceArray = avgWaypointAgentDistanceArray
        self.scoreOverTimeArray = scoreOverTimeArray
        self.foodOverTimeArray = foodOverTimeArray


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


def runGeneralExperiment(mapClass, mapSettingsArray, simSettingsArray, brainArray, runsPerSetting, op):

    shape = (runsPerSetting,) + simSettingsArray.shape
    distanceArrayShape = (runsPerSetting, op.tMax) + simSettingsArray.shape
    scoreArray = np.zeros(shape)
    aucArray = np.zeros(shape)
    bestFoodDensityArray = np.zeros(shape)
    foodCollectedArray = np.zeros(shape)
    maxScoreArray = np.zeros(simSettingsArray.shape)
    maxAUCArray = np.zeros(simSettingsArray.shape)
    avgAgentCenterDistanceArray = np.zeros(distanceArrayShape)
    avgWaypointCenterDistanceArray = np.zeros(distanceArrayShape)
    avgWaypointAgentDistanceArray = np.zeros(distanceArrayShape)
    scoreOverTimeArray = np.zeros(distanceArrayShape)
    foodOverTimeArray = np.zeros(distanceArrayShape)

    if len(mapSettingsArray) == 1:
        mapSettings = mapSettingsArray[0]
        map = mapClass(mapSettings).init()
        pathfinder = Pathfinder(map).init()
        maxScore = map.calculateMaxScore(op.tMax, map.creatureCount, pathfinder)
        maxAUC = map.calculateMaxAUC(op.tMax, map.creatureCount, pathfinder)

    it = np.nditer(np.zeros(simSettingsArray.shape), flags=['multi_index'])
    for _ in it:
        index = it.multi_index

        print(f"Running for index {index}...")
        startTime = time.time()

        simSettings, brain = simSettingsArray[index], brainArray[index]

        if len(mapSettingsArray) > 1:
            mapSettings = mapSettingsArray[index]
            map = mapClass(mapSettings).init()
            pathfinder = Pathfinder(map).init()
            maxScore = map.calculateMaxScore(op.tMax, map.creatureCount, pathfinder)
            maxAUC = map.calculateMaxAUC(op.tMax, map.creatureCount, pathfinder)

        resultsList = runAsync(runSimHidden, runsPerSetting, [map, brain, simSettings, op.tMax])
        scoreArray[:, *index] = np.array([results[0] for results in resultsList])
        aucArray[:, *index] = np.array([results[1] for results in resultsList])
        bestFoodDensityArray[:, *index] = np.array([results[2] for results in resultsList])
        foodCollectedArray[:, *index] = np.array([results[3] for results in resultsList])
        avgAgentCenterDistanceArray[:, :, *index] = np.array([results[4] for results in resultsList])
        avgWaypointCenterDistanceArray[:, :, *index] = np.array([results[5] for results in resultsList])
        avgWaypointAgentDistanceArray[:, :, *index] = np.array([results[6] for results in resultsList])
        scoreOverTimeArray[:, :, *index] = np.array([results[7] for results in resultsList])
        foodOverTimeArray[:, :, *index] = np.array([results[8] for results in resultsList])

        maxScoreArray[index] = maxScore
        maxAUCArray[index] = maxAUC

        dt = int(time.time() - startTime)
        print(f"Run {index}/{len(simSettingsArray)}, minScore={np.amin(scoreArray[:,*index])}, maxScore={np.amax(scoreArray[:,*index])}, avgScore={np.average(scoreArray[:,*index])}, time={dt}s")

    return GeneralExpResults(scoreArray, maxScoreArray, aucArray, maxAUCArray, bestFoodDensityArray, foodCollectedArray,
                             avgAgentCenterDistanceArray, avgWaypointCenterDistanceArray, avgWaypointAgentDistanceArray, scoreOverTimeArray, foodOverTimeArray)


#-----Main-----#


if __name__ == "__main__":

    # Run simulation for different population sizes
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

    # Run simulation for different communication ranges
    if False:

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


    if False:

        commRangeList = [5]
        runsPerComm = 400
        op = OptimizationParameters()
        op.tMax = 1000
        popSize = 20
        pCommList = [0, 0.025, 0.05, 0.1, 0.15, 0.25, 0.5, 0.75, 1, 999]

        #brainList = [BehaviourTree().initExploringAgent(0, 0.01), BehaviourTree().initExploringAgent(0.0025, 0.01), BehaviourTree().initExploringAgent(0.005, 0.01)]
        brainList = [BehaviourTree().initCommunicatingAgent(30, pComm) for pComm in pCommList]

        simSettings = SimSettings(5, commRangeList[0])
        mapSettings = FourRoomsMapSettings(18, 6, 6, 1, popSize, 10*popSize, 1, 2, 4, 8)
        map = FourRoomsMap(mapSettings).init()

        results = runCommRangeExperiment(map, simSettings, brainList, commRangeList, runsPerComm, op)

        settings = CommRangeExpSettings(mapSettings, simSettings, brainList, commRangeList, runsPerComm, op)
        save(settings, results, "pCommExperiment")

    if False:

        commRangeList = [0,2,4,6,8,10, 12, 14, 16, 18, 20, 22, 24, 26]
        runsPerComm = 300
        op = OptimizationParameters()
        op.tMax = 1000
        popSize = 30
        nCommList = [0.01, 0.015, 0.02, 0.05, 0.1, 999]

        r1 = 18

        #brainList = [BehaviourTree().initExploringAgent(0, 0.01), BehaviourTree().initExploringAgent(0.0025, 0.01), BehaviourTree().initExploringAgent(0.005, 0.01)]
        brainList = [BehaviourTree().initCommunicatingAgent(r1*2, -1)]

        for nComm in nCommList:

            simSettings = SimSettings(5, commRangeList[0], nComm)
            mapSettings = FourRoomsMapSettings(r1, 6, 6, 1, popSize, 10*popSize, 1, 2, 4, 8)
            map = FourRoomsMap(mapSettings).init()

            results = runCommRangeExperiment(map, simSettings, brainList, commRangeList, runsPerComm, op)

            settings = CommRangeExpSettings(mapSettings, simSettings, brainList, commRangeList, runsPerComm, op)
            save(settings, results, "nCommExperiment")


    if True:

        runsPerSetting = 50
        op = OptimizationParameters()
        op.tMax = 5000
        popSize = 20
        r1 = 18
        commRange = 6
        stdDistortCoord = 1
        nCommList = [0.15, 0.3, 0.6]
        pDistortCoordList = [0, 0.01, 0.02, 0.03]
        # nCommList = [0.3]
        # pDistortCoordList = [0.03]

        simSettingsArray = np.zeros((len(nCommList), len(pDistortCoordList)), dtype=SimSettings)
        brainArray = np.zeros((len(nCommList), len(pDistortCoordList)), dtype=Brain)
        for i, nComm in enumerate(nCommList):
            for j, pDistortCoord in enumerate(pDistortCoordList):
                simSettingsArray[i, j] = SimSettings(5, commRange, nComm, 0, 0, pDistortCoord, stdDistortCoord)
                brainArray[i, j] = BehaviourTree().initCommunicatingAgent(r1*2, -1)

        mapSettings = FourRoomsMapSettings(r1, 6, 6, 1, popSize, 10 * popSize, 1, 2, 4, 8)
        mapSettingsArray = [mapSettings]

        settings = GeneralExpSettings(mapSettingsArray, simSettingsArray, brainArray, runsPerSetting, op)
        results = runGeneralExperiment(FourRoomsMap, mapSettingsArray, simSettingsArray, brainArray, runsPerSetting, op)
        save(settings, results, "pDistort-nCommExperiment")














