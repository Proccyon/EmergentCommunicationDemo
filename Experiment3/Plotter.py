
#-----Imports-----#
import numpy as np
import matplotlib.pyplot as plt
import os
import pickle
from Optimizer import Settings, Results, run
from AutomataTester import PopExpSettings, PopExpResults, CommRangeExpSettings, CommRangeExpResults
from Map import getMapDict
from Parallelizer import runAsync
from ParameterOptimizer import ParameterOptimizerSettings, ParameterOptimizerResults, Parameters

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
    map = mapDict[settings.mapSettings.name](settings.mapSettings).generateArrays()

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

    scoreArray = results.scoreArray / results.maxScore
    commRangeList = settings.commRangeList

    maxScore = 0
    for i in range(scoreArray.shape[0]):
        scoreList = scoreArray[i, :, :]
        avgScoreList = np.average(scoreList, axis=1)
        lowerBound = np.percentile(scoreList, 15.9, axis=1)
        upperBound = np.percentile(scoreList, 84.1, axis=1)

        color = colorList[i]
        plt.plot(commRangeList, avgScoreList, label=automataNames[i], color=color)
        plt.scatter(commRangeList, avgScoreList, color=color, s=12)
        plt.plot(commRangeList, lowerBound, alpha=0.1, color=color)
        plt.plot(commRangeList, upperBound, alpha=0.1, color=color)
        plt.fill_between(commRangeList, lowerBound, upperBound, alpha=0.25, color=color)
        maxScore = max(maxScore, np.amax(upperBound))

    plt.title(f"Score vs commRange with Tmax={settings.op.tMax}, population={settings.mapSettings.creatureCount}")
    plt.xlim(0, np.amax(commRangeList))
    plt.ylim(0, 1.1 * maxScore)

    plt.xlabel("Maximum communication range")
    plt.ylabel("Average Score per agent")

    plt.grid(linestyle="--", alpha=0.5)
    plt.legend(fontsize=8)

    plt.show()

def plotCommScoreGraphSingle(settings, results, color, index=0):

    fig, ax1, = plt.subplots(figsize=(10, 5))

    scoreArray = results.scoreArray / results.maxScore
    commRangeList = settings.commRangeList

    maxScore = 0
    maxDensity = np.amax(results.bestFoodDensityArray)
    avgMaxFoodReached = np.average(results.bestFoodDensityArray == maxDensity, axis=2)
    avgFoodCollected = np.average(results.foodCollectedArray, axis=2) / np.amax(results.foodCollectedArray)

    scoreList = scoreArray[index, :, :]
    avgScoreList = np.average(scoreList, axis=1)
    lowerBound = np.percentile(scoreList, 15.9, axis=1)
    upperBound = np.percentile(scoreList, 84.1, axis=1)

    line1, = ax1.plot(commRangeList, avgScoreList, label="Average score(normalized)", color=color)
    ax1.scatter(commRangeList, avgScoreList, color=color, s=12)
    ax1.plot(commRangeList, lowerBound, alpha=0.1, color=color)
    ax1.plot(commRangeList, upperBound, alpha=0.1, color=color)
    ax1.fill_between(commRangeList, lowerBound, upperBound, alpha=0.25, color=color)

    line2, = ax1.plot(avgMaxFoodReached[index,:], linestyle="--", color="black", label="p(bestFoodReached)")
    line3, = ax1.plot(avgFoodCollected[index,:], linestyle="--", color="red", label="Average food collected(normalized)")

    ax1.set_title(f"Score vs commRange with Tmax={settings.op.tMax}, population={settings.mapSettings.creatureCount}, R={settings.mapSettings.r1}")
    ax1.set_xlim(0, np.amax(commRangeList))
    ax1.set_ylim(0, 1.05)

    ax1.set_xlabel("Maximum communication range")
    ax1.set_ylabel("Fraction")

    ax1.grid(linestyle="--", alpha=0.5)

    lines = [line1, line2, line3]
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, loc='upper right', fontsize=8)

    plt.show()



