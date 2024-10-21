
#-----Imports-----#
import numpy as np
import matplotlib.pyplot as plt
import os
import pickle
from Optimizer import Settings, Results, run
from AutomataTester import PopExpSettings, PopExpResults, CommRangeExpSettings, CommRangeExpResults
from Map import getMapDict
from Parallelizer import runAsync

#-----ResultsReader-----#

def readResults(folderName):

    settingsArray = []
    resultsArray = []

    i = 1
    while True:

        folderPath = folderName + str(i)
        i += 1

        if not os.path.isdir(folderPath):
            return settingsArray, resultsArray

        with open(folderPath + "/PickledSettings.obj", 'rb') as settingsFile:
            settings = pickle.load(settingsFile)

        settingsArray.append(settings)

        resultsArray.append([])

        j = 1
        while True:
            resultsPath = folderPath + "/Run" + str(j)
            j += 1

            if not os.path.isdir(resultsPath):
                break

            with open(resultsPath + "/PickledResults.obj", 'rb') as resultsFile:
                results = pickle.load(resultsFile)

            resultsArray[-1].append(results)

    return settingsArray, resultsArray

#-----OptimizerPlotter----#

def plotScore(results):

    avgScore = np.average(results.scoreArray, axis=1)
    maxScore = np.amax(results.scoreArray, axis=1)

    plt.plot(avgScore, color="green", label="avgScore")
    plt.plot(maxScore, color="red", label="maxScore")

    plt.xlabel("runs")
    plt.ylabel("score")

    plt.xlim(0, len(avgScore)-1)
    plt.ylim(0, 1.2 * np.amax(results.scoreArray))

    plt.grid(linestyle="--", alpha=0.5)

    plt.legend()

    plt.show()

def plotSize(results):

    sizeArray = [[automata.size() for automata in automataList] for automataList in results.automataArray]
    avgSize = np.average(sizeArray, axis=1)
    minSize = np.amin(sizeArray, axis=1)
    maxSize = np.amax(sizeArray, axis=1)

    plt.plot(avgSize, color="green",label="avgSize")
    plt.plot(minSize, color="blue",label="minSize")
    plt.plot(maxSize, color="red",label="maxSize")

    plt.xlabel("runs")
    plt.ylabel("size")

    plt.xlim(0, len(avgSize)-1)
    plt.ylim(0, 1.2 * np.amax(maxSize))

    plt.grid(linestyle="--", alpha=0.5)

    plt.legend()

    plt.show()

def printBestAutomata(results):

    for i in range(len(results.scoreArray)):
        jMax = np.argmax(results.scoreArray[i, :])
        bestAutomata = results.automataArray[i, jMax]
        score = results.scoreArray[i, jMax]

        print(f"#---Best-Automata-{i}-Score-{score}---#\n{bestAutomata.toString()}")

def getRealScore(settings, results, runs):

    mapDict = getMapDict()
    map = mapDict[settings.mapSettings.name](settings.mapSettings).init()

    automataArray, scoreArray = results.automataArray, results.scoreArray
    bestAutomataList = []
    indList = []

    bestScore = 0
    for i in range(len(scoreArray)):
        jMax = np.argmax(scoreArray[i, :])
        maxScore = scoreArray[i, jMax]
        if maxScore > bestScore:
            bestScore = maxScore
            bestAutomataList.append(automataArray[i, jMax])
            indList.append(i)

    avgScoreList = []
    for automata in bestAutomataList:
        automataList = [automata for _ in range(runs)]
        scoreList = runAsync(run, runs, [map, automataList, settings.op.tMax])
        avgScoreList.append(np.average(scoreList))

    yList = np.full(len(scoreArray[:, 0]), avgScoreList[-1])

    prevInd = 0
    for i, ind in enumerate(indList):
        yList[prevInd:ind+1] = avgScoreList[i]
        prevInd = ind

    return yList


def plotRealScore(scoreList):

    plt.plot(scoreList, color="green")

    plt.xlabel("Generation")
    plt.ylabel("Average score of best automata")

    plt.xlim(0, len(scoreList) - 1)
    plt.ylim(0, 1.2 * np.amax(scoreList))

    plt.grid(linestyle="--", alpha=0.5)

    plt.show()

#-----PopulationExperimentPlotter-----#

def plotPopScoreGraph(settings, results, automataNames):

    scoreArray = results.scoreArray
    popRange = settings.populationRange
    maxScore = 0
    for i in range(scoreArray.shape[0]):
        avgScoreList = np.average(scoreArray[i, :, :], axis=1) / popRange
        plt.scatter(popRange, avgScoreList, s=12)
        plt.plot(popRange, avgScoreList, label=automataNames[i])
        maxScore = max(maxScore, np.amax(avgScoreList))

    plt.xlim(0, 1.05 * np.amax(popRange))
    plt.ylim(0, 1.1 * maxScore)

    plt.title(f"Score vs Population with Tmax={settings.op.tMax}, commRange={settings.simSettings.commRange}")
    plt.xlabel("Population size")
    plt.ylabel("Average Score per agent")

    plt.grid(linestyle="--", alpha=0.5)
    plt.legend(fontsize=8)

    plt.show()

#-----CommExperimentPlotter-----#

def plotCommScoreGraph(settings, results, automataNames, colorList):

    scoreArray = results.scoreArray
    commRangeList = settings.commRangeList

    maxScore = 0
    for i in range(scoreArray.shape[0]):
        scoreList = scoreArray[i, :, :] / settings.mapSettings.creatureCount
        avgScoreList = np.average(scoreList, axis=1)
        lowerBound = np.percentile(scoreList, 15.9, axis=1)
        upperBound = np.percentile(scoreList, 84.1, axis=1)

        color = colorList[i]
        plt.plot(commRangeList, avgScoreList, label=automataNames[i], color=color)
        plt.scatter(commRangeList, avgScoreList, color=color, s=12)
        plt.plot(commRangeList, lowerBound, alpha=0.1, color=color)
        plt.plot(commRangeList, upperBound, alpha=0.1, color=color)
        plt.fill_between(commRangeList, lowerBound, upperBound, alpha=0.25, label="15.9% percentile", color=color)
        maxScore = max(maxScore, np.amax(upperBound))

    plt.title(f"Score vs commRange with Tmax={settings.op.tMax}, population={settings.mapSettings.creatureCount}")
    plt.xlim(0, np.amax(commRangeList))
    plt.ylim(0, 1.1 * maxScore)

    plt.xlabel("Maximum communication range")
    plt.ylabel("Average Score per agent")

    plt.grid(linestyle="--", alpha=0.5)
    plt.legend(fontsize=8)

    plt.show()


if __name__ == "__main__":

    if True:
        settingsArray, resultsArray = readResults()
        settings = settingsArray[0]
        results = resultsArray[0][0]

        scoreList = getRealScore(settings, results, 100)

        plotRealScore(scoreList)

        # plotScore(results)
        # plotSize(results)
        #
        # printBestAutomata(results)

    if False:
        settingsArray, resultsArray = readResults("PopExperiment")

        settings = settingsArray[2]
        results = resultsArray[2][0]

        plotPopScoreGraph(settings, results, ["Mute Agent", "Communicating Agent"])

    if False:

        settingsArray, resultsArray = readResults("CommRangeExperiment")

        settings = settingsArray[2]
        results = resultsArray[2][0]

        plotCommScoreGraph(settings, results, ["Communicating Agent"], ["green"])




