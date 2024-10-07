
#-----Imports-----#
import numpy as np
from Simulation import runSimHidden, SimSettings
from Parallelizer import runAsync
from Map import FourRoomsMap, FourRoomsMapSettings
from Automata import Automata
from Conditions import OptimizationParameters
from Saver import save
import time

def run(i, map, automata, simSettings, tMax):
    score = runSimHidden(i, map, automata, simSettings, tMax)
    return score

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

    def __init__(self, scoreArray):
        self.scoreArray = scoreArray

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

    def __init__(self, scoreArray):
        self.scoreArray = scoreArray


def runPopExperiment(map, simSettings, automataList, populationRange, runsPerPop, op):

    scoreArray = np.zeros((len(automataList), len(populationRange), runsPerPop))
    baseFoodAmount = map.foodAmount

    for i, populationSize in enumerate(populationRange):
        print(f"Running for population size {populationSize}...")
        for j, automata in enumerate(automataList):
            print(f"Running for automata {j+1}...")
            startTime = time.time()
            map.creatureCount = populationSize
            map.foodAmount = populationSize * baseFoodAmount
            map.generateCreatures()
            map.generateFood()
            scoreList = runAsync(run, runsPerPop, [map, automata, simSettings, op.tMax])
            scoreArray[j, i, :] = scoreList
            dt = int(time.time() - startTime)
            print(f"Run {i + 1}.{j+1}/{len(populationRange)}, minScore={np.amin(scoreList)}, maxScore={np.amax(scoreList)}, avgScore={np.average(scoreList)}, time={dt}s")

    return PopExpResults(scoreArray)


def runCommRangeExperiment(map, simSettings, automataList, commRangeList, runsPerComm, op):

    scoreArray = np.zeros((len(automataList), len(commRangeList), runsPerComm))

    for i, commRange in enumerate(commRangeList):
        print(f"Running for comm Range {commRange}...")
        for j, automata in enumerate(automataList):
            print(f"Running for automata {j+1}...")
            startTime = time.time()
            simSettings.commRange = commRange
            scoreList = runAsync(run, runsPerComm, [map, automata, simSettings, op.tMax])
            scoreArray[j, i, :] = scoreList
            dt = int(time.time() - startTime)
            print(f"Run {i + 1}.{j+1}/{len(commRangeList)}, minScore={np.amin(scoreList)}, maxScore={np.amax(scoreList)}, avgScore={np.average(scoreList)}, time={dt}s")

    return CommRangeExpResults(scoreArray)


#-----Main-----#


if __name__ == "__main__":

    if False:
        populationRange = [1, 2, 3, 5, 8, 10, 15, 20, 30, 40, 50, 75, 100]
        runsPerPop = 200
        op = OptimizationParameters()
        op.tMax = 1000

        automataList = [Automata().initMemorizingAutomata(), Automata().initCommunicatingAutomata()]

        simSettings = SimSettings(5, 5)
        mapSettings = FourRoomsMapSettings(6, 6, 6, 1, populationRange[0], 10, 1, 2, 4, 8)
        map = FourRoomsMap(mapSettings).init()

        results = runPopExperiment(map, simSettings, automataList, populationRange, runsPerPop, op)

        settings = PopExpSettings(mapSettings, simSettings, automataList, populationRange, runsPerPop, op)
        save(settings, results, "PopExperiment")

    if True:

        commRangeList = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        runsPerComm = 300
        op = OptimizationParameters()
        op.tMax = 1000
        popSize = 30

        automataList = [Automata().initCommunicatingAutomata()]

        simSettings = SimSettings(5, commRangeList[0])
        mapSettings = FourRoomsMapSettings(6, 6, 6, 1, popSize, 10*popSize, 1, 2, 4, 8)
        map = FourRoomsMap(mapSettings).init()

        results = runCommRangeExperiment(map, simSettings, automataList, commRangeList, runsPerComm, op)

        settings = CommRangeExpSettings(mapSettings, simSettings, automataList, commRangeList, runsPerComm, op)
        save(settings, results, "CommRangeExperiment")




