def plotCommScoreMultSizes(settingsList, resultsList, colorList, useAUC=False, plotPopulation=False):

    maxScore = 0
    xMax = 0
    yMax = 0
    for i in range(len(settingsList)):
        settings, results, color = settingsList[i], resultsList[i], colorList[i]

        if useAUC:
            scoreArray = results.uacArray / results.maxUAC
        else:
            scoreArray = results.scoreArray / results.maxScore
        commRangeList = settings.commRangeList

        scoreList = scoreArray[0, :, :]
        avgScoreList = np.average(scoreList, axis=1)

        color = colorList[i]
        if plotPopulation:
            label = f"popSize={settings.mapSettings.creatureCount}"
        else:
            label = f"{settings.mapSettings.name}(R={settings.mapSettings.r1})"

        plt.plot(commRangeList, avgScoreList, label=label, color=color)
        plt.scatter(commRangeList, avgScoreList, color=color, s=12)

        maxScore = max(maxScore, np.amax(scoreList))
        xMax = max(xMax, np.amax(commRangeList))
        yMax = max(yMax, np.amax(avgScoreList))

    if useAUC:
        metric = "AUC"
    else:
        metric = "Score"

    if plotPopulation:
        plt.title(f"{metric} vs commRange with Tmax={settings.op.tMax}, R={settings.mapSettings.r1}")
    else:
        plt.title(f"{metric} vs commRange with Tmax={settings.op.tMax}, population={settings.mapSettings.creatureCount}")

    plt.xlim(0, xMax)
    plt.ylim(0, min(yMax * 1.1, 1))

    plt.xlabel("Maximum communication range")
    plt.ylabel("Average Score / max theoretical score")

    plt.grid(linestyle="--", alpha=0.5)
    plt.legend(fontsize=8)

    plt.show()

def plotCommRangeOptimizerProgession(settings, results):


    parameterArray = results.parameterArray

    commRangeArray = np.array([[parameter.valueDict["commRange"] for parameter in parameterList] for parameterList in parameterArray])
    # plt.xticks(range(len(commRangeArray)))


    commRangeAvg = np.average(commRangeArray[3:,:])


    for i in range(commRangeArray.shape[1]):
        plt.scatter(range(len(commRangeArray)), commRangeArray[:,i], color="black",alpha=0.5)


    plt.yticks(range(int(np.amax(commRangeArray))+2))
    plt.xlim(-1, len(commRangeArray))
    plt.hlines(commRangeAvg, -10, len(commRangeArray), linestyle="--", color="red", label="average")
    plt.title(f"CommRange optimization for R={settings.mapSettings.r1}, popSize={settings.mapSettings.creatureCount}")

    plt.xlabel("Generation")
    plt.ylabel("Communication range")

    plt.grid(linestyle="--", alpha=0.5)
    plt.legend()

    plt.show()

def plotOptimalCommRange(settingsList, resultsList, nCut = 3, xPopSize=False):

    RList = []
    popSizeList = []
    commRangeList = []

    for i in range(len(settingsList)):

        settings, results = settingsList[i], resultsList[i]
        parameterArray = results.parameterArray

        commRangeArray = np.array(
            [[parameter.valueDict["commRange"] for parameter in parameterList] for parameterList in parameterArray])

        R, popSize = settings.mapSettings.r1, settings.mapSettings.creatureCount
        commRange = np.average(commRangeArray[3:, :])

        RList.append(R)
        popSizeList.append(popSize)
        commRangeList.append(commRange)

    RList, popSizeList, commRangeList = np.array(RList), np.array(popSizeList), np.array(commRangeList)

    if xPopSize:

        for R in np.unique(RList):
            cond = RList == R


            plt.plot(popSizeList[cond], commRangeList[cond], label=f"roomSize={R}")
            plt.scatter(popSizeList[cond], commRangeList[cond])

        plt.xlabel("Population Size")
    else:

        for popSize in np.unique(popSizeList):
            cond = popSizeList == popSize

            plt.plot(RList[cond], commRangeList[cond], label=f"popSize={popSize}")
            plt.scatter(RList[cond], commRangeList[cond])

        plt.xlabel("Room Size")

    plt.ylabel("Optimal Communication range")

    plt.legend()
    plt.grid(linestyle="--")
    plt.show()





if __name__ == "__main__":

    if False:
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

        settings = settingsArray[14]
        results = resultsArray[14][0]

        plotCommScoreGraphSingle(settings, results, "green")

    if False:

        indices = [11, 12, 13, 14, 15]

        settingsArray, resultsArray = readResults("CommRangeExperiment")

        settingsList = [settingsArray[i] for i in indices]
        resultsList = [resultsArray[i][0] for i in indices]
        colorList = ["red", "blue", "green", "orange", "purple"]

        plotCommScoreMultSizes(settingsList, resultsList, colorList, False)

    if False:

        indices = [14, 16, 17, 18]

        settingsArray, resultsArray = readResults("CommRangeExperiment")

        settingsList = [settingsArray[i] for i in indices]
        resultsList = [resultsArray[i][0] for i in indices]
        colorList = ["red", "blue", "green", "orange"]

        plotCommScoreMultSizes(settingsList, resultsList, colorList, True, True)

    if False:

        settingsArray, resultsArray = readResults("CommRangeOptimizer")

        index = 12
        settings = settingsArray[index]
        results = resultsArray[index][0]

        plotCommRangeOptimizerProgession(settings, results)

    if True:

        settingsArray, resultsArray = readResults("CommRangeOptimizer")

        indices = range(12, 31)
        settingsList = [settingsArray[i] for i in indices]
        resultsList = [resultsArray[i][0] for i in indices]

        plotOptimalCommRange(settingsList, resultsList, 3, True)





